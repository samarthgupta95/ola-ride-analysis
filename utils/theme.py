"""Visual theme: Ola colours, global CSS and small HTML building blocks."""
from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from .compat import stretch

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# ---------------------------------------------------------------- colours
LIME = "#D6DE1F"          # Ola lime, sampled from the logo
BG = "#0A0A0A"
SURFACE = "#141414"
SURFACE_2 = "#1C1C1C"
BORDER = "#262626"
GRID = "#1F1F1F"
TEXT = "#F2F2F2"
MUTED = "#9CA3AF"
GREY = "#4B5563"          # neutral bars; lime is reserved for the point of a chart
AMBER = "#F5A524"
RED = "#EF4444"
VIOLET = "#A78BFA"
SKY = "#38BDF8"
STEEL = "#6B7A90"

FONT = "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

OUTCOME_COLORS = {
    "Completed": LIME,
    "Incomplete": AMBER,
    "Canceled by Driver": RED,
    "Canceled by Customer": VIOLET,
    "Driver Not Found": STEEL,
}
PAYMENT_COLORS = {
    "Cash": "#8A9099",
    "UPI": LIME,
    "Credit Card": SKY,
    "Debit Card": VIOLET,
}
KPI_ACCENTS = [LIME, SKY, AMBER, VIOLET]

# Vehicle icons come from the original workbook (Sheet2). If a PNG with the
# vehicle's name exists in assets/vehicles (for example prime_sedan.png) it is
# used instead, so the dashboard also works offline.
VEHICLE_ICON_URLS = {
    "Prime Sedan": "https://cdn-icons-png.flaticon.com/128/14183/14183770.png",
    "Bike": "https://cdn-icons-png.flaticon.com/128/9983/9983173.png",
    "Prime SUV": "https://cdn-icons-png.flaticon.com/128/9983/9983204.png",
    "eBike": "https://cdn-icons-png.flaticon.com/128/6839/6839867.png",
    "Mini": "https://cdn-icons-png.flaticon.com/128/3202/3202926.png",
    "Prime Plus": "https://cdn-icons-png.flaticon.com/128/11409/11409716.png",
    "Auto": "https://cdn-icons-png.flaticon.com/128/16526/16526595.png",
}

# ---------------------------------------------------------------- formatting


def fmt_int(n) -> str:
    return f"{int(round(n)):,}"


def fmt_pct(x, digits: int = 1) -> str:
    """x is a fraction (0.583 -> 58.3%)."""
    return f"{x * 100:.{digits}f}%"


def fmt_inr(x) -> str:
    """Indian style short money format."""
    x = float(x)
    if abs(x) >= 1e7:
        return f"Rs {x / 1e7:.2f} Cr"
    if abs(x) >= 1e5:
        return f"Rs {x / 1e5:.1f} L"
    return f"Rs {x:,.0f}"


# ---------------------------------------------------------------- css
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp, h1, h2, h3, h4, h5, h6, p, li, label, button, input, textarea, select {
    font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}
.stApp { background: #0A0A0A; }
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px; }
footer { visibility: hidden; }

[data-testid="stSidebar"] { background: #0F0F0F; border-right: 1px solid #1F1F1F; }
.side-title { font-size: 1.05rem; font-weight: 700; color: #F2F2F2; margin: 0.2rem 0 0.4rem 0; }
.side-note { font-size: 0.78rem; color: #8A9099; line-height: 1.5; margin-top: 0.8rem; }
.count-card { background: #141414; border: 1px solid #232323; border-radius: 12px;
              padding: 12px 14px; margin: 0.6rem 0; }
.count-card b { font-size: 1.15rem; color: #F2F2F2; font-weight: 700; }
.count-card span { font-size: 0.8rem; color: #9CA3AF; }

/* selected tags and primary buttons: lime with dark text for contrast */
span[data-baseweb="tag"] { background-color: #D6DE1F !important; color: #0A0A0A !important; font-weight: 600; }
span[data-baseweb="tag"] span, span[data-baseweb="tag"] svg { color: #0A0A0A !important; fill: #0A0A0A !important; }
button[kind="primary"], [data-testid="stBaseButton-primary"] {
    background: #D6DE1F !important; color: #0A0A0A !important; border: none !important; font-weight: 600;
}
button[kind="primary"] p, [data-testid="stBaseButton-primary"] p { color: #0A0A0A !important; }

div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 14px; border-color: #232323 !important; }
[data-testid="stExpander"] { border-color: #232323 !important; border-radius: 12px; }
[data-testid="stTextArea"] textarea {
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
    font-size: 0.88rem;
}

/* page header */
.page-title { font-size: 1.75rem; font-weight: 800; letter-spacing: -0.02em; color: #F5F5F5; margin: 0; }
.page-sub { color: #9CA3AF; font-size: 0.95rem; margin: 0.3rem 0 1.4rem 0; line-height: 1.5; }
.section-title { font-size: 1.2rem; font-weight: 700; letter-spacing: -0.01em; color: #F5F5F5; margin: 1.8rem 0 0.15rem 0; }
.section-sub { color: #9CA3AF; font-size: 0.88rem; margin: 0 0 0.9rem 0; line-height: 1.5; }
.chart-title { font-size: 0.98rem; font-weight: 600; color: #F2F2F2; margin: 0.1rem 0 0.1rem 0; }
.chart-sub { font-size: 0.8rem; color: #8A9099; margin: 0 0 0.4rem 0; line-height: 1.45; }

/* hero */
.hero { position: relative; overflow: hidden; border-radius: 18px; padding: 32px 36px;
        background: linear-gradient(135deg, #0A0A0A 0%, #141414 55%, #1D2008 100%);
        border: 1px solid #262626; margin-bottom: 1.2rem; }
.hero::after { content: ''; position: absolute; right: -90px; top: -90px; width: 320px; height: 320px;
               border-radius: 50%; background: radial-gradient(circle, rgba(214,222,31,0.26), rgba(214,222,31,0) 70%); }
.hero-inner { position: relative; z-index: 1; display: flex; justify-content: space-between; align-items: center; gap: 24px; }
.hero .eyebrow { font-size: 0.74rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #D6DE1F; }
.hero h1 { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.025em; margin: 0.35rem 0 0.5rem 0; color: #FFFFFF; padding: 0; line-height: 1.15; }
.hero p { color: #B6BBC2; font-size: 0.98rem; max-width: 640px; margin: 0 0 1.1rem 0; line-height: 1.55; }
.hero img.hero-logo { height: 64px; opacity: 0.95; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { border: 1px solid #2E2E2E; background: rgba(255,255,255,0.04); color: #D9DCE0; border-radius: 999px;
        padding: 5px 13px; font-size: 0.8rem; font-weight: 500; }
@media (max-width: 800px) { .hero img.hero-logo { display: none; } .hero h1 { font-size: 1.7rem; } }

/* kpi cards */
.kpi { background: #141414; border: 1px solid #232323; border-left: 3px solid var(--accent, #D6DE1F);
       border-radius: 12px; padding: 14px 16px 13px 16px; min-height: 108px; }
.kpi .label { font-size: 0.7rem; letter-spacing: 0.07em; text-transform: uppercase; color: #9CA3AF; font-weight: 600; }
.kpi .value { font-size: clamp(1.25rem, 1.7vw, 1.65rem); font-weight: 700; color: #F5F5F5; line-height: 1.2;
              margin-top: 7px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
              font-variant-numeric: tabular-nums; letter-spacing: -0.01em; }
.kpi .sub { font-size: 0.78rem; color: #8A9099; margin-top: 5px; line-height: 1.35; }

/* vehicle cards */
.vgrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(158px, 1fr)); gap: 12px; margin: 0.4rem 0 0.4rem 0; }
.vcard { background: #141414; border: 1px solid #232323; border-radius: 14px; padding: 16px 14px 14px 14px; }
.vlogo { width: 56px; height: 56px; border-radius: 14px; background: #1C1C1C; border: 1px solid #262626;
         display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;
         font-weight: 700; color: #4B5563; font-size: 1.2rem; }
.vlogo img { position: absolute; inset: 7px; width: calc(100% - 14px); height: calc(100% - 14px); object-fit: contain; }
.vname { font-size: 1rem; font-weight: 700; color: #F5F5F5; margin: 10px 0 8px 0; }
.vrow { display: flex; justify-content: space-between; font-size: 0.8rem; color: #8A9099; padding: 3px 0; }
.vrow b { color: #E5E7EB; font-weight: 600; font-variant-numeric: tabular-nums; }

/* takeaway, callout */
.takeaway { background: #141414; border: 1px solid #232323; border-left: 3px solid #D6DE1F; border-radius: 12px;
            padding: 16px 20px; color: #C9CDD3; font-size: 0.92rem; line-height: 1.6; margin-top: 1.2rem; }
.takeaway b { color: #F5F5F5; }
.callout { border: 1px solid rgba(245,165,36,0.45); background: rgba(245,165,36,0.05); border-radius: 14px; padding: 18px 22px; }
.callout .ctitle { color: #F5A524; font-weight: 700; font-size: 1.05rem; margin-bottom: 10px; }
.callout ul { margin: 0; padding-left: 18px; color: #C9CDD3; font-size: 0.88rem; line-height: 1.6; }
.callout li { margin-bottom: 7px; }
.callout li b { color: #F5F5F5; }

/* findings and recommendations */
.grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-bottom: 0.4rem; }
@media (max-width: 900px) { .grid-2 { grid-template-columns: minmax(0, 1fr); } }
.fcard { background: #141414; border: 1px solid #232323; border-radius: 14px; padding: 20px 22px 16px 22px;
         display: flex; flex-direction: column; }
.fcard .tag { font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700; }
.fcard .ftitle { font-size: 1.08rem; font-weight: 700; color: #F5F5F5; margin: 8px 0 10px 0; line-height: 1.3; }
.fcard .fbody { font-size: 0.9rem; color: #B6BBC2; line-height: 1.55; margin: 0 0 14px 0; flex: 1; }
.fcard .fbody b { color: #F2F2F2; }
.fcard .evidence { border-top: 1px solid #232323; padding-top: 10px; font-size: 0.8rem; color: #8A9099; line-height: 1.45; }
.fcard .evidence b { color: #E5E7EB; }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- html blocks
def _h(s: str) -> str:
    """Collapse indentation so Streamlit's markdown never treats HTML as a code block."""
    return "".join(line.strip() for line in s.strip().splitlines())


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        _h(f"<div class='page-title'>{title}</div><div class='page-sub'>{subtitle}</div>"),
        unsafe_allow_html=True,
    )


def section(title: str, caption: str = "") -> None:
    cap = f"<div class='section-sub'>{caption}</div>" if caption else ""
    st.markdown(_h(f"<div class='section-title'>{title}</div>{cap}"), unsafe_allow_html=True)


def chart_title(title: str, caption: str = "") -> None:
    cap = f"<div class='chart-sub'>{caption}</div>" if caption else ""
    st.markdown(_h(f"<div class='chart-title'>{title}</div>{cap}"), unsafe_allow_html=True)


def hero(eyebrow: str, title: str, subtitle: str, chips: list[str]) -> None:
    logo = ASSETS / "ola_logo_dark.png"
    logo_html = f"<img class='hero-logo' src='data:image/png;base64,{_b64(logo)}' alt='Ola'>" if logo.exists() else ""
    chip_html = "".join(f"<span class='chip'>{c}</span>" for c in chips)
    st.markdown(
        _h(
            f"""
            <div class='hero'><div class='hero-inner'>
              <div>
                <div class='eyebrow'>{eyebrow}</div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
                <div class='chips'>{chip_html}</div>
              </div>
              {logo_html}
            </div></div>
            """
        ),
        unsafe_allow_html=True,
    )


def kpi_html(label: str, value: str, sub: str = "", accent: str = LIME) -> str:
    return _h(
        f"""
        <div class='kpi' style='--accent:{accent}'>
          <div class='label'>{label}</div>
          <div class='value'>{value}</div>
          <div class='sub'>{sub}</div>
        </div>
        """
    )


def kpi_row(items: list[tuple]) -> None:
    """items: (label, value, sub) tuples. Accent colours cycle automatically."""
    cols = st.columns(len(items))
    for i, (col, item) in enumerate(zip(cols, items)):
        label, value, sub = (list(item) + [""])[:3]
        col.markdown(kpi_html(label, value, sub, KPI_ACCENTS[i % len(KPI_ACCENTS)]), unsafe_allow_html=True)


def takeaway(text: str) -> None:
    st.markdown(_h(f"<div class='takeaway'><b>Takeaway.</b> {text}</div>"), unsafe_allow_html=True)


def callout(title: str, bullets: list[str]) -> None:
    items = "".join(f"<li>{b}</li>" for b in bullets)
    st.markdown(
        _h(f"<div class='callout'><div class='ctitle'>{title}</div><ul>{items}</ul></div>"),
        unsafe_allow_html=True,
    )


def card_grid(cards: list[dict]) -> None:
    """cards: dicts with tag, color, title, body, foot_label, foot_text."""
    html = ""
    for c in cards:
        html += (
            "<div class='fcard'>"
            f"<div class='tag' style='color:{c['color']}'>{c['tag']}</div>"
            f"<div class='ftitle'>{c['title']}</div>"
            f"<div class='fbody'>{c['body']}</div>"
            f"<div class='evidence'><b>{c['foot_label']}</b> {c['foot_text']}</div>"
            "</div>"
        )
    st.markdown(_h(f"<div class='grid-2'>{html}</div>"), unsafe_allow_html=True)


def vehicle_logo_html(vehicle: str) -> str:
    slug = vehicle.lower().replace(" ", "_")
    local = ASSETS / "vehicles" / f"{slug}.png"
    if local.exists():
        src = f"data:image/png;base64,{_b64(local)}"
    else:
        src = VEHICLE_ICON_URLS.get(vehicle, "")
    img = f"<img src='{src}' alt='' loading='lazy'>" if src else ""
    return f"<div class='vlogo'>{vehicle[:1].upper()}{img}</div>"


def vehicle_cards(rows: list[dict]) -> None:
    """rows: dicts with name and a list of (label, value) stats."""
    html = ""
    for r in rows:
        stats = "".join(f"<div class='vrow'><span>{k}</span><b>{v}</b></div>" for k, v in r["stats"])
        html += f"<div class='vcard'>{vehicle_logo_html(r['name'])}<div class='vname'>{r['name']}</div>{stats}</div>"
    st.markdown(_h(f"<div class='vgrid'>{html}</div>"), unsafe_allow_html=True)


def show_table(df, height: int | None = None, hide_index: bool = True) -> None:
    kwargs = {"hide_index": hide_index, **stretch(st.dataframe)}
    if height:
        kwargs["height"] = height
    st.dataframe(df, **kwargs)
