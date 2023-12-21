import xml.etree.ElementTree as ET

class TCXParser:
    @staticmethod
    def parse(file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()

        namespace = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
                     'ns2': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'}

        (times, distances, heart_rates, speeds,
         cadances, altitude_meters) = [], [], [], [], [], []

        for trackpoint in root.findall('.//tcx:Trackpoint', namespace):
            time = trackpoint.find('.//tcx:Time', namespace).text
            distance = trackpoint.find('.//tcx:DistanceMeters', namespace).text
            heart_rate = trackpoint.find('.//tcx:HeartRateBpm/tcx:Value',
                                         namespace).text
            speed = trackpoint.find('.//ns2:Speed', namespace).text
            cadance = trackpoint.find('.//ns2:RunCadence', namespace).text
            altitude_meter = trackpoint.find('.//tcx:AltitudeMeters',
                                             namespace).text

            time = time.replace('T', ' ').replace('Z', '')
            times.append(time)
            distances.append(distance)
            heart_rates.append(heart_rate)
            speeds.append(speed)
            cadances.append(int(cadance) * 2)
            altitude_meters.append(altitude_meter)

        return times, distances, heart_rates, speeds, cadances, altitude_meters