"""Data loading, sidebar filters and the in-memory DuckDB table behind the SQL playground."""
from __future__ import annotations

import re
import threading
import time
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

from .compat import stretch

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "ola_data_clean.parquet"   # compact copy of ola_data_clean.csv (about 3 MB)
TABLE = "ola_data_clean"

OUTCOME_ORDER = ["Completed", "Incomplete", "Canceled by Driver", "Canceled by Customer", "Driver Not Found"]
NEVER_STARTED = ["Canceled by Driver", "Canceled by Customer", "Driver Not Found"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TOD_ORDER = ["Late Night", "Morning", "Afternoon", "Evening", "Night"]
TOD_HOURS = {"Late Night": 5, "Morning": 7, "Afternoon": 5, "Evening": 4, "Night": 3}  # hours in each window

LOAD_COLUMNS = [
    "booking_id", "booking_datetime", "hour", "day_name", "day_of_week", "is_weekend", "time_of_day",
    "customer_id", "vehicle_type", "pickup_location", "drop_location", "same_pickup_drop",
    "booking_status", "ride_outcome", "canceled_by_customer_reason", "canceled_by_driver_reason",
    "incomplete_rides", "incomplete_reason", "v_tat", "c_tat", "booking_value", "ride_distance",
    "payment_method", "driver_ratings", "customer_rating",
]


# ------------------------------------------------------------------ loading
@st.cache_data(show_spinner="Loading data")
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(
            f"Data file not found: data/{DATA_PATH.name}. Run notebooks/OLA_Data_Preprocessing.ipynb to create it, "
            "or copy it into the data folder of the repository."
        )
        st.stop()
    df = pd.read_parquet(DATA_PATH, columns=LOAD_COLUMNS)
    df["booking_datetime"] = pd.to_datetime(df["booking_datetime"])
    for col in ["vehicle_type", "pickup_location", "drop_location", "booking_status", "payment_method",
                "incomplete_rides", "incomplete_reason", "canceled_by_customer_reason", "canceled_by_driver_reason"]:
        df[col] = df[col].astype(str).where(df[col].notna(), None)
    df["date"] = df["booking_datetime"].dt.normalize()
    df["ride_outcome"] = pd.Categorical(df["ride_outcome"], categories=OUTCOME_ORDER, ordered=True)
    df["day_name"] = pd.Categorical(df["day_name"], categories=DAY_ORDER, ordered=True)
    df["time_of_day"] = pd.Categorical(df["time_of_day"], categories=TOD_ORDER, ordered=True)
    df["completed"] = df["ride_outcome"] == "Completed"
    df["failed"] = df["ride_outcome"].isin(NEVER_STARTED)       # cancelled or no driver found
    df["ran"] = df["booking_status"] == "Success"                # a ride actually started
    return df


def date_bounds(df: pd.DataFrame):
    return df["date"].min().date(), df["date"].max().date()


# ------------------------------------------------------------------ filters
def _all_vehicles(df: pd.DataFrame) -> list[str]:
    return sorted(df["vehicle_type"].unique())


def selected_range(df: pd.DataFrame):
    """Start and end date currently selected in the sidebar (falls back to the full range)."""
    lo, hi = date_bounds(df)
    val = st.session_state.get("f_dates")
    if isinstance(val, (tuple, list)) and len(val) == 2:
        return val[0], val[1]
    return lo, hi


@st.cache_data(show_spinner=False)
def _apply(start, end, vehicles: tuple, outcomes: tuple, daytype: str) -> pd.DataFrame:
    df = load_data()
    mask = (df["date"] >= pd.Timestamp(start)) & (df["date"] <= pd.Timestamp(end))
    mask &= df["vehicle_type"].isin(vehicles)
    mask &= df["ride_outcome"].isin(outcomes)
    if daytype == "Weekdays":
        mask &= ~df["is_weekend"]
    elif daytype == "Weekends":
        mask &= df["is_weekend"]
    return df.loc[mask]


def get_filtered() -> pd.DataFrame:
    df = load_data()
    s = st.session_state
    start, end = selected_range(df)
    vehicles = tuple(s.get("f_vehicle", _all_vehicles(df)))
    outcomes = tuple(s.get("f_outcome", OUTCOME_ORDER))
    return _apply(start, end, vehicles, outcomes, s.get("f_daytype", "All days"))


def require_data(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("No bookings match the current filters. Widen the filters in the sidebar to see this page.")
        st.stop()


def _reset_filters() -> None:
    df = load_data()
    lo, hi = date_bounds(df)
    st.session_state["f_dates"] = (lo, hi)
    st.session_state["f_vehicle"] = _all_vehicles(df)
    st.session_state["f_outcome"] = list(OUTCOME_ORDER)
    st.session_state["f_daytype"] = "All days"


def render_sidebar_filters() -> None:
    df = load_data()
    lo, hi = date_bounds(df)
    st.markdown("<div class='side-title'>Filters</div>", unsafe_allow_html=True)
    st.date_input("Booking dates", value=(lo, hi), min_value=lo, max_value=hi, key="f_dates", format="DD/MM/YYYY")
    st.multiselect("Vehicle type", _all_vehicles(df), default=_all_vehicles(df), key="f_vehicle")
    st.multiselect("Ride outcome", OUTCOME_ORDER, default=OUTCOME_ORDER, key="f_outcome")
    st.selectbox("Day type", ["All days", "Weekdays", "Weekends"], key="f_daytype")
    n = len(get_filtered())
    st.markdown(
        f"<div class='count-card'><b>{n:,}</b> <span>of {len(df):,} bookings in view</span></div>",
        unsafe_allow_html=True,
    )
    st.button("Reset filters", on_click=_reset_filters, **stretch(st.button))
    st.markdown(
        "<div class='side-note'>Filters apply to Overview, Vehicles, Demand and Cancellations. "
        "The SQL playground and the Findings page always use the full dataset.</div>",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------ DuckDB (SQL playground)
@st.cache_resource(show_spinner=False)
def get_duck():
    """One in-memory DuckDB database holding the cleaned table, locked down after loading."""
    con = duckdb.connect(":memory:")
    path = DATA_PATH.as_posix().replace("'", "''")
    con.execute(f"CREATE TABLE {TABLE} AS SELECT * FROM read_parquet('{path}')")
    for stmt in ("SET enable_external_access=false", "SET lock_configuration=true"):
        try:
            con.execute(stmt)
        except Exception:
            pass
    return con


_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|attach|detach|copy|export|import|install|load|"
    r"pragma|call|set|reset|truncate|vacuum|checkpoint|grant|revoke|merge|use|begin|commit|rollback)\b",
    re.IGNORECASE,
)


def validate_sql(sql: str) -> tuple[str | None, str]:
    """Return (error message or None, cleaned query without trailing semicolon)."""
    if not sql or not sql.strip():
        return "Type a query first.", ""
    if len(sql) > 5000:
        return "That query is too long (limit 5,000 characters).", ""
    cleaned = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    cleaned = re.sub(r"--[^\n]*", " ", cleaned).strip().rstrip(";").strip()
    if not cleaned:
        return "Type a query first.", ""
    if ";" in re.sub(r"'(?:[^']|'')*'", "''", cleaned):
        return "Run one statement at a time (remove the extra semicolon).", ""
    if not re.match(r"(?is)^(select|with|from)\b", cleaned):
        return "Only read-only queries are allowed. Start with SELECT or WITH.", ""
    bare = re.sub(r"'(?:[^']|'')*'", "''", cleaned)
    hit = _FORBIDDEN.search(bare)
    if hit:
        return f"This playground is read-only, so the keyword '{hit.group(1).upper()}' is not allowed.", ""
    return None, cleaned


def run_query(sql: str, limit: int = 1000, timeout: int = 15) -> dict:
    """Run a validated read-only query. Returns rows (capped), total row count and runtime."""
    cur = get_duck().cursor()
    timer = threading.Timer(timeout, cur.interrupt)
    timer.start()
    started = time.perf_counter()
    try:
        total = cur.execute(f"SELECT COUNT(*) FROM ({sql}) AS _q").fetchone()[0]
        result = cur.execute(f"SELECT * FROM ({sql}) AS _q LIMIT {int(limit)}").fetchdf()
    finally:
        timer.cancel()
        cur.close()
    return {"df": result, "total": int(total), "seconds": time.perf_counter() - started}
