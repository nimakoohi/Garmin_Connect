# 1. Add all wourkout on Database
# 2. Compare long run with each other
# 3. Link to the site
# 4. Add other plot
# 5. get a tcx files in folder and extract word and pictures into another folder.

import os
import pandas as pd
from DatabaseManager import DatabaseManager
from TCXParser import TCXParser
from Plotting import Plotting
from ConfigHandler import read_config
from export_to_word import running_evaluation_questions

def connect_to_database(file_path, name, types_of_runs):
    config = read_config()

    db = DatabaseManager(config)

    (times, distances, heart_rates, speeds,
     cadances, altitude_meters) = TCXParser.parse(file_path)

    time_column = times
    heart_rate_column = heart_rates
    speed_column = speeds
    cadence_column = cadances
    altitude_column = altitude_meters

    if db.establish_connection():
        insert_query_run_name = ("""
                                 INSERT INTO Run_Name(run_name) VALUES (%s)
                                 """)

        run_name = f'{name} - {types_of_runs} - {times[0].split()[0]} - {(distances[-1])[:2]}km'

        db.cursor.execute(insert_query_run_name, (run_name, ))

        db.cursor.execute(f"SELECT * FROM Run_Name WHERE run_name = '{run_name}'")
        run_name_id = db.cursor.fetchone()[0]
        run_name_id = [run_name_id]

        run_name_id.extend([run_name_id[0]] * (len(times) - 1))
        
        data = list(zip(run_name_id, times, distances, heart_rates, speeds,
                    cadances, altitude_meters))

        insert_query = ("""
        INSERT INTO ActivityData (run_name_id, Time, Distance, Heart_Rate,
        Speed, Cadance, Altitude_Meters) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """)

        db.cursor.executemany(insert_query, data)
        db.connection.commit()
    else:
        print("Failed to establish connection")
        
    return (times, time_column, heart_rate_column, speed_column,
            cadence_column, altitude_column, db, distances)

def create_directory(directory_path):
    try:
        # Create target directory
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_path}' already exists.")


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

    save_directory = os.path.join(os.getcwd(),
                                  input("Please insert the directory where you want store your files: "))
    create_directory(save_directory)
    
    file_path = input('Please insert the directory where tcx files are stored: ')
    while not os.path.exists(file_path):
        print("Error: The specified directory does not exist.")
        file_path = input('Please insert the directory where tcx files are stored: ')

    name = input("Please insert your full name: ")

    types_of_runs = input(''' Please tell us what types of runs you do:
    - Recovery Run
    - Long Run
    - Interval Run
    - Tempo Run
    - Fartlek Run
    - Hill Run
    - Progression Run
    - Cross-Training Run 
    ''')

    (times, time_column, heart_rate_column, speed_column,
     cadence_column, altitude_column, db, distances) = connect_to_database(file_path, name, types_of_runs)

    find_total_km = "SELECT Distance AS row_count FROM ActivityData ORDER BY id DESC LIMIT 1;"

    db.cursor.execute(find_total_km)
    total_km_result = db.cursor.fetchone()[0]

    if total_km_result:
        total_km = round(total_km_result/1000)
        total_km_extra = total_km_result - (total_km*1000)
    else:
        print("Failed to retrieve Total km.")

    Plotting(time_column, heart_rate_column, speed_column, cadence_column,
             altitude_column, save_directory, name, types_of_runs, times, distances)

    find_total_km = '''SELECT Distance AS row_count FROM ActivityData
    ORDER BY id DESC LIMIT 1'''

    db.cursor.execute(find_total_km)
    total_km_result = round(db.cursor.fetchone()[0])

    # Create a pandas dataframe
    df = pd.DataFrame({
        "Pace (m/s)": speed_column,
        "Heart Rate (bpm)": heart_rate_column,
        "Cadence (steps/min)": cadence_column,
        "Altitude (m)": altitude_column
    })

    # Convert 'Pace (m/s)' column to numeric values
    df['Pace (m/s)'] = pd.to_numeric(df['Pace (m/s)'], errors='coerce')

    # Calculate the standard deviation of pace
    standard_deviation_pace = df['Pace (m/s)'].std()

    df['Heart Rate (bpm)'] = pd.to_numeric(df['Heart Rate (bpm)'], errors='coerce')
    # Calculate the standard deviation of heart rate
    standard_deviation_heart_rate = df['Heart Rate (bpm)'].std()

    df['Cadence (steps/min)'] = pd.to_numeric(df['Cadence (steps/min)'], errors='coerce')
    # Calculate the standard deviation of cadence
    standard_deviation_cadence = df['Cadence (steps/min)'].std()

    df['Altitude (m)'] = pd.to_numeric(df['Altitude (m)'], errors='coerce')
    # Calculate the standard deviation of altitude
    standard_deviation_altitude = df['Altitude (m)'].std()

    try:
        for find_another_km in range(0, total_km):
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
            WHERE Distance BETWEEN {find_another_km}000
            AND {find_another_km+1}000
            '''
            
            db.connection.commit()
            db.cursor.execute(another_km)
            another_km = db.cursor.fetchone()[0]
            res_Speed.append(another_km)
            
            hr = f'''
            SELECT CEILING(AVG(Heart_Rate)) AS HR100 FROM activitydata
            WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000 ORDER BY id DESC LIMIT 1;
            '''
            
            db.connection.commit()
            db.cursor.execute(hr)
            hr = db.cursor.fetchone()[0]
            res_hr.append(hr)
            
            cd = f'''
            SELECT CEILING(AVG(Cadance)) AS cd FROM activitydata
            WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000 ORDER BY id DESC LIMIT 1;
            '''
            
            db.connection.commit()
            db.cursor.execute(cd)
            cd = db.cursor.fetchone()[0]
            res_cd.append(cd)

            al_me = f'''
            SELECT CEILING(AVG(Altitude_Meters)) AS AL_Me FROM activitydata
            WHERE Distance BETWEEN {find_another_km}000 AND {find_another_km+1}000 ORDER BY id DESC LIMIT 1;
            '''

            db.connection.commit()
            db.cursor.execute(al_me)
            al_me = db.cursor.fetchone()[0]
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

            db.connection.commit()
            db.cursor.execute(last_km)
            last_km = db.cursor.fetchone()[0]

            res_Speed.append(last_km)

            hr = f'''
            SELECT CEILING(AVG(Heart_Rate)) AS HR100 FROM activitydata
            WHERE Distance BETWEEN {total_km*1000} AND {total_km_result} ORDER BY id DESC LIMIT 1;
            '''

            db.connection.commit()
            db.cursor.execute(hr)
            hr = db.cursor.fetchone()[0]
            res_hr.append(hr)

            cd = f'''
            SELECT CEILING(AVG(Cadance)) AS cd FROM activitydata
            WHERE Distance BETWEEN {total_km*1000} AND {total_km_result} ORDER BY id DESC LIMIT 1;
            '''

            db.connection.commit()
            db.cursor.execute(cd)
            cd = db.cursor.fetchone()[0]
            res_cd.append(cd)

            al_me = f'''
            SELECT CEILING(AVG(Altitude_Meters)) AS AL_Me FROM activitydata
            WHERE Distance BETWEEN {total_km*1000} AND {total_km_result} ORDER BY id DESC LIMIT 1;
            '''

            db.connection.commit()
            db.cursor.execute(al_me)
            al_me = db.cursor.fetchone()[0]
            res_al.append(al_me)

    except db.connector.Error as e:
        print(f"Database error: {e.errno} - {e.msg}")
    except Exception as e:
        print(f"Other error: {e}")

    db.close_connection()

    running_evaluation_questions(times, types_of_runs,
                                 res_Speed, res_hr, res_cd, res_al,
                                 standard_deviation_pace,
                                 standard_deviation_heart_rate,
                                 standard_deviation_cadence,
                                 standard_deviation_altitude, save_directory,
                                 name, distances)

if __name__ == "__main__":
    main()