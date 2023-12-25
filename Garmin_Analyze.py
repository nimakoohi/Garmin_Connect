# 1. Add all wourkout on Database
# 2. Compare long run with each other
# 3. Link to the site
# 4. Add other plot
# 5. get a tcx files in folder and extract word and pictures into another folder.

import os
from Plotting import Plotting
from connect_to_database import connect_to_database
from pandas_dataframe import pandas_dataframe
from export_to_word import running_evaluation_questions
from avg_db_garmin import avg_db_garmin

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

    Plotting(time_column, heart_rate_column, speed_column, cadence_column,
             altitude_column, save_directory, name, types_of_runs, times,
             distances)

    (standard_deviation_pace,
     standard_deviation_heart_rate,
     standard_deviation_cadence,
     standard_deviation_altitude) = pandas_dataframe(speed_column,
                                                   heart_rate_column,
                                                   cadence_column, altitude_column)
     
    total_km_result, total_km = avg_db_garmin(db, res_Speed, res_hr, res_cd, res_al)

    running_evaluation_questions(times, types_of_runs,
                                 res_Speed, res_hr, res_cd, res_al,
                                 standard_deviation_pace,
                                 standard_deviation_heart_rate,
                                 standard_deviation_cadence,
                                 standard_deviation_altitude, save_directory,
                                 name, distances, total_km_result, total_km)

if __name__ == "__main__":
    main()