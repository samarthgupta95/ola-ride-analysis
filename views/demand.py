"""Page 3: Demand & Timing."""
import pandas as pd
import streamlit as st

from utils import charts as C
from utils import data, metrics as M
from utils import theme as T

full = data.load_data()
df = data.get_filtered()
data.require_data(df)
start, end = data.selected_range(full)
n_days = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
occ = M.weekday_occurrences(start, end)

T.page_header(
    "Demand and timing",
    "When bookings arrive. Weekday figures are averages per day, because months do not contain equal numbers of each weekday.",
)

day_tot = df.groupby("day_name", observed=True).size().reindex(data.DAY_ORDER, fill_value=0)
present = [d for d in data.DAY_ORDER if day_tot[d] > 0 and occ[d] > 0]
per_day = (day_tot[present] / occ[present])
hour_tot = df.groupby("hour").size().reindex(range(24), fill_value=0)
hour_avg = hour_tot / n_days
peak_hour = int(hour_avg.idxmax())
wk_days = int(sum(1 for d in pd.date_range(start, end) if d.dayofweek < 5))
we_days = n_days - wk_days
wk_avg = df.loc[~df["is_weekend"]].shape[0] / wk_days if wk_days else float("nan")
we_avg = df.loc[df["is_weekend"]].shape[0] / we_days if we_days else float("nan")

T.section("At a glance")
T.kpi_row([
    ("Avg bookings per day", f"{len(df) / n_days:,.0f}", f"{n_days} days in the selected range"),
    ("Busiest weekday", per_day.idxmax(), f"{per_day.max():,.0f} bookings per day"),
    ("Quietest weekday", per_day.idxmin(), f"{per_day.min():,.0f} bookings per day"),
    ("Peak hour", f"{peak_hour:02d}:00", f"{hour_avg.max():,.0f} bookings per day"),
])

T.section("Daily trend")
with st.container(border=True):
    T.chart_title("Bookings per day", "Shaded columns are weekends. Dotted line is the average day.")
    daily = df.groupby("date").size().reset_index(name="bookings")
    weekends = list(daily.loc[daily["date"].dt.dayofweek >= 5, "date"])
    fig = C.lines(daily["date"], [{"name": "Bookings", "y": daily["bookings"], "color": T.LIME}],
                  height=300, weekend_dates=weekends, legend=False, y_range=[0, float(daily["bookings"].max()) * 1.18])
    fig.add_hline(y=float(daily["bookings"].mean()), line_dash="dot", line_color=T.MUTED, line_width=1)
    C.show(fig)

T.section("Weekday and hour patterns")
c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        T.chart_title("Bookings by weekday")
        raw = st.toggle("Show raw totals instead of per-day averages", value=False,
                        help="Raw totals favour weekdays that occur five times in the month. Averages remove that effect.")
        if raw:
            vals, fmt = day_tot[present], "{:,.0f}"
            st.caption("Raw totals: a weekday that appears five times in the month looks busier only because it appears more often.")
        else:
            vals, fmt = per_day, "{:,.0f}"
            st.caption("Average bookings on one such day. Lime marks the highest.")
        C.show(C.bar(vals.index, vals.values, highlight=[vals.idxmax()], fmt=fmt, height=290))
with c2:
    with st.container(border=True):
        T.chart_title("Bookings by hour of day", "Average bookings in each hour on a typical day. Lime marks the peak hour.")
        C.show(C.bar([f"{h:02d}" for h in hour_avg.index], hour_avg.values, highlight=[f"{peak_hour:02d}"],
                     fmt="{:,.0f}", height=320))

with st.container(border=True):
    T.chart_title("Weekday by hour", "Average bookings per day for each weekday and hour. The scale starts at zero, so an even colour means even demand.")
    pv = df.pivot_table(index="day_name", columns="hour", values="booking_id", aggfunc="count", observed=True).reindex(index=present, columns=range(24)).fillna(0)
    pv = pv.div(occ[present], axis=0)
    C.show(C.heatmap(pv.values.tolist(), list(range(24)), present, height=320))

T.section("Time of day and day type")
c3, c4 = st.columns(2)
with c3:
    with st.container(border=True):
        T.chart_title("Bookings per hour by time-of-day window", "Windows have different lengths, so each is divided by its hours. Lime marks the highest.")
        tod = df.groupby("time_of_day", observed=True).size().reindex(data.TOD_ORDER, fill_value=0)
        per_hour = pd.Series({w: tod[w] / (data.TOD_HOURS[w] * n_days) for w in data.TOD_ORDER})
        labels = [f"{w} ({data.TOD_HOURS[w]} h)" for w in per_hour.index]
        top = labels[int(per_hour.values.argmax())]
        C.show(C.bar(labels, per_hour.values, highlight=[top], fmt="{:,.0f}", height=290))
with c4:
    with st.container(border=True):
        T.chart_title("Outcome mix: weekdays and weekends", "Share of bookings by outcome")
        tmp = df.assign(day_type=df["is_weekend"].map({True: "Weekend", False: "Weekday"}))
        mix = pd.crosstab(tmp["day_type"], tmp["ride_outcome"], normalize="index") * 100
        mix = mix[[o for o in data.OUTCOME_ORDER if o in mix.columns]]
        C.show(C.stacked_share(list(mix.index), {o: list(mix[o]) for o in mix.columns}, T.OUTCOME_COLORS, height=290))

spread = (per_day.max() - per_day.min()) / per_day.mean() * 100
note = ""
if occ.max() != occ.min():
    note = (f" Raw weekday totals look uneven only because this range holds {int(occ.max())} of some weekdays "
            f"and {int(occ.min())} of others, which is why the page uses per-day averages.")
T.takeaway(
    f"Demand is <b>steady</b>. Weekday averages sit between {per_day.min():,.0f} and {per_day.max():,.0f} bookings per day "
    f"(a {spread:.0f}% spread), hourly demand barely moves, and weekdays average {wk_avg:,.0f} bookings against {we_avg:,.0f} on weekends.{note} "
    "There is no rush hour to staff for in this export, and the Findings page covers why that is a data limitation as much as a business fact."
)
