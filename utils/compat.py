"""Small compatibility helpers so the app runs on both older and newer Streamlit releases."""
import inspect

import streamlit as st


def stretch(fn) -> dict:
    """Return the keyword that makes a Streamlit element fill its container.

    Newer Streamlit versions use width="stretch"; older ones use use_container_width=True.
    """
    params = inspect.signature(fn).parameters
    if "width" in params:
        return {"width": "stretch"}
    return {"use_container_width": True}
