# Ola Ride Insights

An end-to-end analytics project on 103,024 Ola cab bookings from July 2024. It covers SQL analysis, Python data preprocessing, an interactive Streamlit dashboard and a Power BI dashboard, and it answers one question: **why do four in ten bookings never turn into a completed ride, and what would it take to fix that?**

> Live dashboard: [Click here to access!](https://ola-rides-analysis.streamlit.app/)

---

## Contents

1. [Project overview](#project-overview)
2. [Business questions](#business-questions)
3. [Dataset](#dataset)
4. [Deliverables and workflow](#deliverables-and-workflow)
5. [Repository structure](#repository-structure)
6. [Key findings snapshot](#key-findings-snapshot)
7. [Recommendations snapshot](#recommendations-snapshot)
8. [Limitations and biases](#limitations-and-biases)
9. [Streamlit dashboard](#streamlit-dashboard)
10. [Power BI dashboard](#power-bi-dashboard)
11. [How to run](#how-to-run)
12. [Tech stack](#tech-stack)
13. [Author](#author)

---

## Project overview

Ride-hailing lives or dies on completed rides. A booking that is cancelled, never gets a driver or stops halfway earns nothing and costs the customer's trust. This project takes a month of Ola booking records, cleans them, answers ten defined SQL questions, and builds dashboards that show how bookings end, why they fail and what the data can and cannot support.

A deliberate part of the project is honesty about the data. Several results are flat across vehicle types, hours and areas, and a few fields behave in ways real data would not (for example, fare does not change with distance). The dashboards say so instead of inventing patterns.

## Business questions

1. How many bookings complete, and how much quoted booking value is lost when they do not?
2. Who ends the bookings that fail: drivers, customers, or the lack of a driver?
3. What reasons do drivers and customers give for cancelling?
4. Do failures concentrate in particular hours, weekdays, vehicle types or areas?
5. How do vehicle types differ in distance, fares, payments and ratings?
6. When does demand arrive across the day and the week?

## Dataset

| Item | Detail |
|---|---|
| Source file | `data/raw/OLA_DataSet.xlsx`, sheet "July" |
| Period | 1 July 2024 to 31 July 2024 |
| Size | 103,024 bookings, 31 days |
| Vehicle types | Auto, Bike, eBike, Mini, Prime Plus, Prime Sedan, Prime SUV |
| Outcomes | Completed, Incomplete, Canceled by Driver, Canceled by Customer, Driver Not Found |
| Cleaned files | `data/ola_data_clean.parquet` (about 3 MB, read by the Streamlit app) and `data/ola_data_clean.csv` (same 30 columns, about 29 MB) |

**What the cleaning step does** (full detail in `notebooks/OLA_Data_Preprocessing.ipynb`):

- Audits nulls, duplicates, whitespace, ID formats and categories. There were no duplicates and no bad IDs.
- Recognises that missing values are structural (ratings exist only for rides that ran, cancellation reasons only for cancelled bookings), so categorical gaps become `Not Applicable` and numeric gaps stay null.
- Converts ride distance from 0 to null for rides that never happened, so averages are not dragged down.
- Rebuilds date and time into one timestamp and adds `hour`, `day_name`, `is_weekend`, `time_of_day`, `ride_outcome`, `cancellation_reason`, `route` and `same_pickup_drop`.
- Validates the result with assertions and exports the clean data as CSV and as Parquet. Parquet holds the same data in about a tenth of the size, which keeps the repository under GitHub's upload limit.

## Deliverables and workflow

| # | Deliverable | Tool | Location | Status |
|---|---|---|---|---|
| 1 | SQL analysis of ten business questions | PostgreSQL | `sql/ola_ride_insights.sql` | Done |
| 2 | Data preprocessing notebook and clean dataset | Python (pandas) | `notebooks/`, `data/` | Done |
| 3 | Interactive six-page dashboard | Streamlit, Plotly, DuckDB | `app.py`, `views/`, `utils/` | Done |
| 4 | Business intelligence dashboard | Power BI | `powerbi/` | In progress |

```
Raw Excel  ->  Preprocessing notebook  ->  Clean CSV  ->  PostgreSQL analysis
                                              |
                                              +-------->  Streamlit dashboard (with SQL playground)
                                              +-------->  Power BI dashboard
```

The ten SQL questions are:

1. Retrieve all successful bookings
2. Average ride distance for each vehicle type
3. Total cancelled rides by customers
4. Top 5 customers by number of rides booked
5. Rides cancelled by drivers for personal and car-related issues
6. Maximum and minimum driver ratings for Prime Sedan
7. All rides paid using UPI
8. Average customer rating per vehicle type
9. Total booking value of rides completed successfully
10. All incomplete rides along with the reason

The same queries run live inside the Streamlit app on the SQL Playground page.

## Repository structure

```
ola-ride-insights/
├── README.md
├── app.py                        Streamlit entry point: navigation, theme, shared filters
├── requirements.txt
├── .streamlit/
│   └── config.toml               Ola colour theme (black and lime)
├── assets/
│   ├── ola_logo.png              Original logo
│   ├── ola_logo_dark.png         Logo prepared for the dark theme
│   ├── ola_icon.png              Favicon
│   └── vehicles/                 Optional local vehicle icons (see below)
├── data/
│   ├── raw/OLA_DataSet.xlsx      Original dataset
│   ├── ola_data_clean.parquet    Clean data used by the app (about 3 MB)
│   └── ola_data_clean.csv        Same data as CSV for PostgreSQL and Power BI (zipped in the repo, see below)
├── notebooks/
│   └── OLA_Data_Preprocessing.ipynb
├── sql/
│   └── ola_ride_insights.sql     Table setup and the ten analysis queries
├── views/                        One file per dashboard page
│   ├── overview.py
│   ├── vehicles.py
│   ├── demand.py
│   ├── cancellations.py
│   ├── sql_playground.py
│   └── findings.py
├── utils/
│   ├── theme.py                  Colours, CSS and HTML building blocks
│   ├── charts.py                 Plotly helpers
│   ├── data.py                   Loading, filters, read-only DuckDB layer
│   ├── metrics.py                Shared calculations
│   ├── insights.py               Statistics behind the Findings page
│   ├── sql_library.py            Queries shown in the SQL playground
│   └── compat.py                 Streamlit version compatibility
└── powerbi/                      Power BI file and screenshots (to be added)
```

## Key findings snapshot

These figures come from the full July 2024 dataset. The Findings page in the app recalculates them live.

| Area | Finding |
|---|---|
| Completion | 58.3% of bookings (60,041) completed. The other 41.7% carried Rs 2.37 Cr of quoted fare, 41.9% of everything quoted. |
| Drivers | Drivers cancelled 18,434 bookings against 10,499 cancelled by customers (1.76 times as many). Driver cancellations are 43% of lost value. The top recorded reason is personal and car-related issues (35.5%). |
| Customers | 55.7% of customer cancellations say the driver was not moving towards the pickup or asked the customer to cancel. |
| No driver | 10,124 bookings (9.8%) ended with no driver found. |
| Incomplete rides | 3,926 rides started but did not finish: customer demand 40.8%, vehicle breakdown 40.5%, other 18.7%. |
| No pattern | Nine tests of completion and ratings against vehicle type, hour, weekday, weekend, pickup, drop and payment found none below p = 0.05. Completion ranges only from 57.7% to 58.9% across vehicle types. |
| Vehicles | Auto rides average 10.0 km against 25.0 km for other types, yet the average completed fare is about the same (Rs 550 against Rs 546). |
| Payments | Cash 54.8%, UPI 40.5%, cards 4.8% of rides that ran. |
| Demand | Steady all month: 3,072 to 3,432 bookings per day, with no rush hour. |

## Recommendations snapshot

| Recommendation | Strength of support |
|---|---|
| Cut driver cancellations first, starting with driver readiness checks and prompts before accepting rides | Data-backed |
| Treat many customer cancellations as a driver problem: live alerts for drivers not heading to pickup, and flag drivers who ask riders to cancel | Data-backed |
| Do not target by hour, vehicle type or area, because failure rates are flat across all of them | Data-backed |
| Recover "driver not found" bookings with retries or wider search, tested on a small random share | Reasoned, not measured |
| Audit the fare logic before any pricing work, because fare ignores distance | Data gap |
| Test nudges that move cash riders to UPI | Reasoned, not measured |

## Limitations and biases

- **One month only.** There is no trend, growth or seasonality to study.
- **The data looks simulated.** Outcome rates are nearly identical across hours and vehicle types, ratings never fall below 3.0 and fare is unrelated to distance (correlation 0.00). Confirm the source before presenting results as facts about Ola.
- **Quoted value is not revenue.** Booking value is filled in even for cancelled bookings.
- **Locations are labels.** There are no coordinates, and 2.1% of bookings have the same pickup and drop area. They are flagged, not removed.
- **Few repeat customers.** 91.6% of customers booked once, so retention cannot be analysed.
- **Ratings exist only for rides that ran**, so they cannot explain cancellations.
- **Many comparisons.** Nine tests were run, so Bonferroni correction is applied. It is strict and could hide a very small real effect.
- **Association, not causation.** Cancellation reasons are recorded labels, not verified causes.
- **Calendar effect.** July 2024 has five Mondays, Tuesdays and Wednesdays but four of every other weekday. Raw weekday totals therefore mislead, and the dashboard uses per-day averages.

## Streamlit dashboard

Six pages share one set of sidebar filters (date range, vehicle type, ride outcome, day type).

| Page | What it shows |
|---|---|
| Overview | Headline KPIs, outcome mix, daily bookings, quoted value by outcome, vehicle mix |
| Vehicles, Payments & Ratings | A card per vehicle type with its icon, value and distance by vehicle, payment mix, rating distributions, fare against distance |
| Demand & Timing | Daily trend, weekday and hour patterns, heatmap, time-of-day windows, weekday against weekend |
| Cancellations & Failures | Who cancels, why, value lost, and whether failures concentrate by vehicle, hour or area, with chance bands |
| SQL Playground | The ten project queries plus extras, and a read-only box for custom queries |
| Findings & Recommendations | Live-calculated findings, recommendations with evidence strength, and the limitations box |

The SQL Playground and Findings pages always use the full dataset. Custom queries are limited to a single read-only statement, results are capped at 1,000 rows and file access is disabled in the database engine.

**Vehicle icons.** The icons on the Vehicles page come from the links in the original workbook. To work offline, save PNGs named after each type (`auto.png`, `bike.png`, `ebike.png`, `mini.png`, `prime_plus.png`, `prime_sedan.png`, `prime_suv.png`) in `assets/vehicles/` and they take priority.

## Power BI dashboard

The Power BI dashboard is the fourth deliverable and is built separately from the Streamlit app, from the same cleaned data (`ola_data_clean.csv` or the Parquet file).

- File: `powerbi/ola_ride_insights.pbix` (to be added)
- Screenshots: `powerbi/screenshots/` (to be added)

Add a preview here once published:

```
![Power BI overview](powerbi/screenshots/overview.png)
```

## How to run

```bash
git clone https://github.com/samarthgupta95/ola-ride-insights.git
cd ola-ride-insights
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

To rebuild the clean dataset from the raw file, open `notebooks/OLA_Data_Preprocessing.ipynb` and run all cells from the `notebooks/` folder. It writes both the Parquet and the CSV file.

The app only needs `data/ola_data_clean.parquet`. The 29 MB CSV is too big for a normal GitHub upload, so it can be stored as a zip (`data/ola_data_clean.zip`) and unzipped when you need it for PostgreSQL or Power BI.

To reproduce the SQL analysis, create the table with the setup section of `sql/ola_ride_insights.sql` in PostgreSQL and import the unzipped `ola_data_clean.csv` with pgAdmin (Header on, NULL string empty).

## Tech stack

Python, pandas, NumPy, SciPy, PyArrow, Plotly, Streamlit, DuckDB, PostgreSQL, Power BI, Jupyter.

## Author

**Samarth Gupta**
GitHub: [github.com/samarthgupta95](https://github.com/samarthgupta95)
