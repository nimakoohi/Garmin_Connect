import xml.etree.ElementTree as ET
import mysql.connector
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from docx import Document



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
    res_hr = []
    res_cd = []
    res_al = []


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

        
        time_column = times
        distance_column = distances
        heart_rate_column = heart_rates
        speed_column = speeds
        cadence_column = cadances
        altitude_column = altitude_meters
        
            # Plotting speeds against times
        try:

            plt.plot(time_column, speed_column)

            plt.xticks([])
            plt.yticks([])
            plt.xlabel("Time")
            plt.ylabel("Pace")
            plt.title("Speed vs Time")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('my_plot.png')
            plt.show()

        except Exception as e:
            print(f"Error plotting speeds: {e}")


        find_total_km= "SELECT Distance AS row_count FROM ActivityData ORDER BY id DESC LIMIT 1;"

        db_manager.cursor.execute(find_total_km)
        total_km_result = round(db_manager.cursor.fetchone()[0])
        
        
        if total_km_result:
            total_km = round(total_km_result/1000)
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
                WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000 
                '''
                
                
                db_manager.connection.commit()
                db_manager.cursor.execute(another_km)
                another_km = db_manager.cursor.fetchone()[0]
                res_Speed.append(another_km)

                
                hr = f'''
                SELECT CEILING(AVG(Heart_Rate)) AS HR100 FROM activitydata
                WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000 ORDER BY id DESC LIMIT 1;
                '''
                
                db_manager.connection.commit()
                db_manager.cursor.execute(hr)
                hr = db_manager.cursor.fetchone()[0]
                res_hr.append(hr)

                
                cd = f'''
                SELECT CEILING(AVG(Cadance)) AS cd FROM activitydata
                WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000 ORDER BY id DESC LIMIT 1;
                '''
                
                db_manager.connection.commit()
                db_manager.cursor.execute(cd)
                cd = db_manager.cursor.fetchone()[0]
                res_cd.append(cd)


                al_me = f'''
                SELECT CEILING(AVG(Altitude_Meters)) AS AL_Me FROM activitydata
                WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000 ORDER BY id DESC LIMIT 1;
                '''
                
                db_manager.connection.commit()
                db_manager.cursor.execute(al_me)
                al_me = db_manager.cursor.fetchone()[0]
                res_al.append(al_me)
                
                
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

                hr = f'''
                SELECT CEILING(AVG(Heart_Rate)) AS HR100 FROM activitydata
                WHERE Distance BETWEEN {total_km*1000} AND {total_km_result} ORDER BY id DESC LIMIT 1;
                '''
                
                db_manager.connection.commit()
                db_manager.cursor.execute(hr)
                hr = db_manager.cursor.fetchone()[0]
                res_hr.append(hr)

                cd = f'''
                SELECT CEILING(AVG(Cadance)) AS cd FROM activitydata
                WHERE Distance BETWEEN {total_km*1000} AND {total_km_result} ORDER BY id DESC LIMIT 1;
                '''
                
                db_manager.connection.commit()
                db_manager.cursor.execute(cd)
                cd = db_manager.cursor.fetchone()[0]
                res_cd.append(cd)

                
                al_me = f'''
                SELECT CEILING(AVG(Altitude_Meters)) AS AL_Me FROM activitydata
                WHERE Distance BETWEEN {total_km*1000} AND {total_km_result} ORDER BY id DESC LIMIT 1;
                '''
                
                db_manager.connection.commit()
                db_manager.cursor.execute(al_me)
                al_me = db_manager.cursor.fetchone()[0]
                res_al.append(al_me)
                
                
                
        except:
            print("This was Just First km!!!") 

        db_manager.close_connection()

        Physical_Comfort_Response1 = input('''How did your body feel during the run? Any specific areas of discomfort or pain?''')
        Physical_Comfort_Response2 = input('''Did you experience any muscle tightness, soreness, or stiffness?''')
        
        Breathing_and_Cardiovascular_Response1 = input('''How was your breathing throughout the run? Was it comfortable or labored? ''')
        Breathing_and_Cardiovascular_Response2 = input('''Did you notice any changes in your heart rate, and if so, were they within a comfortable range? ''')
        
        Energy_Levels_Response = input('''How would you describe your energy levels during the run? Did you feel fatigued at any point? ''')

        Mental_State_Response1 = input('''What was your mental state like during the run? Were you focused, distracted, or perhaps in a flow state? ''')
        Mental_State_Response2 = input('''Did you experience any mental barriers or breakthroughs? ''')

        Running_Form_Response1 = input('''Were you mindful of your running form? Did you notice any changes in your gait or posture? ''')
        Running_Form_Response2 = input('''Did you encounter any challenges related to your form? ''')
        
        Terrain_and_Environment_Response1 = input('''How did the terrain (e.g., flat, hilly, uneven) impact your running experience? ''')
        Terrain_and_Environment_Response2 = input('''Did the weather or environmental conditions affect your performance or enjoyment? ''')

        Hydration_and_Nutrition_Response1 = input('''Did you feel adequately hydrated and fueled before and during the run? ''')
        Hydration_and_Nutrition_Response2 = input('''Did you experience any issues related to nutrition or hydration? ''')

        Goal_Achievement_Response1 = input('''Were you able to meet the goals you set for yourself during the run? ''')
        Goal_Achievement_Response2 = input('''How do you feel about your overall performance and progress? ''')

        Recovery_Response1 = input('''How is your body feeling post-run? Any lingering discomfort or signs of quick recovery? ''')
        Recovery_Response2 = input('''Did you engage in any post-run stretching or recovery activities? ''')

        
        Overall_Satisfaction1 = input('''On a scale of 1 to 10, how satisfied are you with your running experience today? ''')
        Overall_Satisfaction2 = input('''What aspects of the run brought you the most joy or fulfillment? ''')
        
        # Create a new Word document
        doc = Document()


        # Add content to the document 
        doc.add_heading(f'{total_km_result} meters on {times[0]}', level=1)


        output_text = (f'''
        Hi.
        I hope this message finds you well. Today, I completed a run covering a distance of  {total_km_result} meters,
        from {times[0]} to {times[-1]}
        I would greatly appreciate it if you could analyze my pace and share some feedback. 
        Here's the breakdown of my pace for each kilometer:
        {res_Speed},
        Additionally, my heart rate for each kilometer was:
        {res_hr},
        my cadence: {res_cd},
        and the altitude: {res_al},
        I would be grateful for any insights or recommendations you can provide based on this data.
        Thank you in advance for your guidance!
        Best regards
        
        Physical Comfort:
        How did your body feel during the run? Any specific areas of discomfort or pain?
        {Physical_Comfort_Response1}
        Did you experience any muscle tightness, soreness, or stiffness?
        {Physical_Comfort_Response2}

        
        Breathing and Cardiovascular Response:
        How was your breathing throughout the run? Was it comfortable or labored?
        {Breathing_and_Cardiovascular_Response1}
        Did you notice any changes in your heart rate, and if so, were they within a comfortable range?
        {Breathing_and_Cardiovascular_Response2}

        Energy Levels:
        How would you describe your energy levels during the run? Did you feel fatigued at any point?
        {Energy_Levels_Response}

        Mental State:
        What was your mental state like during the run? Were you focused, distracted, or perhaps in a flow state?
        {Mental_State_Response1}
        Did you experience any mental barriers or breakthroughs?
        {Mental_State_Response2}
        
        Running Form:
        Were you mindful of your running form? Did you notice any changes in your gait or posture?
        {Running_Form_Response1}
        Did you encounter any challenges related to your form?
        {Running_Form_Response2}
        
        Terrain and Environment:
        How did the terrain (e.g., flat, hilly, uneven) impact your running experience?
        {Terrain_and_Environment_Response1}
        Did the weather or environmental conditions affect your performance or enjoyment?
        {Terrain_and_Environment_Response2}
        
        
        Hydration and Nutrition:
        Did you feel adequately hydrated and fueled before and during the run?
        {Hydration_and_Nutrition_Response1}
        Did you experience any issues related to nutrition or hydration?
        {Hydration_and_Nutrition_Response2}
        
        
        Goal Achievement:
        Were you able to meet the goals you set for yourself during the run?
        {Goal_Achievement_Response1}
        How do you feel about your overall performance and progress?
        {Goal_Achievement_Response2}
        
        
        Recovery:
        How is your body feeling post-run? Any lingering discomfort or signs of quick recovery?
        {Recovery_Response1}
        Did you engage in any post-run stretching or recovery activities?
        {Recovery_Response2}
        
        
        Overall Satisfaction:
        On a scale of 1 to 10, how satisfied are you with your running experience today?
        {Overall_Satisfaction1}
        What aspects of the run brought you the most joy or fulfillment?
        {Overall_Satisfaction2}
        ''')
        
        # Add the output text to the document
        doc.add_paragraph(output_text)

        # Save the document
        doc.save(f'{times[0].split()[0]} - {total_km_result}.docx')

        print("Output has been printed to Word document.")

    
if __name__ == "__main__":
    main()