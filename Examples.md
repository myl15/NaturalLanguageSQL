# Examples

## Description
Here are some example runs of the program with their corresponding outputs.

## Example 1
```
Enter your question about the self-driving car database: Find all incidents that involved Lidar and join them with the vehicle information.
Attempting zero-shot SQL query generation...
Generated SQL Query:
SELECT i.*, v.*
FROM Incidents i
JOIN Vehicles v ON i.vehicleId = v.id
WHERE EXISTS (
  SELECT 1
  FROM Sensors s
  WHERE s.vehicleId = v.id
    AND s.sensor_type = 'lidar'
);

Executing the query...
Query Results:
(1, 1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system', 1, '1HGBH41JXMN109186', 'AutoCruiser-X', 'AutoMakers', 2024, 'v1.2.0')
(2, 1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system', 1, '1HGBH41JXMN109186', 'AutoCruiser-X', 'AutoMakers', 2024, 'v1.2.0')
(3, 1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system', 1, '1HGBH41JXMN109186', 'AutoCruiser-X', 'AutoMakers', 2024, 'v1.2.0')
(4, 1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system', 1, '1HGBH41JXMN109186', 'AutoCruiser-X', 'AutoMakers', 2024, 'v1.2.0')

Natural Language Summary of Results:
Four incidents (IDs 1û4) for vehicle ID 1 (VIN 1HGBH41JXMN109186): all occurred at 2025-09-24T08:45:12, severity = medium, type = near_miss, description = "Pedestrian suddenly stepped into crosswalk", location = (40.7350, -74.0001), recorded_by = auto_system; vehicle = AutoCruiser-X, AutoMakers, 2024, currentSoftwareVersion = v1.2.0.
Took 20250926-105319 - 20250926-105258 seconds

Attempting few-shot single-domain SQL query generation...
Generated SQL Query:
SELECT i.*, v.*
FROM incidents i
JOIN vehicles v ON i.vehicle_id = v.id
WHERE LOWER(COALESCE(i.description, '')) LIKE '%lidar%'
   OR LOWER(COALESCE(i.equipment, '')) LIKE '%lidar%'
   OR LOWER(COALESCE(i.notes, '')) LIKE '%lidar%'
   OR LOWER(COALESCE(i.sensor_type, '')) LIKE '%lidar%';

Executing the query...
An error occurred: no such column: i.equipment
Took 20250926-105328 - 20250926-105319 seconds

Attempting cross-domain few-shot SQL query generation...
Generated SQL Query:
SELECT DISTINCT i.*, v.*
FROM incidents i
JOIN vehicles v ON i.vehicleId = v.id
LEFT JOIN sensors s ON s.vehicleId = v.id
WHERE LOWER(COALESCE(i.type, '') || ' ' || COALESCE(i.description, '') || ' ' || COALESCE(i.recorded_by, '')) LIKE '%lidar%'
   OR LOWER(s.sensor_type) LIKE '%lidar%';

Executing the query...
Query Results:
(1, 1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system', 1, '1HGBH41JXMN109186', 'AutoCruiser-X', 'AutoMakers', 2024, 'v1.2.0')
(2, 1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system', 1, '1HGBH41JXMN109186', 'AutoCruiser-X', 'AutoMakers', 2024, 'v1.2.0')
(3, 1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system', 1, '1HGBH41JXMN109186', 'AutoCruiser-X', 'AutoMakers', 2024, 'v1.2.0')
(4, 1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system', 1, '1HGBH41JXMN109186', 'AutoCruiser-X', 'AutoMakers', 2024, 'v1.2.0')

Natural Language Summary of Results:
The query returned four rows showing the same incident(s) for vehicle id 1 (VIN 1HGBH41JXMN109186, AutoCruiser-X, AutoMakers, 2024, currentSoftwareVersion v1.2.0): a medium near_miss at 2025-09-24T08:45:12 ù "Pedestrian suddenly stepped into crosswalk" at 40.7350, -74.0001, recorded_by auto_system.
Took 20250926-105352 - 20250926-105328 seconds
Done.
```

## Example 2
```
Enter your question about the self-driving car database: What is the most common cause of incidents that occur in the fall?
Attempting zero-shot SQL query generation...
Generated SQL Query:
SELECT type, COUNT(*) AS cnt
FROM Incidents
WHERE EXTRACT(MONTH FROM incident_time) IN (9,10,11)
GROUP BY type
ORDER BY cnt DESC
LIMIT 1;

Executing the query...
An error occurred: near "FROM": syntax error
Took 20250926-112359 - 20250926-112352 seconds

Attempting few-shot single-domain SQL query generation...
Generated SQL Query:
SELECT cause, cnt
FROM (
  SELECT cause,
         COUNT(*) AS cnt,
         RANK() OVER (ORDER BY COUNT(*) DESC) AS rnk
  FROM incidents
  WHERE EXTRACT(MONTH FROM incident_date) IN (9, 10, 11)
  GROUP BY cause
) t
WHERE rnk = 1;

Executing the query...
An error occurred: near "FROM": syntax error
Took 20250926-112411 - 20250926-112359 seconds

Attempting cross-domain few-shot SQL query generation...
Generated SQL Query:
SELECT type, COUNT(*) AS incident_count
FROM incidents
WHERE strftime('%m', incident_time) IN ('09','10','11')
GROUP BY type
ORDER BY incident_count DESC
LIMIT 1;

Executing the query...
Query Results:
('sensor_fault', 414)

Natural Language Summary of Results:
The most common cause of incidents in the fall is "sensor_fault", accounting for 414 incidents.
Took 20250926-112420 - 20250926-112411 seconds
Done.
```

## Example 3
```
Enter your question about the self-driving car database: Which incidents involving pointclouds_meta also involved animals crossing the road?
Attempting zero-shot SQL query generation...
Generated SQL Query:
SELECT i.*
FROM Incidents i
WHERE (
    i.recorded_by = 'pointclouds_meta'
    OR EXISTS (
        SELECT 1 FROM Sensors s
        WHERE s.vehicleId = i.vehicleId
          AND lower(s.name) = 'pointclouds_meta'
    )
)
AND (
    lower(i.type) LIKE '%animal%'
    OR lower(i.type) LIKE '%animal_cross%'
    OR lower(i.description) LIKE '%animal crossing%'
    OR (lower(i.description) LIKE '%animal%' AND lower(i.description) LIKE '%cross%')
);

Executing the query...
Query Results:

Natural Language Summary of Results:
Incidents that were either recorded_by 'pointclouds_meta' or occurred on vehicles with a sensor named 'pointclouds_meta', and whose type or description indicates an animal crossing the road (matches 'animal', 'animal_cross', 'animal crossing', or contains both 'animal' and 'cross').
Took 20250926-112804 - 20250926-112733 seconds

Attempting few-shot single-domain SQL query generation...
Generated SQL Query:
SELECT DISTINCT i.id AS incident_id,
       i.title,
       i.description,
       pm.id AS pointclouds_meta_id
FROM incidents i
JOIN pointclouds_meta pm ON pm.incident_id = i.id
LEFT JOIN incident_events e ON e.incident_id = i.id
LEFT JOIN incident_tags t ON t.incident_id = i.id
WHERE (
  LOWER(COALESCE(i.description, '')) LIKE '%animal%'
  OR LOWER(COALESCE(i.description, '')) LIKE '%animals%'
  OR LOWER(COALESCE(i.description, '')) LIKE '%animal crossing%'
  OR LOWER(COALESCE(e.event_type, '')) LIKE '%animal%'
  OR LOWER(COALESCE(e.event_description, '')) LIKE '%animal%'
  OR LOWER(COALESCE(t.tag, '')) LIKE '%animal%'
);

Executing the query...
An error occurred: no such table: pointclouds_meta
Took 20250926-112819 - 20250926-112804 seconds

Attempting cross-domain few-shot SQL query generation...
Generated SQL Query:
SELECT i.* 
FROM incidents i
JOIN sensors s ON s.vehicleId = i.vehicleId
JOIN sensorReadings sr ON sr.sensorId = s.id
WHERE sr.readingType = 'pointclouds_meta'
  AND sr.timestamp BETWEEN datetime(i.incident_time, '-5 seconds') AND datetime(i.incident_time, '+5 seconds')
  AND (i.type = 'animal_crossing' OR i.type LIKE '%animal%' OR i.description LIKE '%animal%');

Executing the query...
Query Results:

Natural Language Summary of Results:
Incidents that are animal-related (type = 'animal_crossing' or whose type/description contains "animal") and that have at least one pointclouds_meta sensorReading from a sensor on the same vehicle within ±5 seconds of the incident_time.
Took 20250926-112838 - 20250926-112819 seconds
Done.
```

## Example 4
```
Enter your question about the self-driving car database: Find what season of the year involved the most incidents with animals.
Attempting zero-shot SQL query generation...
Generated SQL Query:
SELECT season, COUNT(*) AS incident_count
FROM (
  SELECT
    CASE
      WHEN EXTRACT(MONTH FROM CAST(incident_time AS TIMESTAMP)) IN (12,1,2) THEN 'winter'
      WHEN EXTRACT(MONTH FROM CAST(incident_time AS TIMESTAMP)) IN (3,4,5) THEN 'spring'
      WHEN EXTRACT(MONTH FROM CAST(incident_time AS TIMESTAMP)) IN (6,7,8) THEN 'summer'
      WHEN EXTRACT(MONTH FROM CAST(incident_time AS TIMESTAMP)) IN (9,10,11) THEN 'autumn'
    END AS season
  FROM incidents
  WHERE LOWER(COALESCE(type, '')) LIKE '%animal%' OR LOWER(COALESCE(description, '')) LIKE '%animal%'
) AS seasons
GROUP BY season
ORDER BY incident_count DESC
LIMIT 1;

Executing the query...
An error occurred: near "FROM": syntax error
Took 20250926-113017 - 20250926-113008 seconds

Attempting few-shot single-domain SQL query generation...
Generated SQL Query:
SELECT
  CASE
    WHEN EXTRACT(MONTH FROM incident_date) IN (12,1,2) THEN 'Winter'
    WHEN EXTRACT(MONTH FROM incident_date) IN (3,4,5) THEN 'Spring'
    WHEN EXTRACT(MONTH FROM incident_date) IN (6,7,8) THEN 'Summer'
    WHEN EXTRACT(MONTH FROM incident_date) IN (9,10,11) THEN 'Fall'
  END AS season,
  COUNT(*) AS incidents_count
FROM incidents
WHERE animal_involved = TRUE
GROUP BY
  CASE
    WHEN EXTRACT(MONTH FROM incident_date) IN (12,1,2) THEN 'Winter'
    WHEN EXTRACT(MONTH FROM incident_date) IN (3,4,5) THEN 'Spring'
    WHEN EXTRACT(MONTH FROM incident_date) IN (6,7,8) THEN 'Summer'
    WHEN EXTRACT(MONTH FROM incident_date) IN (9,10,11) THEN 'Fall'
  END
ORDER BY incidents_count DESC
LIMIT 1;

Executing the query...
An error occurred: near "FROM": syntax error
Took 20250926-113041 - 20250926-113017 seconds

Attempting cross-domain few-shot SQL query generation...
Generated SQL Query:
SELECT CASE
    WHEN CAST(strftime('%m', incident_time) AS INTEGER) IN (12,1,2) THEN 'winter'
    WHEN CAST(strftime('%m', incident_time) AS INTEGER) IN (3,4,5) THEN 'spring'
    WHEN CAST(strftime('%m', incident_time) AS INTEGER) IN (6,7,8) THEN 'summer'
    WHEN CAST(strftime('%m', incident_time) AS INTEGER) IN (9,10,11) THEN 'fall'
END AS season,
COUNT(*) AS incident_count
FROM incidents
WHERE lower(type) LIKE '%animal%' OR lower(description) LIKE '%animal%'
GROUP BY season
ORDER BY incident_count DESC
LIMIT 1;

Executing the query...
Query Results:
('summer', 958)

Natural Language Summary of Results:
Summer had the most incidents involving animals, with 958 incidents.
Took 20250926-113053 - 20250926-113041 seconds
Done.
```

## Example 5
```
Enter your question about the self-driving car database: What are the three most incident-prone car makes?                                       
Attempting zero-shot SQL query generation...
Generated SQL Query:
SELECT v.make, COUNT(*) AS incident_count
FROM incidents i
JOIN vehicles v ON v.id = i.vehicleId
GROUP BY v.make
ORDER BY incident_count DESC, v.make ASC
LIMIT 3;

Executing the query...
Query Results:
('DriveTech', 1950)
('ElectraDrive', 1674)
('RoboCars', 1643)

Natural Language Summary of Results:
DriveTech, ElectraDrive, and RoboCars—recording 1950, 1674, and 1643 incidents, respectively.
Took 20250926-113326 - 20250926-113307 seconds

Attempting few-shot single-domain SQL query generation...
Generated SQL Query:
SELECT v.make, COUNT(*) AS incident_count
FROM incidents i
JOIN vehicles v ON v.id = i.vehicle_id
GROUP BY v.make
ORDER BY incident_count DESC, v.make ASC
LIMIT 3;

Executing the query...
An error occurred: no such column: i.vehicle_id
Took 20250926-113334 - 20250926-113326 seconds

Attempting cross-domain few-shot SQL query generation...
Generated SQL Query:
SELECT v.make, COUNT(*) AS incident_count
FROM incidents i
JOIN vehicles v ON i.vehicleId = v.id
GROUP BY v.make
ORDER BY incident_count DESC
LIMIT 3;

Executing the query...
Query Results:
('DriveTech', 1950)
('ElectraDrive', 1674)
('RoboCars', 1643)

Natural Language Summary of Results:
DriveTech (1950), ElectraDrive (1674), and RoboCars (1643)
Took 20250926-113344 - 20250926-113334 seconds
Done.
```

## Example 6
``` 
Enter your question about the self-driving car database: Which incidents that occurred at night also invovled camera sensors?
Attempting zero-shot SQL query generation...
Generated SQL Query:
SELECT DISTINCT i.*
FROM incidents i
JOIN sensors s ON s.vehicleId = i.vehicleId
WHERE s.sensor_type = 'camera'
  AND (s.installed_at IS NULL OR s.installed_at <= i.incident_time)
  AND (EXTRACT(HOUR FROM i.incident_time) >= 20 OR EXTRACT(HOUR FROM i.incident_time) < 6);

Executing the query...
An error occurred: near "FROM": syntax error
Took 20250926-113526 - 20250926-113510 seconds

Attempting few-shot single-domain SQL query generation...
Generated SQL Query:
SELECT DISTINCT i.*
FROM incidents i
WHERE (EXTRACT(HOUR FROM i.occurred_at) >= 20 OR EXTRACT(HOUR FROM i.occurred_at) < 6)
  AND EXISTS (
    SELECT 1
    FROM incident_sensors isx
    JOIN sensors s ON s.id = isx.sensor_id
    WHERE isx.incident_id = i.id
      AND LOWER(s.sensor_type) = 'camera'
  );

Executing the query...
An error occurred: near "FROM": syntax error
Took 20250926-113550 - 20250926-113526 seconds

Attempting cross-domain few-shot SQL query generation...
Generated SQL Query:
SELECT DISTINCT i.*
FROM incidents i
JOIN sensors s ON s.vehicleId = i.vehicleId AND s.sensor_type = 'camera'
JOIN sensorReadings sr ON sr.sensorId = s.id
WHERE (strftime('%H:%M:%S', i.incident_time) BETWEEN '20:00:00' AND '23:59:59'
       OR strftime('%H:%M:%S', i.incident_time) BETWEEN '00:00:00' AND '06:00:00')
  AND sr.timestamp BETWEEN datetime(i.incident_time, '-5 seconds') AND datetime(i.incident_time, '+5 seconds');

Executing the query...
Query Results:

Natural Language Summary of Results:
None—no night-time incidents with camera sensor involvement were found.
Took 20250926-113621 - 20250926-113550 seconds
Done.
```