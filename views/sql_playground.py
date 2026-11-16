"""Page 5: SQL Playground."""
import streamlit as st

from utils import data
from utils import sql_library as lib
from utils import theme as T
from utils.compat import stretch

T.page_header(
    "SQL playground",
    "Run read-only SQL against the cleaned table. Nothing you type can change the data. "
    "This page always uses the full dataset, whatever the sidebar filters say.",
)

con = data.get_duck()
total_rows = con.execute(f"SELECT COUNT(*) FROM {data.TABLE}").fetchone()[0]

with st.expander("Table reference (name and columns)"):
    st.markdown(
        f"Table: `{data.TABLE}` with **{total_rows:,}** rows. Queries run in DuckDB, which accepts the same "
        "PostgreSQL style syntax used in `sql/ola_ride_insights.sql`."
    )
    cols = con.execute(f"DESCRIBE {data.TABLE}").fetchdf()[["column_name", "column_type"]]
    cols["what it holds"] = cols["column_name"].map(lib.COLUMN_NOTES).fillna("")
    cols.columns = ["column", "type", "what it holds"]
    T.show_table(cols, height=320)


def render_result(res: dict, key: str, limit: int) -> None:
    shown = len(res["df"])
    note = f"{res['total']:,} rows returned in {res['seconds'] * 1000:.0f} ms"
    if res["total"] > shown:
        note += f" (showing the first {shown:,})"
    st.caption(note)
    T.show_table(res["df"], height=min(420, 38 + 35 * max(shown, 1)))
    st.download_button(
        "Download shown rows as CSV", res["df"].to_csv(index=False).encode("utf-8"),
        file_name=f"{key}.csv", mime="text/csv", key=f"dl_{key}",
    )


# ------------------------------------------------------------------ part 1
T.section("Part 1: Analysis library", "The ten project questions plus extra analysis. Pick one to see the query and its result.")
labels = [q["label"] for q in lib.LIBRARY]
choice = st.selectbox("Choose an analysis", labels, index=1)
query = next(q for q in lib.LIBRARY if q["label"] == choice)
st.code(query["sql"], language="sql")
try:
    render_result(data.run_query(query["sql"], limit=500), key="library_result", limit=500)
except Exception as exc:  # pragma: no cover
    st.error(f"This query could not be run: {exc}")

# ------------------------------------------------------------------ part 2
T.section("Part 2: Write your own query", f"Query the table `{data.TABLE}`. Results are capped at 1,000 rows and queries stop after 15 seconds.")
sql_text = st.text_area("SQL query", value=lib.DEFAULT_CUSTOM, height=220, key="custom_sql", label_visibility="collapsed")
run = st.button("Run query", type="primary")
if run:
    error, cleaned = data.validate_sql(sql_text)
    if error:
        st.error(error)
    else:
        try:
            with st.spinner("Running"):
                res = data.run_query(cleaned, limit=1000)
            render_result(res, key="custom_result", limit=1000)
        except Exception as exc:
            msg = str(exc).splitlines()[0] if str(exc) else "Unknown error"
            st.error(f"The query failed: {msg}")
else:
    st.caption("Edit the query above and press Run query.")
