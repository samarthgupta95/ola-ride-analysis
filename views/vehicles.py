"""Page 2: Vehicles, Payments & Ratings."""
import pandas as pd
import streamlit as st

from utils import charts as C
from utils import data, metrics as M
from utils import theme as T

df = data.get_filtered()
data.require_data(df)
ran = df[df["ran"]]

T.page_header(
    "Vehicles, payments and ratings",
    "How each vehicle type performs, how riders pay, and how drivers and customers rate the rides that ran.",
)

# ------------------------------------------------------------------ vehicle cards
g = df.groupby("vehicle_type").agg(
    bookings=("booking_id", "size"),
    completion=("completed", "mean"),
    distance=("ride_distance", "mean"),
    rating=("customer_rating", "mean"),
).sort_values("bookings", ascending=False)

T.section("Vehicle types", "One card per type, ordered by number of bookings.")
T.vehicle_cards([
    {
        "name": name,
        "stats": [
            ("Bookings", f"{int(r.bookings):,}"),
            ("Completion", T.fmt_pct(r.completion)),
            ("Avg distance", f"{r.distance:.1f} km" if pd.notna(r.distance) else "n/a"),
            ("Avg rating", f"{r.rating:.2f}" if pd.notna(r.rating) else "n/a"),
        ],
    }
    for name, r in g.iterrows()
])

# ------------------------------------------------------------------ performance
T.section("Performance by vehicle type")
c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        T.chart_title("Completed booking value", "Quoted fare of completed rides. Lime marks the highest.")
        v = df[df["completed"]].groupby("vehicle_type")["booking_value"].sum().sort_values(ascending=False)
        C.show(C.bar(v.index, v.values, highlight=[v.index[0]], text=[T.fmt_inr(x) for x in v.values], height=300))
with c2:
    with st.container(border=True):
        T.chart_title("Average ride distance (km)", "Rides that actually ran. Lime marks the shortest.")
        d = ran.groupby("vehicle_type")["ride_distance"].mean().sort_values(ascending=False)
        C.show(C.bar(d.index, d.values, highlight=[d.index[-1]], fmt="{:.1f}", height=300))

c3, c4 = st.columns(2)
with c3:
    with st.container(border=True):
        T.chart_title("Completion rate", "Axis starts at zero on purpose. Differences between types are small, see Findings.")
        cr = (df.groupby("vehicle_type")["completed"].mean() * 100).sort_values(ascending=False)
        C.show(C.bar(cr.index, cr.values, highlight=[cr.index[0]], fmt="{:.1f}%", axis_range=[0, 100], height=300))
with c4:
    with st.container(border=True):
        T.chart_title("Average fare per completed ride", "Quoted fare in Rs. Lime marks the highest.")
        fare = df[df["completed"]].groupby("vehicle_type")["booking_value"].mean().sort_values(ascending=False)
        C.show(C.bar(fare.index, fare.values, highlight=[fare.index[0]], fmt="Rs {:,.0f}", height=300))

# ------------------------------------------------------------------ payments
T.section("Payments", "Payment method is recorded only for rides that ran.")
p1, p2 = st.columns([4, 6])
with p1:
    with st.container(border=True):
        T.chart_title("Payment method mix", "Share of rides that ran")
        pm = ran["payment_method"].value_counts()
        C.show(C.donut(
            list(pm.index), list(pm.values), [T.PAYMENT_COLORS.get(x, T.GREY) for x in pm.index],
            center_title=T.fmt_int(len(ran)), center_sub="rides", height=310,
        ))
with p2:
    with st.container(border=True):
        T.chart_title("Payment method by vehicle type", "Each bar adds up to 100% of that vehicle's rides.")
        ct = pd.crosstab(ran["vehicle_type"], ran["payment_method"], normalize="index") * 100
        order = [m for m in pm.index if m in ct.columns]
        ct = ct.loc[g.index.intersection(ct.index)]
        C.show(C.stacked_share(
            list(ct.index), {m: list(ct[m]) for m in order}, T.PAYMENT_COLORS, height=310,
        ))

# ------------------------------------------------------------------ ratings
T.section("Ratings", "Ratings exist only for rides that ran, and every rating in the export sits between 3.0 and 5.0.")
r1, r2 = st.columns(2)
with r1:
    with st.container(border=True):
        T.chart_title("Customer rating distribution", f"Average {ran['customer_rating'].mean():.2f}")
        C.show(C.hist(ran["customer_rating"].dropna(), T.LIME, "Customer rating"))
with r2:
    with st.container(border=True):
        T.chart_title("Driver rating distribution", f"Average {ran['driver_ratings'].mean():.2f}")
        C.show(C.hist(ran["driver_ratings"].dropna(), T.SKY, "Driver rating"))

r3, r4 = st.columns(2)
with r3:
    with st.container(border=True):
        T.chart_title("Average rating by vehicle type", "Scale runs from 0 to 5 so small gaps are not exaggerated.")
        ar = ran.groupby("vehicle_type")[["customer_rating", "driver_ratings"]].mean().loc[g.index.intersection(ran["vehicle_type"].unique())]
        fig = C.go.Figure()
        fig.add_trace(C.go.Bar(name="Customer rating", x=list(ar.index), y=list(ar["customer_rating"]), marker_color=T.LIME,
                               text=[f"{x:.2f}" for x in ar["customer_rating"]], textposition="outside", cliponaxis=False,
                               textfont=dict(color=T.TEXT, size=10)))
        fig.add_trace(C.go.Bar(name="Driver rating", x=list(ar.index), y=list(ar["driver_ratings"]), marker_color=T.SKY,
                               text=[f"{x:.2f}" for x in ar["driver_ratings"]], textposition="outside", cliponaxis=False,
                               textfont=dict(color=T.TEXT, size=10)))
        C.style(fig, 300, legend=True)
        fig.update_layout(barmode="group", bargap=0.3)
        fig.update_yaxes(range=[0, 5.6], showticklabels=False)
        fig.update_xaxes(showgrid=False)
        C.show(fig)
with r4:
    with st.container(border=True):
        corr = ran["booking_value"].corr(ran["ride_distance"])
        T.chart_title("Does the fare follow distance?", f"Median fare by distance band. Correlation between fare and distance is {corr:+.2f}.")
        bands = pd.cut(ran["ride_distance"], [0, 5, 10, 20, 30, 40, 50],
                       labels=["1 to 5 km", "6 to 10 km", "11 to 20 km", "21 to 30 km", "31 to 40 km", "41 to 50 km"])
        mf = ran.groupby(bands, observed=True)["booking_value"].median()
        C.show(C.bar(mf.index, mf.values, fmt="Rs {:,.0f}", height=300))

best = v.index[0]
shortest = d.index[-1]
T.takeaway(
    f"<b>{best}</b> brings in the most completed booking value, and <b>{shortest}</b> rides are the shortest at "
    f"{d.iloc[-1]:.1f} km against {ran.loc[ran['vehicle_type'] != shortest, 'ride_distance'].mean():.1f} km for the rest. "
    f"Completion, fares and ratings are nearly the same across types. The fare does not move with distance "
    f"(correlation {corr:+.2f}), which is unusual for a taxi service and is treated as a data limitation, not a business finding."
)
