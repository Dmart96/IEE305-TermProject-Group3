/* ============================================================================
    IEE 305 Term Project
    SQL Query Set (10 total)
    Covers required SQL concepts: JOIN, GROUP BY, HAVING, subqueries, 
    filtering, ORDER BY, LIMIT, and parameters.
============================================================================ */


/* ---------------------------------------------------------------------------
   Query 1 – Parks in California with entrance fee < $35
--------------------------------------------------------------------------- */
SELECT 'Query 1 – Parks in California with entrance fee < $35' AS description;

SELECT park_code,
       name,
       state_code,
       entrance_fee
FROM parks
WHERE state_code = 'CA'
  AND entrance_fee < 35;


/* ---------------------------------------------------------------------------
   Query 2 – Event count per park (filter by year)
--------------------------------------------------------------------------- */
SELECT 'Query 2 – Event count per park (year = 2025)' AS description;

SELECT p.park_code,
       p.name,
       COUNT(e.id) AS event_count
FROM parks AS p
LEFT JOIN events AS e
  ON e.park_code = p.park_code
  AND strftime('%Y', e.start_date) = '2025'   -- adjust year as needed
GROUP BY p.park_code, p.name
ORDER BY event_count DESC;


/* ---------------------------------------------------------------------------
   Query 3 – Parks with more events than the overall average
--------------------------------------------------------------------------- */
SELECT 'Query 3 – Parks with more events than the overall average' AS description;

SELECT p.park_code,
       p.name,
       ec.event_count
FROM parks AS p
JOIN (
    SELECT park_code,
           COUNT(*) AS event_count
    FROM events
    GROUP BY park_code
) AS ec
  ON ec.park_code = p.park_code
WHERE ec.event_count >
    (
        SELECT AVG(event_count)
        FROM (
            SELECT COUNT(*) AS event_count
            FROM events
            GROUP BY park_code
        ) AS sub
    )
ORDER BY ec.event_count DESC;


/* ---------------------------------------------------------------------------
   Query 4 – Top 5 parks by number of free events
--------------------------------------------------------------------------- */
SELECT 'Query 4 – Top 5 parks by number of free events' AS description;

SELECT p.park_code,
       p.name,
       COUNT(e.id) AS free_event_count
FROM parks AS p
JOIN events AS e
  ON e.park_code = p.park_code
WHERE e.is_free = 1
GROUP BY p.park_code, p.name
ORDER BY free_event_count DESC
LIMIT 5;


/* --------------------------------------------------------------------
   Query 5 – Events with park name and all visitor centers per park
   (3-table JOIN + GROUP_CONCAT to keep one row per event)
---------------------------------------------------------------------*/
SELECT 'Query 5 – Events with park name and all visitor centers per park' AS description;

SELECT  e.id                    AS event_id,
        e.event_title,
        p.name                  AS park_name,
        GROUP_CONCAT(vc.center_name, ', ') AS all_centers
FROM events AS e
JOIN parks AS p
  ON e.park_code = p.park_code
JOIN visitor_centers AS vc
  ON vc.park_code = p.park_code
GROUP BY e.id, e.event_title, p.name
ORDER BY p.name, e.event_title;


/* ---------------------------------------------------------------------------
   Query 6 – Parks with >= 1 visitor center AND >= 6 events (year filter)
--------------------------------------------------------------------------- */
SELECT 'Query 6 – Parks with >= 1 visitor center AND >= 6 events (year = 2025)' AS description;

SELECT p.park_code,
       p.name,
       COUNT(DISTINCT vc.id) AS visitor_center_count,
       COUNT(DISTINCT e.id)  AS event_count
FROM parks AS p
LEFT JOIN visitor_centers AS vc
  ON vc.park_code = p.park_code
LEFT JOIN events AS e
  ON e.park_code = p.park_code
  AND strftime('%Y', e.start_date) = '2025'
GROUP BY p.park_code, p.name
HAVING visitor_center_count >= 1
   AND event_count >= 6;


/* ---------------------------------------------------------------------------
   Query 7 – Events for a park within a date range (parameterized template)
   (Template used in application code; not executed directly in sqlite3)

   -- Template form:
   -- SELECT e.id,
   --        e.event_title,
   --        e.start_date,
   --        e.end_date,
   --        e.is_free
   -- FROM events AS e
   -- WHERE e.park_code   = :park_code
   --   AND e.start_date >= :start_date
   --   AND e.start_date <= :end_date
   -- ORDER BY e.start_date, e.event_title;
--------------------------------------------------------------------------- */

SELECT 'Query 7 – Example: Events in YOSE between 2025-01-01 and 2025-12-31' AS description;

SELECT e.id,
       e.event_title,
       e.start_date,
       e.end_date,
       e.is_free
FROM events AS e
WHERE e.park_code   = 'yose'
  AND e.start_date >= '2025-01-01'
  AND e.start_date <= '2025-12-31'
ORDER BY e.start_date, e.event_title;


/* ---------------------------------------------------------------------------
   Query 8 – Parks with no or limited events (<= 2)
--------------------------------------------------------------------------- */
SELECT 'Query 8 – Parks with no or limited events (<= 2)' AS description;

SELECT p.park_code,
       p.name,
       COUNT(e.id) AS event_count
FROM parks AS p
LEFT JOIN events AS e
  ON e.park_code = p.park_code
GROUP BY p.park_code, p.name
HAVING event_count IS NULL OR event_count <= 2
ORDER BY event_count ASC, p.name;


/* ---------------------------------------------------------------------------
   Query 9 – Parks and events for a given state + date range (parameterized)
   (Template for code; example for report)
   
   -- Template form:
   -- SELECT p.state_code,
   --        p.park_code,
   --        p.name        AS park_name,
   --        e.event_title,
   --        e.start_date,
   --        e.end_date
   -- FROM parks AS p
   -- JOIN events AS e
   --   ON e.park_code = p.park_code
   -- WHERE p.state_code   = :state_code
   --   AND e.start_date >= :start_date
   --   AND e.start_date <= :end_date
   -- ORDER BY e.start_date, p.name, e.event_title;
--------------------------------------------------------------------------- */

SELECT 'Query 9 – Example: Parks/events in AZ between 2025-12-01 and 2026-12-31' AS description;

SELECT p.state_code,
       p.park_code,
       p.name        AS park_name,
       e.event_title,
       e.start_date,
       e.end_date
FROM parks AS p
JOIN events AS e
  ON e.park_code = p.park_code
WHERE p.state_code   = 'AZ'
  AND e.start_date >= '2025-12-01'
  AND e.start_date <= '2026-12-31'
ORDER BY e.start_date, p.name, e.event_title;


/* ---------------------------------------------------------------------------
   Query 10 – Parks with entrance fee between $30 and $40
--------------------------------------------------------------------------- */
SELECT 'Query 10 – Parks with entrance fee between $30 and $40' AS description;

SELECT park_code,
       name,
       state_code,
       entrance_fee
FROM parks
WHERE entrance_fee > 30
  AND entrance_fee < 40
ORDER BY entrance_fee DESC;


