import os

# Sensor address for Sodabot
TEMP_SENSOR_DIR = "/sys/bus/w1/devices/28-031504ab36ff"
# Virtual file containing the current temperature
TEMP_FILE = "w1_slave"

def read_therm_sensor(path=TEMP_SENSOR_DIR+'/'+TEMP_FILE):
    if os.path.isfile(path):
        print("Sensor file exists.")

        sensor_data = ""
        with open(path) as sensor_out:
            sensor_data = sensor_out.readlines()

        # Extract temperature from w1_therm's output
        # E.x.: a3 00 55 00 7f ff 0c 10 0a t=10187 --> 10.187
        temp_str = sensor_data[1].strip().split('t=')[-1]
        temp = float(temp_str) / 1000.

        return temp

    else:
        raise IOError("No such sensor connected at this path.")


# Test
#read_therm_sensor(TEMP_FILE)