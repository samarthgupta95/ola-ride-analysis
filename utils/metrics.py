"""Reusable calculations shared by several pages."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import DAY_ORDER


def kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    completed = int(df["completed"].sum())
    ran = df[df["ran"]]
    value_total = float(df["booking_value"].sum())
    value_completed = float(df.loc[df["completed"], "booking_value"].sum())
    return {
        "total": total,
        "completed": completed,
        "completion": completed / total if total else 0.0,
        "not_completed": 1 - (completed / total if total else 0.0),
        "value_total": value_total,
        "value_completed": value_completed,
        "value_lost": value_total - value_completed,
        "avg_distance": float(ran["ride_distance"].mean()) if len(ran) else float("nan"),
        "avg_customer_rating": float(ran["customer_rating"].mean()) if len(ran) else float("nan"),
        "avg_driver_rating": float(ran["driver_ratings"].mean()) if len(ran) else float("nan"),
        "days": df["date"].nunique(),
    }


def weekday_occurrences(start, end) -> pd.Series:
    """How many Mondays, Tuesdays and so on fall inside the selected date range."""
    names = pd.Series(pd.date_range(start, end).day_name())
    return names.value_counts().reindex(DAY_ORDER, fill_value=0)


def safe_mean(s: pd.Series) -> float:
    s = s.dropna()
    return float(s.mean()) if len(s) else float("nan")


def share(part: float, whole: float) -> float:
    return part / whole if whole else float("nan")


def ci_half_width_pp(p: float, n: float) -> float:
    return 1.96 * float(np.sqrt(p * (1 - p) / n)) * 100 if n else 0.0
