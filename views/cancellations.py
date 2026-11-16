"""Page 4: Cancellations & Failures."""
import pandas as pd
import streamlit as st

from utils import charts as C
from utils import data, metrics as M
from utils import insights
from utils import theme as T

df = data.get_filtered()
data.require_data(df)
n = len(df)

T.page_header(
    "Cancellations and failures",
    "Bookings that never started (cancelled or no driver found) and rides that started but did not finish.",
)

oc = df["ride_outcome"].value_counts()
drv, cus, nod, inc = (int(oc.get(x, 0)) for x in ["Canceled by Driver", "Canceled by Customer", "Driver Not Found", "Incomplete"])
failed = drv + cus + nod
value_lost = float(df.loc[~df["completed"], "booking_value"].sum())
cus_reasons = df.loc[df["canceled_by_customer_reason"] != "Not Applicable", "canceled_by_customer_reason"].value_counts()
drv_reasons = df.loc[df["canceled_by_driver_reason"] != "Not Applicable", "canceled_by_driver_reason"].value_counts()
behaviour = int(cus_reasons.reindex(insights.DRIVER_BEHAVIOUR_REASONS).fillna(0).sum())

T.section("At a glance", "Rates are shares of all bookings in view.")
T.kpi_row([
    ("Never started", T.fmt_pct(M.share(failed, n)), f"{failed:,} bookings cancelled or without a driver"),
    ("Cancelled by drivers", T.fmt_pct(M.share(drv, n)), f"{drv:,} bookings"),
    ("Cancelled by customers", T.fmt_pct(M.share(cus, n)), f"{cus:,} bookings"),
    ("Driver not found", T.fmt_pct(M.share(nod, n)), f"{nod:,} bookings"),
])
st.write("")
T.kpi_row([
    ("Booking value lost", T.fmt_inr(value_lost), "quoted fare of every booking not completed"),
    ("Incomplete rides", T.fmt_pct(M.share(inc, n)), f"{inc:,} rides started but did not finish"),
    ("Driver cancels per customer cancel", f"{drv / cus:.2f}x" if cus else "n/a", "more than 1 means drivers cancel more"),
    ("Customer cancels citing the driver", T.fmt_pct(M.share(behaviour, cus)) if cus else "n/a", "driver not moving or asked to cancel"),
])

# ------------------------------------------------------------------ where bookings end
T.section("Where non-completed bookings end up")
c1, c2 = st.columns(2)
bad = [o for o in data.OUTCOME_ORDER if o != "Completed"]
with c1:
    with st.container(border=True):
        T.chart_title("Bookings by outcome", "Count and share of all bookings in view")
        vals = [int(oc.get(o, 0)) for o in bad]
        C.show(C.bar(bad, vals, horizontal=True, colors=[T.OUTCOME_COLORS[o] for o in bad],
                     text=[f"{v:,} ({M.share(v, n) * 100:.1f}%)" for v in vals], height=280))
with c2:
    with st.container(border=True):
        T.chart_title("Quoted booking value lost", "Share of the total lost value")
        lv = df[~df["completed"]].groupby("ride_outcome", observed=True)["booking_value"].sum().reindex(bad).fillna(0)
        C.show(C.bar(bad, lv.values, horizontal=True, colors=[T.OUTCOME_COLORS[o] for o in bad],
                     text=[f"{T.fmt_inr(v)} ({M.share(v, value_lost) * 100:.0f}%)" for v in lv.values], height=280))

# ------------------------------------------------------------------ reasons
T.section("Why bookings are cancelled", "Reasons are the labels recorded in the export. Shares add up to 100% within each chart.")
r1, r2 = st.columns(2)
with r1:
    with st.container(border=True):
        T.chart_title("Customer cancellation reasons", "Lime bars point at the driver's behaviour")
        if len(cus_reasons):
            sh = cus_reasons / cus_reasons.sum() * 100
            C.show(C.bar(sh.index, sh.values, horizontal=True, highlight=insights.DRIVER_BEHAVIOUR_REASONS,
                         fmt="{:.1f}%", height=300))
        else:
            st.info("No customer cancellations in the current view.")
with r2:
    with st.container(border=True):
        T.chart_title("Driver cancellation reasons", "Lime marks the most common reason")
        if len(drv_reasons):
            sh = drv_reasons / drv_reasons.sum() * 100
            C.show(C.bar(sh.index, sh.values, horizontal=True, highlight=[sh.index[0]], fmt="{:.1f}%", height=300))
        else:
            st.info("No driver cancellations in the current view.")

# ------------------------------------------------------------------ concentration
overall = df["failed"].mean() * 100
T.section(
    "Where failures concentrate",
    f"Failure rate is the share of bookings that never started. The shaded band is the range chance alone would produce around the overall rate of {overall:.1f}%.",
)
f1, f2 = st.columns(2)
with f1:
    with st.container(border=True):
        T.chart_title("Failure rate by vehicle type")
        vr = (df.groupby("vehicle_type")["failed"].mean() * 100).sort_values(ascending=False)
        half = C.rate_half_width(overall / 100, df.groupby("vehicle_type").size().median())
        fig = C.bar(vr.index, vr.values, highlight=[vr.index[0]], fmt="{:.1f}%", height=300,
                    axis_range=[max(overall - 15, 0), overall + 15])
        C.add_band(fig, overall, half)
        C.show(fig)
with f2:
    with st.container(border=True):
        T.chart_title("Failure rate by hour of day")
        hr = df.groupby("hour")["failed"].mean() * 100
        half = C.rate_half_width(overall / 100, df.groupby("hour").size().median())
        fig = C.lines(hr.index, [{"name": "Failure rate", "y": hr.values, "color": T.LIME}], height=300,
                      legend=False, yfmt=".1f", markers=True, y_range=[max(overall - 15, 0), overall + 15])
        fig.update_xaxes(dtick=2, title_text="Hour of day")
        C.add_band(fig, overall, half)
        C.show(fig)

f3, f4 = st.columns([6, 4])
with f3:
    with st.container(border=True):
        T.chart_title("Pickup areas with the highest failure rate", "Top 15 of all pickup areas")
        pr = (df.groupby("pickup_location")["failed"].mean() * 100).sort_values(ascending=False).head(15)
        half = C.rate_half_width(overall / 100, df.groupby("pickup_location").size().median())
        fig = C.bar(pr.index, pr.values, horizontal=True, highlight=[pr.index[0]], fmt="{:.1f}%", height=470,
                    axis_range=[0, max(pr.max() * 1.15, overall + 10)])
        C.add_band(fig, overall, half, horizontal=True)
        C.show(fig)
with f4:
    with st.container(border=True):
        T.chart_title("Why started rides did not finish", "Share of incomplete rides")
        ir = df.loc[df["incomplete_reason"] != "Not Applicable", "incomplete_reason"].value_counts()
        if len(ir):
            palette = [T.AMBER, T.SKY, T.VIOLET, T.STEEL]
            C.show(C.donut(list(ir.index), list(ir.values), palette[: len(ir)],
                           center_title=T.fmt_int(ir.sum()), center_sub="incomplete rides", height=300))
        else:
            st.info("No incomplete rides in the current view.")

top_cus = cus_reasons.index[0] if len(cus_reasons) else "n/a"
top_drv = drv_reasons.index[0] if len(drv_reasons) else "n/a"
T.takeaway(
    f"<b>{T.fmt_pct(M.share(failed, n))}</b> of bookings never started, and {T.fmt_pct(M.share(drv, n))} of all bookings were cancelled by drivers, "
    f"more than the {T.fmt_pct(M.share(cus, n))} cancelled by customers. The most common driver reason is <b>{top_drv}</b> and the most common customer reason is "
    f"<b>{top_cus}</b>. Failure rates by vehicle, hour and area all sit close to the overall rate, so the problem looks like a "
    "process issue across the whole service, not a pocket of bad hours or areas."
)
