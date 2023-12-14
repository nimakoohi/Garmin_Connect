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
        insert_query = """
        INSERT INTO ActivityData (Time, Distance, Heart_Rate, Speed, Cadance, Altitude_Meters)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        #Find 1km on Distance on ActivityData on MySQL
        #
        
        cursor.execute(insert_query, (each_time, each_distance, each_heart_rate, each_speed, each_cadence, each_altitude_meters))

    connection.commit()
    
    find_total_km= "SELECT Distance AS row_count FROM ActivityData ORDER BY id DESC LIMIT 1;"

    cursor.execute(find_total_km)
    total_km_result = round(cursor.fetchone()[0])
    print("Total km:", total_km_result)
    if total_km_result:
        total_km = round(total_km_result/1000)
        total_km_extra = total_km_result - (total_km*1000)
    else:
        print("Failed to retrieve Total km.")

    
    find_First_km = '''SELECT 
    CONCAT(
        CASE
            WHEN LENGTH(FLOOR(60 / (AVG(Speed) * 3.6))) = 1 THEN '0'
            ELSE ''
        END,
        FLOOR(60 / (AVG(Speed) * 3.6)),
        ':',
        LPAD(CEILING(((60 / (AVG(Speed) * 3.6)) - FLOOR(60 / (AVG(Speed) * 3.6))) * 60), 2, '0')
    ) AS result
    FROM ActivityData
    WHERE Distance <= 1000;'''

    
    connection.commit()
    cursor.execute(find_First_km)
    first_row = cursor.fetchone()[0]
    print("1:",first_row)
    
    try:
        for find_another_km in range(1,total_km):
            another_km = f'''SELECT
            CONCAT(
                CASE
                    WHEN LENGTH(FLOOR(60 / (AVG(Speed) * 3.6))) = 1 THEN '0'
                    ELSE ''
                END,
                FLOOR(60 / (AVG(Speed) * 3.6)),
                ':',
                LPAD(CEILING(((60 / (AVG(Speed) * 3.6)) - FLOOR(60 / (AVG(Speed) * 3.6))) * 60), 2, '0')
            ) AS result
            FROM ActivityData
            WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000 '''
            
            connection.commit()
            cursor.execute(another_km)
            another_km = cursor.fetchone()[0]
            print(f"{find_another_km+1}: {another_km}")
            
        if total_km_extra > 0:
            last_km = f'''SELECT
            CONCAT(
                CASE
                    WHEN LENGTH(FLOOR(60 / (AVG(Speed) * 3.6))) = 1 THEN '0'
                    ELSE ''
                END,
                FLOOR(60 / (AVG(Speed) * 3.6)),
                ':',
                LPAD(CEILING(((60 / (AVG(Speed) * 3.6)) - FLOOR(60 / (AVG(Speed) * 3.6))) * 60), 2, '0')
            ) AS result
            FROM ActivityData
            WHERE Distance BETWEEN {total_km*1000} AND {total_km_result} '''
            
            connection.commit()
            cursor.execute(last_km)
            last_km = cursor.fetchone()[0]
            print(f"0.{total_km_extra}: {last_km}")
            
    except:
           print("This was Just First km!!!") 
             
    connection.close()


if __name__ == "__main__":
    main()