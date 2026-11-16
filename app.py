"""Ola Ride Insights: Streamlit entry point (navigation, theme and shared sidebar filters)."""
from pathlib import Path

import streamlit as st

from utils import data
from utils import theme as T

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Ola Ride Insights",
    page_icon=str(ROOT / "assets" / "ola_icon.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)
T.inject_css()
st.logo(
    str(ROOT / "assets" / "ola_logo_dark.png"),
    icon_image=str(ROOT / "assets" / "ola_icon.png"),
    size="large",
)

pages = [
    st.Page("views/overview.py", title="Overview", icon=":material/dashboard:", default=True),
    st.Page("views/vehicles.py", title="Vehicles, Payments & Ratings", icon=":material/local_taxi:", url_path="vehicles"),
    st.Page("views/demand.py", title="Demand & Timing", icon=":material/schedule:", url_path="demand"),
    st.Page("views/cancellations.py", title="Cancellations & Failures", icon=":material/cancel:", url_path="cancellations"),
    st.Page("views/sql_playground.py", title="SQL Playground", icon=":material/terminal:", url_path="sql"),
    st.Page("views/findings.py", title="Findings & Recommendations", icon=":material/fact_check:", url_path="findings"),
]
page = st.navigation(pages)

with st.sidebar:
    st.divider()
    data.render_sidebar_filters()

page.run()
