import xml.etree.ElementTree as ET
import mysql.connector
import os
from datetime import datetime


connection = None
cursor = None

def establish_db_connection():
    """Establish a connection to the MySQL server and create tables."""
    global connection, cursor
    
    host = "localhost"
    user = "nirosql" 
    password = "NiroV@159726SQL" 
    database = "Garmin" 
   
    # Establish a connection to the MySQL server
    try:
        connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4',
        )

        print("Connected to MySQL!")
       
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()
       
        create_tables_query = """
        DROP TABLE IF EXISTS ActivityData;
        
        CREATE TABLE IF NOT EXISTS ActivityData (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Time DATETIME,
            Distance FLOAT,
            Heart_Rate FLOAT,
            Speed FLOAT,
            Cadance INT,
            Altitude_Meters FLOAT
        )
        """

        # Execute each statement separately
        for statement in create_tables_query.split(';'):
            if statement.strip():
                cursor.execute(statement)

        # Commit the changes to the database
        connection.commit() 

        return connection, cursor
       
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None, None
   

def parse_tcx(file_path):
    """Parse the TCX file and extract relevant data."""
    # Parse the TCX file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Define the namespace with the required prefixes
    namespace = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
                 'ns2': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'}

    # Extract data from Trackpoints
    times, distances, heart_rates, speeds, cadances, altitude_meters = [], [], [], [], [], []

    # Loop through each Trackpoint
    for trackpoint in root.findall('.//tcx:Trackpoint', namespace):
        time = trackpoint.find('.//tcx:Time', namespace).text
        distance = trackpoint.find('.//tcx:DistanceMeters', namespace).text
        heart_rate = trackpoint.find('.//tcx:HeartRateBpm/tcx:Value', namespace).text
        speed = trackpoint.find('.//ns2:Speed', namespace).text
        cadance = trackpoint.find('.//ns2:RunCadence', namespace).text
        altitude_meter = trackpoint.find('.//tcx:AltitudeMeters', namespace).text

        # Append data to lists
        times.append(time)
        distances.append(distance)
        heart_rates.append(heart_rate)
        speeds.append(speed)
        cadances.append(int(cadance)*2)
        altitude_meters.append(altitude_meter)

    return times, distances, heart_rates, speeds, cadances, altitude_meters


def main():
    """The main function that parses TCX files and inserts the extracted data into the MySQL database."""
    file_path = input('Please insert the directory where files are stored: ')
    if not os.path.exists(file_path):
        print("Error: The specified directory does not exist.")
        return

    connection, cursor = establish_db_connection()
    if connection is None:
        return

    times, distances, heart_rates, speeds, cadances, altitude_meters = parse_tcx(file_path)

    for each_time, each_distance, each_heart_rate, each_speed, each_cadence, each_altitude_meters in zip(times, distances, heart_rates, speeds, cadances, altitude_meters):
        each_time = each_time.replace('T', ' ').replace('Z', '')
        print("Inserting data:", each_time, each_distance, each_heart_rate, each_speed, each_cadence, each_altitude_meters)
        insert_query = """
        INSERT INTO ActivityData (Time, Distance, Heart_Rate, Speed, Cadance, Altitude_Meters)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        #Find 1km on Distance on ActivityData on MySQL
        #
        
        cursor.execute(insert_query, (each_time, each_distance, each_heart_rate, each_speed, each_cadence, each_altitude_meters))

    connection.commit()
    
    find_every_one_km = "SELECT CONCAT (FLOOR(60 / (AVG(Speed) * 3.6)), ':' , CEILING(((60 / (AVG(Speed) * 3.6)) - FLOOR(60 / (AVG(Speed) * 3.6)))*60)) AS result FROM ActivityData WHERE Distance <= 1000;"
    connection.commit()
    cursor.execute(find_every_one_km)
    first_row = cursor.fetchone()
    print(first_row)
    
    connection.close()


if __name__ == "__main__":
    main()