import sqlite3

from gpt_query import zero_shot_sql_query, few_shot_single_domain_sql_query, cross_domain_few_shot_sql_query, load_client, get_key, nl_sql_response
import time
import random
import uuid
import json
from datetime import datetime, timedelta

def connect_to_db(db_name="database.db"):
	conn = sqlite3.connect(db_name)
	return conn

def create_cursor(conn):
	cursor = conn.cursor()
	return cursor

## DATABASE SCHEMA
"""
vehicles: self-driving cars
trips: driving sessions and routes
incidents: accidents, near-misses, etc.
sensors: sensors on each vehicle
sensorReadings: the readings on each sensor, timestamped 
"""

def create_table(cursor, conn):
	cursor.execute("""
				CREATE TABLE IF NOT EXISTS vehicles (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					vin VARCHAR(30) UNIQUE,
					model VARCHAR(30),
					make VARCHAR(30),
					year INTEGER,
					currentSoftwareVersion VARCHAR(9)
				);""")
	cursor.execute("""
				CREATE TABLE IF NOT EXISTS trips (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					vehicleId INTEGER NOT NULL,
					start_time DATETIME NOT NULL,
					end_time DATETIME,
					start_lat VARCHAR NOT NULL,
					start_lon VARCHAR NOT NULL,
					end_lat VARCHAR,
					end_lon VARCHAR,
					route_summary TEXT,
					FOREIGN KEY (vehicleId) REFERENCES vehicles(id)
						ON DELETE CASCADE
				);""")
	cursor.execute("""
				CREATE TABLE IF NOT EXISTS incidents (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					vehicleId INTEGER NOT NULL,
					tripId INTEGER,                       
					incident_time DATETIME NOT NULL,
					severity TEXT CHECK (severity IN ('low','medium','high','critical')) DEFAULT 'low',
					type TEXT,                           
					description TEXT,
					incident_lat VARCHAR,
					incident_lon VARCHAR,
					recorded_by TEXT,                  
					FOREIGN KEY (vehicleId) REFERENCES vehicles(id) 
						ON DELETE CASCADE,
					FOREIGN KEY (tripId) REFERENCES trips(id) 
						ON DELETE SET NULL
				);""")
	cursor.execute("""
				CREATE TABLE IF NOT EXISTS sensors (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					vehicleId INTEGER NOT NULL,
					name TEXT NOT NULL,                   
					sensor_type VARCHAR(30) NOT NULL,                     
					installed_at DATETIME,
					serial_number VARCHAR(50) UNIQUE,
					FOREIGN KEY (vehicleId) REFERENCES vehicles(id) 
						ON DELETE CASCADE
				);""")
	cursor.execute("""
				CREATE TABLE IF NOT EXISTS sensorReadings (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					sensorId INTEGER NOT NULL,
					timestamp TEXT NOT NULL,
					readingType VARCHAR(30) NOT NULL,                     
					readingValue TEXT,                    
					fileRef TEXT,                         
					FOREIGN KEY (sensorId) REFERENCES sensors(id) 
						ON DELETE CASCADE
				);""")
	cursor.executescript("""

				-- Insert sample data
				INSERT INTO vehicles (vin, model, year, make, currentSoftwareVersion)
				VALUES ('1HGBH41JXMN109118623', 'AutoCruiser-X', 2024, 'AutoMakers', 'v1.2.0');

				INSERT INTO trips (vehicleId, start_time, end_time, start_lat, start_lon, end_lat, end_lon, route_summary)
				VALUES (1, '2025-09-24T08:30:00', '2025-09-24T09:10:00', '40.7128', '-74.0060', '40.7580', '-73.9855', 'downtown commute');

				INSERT INTO incidents (vehicleId, tripId, incident_time, severity, type, description, incident_lat, incident_lon, recorded_by)
				VALUES (1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system');

				INSERT INTO sensors (vehicleId, name, sensor_type, serial_number)
				VALUES (1, 'front_lidar', 'lidar', 'LDR-001223'),
					(1, 'front_camera', 'camera', 'CAM-00938');

				INSERT INTO sensorReadings (sensorId, timestamp, readingType, readingValue, fileRef)
				VALUES (1, '2025-09-24T08:45:11', 'pointcloud_meta', '{"points": 45234}', '/data/vehicle1/pc_084511.pcd'),
					(2, '2025-09-24T08:45:11', 'image_meta', '{"objects_detected": 3}', '/data/vehicle1/img_084511.jpg');
				
				INSERT INTO vehicles (vin, model, make, year, currentSoftwareVersion) VALUES
				('1HGBH41JXMN109189', 'AutoCruiser-X', 'AutoMakers', 2024, 'v1.2.0'),
				('2FAGH41JXMN109187', 'RoboRider-Z', 'RoboCars', 2023, 'v3.4.1');
				
				INSERT INTO trips (vehicleId, start_time, end_time, start_lat, start_lon, end_lat, end_lon, route_summary) VALUES
				(1, '2025-09-24T08:30:00',	 '2025-09-24T09:10:00', '40.7128', '-74.0060', '40.7580', '-73.9855', 'downtown commute'),
				(2, '2025-09-25T14:00:00', '2025-09-25T14:45:00', '34.0522', '-118.2437', '34.1015', '-118.3265', 'airport run');
				
				INSERT INTO incidents (vehicleId, tripId, incident_time, severity, type, description, incident_lat, incident_lon, recorded_by) VALUES
				(1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system'),
				(2, 2, '2025-09-25T14:15:30', 'high', 'collision', 'Minor collision with another vehicle at intersection', '34.0700', '-118.2500', 'driver_report');
				
				INSERT INTO sensors (vehicleId, name, sensor_type, installed_at, serial_number) VALUES
				(1, 'front_lidar', 'lidar', '2024-015T10:00:00', 'LDR-001233'),
				(1, 'front_camera', 'camera', '2024-06-20T10:00:00', 'CAM-00982'),
				(2, 'rear_radar', 'radar', '2023-11-05T09:30:00', 'RDR-04561');
				
				INSERT INTO sensorReadings (sensorId, timestamp, readingType, readingValue, fileRef) VALUES
				(1, '2025-09-24T08:45:11', 'pointcloud_meta', '{"points": 45234}', '/data/vehicle1/pc_084511.pcd'),
				(2, '2025-09-24T08:45:11', 'image_meta', '{"objects_detected": 3}', '/data/vehicle1/img_084511.jpg'),
				(3, '2025-09-25T14:15:29', 'radar_meta', '{"vehicles_detected": 2}', '/data/vehicle2/radar_141529.dat');	
				   """)
	
	conn.commit()


def test_query(cursor):
	cursor.execute("SELECT * FROM vehicles;")
	rows = cursor.fetchall()
	for row in rows:
		print(row)

def close_connection(conn):
	conn.close()


def setup_database():
	conn = connect_to_db()
	cursor = create_cursor(conn)
	return (cursor, conn)


def _random_vin():
    # simple VIN-like generator (17 chars, uppercase alnum excluding I,O,Q could be added)
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(alphabet) for _ in range(17))

def _random_iso(dt):
    return dt.isoformat(timespec='seconds')


# ChatGPT generated sample data population function
def upload_sample_data(cursor, conn,
                       n_vehicles=100,
                       trips_per_vehicle=(1, 6),
                       sensors_per_vehicle=(2, 6),
                       readings_per_sensor=(5, 30),
                       incidents_per_trip=(0, 3),
                       seed=None):
    """
    Populate the database with a large variety of sample rows.
    Pass a sqlite3 cursor and connection. Commits at the end.

    Parameters:
    - n_vehicles: how many vehicle rows to create
    - trips_per_vehicle: (min,max) integer trip count per vehicle
    - sensors_per_vehicle: (min,max) sensors per vehicle
    - readings_per_sensor: (min,max) readings per sensor
    - incidents_per_trip: (min,max) incidents per trip
    - seed: optional random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)

    cursor.execute("PRAGMA foreign_keys = ON;")

    # Some catalog data to pick from
    makes_models = [
        ("AutoMakers", "AutoCruiser-X"),
        ("RoboCars", "RoboRider-Z"),
        ("DriveTech", "Pathfinder-2"),
        ("NeuMotion", "NaviCore"),
        ("UrbanMove", "CityGlide"),
        ("HorizonMotors", "Horizon-S"),
        ("ElectraDrive", "VoltRunner"),
    ]
    sw_versions = ["v1.0.0", "v1.2.0", "v1.3.5", "v2.0.0", "v3.1.4", "v3.4.1", "v4.0.0-beta"]
    sensor_types = ["lidar", "camera", "radar", "gps", "imu", "ultrasonic"]
    incident_types = ["near_miss", "collision", "hard_brake", "sensor_fault", "animal_strike", "road_hazard"]
    recorded_by_opts = ["auto_system", "driver_report", "bystander_report", "fleet_operator"]

    # Helper to pick random datetime between two datetimes
    def rand_dt(start, end):
        delta = end - start
        seconds = random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=seconds)

    # Date ranges
    earliest = datetime(2019, 1, 1)
    latest = datetime(2025, 9, 25, 23, 59, 59)  # keep before current date in dev instructions

    # City bounding boxes for varied lat/lon (approx)
    cities_bbox = {
        "NYC": (40.55, 40.92, -74.25, -73.7),
        "LA": (33.7, 34.34, -118.67, -117.9),
        "SF": (37.6, 37.82, -122.52, -122.35),
        "Chicago": (41.64, 42.02, -87.95, -87.52),
        "Austin": (30.1, 30.6, -97.95, -97.5),
        "Seattle": (47.45, 47.74, -122.45, -122.2),
        "Denver": (39.57, 39.86, -105.13, -104.6),
    }
    city_keys = list(cities_bbox.keys())

    # Keep lists of inserted ids for linking
    vehicle_ids = []

    # Insert vehicles
    for i in range(n_vehicles):
        make, model = random.choice(makes_models)
        year = random.randint(2018, 2025)
        vin = _random_vin()
        sw = random.choice(sw_versions)
        try:
            cursor.execute(
                "INSERT INTO vehicles (vin, model, make, year, currentSoftwareVersion) VALUES (?, ?, ?, ?, ?)",
                (vin, model, make, year, sw)
            )
        except Exception:
            # try a different VIN if unique constraint fails
            vin = _random_vin()
            cursor.execute(
                "INSERT OR IGNORE INTO vehicles (vin, model, make, year, currentSoftwareVersion) VALUES (?, ?, ?, ?, ?)",
                (vin, model, make, year, sw)
            )
        vid = cursor.lastrowid
        if vid is None:
            # If lastrowid failed (e.g., INSERT OR IGNORE skipped), try to look it up
            cursor.execute("SELECT id FROM vehicles WHERE vin = ?", (vin,))
            row = cursor.fetchone()
            vid = row[0] if row else None
            if vid is None:
                continue
        vehicle_ids.append(vid)

        # Insert sensors for this vehicle
        n_sensors = random.randint(sensors_per_vehicle[0], sensors_per_vehicle[1])
        sensor_ids = []
        for s_idx in range(n_sensors):
            s_type = random.choice(sensor_types)
            name = f"{s_type}_{s_idx+1}"
            installed_at = rand_dt(earliest, latest - timedelta(days=1))
            serial_number = f"{s_type[:3].upper()}-{uuid.uuid4().hex[:10].upper()}"
            try:
                cursor.execute(
                    "INSERT INTO sensors (vehicleId, name, sensor_type, installed_at, serial_number) VALUES (?, ?, ?, ?, ?)",
                    (vid, name, s_type, _random_iso(installed_at), serial_number)
                )
            except Exception:
                # If unique serial conflict somehow, change and retry
                serial_number = f"{s_type[:3].upper()}-{uuid.uuid4().hex[:10].upper()}"
                cursor.execute(
                    "INSERT INTO sensors (vehicleId, name, sensor_type, installed_at, serial_number) VALUES (?, ?, ?, ?, ?)",
                    (vid, name, s_type, _random_iso(installed_at), serial_number)
                )
            sid = cursor.lastrowid
            sensor_ids.append((sid, s_type, serial_number, installed_at))

        # Insert trips for this vehicle
        n_trips = random.randint(trips_per_vehicle[0], trips_per_vehicle[1])
        for t in range(n_trips):
            # choose a city and random start/end near that city
            city = random.choice(city_keys)
            lat_min, lat_max, lon_min, lon_max = cities_bbox[city]
            start_lat = round(random.uniform(lat_min, lat_max), 6)
            start_lon = round(random.uniform(lon_min, lon_max), 6)
            # trip duration between 5 minutes and 2.5 hours
            start_time = rand_dt(datetime(2023, 1, 1), latest - timedelta(hours=1))
            duration_min = random.randint(5, 150)
            end_time = start_time + timedelta(minutes=duration_min)
            # end point slightly different
            end_lat = round(start_lat + random.uniform(-0.2, 0.2), 6)
            end_lon = round(start_lon + random.uniform(-0.2, 0.2), 6)
            route_summary = random.choice([
                "commute", "airport_run", "test_loop", "delivery_route",
                "long_haul", "night_shift", "urban_exploration"
            ]) + (f" ({city})")

            cursor.execute(
                """INSERT INTO trips (vehicleId, start_time, end_time, start_lat, start_lon, end_lat, end_lon, route_summary)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (vid, _random_iso(start_time), _random_iso(end_time),
                 str(start_lat), str(start_lon), str(end_lat), str(end_lon), route_summary)
            )
            trip_id = cursor.lastrowid

            # Insert incidents for this trip
            n_inc = random.randint(incidents_per_trip[0], incidents_per_trip[1])
            for inc_i in range(n_inc):
                inc_time = rand_dt(start_time, end_time - timedelta(seconds=1))
                severity = random.choices(["low", "medium", "high", "critical"], weights=[60,25,12,3])[0]
                itype = random.choice(incident_types)
                description = random.choice([
                    "Pedestrian crossed unexpectedly",
                    "Minor scrape with roadside object",
                    "Hard braking due to unexpected vehicle",
                    "Sensor returned inconsistent data",
                    "Animal crossed road",
                    "Pothole/road hazard detected"
                ])
                # incident coordinates near the trip path
                frac = random.random()
                incident_lat = str(round(start_lat + frac * (end_lat - start_lat) + random.uniform(-0.001, 0.001), 6))
                incident_lon = str(round(start_lon + frac * (end_lon - start_lon) + random.uniform(-0.001, 0.001), 6))
                recorded_by = random.choice(recorded_by_opts)
                cursor.execute(
                    """INSERT INTO incidents (vehicleId, tripId, incident_time, severity, type, description, incident_lat, incident_lon, recorded_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (vid, trip_id, _random_iso(inc_time), severity, itype, description, incident_lat, incident_lon, recorded_by)
                )

        # Insert sensorReadings for sensors of this vehicle
        for (sid, s_type, serial, installed_at) in sensor_ids:
            n_read = random.randint(readings_per_sensor[0], readings_per_sensor[1])
            # reading window: from installed_at (or 2022-01-01 if installed earlier) to latest
            start_window = installed_at if isinstance(installed_at, datetime) else earliest
            for r in range(n_read):
                ts = rand_dt(start_window, latest)
                # map readingType to sensor_type
                if s_type == "lidar":
                    rtype = "pointcloud_meta"
                    readingValue = {"points": random.randint(1000, 200000)}
                    fileExt = "pcd"
                elif s_type == "camera":
                    rtype = "image_meta"
                    readingValue = {"objects_detected": random.randint(0, 12)}
                    fileExt = "jpg"
                elif s_type == "radar":
                    rtype = "radar_meta"
                    readingValue = {"targets": random.randint(0, 8)}
                    fileExt = "dat"
                elif s_type == "gps":
                    rtype = "gps_fix"
                    readingValue = {"lat": round(random.uniform(-90, 90), 6), "lon": round(random.uniform(-180, 180), 6)}
                    fileExt = "json"
                elif s_type == "imu":
                    rtype = "imu_read"
                    readingValue = {"accel_m_s2": round(random.uniform(-10, 10), 3)}
                    fileExt = "json"
                else:  # ultrasonic or others
                    rtype = "distance_mm"
                    readingValue = {"distance_mm": random.randint(50, 10000)}
                    fileExt = "json"

                reading_json = json.dumps(readingValue)
                # fileRef optional
                fileRef = f"/data/vehicle_{vid}/s_{serial}_{_random_iso(ts).replace(':','')}.{fileExt}"
                cursor.execute(
                    "INSERT INTO sensorReadings (sensorId, timestamp, readingType, readingValue, fileRef) VALUES (?, ?, ?, ?, ?)",
                    (sid, _random_iso(ts), rtype, reading_json, fileRef)
                )

    # commit once at the end
    conn.commit()
    print(f"Inserted sample data: vehicles={len(vehicle_ids)} (approx), sensors/trips/incidents/readings varied per vehicle.")



def main():
	cursor, conn = setup_database()
	user_question = input("Enter your question about the self-driving car database: ")
	#user_question = "Find all incidents that involve lidar and join them with the vehicle information."
	client = load_client(get_key("key.env"))

	curr_time = time.strftime("%Y%m%d-%H%M%S")

	print("Attempting zero-shot SQL query generation...")
	
	response = zero_shot_sql_query(client, user_question)
	print("Generated SQL Query:")
	print(response)
	print("\nExecuting the query...")
	try:
		cursor.execute(response)
		results = cursor.fetchall()
		print("Query Results:")
		for result in results:
			print(result)
		nl_response = nl_sql_response(client, user_question, response, results)
		print("\nNatural Language Summary of Results:")
		print(nl_response)
	except sqlite3.Error as e:
		print("An error occurred:", e)
	
	print(f"Took {time.strftime('%Y%m%d-%H%M%S')} - {curr_time} seconds")
	# print("Waiting 2 seconds to avoid rate limits..")
	# time.sleep(2)

	
	
	curr_time = time.strftime("%Y%m%d-%H%M%S")
	print("\nAttempting few-shot single-domain SQL query generation...")
	response = few_shot_single_domain_sql_query(client, user_question)
	print("Generated SQL Query:")
	print(response)
	print("\nExecuting the query...")
	try:
		cursor.execute(response)
		results = cursor.fetchall()
		print("Query Results:")
		for result in results:
			print(result)
		nl_response = nl_sql_response(client, user_question, response, results)
		print("\nNatural Language Summary of Results:")
		print(nl_response)
	except sqlite3.Error as e:
		print("An error occurred:", e)

	print(f"Took {time.strftime('%Y%m%d-%H%M%S')} - {curr_time} seconds")
	# print("Waiting 2 seconds to avoid rate limits..")
	# time.sleep(2)

	curr_time = time.strftime("%Y%m%d-%H%M%S")
	print("\nAttempting cross-domain few-shot SQL query generation...")
	response = cross_domain_few_shot_sql_query(client, user_question)
	print("Generated SQL Query:")
	print(response)
	print("\nExecuting the query...")
	try:
		cursor.execute(response)
		results = cursor.fetchall()
		print("Query Results:")
		for result in results:
			print(result)
		nl_response = nl_sql_response(client, user_question, response, results)
		print("\nNatural Language Summary of Results:")
		print(nl_response)
	except sqlite3.Error as e:
		print("An error occurred:", e)

	print(f"Took {time.strftime('%Y%m%d-%H%M%S')} - {curr_time} seconds")
	print("Done.")
	close_connection(conn)


if __name__ == "__main__":
      #cur, conn = setup_database()
      #upload_sample_data(cur, conn, n_vehicles=2000, seed=40)
      main()