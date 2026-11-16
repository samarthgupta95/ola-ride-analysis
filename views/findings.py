"""Page 6: Findings & Recommendations."""
import streamlit as st

from utils import charts as C
from utils import data, insights
from utils import theme as T

f = insights.compute()
pct = lambda x, d=1: f"{x * 100:.{d}f}%"  # noqa: E731

T.page_header(
    "Findings and recommendations",
    "Every number on this page is calculated from the full dataset when the page loads and does not change with the sidebar filters.",
)

# ------------------------------------------------------------------ findings
T.section("Key findings", "Each card says how strong its evidence is, and what the data cannot tell us.")
T.card_grid([
    {
        "tag": "Headline", "color": T.LIME,
        "title": f"{(1 - f['completion']) * 100:.0f}% of bookings do not complete",
        "body": (f"Only <b>{pct(f['completion'])}</b> of {f['n']:,} bookings ended as a completed ride. The rest carried "
                 f"<b>{T.fmt_inr(f['value_lost'])}</b> of quoted fare, which is {pct(f['value_lost_share'])} of everything quoted."),
        "foot_label": "Evidence:", "foot_text": "strong. These are counts from the export. Quoted fare is not the same as revenue.",
    },
    {
        "tag": "Drivers", "color": T.RED,
        "title": "Drivers cancel more than customers do",
        "body": (f"Drivers cancelled <b>{f['driver_cancels']:,}</b> bookings against <b>{f['customer_cancels']:,}</b> for customers, "
                 f"{f['driver_cancel_ratio']:.2f} times as many. Driver cancellations alone are {pct(f['driver_cancel_value_share'], 0)} of the lost quoted value. "
                 f"The most common recorded reason is <b>{f['top_driver_reason']}</b> ({pct(f['top_driver_reason_share'])})."),
        "foot_label": "Evidence:", "foot_text": "strong for the counts. Why drivers cancel beyond the recorded reason is not in the data.",
    },
    {
        "tag": "Customers", "color": T.VIOLET,
        "title": f"{pct(f['driver_behaviour_share'], 0)} of customer cancellations point at the driver",
        "body": (f"Of every 100 customer cancellations, <b>{f['driver_behaviour_share'] * 100:.0f}</b> say the driver was not moving towards "
                 "the pickup or asked the customer to cancel. Many customer cancellations are therefore a driver problem recorded on the customer side."),
        "foot_label": "Evidence:", "foot_text": "strong for the numbers. Reasons are recorded labels and were not verified.",
    },
    {
        "tag": "Signal", "color": T.SKY,
        "title": "Nothing in the export explains why bookings fail",
        "body": (f"{f['n_tests']} tests across vehicle type, hour, weekday, weekend, pickup, drop and ratings found <b>{f['below_05']}</b> below p = 0.05 "
                 f"(about {f['expected_by_chance']:.1f} expected by chance) and <b>{f['survive_bonferroni']}</b> that survive correction for running {f['n_tests']} tests. "
                 f"The closest is {f['closest_test'].lower()} (p = {f['closest_p']:.3f}). Completion rate only ranges from {f['completion_min']:.1f}% to {f['completion_max']:.1f}% across vehicle types."),
        "foot_label": "Evidence:", "foot_text": "strong that effects are small or absent. This is a statement about this export, not about Ola in general.",
    },
    {
        "tag": "Vehicles and fares", "color": T.AMBER,
        "title": "Auto rides are much shorter but cost about the same",
        "body": (f"Auto rides average <b>{f['auto_distance']:.1f} km</b> against {f['other_distance']:.1f} km for other types, yet the average completed fare is "
                 f"Rs {f['auto_fare']:,.0f} against Rs {f['other_fare']:,.0f}. Across all rides, fare and distance have a correlation of {f['fare_distance_corr']:+.2f}."),
        "foot_label": "Evidence:", "foot_text": "strong for the numbers. A fare that ignores distance points to simulated data or flat pricing, so do not read revenue per km into it.",
    },
    {
        "tag": "Payments", "color": T.LIME,
        "title": "Cash still leads, with UPI close behind",
        "body": (f"Of rides that ran, <b>{pct(f['cash'])}</b> were paid in cash, <b>{pct(f['upi'])}</b> by UPI and {pct(f['cards'])} by cards. "
                 "The mix is almost identical across vehicle types."),
        "foot_label": "Evidence:", "foot_text": "strong. There is no cost-to-serve data, so nothing here says which method is better for Ola.",
    },
    {
        "tag": "Demand", "color": T.STEEL,
        "title": "Demand is steady, with no rush hour",
        "body": (f"Bookings per day stay between {f['daily_min']:,} and {f['daily_max']:,}. Weekday averages sit between {f['weekday_avg_min']:,.0f} and "
                 f"{f['weekday_avg_max']:,.0f} once each weekday is divided by how often it occurs in the month. Completion rate by hour only ranges from "
                 f"{f['hour_completion_min']:.1f}% to {f['hour_completion_max']:.1f}%."),
        "foot_label": "Evidence:", "foot_text": "strong for this month. One month cannot show seasonality or growth.",
    },
    {
        "tag": "Repeat riders", "color": T.SKY,
        "title": "Almost every customer booked once",
        "body": (f"{f['customers']:,} customer IDs made {f['n']:,} bookings, and <b>{pct(f['single_booking_share'])}</b> of customers booked exactly once. "
                 "Repeat behaviour and retention cannot be studied with this export."),
        "foot_label": "Evidence:", "foot_text": "strong. A real month of Ola data would show far more repeat riders.",
    },
])

# ------------------------------------------------------------------ recommendations
T.section("Business recommendations", "Each one follows from a finding above. They are patterns in the data, not proven causes, and each says how strong its support is.")
T.card_grid([
    {
        "tag": "Data-backed", "color": T.LIME,
        "title": "Cut driver cancellations first",
        "body": (f"They are the biggest leak: {f['driver_cancel_ratio']:.2f} times the customer figure and {pct(f['driver_cancel_value_share'], 0)} of lost value. "
                 f"The top recorded reason is {f['top_driver_reason'].lower()}, so start with driver readiness: an availability and vehicle check at the start of a shift, "
                 "and a prompt before a driver accepts a ride they may not be able to take."),
        "foot_label": "Success measure:", "foot_text": "driver cancellations fall below customer cancellations as a share of bookings.",
    },
    {
        "tag": "Data-backed", "color": T.LIME,
        "title": "Treat many customer cancellations as a driver problem",
        "body": (f"{pct(f['driver_behaviour_share'], 0)} of customer cancellations cite the driver not moving or asking to cancel. Live alerts when a driver is "
                 "not heading to the pickup, and flagging drivers who ask riders to cancel, go after the cause directly."),
        "foot_label": "How to use it:", "foot_text": "report these two reasons separately from genuine changes of mind by the customer.",
    },
    {
        "tag": "Data-backed", "color": T.LIME,
        "title": "Do not target by hour, vehicle type or area",
        "body": (f"Failure rates are flat across vehicle types ({f['completion_min']:.1f}% to {f['completion_max']:.1f}% completion) and across hours. "
                 "Time-of-day incentives or area-specific fixes would have little to act on in this data. Fix the process first, then look for pockets "
                 "once request-level supply data exists."),
        "foot_label": "Next step:", "foot_text": "add driver supply and request-time data to the export.",
    },
    {
        "tag": "Reasoned, not measured", "color": T.AMBER,
        "title": "Recover 'driver not found' bookings before the customer gives up",
        "body": (f"{f['no_driver']:,} bookings ({pct(f['no_driver'] / f['n'])}) ended with no driver found. A wider search radius, a retry with a nearby vehicle type, "
                 "or an offer to wait are cheap things to try."),
        "foot_label": "How to test:", "foot_text": "run an automatic retry on a small random share of bookings and compare completion rates.",
    },
    {
        "tag": "Data gap", "color": T.RED,
        "title": "Audit the fare logic before any pricing work",
        "body": (f"Fare does not move with distance (correlation {f['fare_distance_corr']:+.2f}) and Auto rides cost about as much as much longer rides. "
                 "Confirm whether this is a flat fare, a quote field or an export artefact before drawing any pricing or revenue-per-km conclusion."),
        "foot_label": "Next step:", "foot_text": "get the fare components (base, distance, time, surge) from the source system.",
    },
    {
        "tag": "Reasoned, not measured", "color": T.AMBER,
        "title": "Test nudges that move cash riders to UPI",
        "body": (f"Cash is {pct(f['cash'], 0)} of rides and UPI {pct(f['upi'], 0)}. Moving riders to digital payment may cut cash handling, "
                 "but this export has no cost data, so the benefit is not measured here."),
        "foot_label": "How to test:", "foot_text": "offer a small UPI incentive to a random group of cash riders and compare rides and cancellations.",
    },
])

# ------------------------------------------------------------------ chart and limitations
T.section("Where the quoted value went")
left, right = st.columns([4, 6])
with left:
    with st.container(border=True):
        T.chart_title("Quoted booking value by outcome", "Share of everything quoted")
        order = [o for o in data.OUTCOME_ORDER if o in f["value_by_outcome"]]
        vals = [f["value_by_outcome"][o] for o in order]
        C.show(C.bar(order, vals, horizontal=True, colors=[T.OUTCOME_COLORS[o] for o in order],
                     text=[f"{T.fmt_inr(v)} ({v / f['value_total'] * 100:.0f}%)" for v in vals], height=330))
with right:
    T.callout("Limitations and biases", [
        f"<b>One month only.</b> {f['days']} days of July 2024. There is no trend, growth or seasonality to study.",
        f"<b>The data looks simulated.</b> Daily bookings stay within {f['daily_min']:,} to {f['daily_max']:,}, outcome rates are almost identical across hours and vehicle types, "
        f"ratings never fall below {f['rating_min']:.1f}, and fare ignores distance. Confirm where the export came from before presenting these as facts about Ola.",
        "<b>Quoted value is not revenue.</b> Booking value is filled in even for cancelled bookings, so lost value means quoted fare that was not realised.",
        f"<b>Locations are labels.</b> Areas have no coordinates, and {pct(f['same_pickup_drop'])} of bookings have the same pickup and drop area. They were flagged, not removed.",
        f"<b>Few repeat customers.</b> {pct(f['single_booking_share'], 0)} of customers booked once, so retention cannot be analysed.",
        "<b>Ratings only exist for rides that ran.</b> They cannot explain cancellations, and every rating sits between 3.0 and 5.0.",
        f"<b>Many comparisons.</b> {f['n_tests']} tests were run, so a few would pass at 5% by luck. Bonferroni correction is strict and could hide a very small real effect.",
        "<b>Association, not causation.</b> Cancellation reasons are recorded labels, and a pattern in them does not prove what caused a cancellation.",
        "<b>Calendar effect.</b> July 2024 has five Mondays, Tuesdays and Wednesdays but four of every other weekday, so raw weekday totals mislead. The dashboard uses per-day averages.",
    ])
