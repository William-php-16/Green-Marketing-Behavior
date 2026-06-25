-- ── 1. CHECK DATABASE CONNECTION ──────────────────────────────────────────────
-- Lists all tables in the database; confirms the connection is alive
SELECT name, type
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;

-- ── 2. CHECK TABLE EXISTS ──────────────────────────────────────────────────────
-- Returns 1 if the table was created, 0 if not
SELECT COUNT(*) AS table_exists
FROM sqlite_master
WHERE type = 'table'
  AND name = 'green_consumption_behavior';

-- ── 3. INSPECT TABLE SCHEMA ────────────────────────────────────────────────────
-- Shows each column: id, name, data type, not-null flag, default, primary key
PRAGMA table_info(green_consumption_behavior);

-- ── 4. CHECK ROW COUNT ─────────────────────────────────────────────────────────
-- Confirms data was loaded; should match the CSV row count
SELECT COUNT(*) AS total_rows
FROM green_consumption_behavior;

-- ── 5. PREVIEW FIRST 5 ROWS ────────────────────────────────────────────────────
-- Quick sanity check that values look correct
SELECT *
FROM green_consumption_behavior
LIMIT 5;

-- ── 6. CHECK FOR NULL VALUES IN CRITICAL COLUMNS ──────────────────────────────
-- All counts should be 0 after cleaning
SELECT
    SUM(CASE WHEN User_ID            IS NULL THEN 1 ELSE 0 END) AS null_user_id,
    SUM(CASE WHEN Age                IS NULL THEN 1 ELSE 0 END) AS null_age,
    SUM(CASE WHEN Gender             IS NULL THEN 1 ELSE 0 END) AS null_gender,
    SUM(CASE WHEN Income_Level       IS NULL THEN 1 ELSE 0 END) AS null_income_level,
    SUM(CASE WHEN Green_Purchase_Made IS NULL THEN 1 ELSE 0 END) AS null_green_purchase
FROM green_consumption_behavior;

-- ── 7. CHECK DISTINCT VALUES IN CATEGORICAL COLUMNS ───────────────────────────
-- Verifies normalization (no mixed casing / extra spaces)
SELECT DISTINCT Gender        FROM green_consumption_behavior ORDER BY Gender;
SELECT DISTINCT Income_Level  FROM green_consumption_behavior ORDER BY Income_Level;
SELECT DISTINCT Device_Type   FROM green_consumption_behavior ORDER BY Device_Type;
SELECT DISTINCT Referral_Source FROM green_consumption_behavior ORDER BY Referral_Source;
SELECT DISTINCT Product_Category FROM green_consumption_behavior ORDER BY Product_Category;
