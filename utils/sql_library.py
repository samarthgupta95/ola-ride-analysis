"""Read-only analysis queries shown on the SQL playground page.

Queries 1 to 10 are the project questions (same as sql/ola_ride_insights.sql).
They run in DuckDB inside the app, which accepts the same PostgreSQL style syntax.
"""

LIBRARY = [
    {
        "label": "Overview: bookings, customers and date span",
        "sql": """SELECT
    COUNT(*)                    AS bookings,
    COUNT(DISTINCT customer_id) AS customers,
    MIN(date)                   AS first_date,
    MAX(date)                   AS last_date
FROM ola_data_clean""",
    },
    {
        "label": "Project question 1: Retrieve all successful bookings",
        "sql": """SELECT *
FROM ola_data_clean
WHERE booking_status = 'Success'""",
    },
    {
        "label": "Project question 2: Average ride distance for each vehicle type",
        "sql": """SELECT
    vehicle_type,
    ROUND(AVG(ride_distance), 2) AS avg_ride_distance_km
FROM ola_data_clean
GROUP BY vehicle_type
ORDER BY avg_ride_distance_km DESC""",
    },
    {
        "label": "Project question 3: Total number of cancelled rides by customers",
        "sql": """SELECT COUNT(*) AS cancelled_by_customers
FROM ola_data_clean
WHERE booking_status = 'Canceled by Customer'""",
    },
    {
        "label": "Project question 4: Top 5 customers by number of rides booked",
        "sql": """SELECT
    customer_id,
    COUNT(*) AS total_rides_booked
FROM ola_data_clean
GROUP BY customer_id
ORDER BY total_rides_booked DESC, customer_id
LIMIT 5""",
    },
    {
        "label": "Project question 5: Rides cancelled by drivers for personal and car-related issues",
        "sql": """SELECT COUNT(*) AS cancelled_personal_car_issues
FROM ola_data_clean
WHERE canceled_by_driver_reason = 'Personal & Car related issue'""",
    },
    {
        "label": "Project question 6: Maximum and minimum driver ratings for Prime Sedan",
        "sql": """SELECT
    MAX(driver_ratings) AS max_driver_rating,
    MIN(driver_ratings) AS min_driver_rating
FROM ola_data_clean
WHERE vehicle_type = 'Prime Sedan'""",
    },
    {
        "label": "Project question 7: All rides paid using UPI",
        "sql": """SELECT *
FROM ola_data_clean
WHERE payment_method = 'UPI'""",
    },
    {
        "label": "Project question 8: Average customer rating per vehicle type",
        "sql": """SELECT
    vehicle_type,
    ROUND(AVG(customer_rating), 2) AS avg_customer_rating
FROM ola_data_clean
GROUP BY vehicle_type
ORDER BY avg_customer_rating DESC""",
    },
    {
        "label": "Project question 9: Total booking value of rides completed successfully",
        "sql": """SELECT SUM(booking_value) AS total_booking_value
FROM ola_data_clean
WHERE ride_outcome = 'Completed'""",
    },
    {
        "label": "Project question 10: All incomplete rides along with the reason",
        "sql": """SELECT
    booking_id,
    customer_id,
    vehicle_type,
    pickup_location,
    drop_location,
    incomplete_reason
FROM ola_data_clean
WHERE ride_outcome = 'Incomplete'""",
    },
    {
        "label": "Extra analysis: Outcome mix of all bookings",
        "sql": """SELECT
    ride_outcome,
    COUNT(*) AS bookings,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM ola_data_clean
GROUP BY ride_outcome
ORDER BY bookings DESC""",
    },
    {
        "label": "Extra analysis: Completion rate by vehicle type",
        "sql": """SELECT
    vehicle_type,
    COUNT(*) AS bookings,
    ROUND(100.0 * AVG((ride_outcome = 'Completed')::int), 1) AS completion_rate_pct
FROM ola_data_clean
GROUP BY vehicle_type
ORDER BY completion_rate_pct DESC""",
    },
    {
        "label": "Extra analysis: Quoted booking value lost by outcome",
        "sql": """SELECT
    ride_outcome,
    COUNT(*) AS bookings,
    SUM(booking_value) AS booking_value_lost
FROM ola_data_clean
WHERE ride_outcome <> 'Completed'
GROUP BY ride_outcome
ORDER BY booking_value_lost DESC""",
    },
    {
        "label": "Extra analysis: Why customers cancel",
        "sql": """SELECT
    canceled_by_customer_reason AS reason,
    COUNT(*) AS cancellations,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM ola_data_clean
WHERE booking_status = 'Canceled by Customer'
GROUP BY reason
ORDER BY cancellations DESC""",
    },
    {
        "label": "Extra analysis: Why drivers cancel",
        "sql": """SELECT
    canceled_by_driver_reason AS reason,
    COUNT(*) AS cancellations,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM ola_data_clean
WHERE booking_status = 'Canceled by Driver'
GROUP BY reason
ORDER BY cancellations DESC""",
    },
    {
        "label": "Extra analysis: Payment mix of rides that ran",
        "sql": """SELECT
    payment_method,
    COUNT(*) AS rides,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM ola_data_clean
WHERE booking_status = 'Success'
GROUP BY payment_method
ORDER BY rides DESC""",
    },
    {
        "label": "Extra analysis: Average bookings per day by weekday",
        "sql": """WITH daily AS (
    SELECT date, day_name, COUNT(*) AS bookings
    FROM ola_data_clean
    GROUP BY date, day_name
)
SELECT
    day_name,
    COUNT(*) AS days_in_month,
    ROUND(AVG(bookings), 0) AS avg_bookings_per_day
FROM daily
GROUP BY day_name
ORDER BY avg_bookings_per_day DESC""",
    },
    {
        "label": "Extra analysis: Pickup areas with the highest failure rate",
        "sql": """SELECT
    pickup_location,
    COUNT(*) AS bookings,
    ROUND(100.0 * AVG((ride_outcome IN ('Canceled by Driver', 'Canceled by Customer', 'Driver Not Found'))::int), 1) AS failure_rate_pct
FROM ola_data_clean
GROUP BY pickup_location
ORDER BY failure_rate_pct DESC
LIMIT 10""",
    },
]

DEFAULT_CUSTOM = """SELECT
    vehicle_type,
    payment_method,
    COUNT(*) AS rides,
    ROUND(AVG(booking_value), 0) AS avg_fare
FROM ola_data_clean
WHERE ride_outcome = 'Completed'
GROUP BY vehicle_type, payment_method
ORDER BY rides DESC
LIMIT 20"""

COLUMN_NOTES = {
    "booking_id": "Unique booking reference",
    "booking_datetime": "Date and time of the booking",
    "date": "Booking date",
    "time": "Booking time",
    "hour": "Hour of day, 0 to 23",
    "day_name": "Weekday name",
    "day_of_week": "1 = Monday to 7 = Sunday",
    "week_of_month": "Week of the month, 1 to 5",
    "is_weekend": "True for Saturday and Sunday",
    "time_of_day": "Late Night, Morning, Afternoon, Evening or Night window",
    "customer_id": "Customer reference",
    "vehicle_type": "Auto, Bike, eBike, Mini, Prime Plus, Prime Sedan or Prime SUV",
    "pickup_location": "Pickup area label",
    "drop_location": "Drop area label",
    "route": "Pickup to drop, as one label",
    "same_pickup_drop": "True when pickup and drop are the same area",
    "booking_status": "Success, Canceled by Driver, Canceled by Customer or Driver Not Found",
    "ride_outcome": "Completed, Incomplete, Canceled by Driver, Canceled by Customer or Driver Not Found",
    "canceled_by_customer_reason": "Reason given by the customer, or Not Applicable",
    "canceled_by_driver_reason": "Reason given by the driver, or Not Applicable",
    "cancellation_reason": "Single cancellation reason column, or Not Applicable",
    "incomplete_rides": "Yes, No or Not Applicable",
    "incomplete_reason": "Why a started ride did not finish, or Not Applicable",
    "v_tat": "Vehicle turnaround time (successful bookings only)",
    "c_tat": "Customer turnaround time (successful bookings only)",
    "booking_value": "Quoted fare in Rs (filled even for cancelled bookings)",
    "ride_distance": "Kilometres, empty when the ride never happened",
    "payment_method": "Cash, UPI, Credit Card, Debit Card or Not Applicable",
    "driver_ratings": "Rating given to the driver (successful bookings only)",
    "customer_rating": "Rating given by the customer (successful bookings only)",
}
