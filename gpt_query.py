from openai import OpenAI

def get_key(filename):
    with open(filename, "r") as f:
        key = f.readline().split("=")[1]
        return key
    
def load_client(key):
    client = OpenAI(
        api_key=key
    )
    return client

def cross_domain_few_shot_sql_query(client, question):
    context = """You are an expert SQL generator. Given a question, generate a syntactically correct SQL query to answer the question using the following database schema:
    
				CREATE TABLE IF NOT EXISTS vehicles (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					vin VARCHAR(30) UNIQUE,
					model VARCHAR(30),
					make VARCHAR(30),
					year INTEGER,
					currentSoftwareVersion VARCHAR(9)
				);
	
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
				);
	
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
				);
	
				CREATE TABLE IF NOT EXISTS sensors (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					vehicleId INTEGER NOT NULL,
					name TEXT NOT NULL,                   
					sensor_type VARCHAR(30) NOT NULL,                     
					installed_at DATETIME,
					serial_number VARCHAR(50) UNIQUE,
					FOREIGN KEY (vehicleId) REFERENCES vehicles(id) 
						ON DELETE CASCADE
				);
	
				CREATE TABLE IF NOT EXISTS sensorReadings (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					sensorId INTEGER NOT NULL,
					timestamp TEXT NOT NULL,
					readingType VARCHAR(30) NOT NULL,                     
					readingValue TEXT,                    
					fileRef TEXT,                         
					FOREIGN KEY (sensorId) REFERENCES sensors(id) 
						ON DELETE CASCADE
				);

                Additionally, here are some example natural language questions and their corresponding SQL queries:
                Question: "List all vehicles manufactured by 'AutoMakers' after the year 2020."
                SQL: "SELECT * FROM vehicles WHERE make = 'AutoMakers' AND year > 2020;"
                Question: "Select all incidents that happened during a trip."
                SQL: "SELECT i.*, t.start_time, t.end_time
                    FROM incidents i
                    JOIN trips t ON i.tripId = t.id
                    WHERE i.vehicleId = 1;"
                Question: "Find all sensors installed on vehicle with VIN '1HGBH41JXMN10918623'."
                SQL: "SELECT s.* FROM sensors s
                    JOIN vehicles v ON s.vehicleId = v.id
                    WHERE v.vin = '1HGBH41JXMN10918623';"
                Question: "Find all sensor readings within 5 seconds of an incident time."
                SQL: "SELECT sr.* 
                    FROM sensorReadings sr
                    JOIN sensors s ON sr.sensorId = s.id
                    JOIN incidents i ON i.vehicleId = s.vehicleId
                    WHERE i.id = 1
                    AND sr.timestamp BETWEEN datetime(i.incident_time, '-5 seconds') AND datetime(i.incident_time, '+5 seconds');
                    
                Here is an example of a different database schema:
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100),
                    department VARCHAR(50),
                    hire_date DATE
                );
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100),
                    start_date DATE,
                    end_date DATE
                );
                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employeeId INTEGER,
                    projectId INTEGER,
                    assigned_date DATE,
                    FOREIGN KEY (employeeId) REFERENCES employees(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (projectId) REFERENCES projects(id)
                        ON DELETE CASCADE
                );

                Here are some example questions and SQL queries for this different schema:
                Question: "List all employees in the 'Engineering' department hired after 2020."
                SQL: "SELECT * FROM employees WHERE department = 'Engineering' AND hire_date > '2020-01-01';"
                Question: "Find all projects that started in 2023."
                SQL: "SELECT * FROM projects WHERE start_date BETWEEN '2023-01-01' AND '2023-12-31';"
                Question: "Get all employees assigned to the project named 'Project Phoenix'."
                SQL: "SELECT e.* FROM employees e
                    JOIN assignments a ON e.id = a.employeeId
                    JOIN projects p ON a.projectId = p.id
                    WHERE p.name = 'Project Phoenix';"
                Question: "List all assignments made in the last 30 days."
                SQL: "SELECT * FROM assignments WHERE assigned_date >= DATE('now', '-30 days');"

    Now using the above schema and examples, answer: """ + question + """
    Generate the SQL query to answer the question. Only return the SQL query, do not include any explanations or other text.
                    """
    response = client.responses.create(
        model="gpt-5-mini",
        instructions="You are a helpful assistant that translates natural language to SQL queries.",
        input=context
    )
    return(response.output_text)

def few_shot_single_domain_sql_query(client, question):
    context = """You are an expert SQL generator. Given a question, generate a syntactically correct SQL query to answer the question using the following database schema:
    
				CREATE TABLE IF NOT EXISTS vehicles (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					vin VARCHAR(30) UNIQUE,
					model VARCHAR(30),
					make VARCHAR(30),
					year INTEGER,
					currentSoftwareVersion VARCHAR(9)
				);
	
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
				);
	
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
				);
	
				CREATE TABLE IF NOT EXISTS sensors (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					vehicleId INTEGER NOT NULL,
					name TEXT NOT NULL,                   
					sensor_type VARCHAR(30) NOT NULL,                     
					installed_at DATETIME,
					serial_number VARCHAR(50) UNIQUE,
					FOREIGN KEY (vehicleId) REFERENCES vehicles(id) 
						ON DELETE CASCADE
				);
	
				CREATE TABLE IF NOT EXISTS sensorReadings (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					sensorId INTEGER NOT NULL,
					timestamp TEXT NOT NULL,
					readingType VARCHAR(30) NOT NULL,                     
					readingValue TEXT,                    
					fileRef TEXT,                         
					FOREIGN KEY (sensorId) REFERENCES sensors(id) 
						ON DELETE CASCADE
				);

                Additionally, here are some example natural language questions and their corresponding SQL queries:
                Question: "List all vehicles manufactured by 'AutoMakers' after the year 2020."
                SQL: "SELECT * FROM vehicles WHERE make = 'AutoMakers' AND year > 2020;"
                Question: "Select all incidents that happened during a trip."
                SQL: "SELECT i.*, t.start_time, t.end_time
                    FROM incidents i
                    JOIN trips t ON i.tripId = t.id
                    WHERE i.vehicleId = 1;"
                Question: "Find all sensors installed on vehicle with VIN '1HGBH41JXMN10918623'."
                SQL: "SELECT s.* FROM sensors s
                    JOIN vehicles v ON s.vehicleId = v.id
                    WHERE v.vin = '1HGBH41JXMN10918623';"
                Question: "Find all sensor readings within 5 seconds of an incident time."
                SQL: "SELECT sr.* 
                    FROM sensorReadings sr
                    JOIN sensors s ON sr.sensorId = s.id
                    JOIN incidents i ON i.vehicleId = s.vehicleId
                    WHERE i.id = 1
                    AND sr.timestamp BETWEEN datetime(i.incident_time, '-5 seconds') AND datetime(i.incident_time, '+5 seconds');"

    Now using the above schema and examples, answer: """ + question + """
    Generate the SQL query in Python's SQLLite syntax to answer the question. Only return the SQL query, do not include any explanations or other text.
"""

    response = client.responses.create(
        model = "gpt-5-mini",
        instructions = "You are a helpful assistant that translates natural language to SQL queries. You only return the SQL query, do not include any explanations or other text.",
        input = question,)
    return(response.output_text)

def zero_shot_sql_query(client, question):
    context = """You are an expert SQL generator. Given a question, generate a syntactically correct SQL query to answer the question using the following database schema:
    Vehicles(id, vin, model, year, make, currentSoftwareVersion)
    Trips(id, vehicleId, start_time, end_time, start_lat, start_lon, end_lat, end_lon, route_summary)
    Incidents(id, vehicleId, tripId, incident_time, severity, type, description, incident_lat, incident_lon, recorded_by)
    Sensors(id, vehicleId, name, sensor_type, installed_at, serial_number). 

    Here is an example row from each table, shown as an insert statement:
    INSERT INTO vehicles (vin, model, year, make, currentSoftwareVersion)
    VALUES ('1HGBH41JXMN109118623', 'AutoCruiser-X', 2024, 'AutoMakers', 'v1.2.0');

    INSERT INTO trips (vehicleId, start_time, end_time, start_lat, start_lon, end_lat, end_lon, route_summary)
    VALUES (1, '2025-09-24T08:30:00', '2025-09-24T09:10:00', '40.7128', '-74.0060', '40.7580', '-73.9855', 'downtown commute');

    INSERT INTO incidents (vehicleId, tripId, incident_time, severity, type, description, incident_lat, incident_lon, recorded_by)
    VALUES (1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system');

    INSERT INTO sensors (vehicleId, name, sensor_type, serial_number)
    VALUES (1, 'front_lidar', 'lidar', 'LDR-001223'),

    Now using the above schema and examples, answer: """ + question + """
    Generate the SQL query to answer the question. Only return the SQL query, do not include any explanations or other text.
    """

    response = client.responses.create(
        model="gpt-5-mini",
        instructions = "You are a helpful assistant that translates natural language to SQL queries.",
        input = context 
    )
    return(response.output_text)


def nl_sql_response(client, question, sql_query, sql_response):
    sql_response_str = "\n".join([str(row) for row in sql_response])
    context = f"""Given the SQL query: {sql_query} and responses {sql_response_str}, and the question: {question}, provide a concise answer based on the database schema and the SQL query. Only return the answer, do not include any explanations or other text.
        The database schema is as follows:
        Vehicles(id, vin, model, year, make, currentSoftwareVersion)
        Trips(id, vehicleId, start_time, end_time, start_lat, start_lon, end_lat, end_lon, route_summary)
        Incidents(id, vehicleId, tripId, incident_time, severity, type, description, incident_lat, incident_lon, recorded_by)
        Sensors(id, vehicleId, name, sensor_type, installed_at, serial_number). 

        Here is an example row from each table, shown as an insert statement:
        INSERT INTO vehicles (vin, model, year, make, currentSoftwareVersion)
        VALUES ('1HGBH41JXMN109118623', 'AutoCruiser-X', 2024, 'AutoMakers', 'v1.2.0');

        INSERT INTO trips (vehicleId, start_time, end_time, start_lat, start_lon, end_lat, end_lon, route_summary)
        VALUES (1, '2025-09-24T08:30:00', '2025-09-24T09:10:00', '40.7128', '-74.0060', '40.7580', '-73.9855', 'downtown commute');

        INSERT INTO incidents (vehicleId, tripId, incident_time, severity, type, description, incident_lat, incident_lon, recorded_by)
        VALUES (1, 1, '2025-09-24T08:45:12', 'medium', 'near_miss', 'Pedestrian suddenly stepped into crosswalk', '40.7350', '-74.0001', 'auto_system');

        INSERT INTO sensors (vehicleId, name, sensor_type, serial_number)
        VALUES (1, 'front_lidar', 'lidar', 'LDR-001223'),

        Respond with a concise, natural language answer describing what the query results show.
    """
    response = client.responses.create(
        model="gpt-5-mini",
        instructions="You are a helpful assistant that provides concise answers based on SQL queries and questions.",
        input=context
    )
    return(response.output_text)

def generate_response(client, prompt):
    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )
    return(response.output_text)


if __name__ == ("__main__"):
    client = load_client(key=get_key("key.env"))
    print(zero_shot_sql_query(client, "Find all incidents that involve radar."))