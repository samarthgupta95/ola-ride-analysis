"""Plotly chart helpers. One consistent look: grey bars, lime for the point of the chart."""
from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from . import theme as T
from .compat import stretch

CONFIG = {"displayModeBar": False}


def show(fig: go.Figure) -> None:
    st.plotly_chart(fig, config=CONFIG, **stretch(st.plotly_chart))


def style(fig: go.Figure, height: int = 300, legend: bool = False) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=T.FONT, color=T.TEXT, size=12),
        margin=dict(l=4, r=14, t=10, b=4),
        height=height,
        showlegend=legend,
        bargap=0.38,
        hoverlabel=dict(bgcolor=T.SURFACE_2, bordercolor=T.BORDER, font=dict(family=T.FONT, color=T.TEXT, size=12)),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=11, color=T.MUTED), bgcolor="rgba(0,0,0,0)",
        ),
    )
    axis = dict(
        gridcolor=T.GRID, zeroline=False, linecolor=T.BORDER,
        tickfont=dict(color=T.MUTED, size=11), title_font=dict(color=T.MUTED, size=11),
        automargin=True,
    )
    fig.update_xaxes(**axis)
    fig.update_yaxes(**axis)
    return fig


def bar(labels, values, *, highlight=None, colors=None, horizontal=False, text=None,
        fmt="{:,.0f}", height=300, axis_range=None) -> go.Figure:
    labels = [str(x) for x in labels]
    values = [float(v) for v in values]
    if colors is None:
        hl = set(highlight or [])
        colors = [T.LIME if lab in hl else T.GREY for lab in labels]
    text = text or [fmt.format(v) for v in values]
    vmax = max(values) if values else 1.0
    rng = axis_range or [0, vmax * 1.2 if vmax > 0 else 1]
    common = dict(
        marker_color=colors, text=text, textposition="outside", cliponaxis=False,
        textfont=dict(color=T.TEXT, size=11),
    )
    if horizontal:
        fig = go.Figure(go.Bar(x=values, y=labels, orientation="h",
                               hovertemplate="%{y}: %{text}<extra></extra>", **common))
        fig.update_layout(yaxis=dict(autorange="reversed"))
        style(fig, height)
        fig.update_xaxes(range=rng, showticklabels=False, showgrid=False)
        fig.update_yaxes(showgrid=False)
    else:
        fig = go.Figure(go.Bar(x=labels, y=values, hovertemplate="%{x}: %{text}<extra></extra>", **common))
        style(fig, height)
        fig.update_yaxes(range=rng, showticklabels=False, showgrid=True)
        fig.update_xaxes(showgrid=False)
    return fig


def lines(x, series, *, height=300, y_range=None, weekend_dates=None, legend=True,
          yfmt=",.0f", markers=False) -> go.Figure:
    fig = go.Figure()
    for s in series:
        fig.add_trace(go.Scatter(
            x=x, y=s["y"], name=s["name"], mode="lines+markers" if markers else "lines",
            line=dict(color=s["color"], width=s.get("width", 2.2), dash=s.get("dash")),
            marker=dict(size=5),
            hovertemplate=f"{s['name']}: %{{y:{yfmt}}}<extra></extra>",
        ))
    for d in weekend_dates or []:
        fig.add_vrect(x0=d - pd.Timedelta(hours=12), x1=d + pd.Timedelta(hours=12),
                      fillcolor="rgba(255,255,255,0.05)", line_width=0, layer="below")
    style(fig, height, legend=legend)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(range=y_range, tickformat=yfmt)
    return fig


def donut(labels, values, colors, *, center_title="", center_sub="", height=300) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.68, sort=False, direction="clockwise",
        marker=dict(colors=colors, line=dict(color=T.BG, width=2)), textinfo="none",
        domain=dict(x=[0, 0.58], y=[0, 1]),
        hovertemplate="%{label}: %{value:,.0f} (%{percent})<extra></extra>",
    ))
    style(fig, height, legend=True)
    fig.update_layout(
        legend=dict(orientation="v", x=0.64, y=0.5, xanchor="left", yanchor="middle",
                    font=dict(size=12, color=T.TEXT), bgcolor="rgba(0,0,0,0)"),
        annotations=[dict(
            text=f"<b style='font-size:22px'>{center_title}</b><br><span style='font-size:11px;color:{T.MUTED}'>{center_sub}</span>",
            x=0.29, y=0.5, showarrow=False, font=dict(color=T.TEXT, family=T.FONT),
        )],
    )
    return fig


def heatmap(z, xlabels, ylabels, *, height=320) -> go.Figure:
    zmax = float(max(max(row) for row in z)) if len(z) else 1.0
    fig = go.Figure(go.Heatmap(
        z=z, x=xlabels, y=ylabels, zmin=0, zmax=zmax if zmax > 0 else 1,
        colorscale=[[0, "#141414"], [1, T.LIME]], xgap=2, ygap=2,
        colorbar=dict(thickness=10, outlinewidth=0, tickfont=dict(color=T.MUTED, size=10), len=0.9),
        hovertemplate="%{y}, %{x}:00<br>%{z:,.0f} bookings per day<extra></extra>",
    ))
    style(fig, height)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=False, dtick=2, title_text="Hour of day")
    return fig


def hist(values, color, name, *, height=280) -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=values, name=name, marker_color=color,
        xbins=dict(start=2.95, end=5.05, size=0.1),
        hovertemplate="Rating %{x:.1f}: %{y:,.0f} rides<extra></extra>",
    ))
    style(fig, height)
    fig.update_xaxes(range=[2.9, 5.1], showgrid=False, dtick=0.5, title_text="Rating")
    fig.update_yaxes(title_text="Rides")
    return fig


def stacked_share(categories, series: dict, colors: dict, *, height=300) -> go.Figure:
    """series: name -> list of percentages (one per category, each category sums to 100)."""
    fig = go.Figure()
    for name, vals in series.items():
        fig.add_trace(go.Bar(
            name=name, y=list(categories), x=list(vals), orientation="h",
            marker_color=colors.get(name, T.GREY),
            text=[f"{v:.0f}%" if v >= 4 else "" for v in vals],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="#0A0A0A", size=11),
            hovertemplate=f"{name}: %{{x:.1f}}%<extra></extra>",
        ))
    style(fig, height, legend=True)
    fig.update_layout(barmode="stack", yaxis=dict(autorange="reversed"))
    fig.update_xaxes(range=[0, 100], showticklabels=False, showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig


def rate_half_width(p: float, n: float) -> float:
    """Half width of a 95% band for a proportion p measured on n bookings (in percentage points)."""
    if n <= 0:
        return 0.0
    return 1.96 * math.sqrt(p * (1 - p) / n) * 100


def add_band(fig: go.Figure, overall: float, half: float, *, horizontal=False) -> go.Figure:
    """Shade the range expected from chance alone around the overall rate (all values in percent)."""
    lo, hi = overall - half, overall + half
    if horizontal:
        fig.add_vrect(x0=lo, x1=hi, fillcolor="rgba(214,222,31,0.10)", line_width=0, layer="below")
        fig.add_vline(x=overall, line_dash="dot", line_color=T.MUTED, line_width=1)
    else:
        fig.add_hrect(y0=lo, y1=hi, fillcolor="rgba(214,222,31,0.10)", line_width=0, layer="below")
        fig.add_hline(y=overall, line_dash="dot", line_color=T.MUTED, line_width=1)
    return fig
