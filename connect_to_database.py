from TCXParser import TCXParser
from DatabaseManager import DatabaseManager
from ConfigHandler import read_config
import pandas as pd

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

        activity_data = pd.DataFrame({'Speed': speeds})
        
        # Calculate the result for the entire 'Speed' column
        activity_data['Speed'] = activity_data['Speed'].apply(lambda x: f"{int(60 / (float(x) * 3.6)) // 60:02d}:{int(60 / (float(x) * 3.6)) % 60:02d}:{int(((60 / (float(x) * 3.6)) % 1) * 60):02d}")



        print(activity_data['Speed'])
        
        data = list(zip(run_name_id, times, distances, heart_rates, activity_data['Speed'],
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