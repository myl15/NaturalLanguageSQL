import sqlite3

from gpt_query import zero_shot_sql_query, few_shot_single_domain_sql_query, cross_domain_few_shot_sql_query, load_client, get_key, nl_sql_response
import time

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

def main():
	cursor, conn = setup_database()
	#user_question = input("Enter your question about the self-driving car database: ")
	user_question = "Find all incidents that involve lidar and join them with the vehicle information."
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
	main()