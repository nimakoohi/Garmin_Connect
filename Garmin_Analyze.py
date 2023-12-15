import xml.etree.ElementTree as ET
import mysql.connector
import os
from datetime import datetime


class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def establish_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
            )

            print("Connected to MySQL!")

            self.cursor = self.connection.cursor()

            self.create_tables()

            return True
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return False

    def create_tables(self):
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

        for statement in create_tables_query.split(';'):
            if statement.strip():
                self.cursor.execute(statement)

        self.connection.commit()

    def close_connection(self):
        if self.connection:
            self.connection.close()

class TCXParser:
    @staticmethod
    def parse(file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()

        namespace = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
                     'ns2': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'}

        times, distances, heart_rates, speeds, cadances, altitude_meters = [], [], [], [], [], []

        for trackpoint in root.findall('.//tcx:Trackpoint', namespace):
            time = trackpoint.find('.//tcx:Time', namespace).text
            distance = trackpoint.find('.//tcx:DistanceMeters', namespace).text
            heart_rate = trackpoint.find('.//tcx:HeartRateBpm/tcx:Value', namespace).text
            speed = trackpoint.find('.//ns2:Speed', namespace).text
            cadance = trackpoint.find('.//ns2:RunCadence', namespace).text
            altitude_meter = trackpoint.find('.//tcx:AltitudeMeters', namespace).text

            time = time.replace('T', ' ').replace('Z', '')
            times.append(time)
            distances.append(distance)
            heart_rates.append(heart_rate)
            speeds.append(speed)
            cadances.append(int(cadance) * 2)
            altitude_meters.append(altitude_meter)

        return times, distances, heart_rates, speeds, cadances, altitude_meters

def main():
    """
        The main function of the program. It initializes the database connection,
        retrieves the TCX files from the specified directory, and stores the data
        into the database. The total distance traveled and the average speed for each
        km of the day are calculated and printed to the console.
    """
    
    res_Speed = []
    
    file_path = input('Please insert the directory where files are stored: ')
    if not os.path.exists(file_path):
        print("Error: The specified directory does not exist.")
        return

    db_manager = DatabaseManager(host="localhost", user="nirosql", password="NiroV@159726SQL", database="Garmin")
    if db_manager.establish_connection():
        times, distances, heart_rates, speeds, cadances, altitude_meters = TCXParser.parse(file_path)
        data = list(zip(times, distances, heart_rates, speeds, cadances, altitude_meters))

        insert_query = """
        INSERT INTO ActivityData (Time, Distance, Heart_Rate, Speed, Cadance, Altitude_Meters)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        db_manager.cursor.executemany(insert_query, data)
        db_manager.connection.commit()


        find_total_km= "SELECT Distance AS row_count FROM ActivityData ORDER BY id DESC LIMIT 1;"

        db_manager.cursor.execute(find_total_km)
        total_km_result = round(db_manager.cursor.fetchone()[0])
        
        
        if total_km_result:
            total_km = round(total_km_result/1000)
            print(total_km_result)
            total_km_extra = total_km_result - (total_km*1000)
        else:
            print("Failed to retrieve Total km.")

        
        try:
            for find_another_km in range(0,total_km):
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
                
                db_manager.connection.commit()
                db_manager.cursor.execute(another_km)
                another_km = db_manager.cursor.fetchone()[0]
                
                res_Speed.append(another_km)
                
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
                
                db_manager.connection.commit()
                db_manager.cursor.execute(last_km)
                last_km = db_manager.cursor.fetchone()[0]

                res_Speed.append(last_km)
                
        except:
            print("This was Just First km!!!") 

        db_manager.close_connection()

        print(res_Speed)

    
if __name__ == "__main__":
    main()