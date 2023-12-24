import matplotlib.pyplot as plt
import os

def Plotting(time_column, heart_rate_column, speed_column, cadence_column,
             altitude_column, save_directory, name,
             types_of_runs, times, distances):
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

    except Exception as e:
        print(f"Error plotting speeds: {e}")
    
    # Save the image file
    image_file_path = os.path.join(save_directory,
                                   f'{name} - {types_of_runs} - {times[0].split()[0]} - {(distances[-1])[:2]}km.png')
    try:
        plt.savefig(image_file_path)
        print("Image file saved successfully:", image_file_path)
    except Exception as e:
        print(f"Error saving image file: {e}")