/* =====================================================================
   OLA RIDE INSIGHTS | SQL ANALYSIS (PostgreSQL)
   Dataset : OLA_DataSet.xlsx, sheet "July" (103,024 bookings, July 2024)
   Source  : ola_data_clean.csv (output of the preprocessing notebook)
   ===================================================================== */


/* ---------------------------------------------------------------------
   SECTION 0: SETUP
   The cleaned file has 30 columns: the original ones (renamed to
   snake_case, Vehicle Images dropped) plus engineered columns such as
   ride_outcome, time_of_day and route.
   Cleaning notes that matter for the queries:
     - ride_distance is NULL for rides that never happened (not 0)
     - ratings, tat and distance are NULL for non-successful bookings
     - text fields that do not apply say 'Not Applicable'
   --------------------------------------------------------------------- */

DROP TABLE IF EXISTS ola_data_clean;

CREATE TABLE ola_data_clean (
    booking_id                   VARCHAR(20) PRIMARY KEY,
    booking_datetime             TIMESTAMP,
    date                         DATE,
    time                         TIME,
    hour                         SMALLINT,
    day_name                     VARCHAR(10),
    day_of_week                  SMALLINT,     -- 1 = Monday ... 7 = Sunday
    week_of_month                SMALLINT,
    is_weekend                   BOOLEAN,
    time_of_day                  VARCHAR(15),
    customer_id                  VARCHAR(20),
    vehicle_type                 VARCHAR(20),
    pickup_location              VARCHAR(60),
    drop_location                VARCHAR(60),
    route                        VARCHAR(130),
    same_pickup_drop             BOOLEAN,
    booking_status               VARCHAR(30),
    ride_outcome                 VARCHAR(30),  -- Completed / Incomplete / Canceled by Customer / Canceled by Driver / Driver Not Found
    canceled_by_customer_reason  VARCHAR(80),
    canceled_by_driver_reason    VARCHAR(80),
    cancellation_reason          VARCHAR(80),
    incomplete_rides             VARCHAR(20),  -- 'Yes' / 'No' / 'Not Applicable'
    incomplete_reason            VARCHAR(40),
    v_tat                        NUMERIC,      -- vehicle turnaround time
    c_tat                        NUMERIC,      -- customer turnaround time
    booking_value                INTEGER,
    ride_distance                NUMERIC,      -- km, NULL if the ride never happened
    payment_method               VARCHAR(20),
    driver_ratings               NUMERIC(2,1),
    customer_rating              NUMERIC(2,1)
);

/* Load the CSV in pgAdmin:
   right click the table > Import/Export Data > select ola_data_clean.csv
   > Header ON, leave the NULL string empty.
*/

-- Sanity check after loading (should be 103024)
SELECT COUNT(*) AS total_rows FROM ola_data_clean;

-- Quick look at how the statuses split (useful context for the questions below)
SELECT booking_status, COUNT(*) AS bookings
FROM ola_data_clean
GROUP BY booking_status
ORDER BY bookings DESC;

-- Same split using the cleaned outcome column (Success is divided into Completed and Incomplete)
SELECT ride_outcome, COUNT(*) AS bookings
FROM ola_data_clean
GROUP BY ride_outcome
ORDER BY bookings DESC;


/* ---------------------------------------------------------------------
   SECTION 1: ANALYSIS QUERIES
   --------------------------------------------------------------------- */

-- Q1. Retrieve all successful bookings
SELECT *
FROM ola_data_clean
WHERE booking_status = 'Success';


-- Q2. Find the average ride distance for each vehicle type
SELECT
    vehicle_type,
    ROUND(AVG(ride_distance), 2) AS avg_ride_distance_km
FROM ola_data_clean
GROUP BY vehicle_type
ORDER BY avg_ride_distance_km DESC;


-- Q3. Get the total number of cancelled rides by customers
SELECT COUNT(*) AS cancelled_by_customers
FROM ola_data_clean
WHERE booking_status = 'Canceled by Customer';


-- Q4. List the top 5 customers who booked the highest number of rides
SELECT
    customer_id,
    COUNT(*) AS total_rides_booked
FROM ola_data_clean
GROUP BY customer_id
ORDER BY total_rides_booked DESC, customer_id
LIMIT 5;


-- Q5. Get the number of rides cancelled by drivers due to personal and car-related issues
SELECT COUNT(*) AS cancelled_personal_car_issues
FROM ola_data_clean
WHERE canceled_by_driver_reason = 'Personal & Car related issue';


-- Q6. Find the maximum and minimum driver ratings for Prime Sedan bookings
SELECT
    MAX(driver_ratings) AS max_driver_rating,
    MIN(driver_ratings) AS min_driver_rating
FROM ola_data_clean
WHERE vehicle_type = 'Prime Sedan';


-- Q7. Retrieve all rides where payment was made using UPI
SELECT *
FROM ola_data_clean
WHERE payment_method = 'UPI';


-- Q8. Find the average customer rating per vehicle type
SELECT
    vehicle_type,
    ROUND(AVG(customer_rating), 2) AS avg_customer_rating
FROM ola_data_clean
GROUP BY vehicle_type
ORDER BY avg_customer_rating DESC;


-- Q9. Calculate the total booking value of rides completed successfully
SELECT SUM(booking_value) AS total_booking_value
FROM ola_data_clean
WHERE ride_outcome = 'Completed';


-- Q10. List all incomplete rides along with the reason
SELECT
    booking_id,
    customer_id,
    vehicle_type,
    pickup_location,
    drop_location,
    incomplete_reason
FROM ola_data_clean
WHERE ride_outcome = 'Incomplete';
