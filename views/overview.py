"""Page 1: Overview."""
import pandas as pd
import streamlit as st

from utils import charts as C
from utils import data, metrics as M
from utils import theme as T

full = data.load_data()
df = data.get_filtered()
data.require_data(df)
k = M.kpis(df)
start, end = data.selected_range(full)

T.hero(
    "Ola ride insights | booking performance analysis",
    "Ola ride analytics",
    f"How {len(full):,} Ola bookings from {full['date'].min():%B %Y} ended, which ones failed and why, "
    "and where the booking value leaked.",
    [
        f"{len(df):,} bookings in view",
        f"{start:%d %b %Y} to {end:%d %b %Y}",
        f"{df['vehicle_type'].nunique()} vehicle types",
        f"{df['pickup_location'].nunique()} pickup areas",
    ],
)

T.section("Account summary", "Totals for the bookings currently in view. Completion rate is completed rides divided by all bookings.")
T.kpi_row([
    ("Total bookings", T.fmt_int(k["total"]), f"{k['total'] / max(k['days'], 1):,.0f} per day across {k['days']} days"),
    ("Completed rides", T.fmt_int(k["completed"]), "ran from pickup to drop"),
    ("Completion rate", T.fmt_pct(k["completion"]), "of all bookings"),
    ("Not completed", T.fmt_pct(k["not_completed"]), "cancelled, no driver found or cut short"),
])
st.write("")
T.kpi_row([
    ("Completed booking value", T.fmt_inr(k["value_completed"]), "quoted fare of completed rides"),
    ("Booking value lost", T.fmt_inr(k["value_lost"]), f"{T.fmt_pct(M.share(k['value_lost'], k['value_total']))} of all quoted value"),
    ("Avg ride distance", f"{k['avg_distance']:.1f} km", "rides that actually ran"),
    ("Avg customer rating", f"{k['avg_customer_rating']:.2f}", f"driver rating {k['avg_driver_rating']:.2f}"),
])

T.section("How bookings end", "Every booking lands in exactly one of five outcomes.")
c1, c2 = st.columns([4, 6])
with c1:
    with st.container(border=True):
        T.chart_title("Outcome mix", "Share of all bookings in view")
        oc = df["ride_outcome"].value_counts().reindex(data.OUTCOME_ORDER, fill_value=0)
        oc = oc[oc > 0]
        C.show(C.donut(
            list(oc.index), list(oc.values), [T.OUTCOME_COLORS[o] for o in oc.index],
            center_title=T.fmt_pct(k["completion"]), center_sub="completed", height=310,
        ))
with c2:
    with st.container(border=True):
        T.chart_title("Daily bookings", "All bookings against completed rides. Shaded columns are weekends.")
        daily = df.groupby("date").agg(total=("booking_id", "size"), completed=("completed", "sum")).reset_index()
        weekends = list(daily.loc[daily["date"].dt.dayofweek >= 5, "date"])
        C.show(C.lines(
            daily["date"],
            [
                {"name": "All bookings", "y": daily["total"], "color": "#8A9099"},
                {"name": "Completed", "y": daily["completed"], "color": T.LIME},
            ],
            height=310, weekend_dates=weekends, y_range=[0, float(daily["total"].max()) * 1.15],
        ))

T.section("Value and vehicles")
c3, c4 = st.columns(2)
with c3:
    with st.container(border=True):
        T.chart_title("Quoted booking value by outcome", "Booking value is the quoted fare, so the lost bars are what was quoted, not what was earned.")
        val = df.groupby("ride_outcome", observed=True)["booking_value"].sum().reindex(data.OUTCOME_ORDER).dropna()
        C.show(C.bar(
            val.index, val.values, horizontal=True, colors=[T.OUTCOME_COLORS[o] for o in val.index],
            text=[T.fmt_inr(v) for v in val.values], height=300,
        ))
with c4:
    with st.container(border=True):
        T.chart_title("Bookings by vehicle type", "Lime marks the busiest type.")
        vt = df["vehicle_type"].value_counts()
        C.show(C.bar(vt.index, vt.values, highlight=[vt.index[0]], height=300))

counts = df["ride_outcome"].value_counts()
drv, cus = int(counts.get("Canceled by Driver", 0)), int(counts.get("Canceled by Customer", 0))
T.takeaway(
    f"<b>{T.fmt_pct(k['completion'])}</b> of the bookings in view finished as a completed ride. The other "
    f"{T.fmt_pct(k['not_completed'])} carried <b>{T.fmt_inr(k['value_lost'])}</b> of quoted fare "
    f"({T.fmt_pct(M.share(k['value_lost'], k['value_total']))} of everything quoted). "
    f"Drivers cancelled {drv:,} bookings against {cus:,} cancelled by customers. "
    "The Cancellations page breaks this down, and Findings explains how far the data can be trusted."
)
