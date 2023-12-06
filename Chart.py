import xml.etree.ElementTree as ET

def parse_tcx(file_path):
    # Parse the TCX file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Define the namespace with the required prefixes
    namespace = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
                 'ns2': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'}

    # Extract data from Trackpoints
    times, distances, heart_rates, speeds, cadances, AltitudeMeters = [], [], [], [], [], []

    # Loop through each Trackpoint
    for trackpoint in root.findall('.//tcx:Trackpoint', namespace):
        time = trackpoint.find('.//tcx:Time', namespace).text
        distance = trackpoint.find('.//tcx:DistanceMeters', namespace).text
        heart_rate = trackpoint.find('.//tcx:HeartRateBpm/tcx:Value', namespace).text
        speed = trackpoint.find('.//ns2:Speed', namespace).text
        cadance = trackpoint.find('.//ns2:RunCadence', namespace).text
        AltitudeMeter = trackpoint.find('.//tcx:AltitudeMeters', namespace).text

        # Append data to lists
        times.append(time)
        distances.append(distance)
        heart_rates.append(heart_rate)
        speeds.append(speed)
        cadances.append(int(cadance)*2)
        AltitudeMeters.append(AltitudeMeter)

    return times, distances, heart_rates, speeds, cadances, AltitudeMeters

# Example usage
file_path = r'/home/niroli/Documents/activity_12938332916.tcx'
times, distances, heart_rates, speeds, cadances, AltitudeMeters = parse_tcx(file_path)

# print("Time data:", times)
# print("Distance data:", distances)
#print("Heart_rate_data:", heart_rates)
#print("Speed data:", speeds)
print("Cadance data:", cadances)

