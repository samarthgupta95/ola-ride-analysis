"""Numbers behind the Findings page. Everything is calculated from the full dataset when the page loads."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

from .data import load_data

DRIVER_BEHAVIOUR_REASONS = ["Driver is not moving towards pickup location", "Driver asked to cancel"]


def _chi_p(df: pd.DataFrame, col: str) -> float:
    return float(stats.chi2_contingency(pd.crosstab(df[col], df["completed"]))[1])


def _anova_p(df: pd.DataFrame, value: str, by: str) -> float:
    groups = [g[value].dropna().values for _, g in df.groupby(by, observed=True)]
    return float(stats.f_oneway(*groups)[1])


@st.cache_data(show_spinner="Calculating findings")
def compute() -> dict:
    df = load_data()
    n = len(df)
    ran = df[df["ran"]]
    f: dict = {"n": n, "customers": df["customer_id"].nunique(), "days": df["date"].nunique()}

    # headline
    f["completed"] = int(df["completed"].sum())
    f["completion"] = f["completed"] / n
    f["value_total"] = float(df["booking_value"].sum())
    f["value_lost"] = float(df.loc[~df["completed"], "booking_value"].sum())
    f["value_lost_share"] = f["value_lost"] / f["value_total"]
    f["value_by_outcome"] = df.groupby("ride_outcome", observed=True)["booking_value"].sum().to_dict()
    f["count_by_outcome"] = df["ride_outcome"].value_counts().to_dict()

    # who cancels
    f["driver_cancels"] = int((df["ride_outcome"] == "Canceled by Driver").sum())
    f["customer_cancels"] = int((df["ride_outcome"] == "Canceled by Customer").sum())
    f["no_driver"] = int((df["ride_outcome"] == "Driver Not Found").sum())
    f["incomplete"] = int((df["ride_outcome"] == "Incomplete").sum())
    f["driver_cancel_ratio"] = f["driver_cancels"] / f["customer_cancels"]
    f["driver_cancel_value_share"] = f["value_by_outcome"]["Canceled by Driver"] / f["value_lost"]

    drv = df.loc[df["canceled_by_driver_reason"] != "Not Applicable", "canceled_by_driver_reason"].value_counts()
    cus = df.loc[df["canceled_by_customer_reason"] != "Not Applicable", "canceled_by_customer_reason"].value_counts()
    f["driver_reasons"] = (drv / drv.sum()).to_dict()
    f["customer_reasons"] = (cus / cus.sum()).to_dict()
    f["top_driver_reason"], f["top_driver_reason_share"] = next(iter(f["driver_reasons"].items()))
    f["driver_behaviour_share"] = float(sum(f["customer_reasons"].get(r, 0) for r in DRIVER_BEHAVIOUR_REASONS))

    inc = df.loc[df["incomplete_reason"] != "Not Applicable", "incomplete_reason"].value_counts()
    f["incomplete_reasons"] = (inc / inc.sum()).to_dict()

    # no pattern: tests of completion against every factor in the export
    tests = {
        "Vehicle type": _chi_p(df, "vehicle_type"),
        "Hour of day": _chi_p(df, "hour"),
        "Day of week": _chi_p(df, "day_name"),
        "Weekend vs weekday": _chi_p(df, "is_weekend"),
        "Pickup location": _chi_p(df, "pickup_location"),
        "Drop location": _chi_p(df, "drop_location"),
        "Customer rating by vehicle type": _anova_p(ran, "customer_rating", "vehicle_type"),
        "Customer rating by payment method": _anova_p(ran, "customer_rating", "payment_method"),
        "Driver rating by vehicle type": _anova_p(ran, "driver_ratings", "vehicle_type"),
    }
    f["tests"] = tests
    f["n_tests"] = len(tests)
    f["below_05"] = sum(p < 0.05 for p in tests.values())
    f["expected_by_chance"] = 0.05 * len(tests)
    f["survive_bonferroni"] = sum(p < 0.05 / len(tests) for p in tests.values())
    f["closest_test"], f["closest_p"] = min(tests.items(), key=lambda kv: kv[1])
    comp = df.groupby("vehicle_type")["completed"].mean() * 100
    f["completion_min"], f["completion_max"] = float(comp.min()), float(comp.max())
    hourly = df.groupby("hour")["completed"].mean() * 100
    f["hour_completion_min"], f["hour_completion_max"] = float(hourly.min()), float(hourly.max())

    # daily and weekday demand
    daily = df.groupby("date").size()
    f["daily_min"], f["daily_max"], f["daily_mean"] = int(daily.min()), int(daily.max()), float(daily.mean())
    occ = pd.Series(pd.date_range(df["date"].min(), df["date"].max()).day_name()).value_counts()
    per_day = df.groupby("day_name", observed=True).size() / occ.reindex(df.groupby("day_name", observed=True).size().index)
    f["weekday_avg_min"], f["weekday_avg_max"] = float(per_day.min()), float(per_day.max())
    f["max_occurrence"], f["min_occurrence"] = int(occ.max()), int(occ.min())

    # vehicles and fares
    dist = ran.groupby("vehicle_type")["ride_distance"].mean()
    f["auto_distance"] = float(dist.get("Auto", np.nan))
    f["other_distance"] = float(ran.loc[ran["vehicle_type"] != "Auto", "ride_distance"].mean())
    f["auto_fare"] = float(df.loc[df["completed"] & (df["vehicle_type"] == "Auto"), "booking_value"].mean())
    f["other_fare"] = float(df.loc[df["completed"] & (df["vehicle_type"] != "Auto"), "booking_value"].mean())
    f["fare_distance_corr"] = float(ran["booking_value"].corr(ran["ride_distance"]))
    f["driver_cust_rating_corr"] = float(ran["driver_ratings"].corr(ran["customer_rating"]))
    f["rating_min"] = float(ran["customer_rating"].min())
    f["same_pickup_drop"] = float(df["same_pickup_drop"].mean())

    # payments
    pay = ran["payment_method"].value_counts(normalize=True)
    f["payment_mix"] = pay.to_dict()
    f["cash"], f["upi"] = float(pay.get("Cash", 0)), float(pay.get("UPI", 0))
    f["cards"] = float(pay.get("Credit Card", 0) + pay.get("Debit Card", 0))

    # customers
    counts = df["customer_id"].value_counts()
    f["single_booking_share"] = float((counts == 1).mean())
    return f
