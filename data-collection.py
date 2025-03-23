import os, sys, csv, time
import pandas as pd

from pynput import keyboard
from DIPPID import SensorUDP
from datetime import datetime

PORT_RIGHT = 5701
bela = SensorUDP(PORT_RIGHT)

PARTICIPANT = "luca"
GESTURE = "testing"
if len(sys.argv) == 3:
    PARTICIPANT = sys.argv[1]
    GESTURE = sys.argv[2]

PATH = f"data/{datetime.now().strftime('%y%m%d_%H-%M-%S')}-{PARTICIPANT}-logs.csv"
print(f"Saving file as: {PATH}")
print(f"Recording gesture: {GESTURE}")

started = False
NUM_SENSORS = 8
sensor_data = {
    "timestamp": [],
    "gesture": "",
    **{f"sensor_{sensor}": [] for sensor in range(NUM_SENSORS)},
}


def printDataToConsole(data):
    print(f"recieved data: {data}, type: {type(data[0])}")


def clear_dict():
    global sensor_data
    keys = list(sensor_data.keys())
    for k in keys:
        sensor_data[k] = []
    print("sensor data buffer cleared")


def save_data(data_dict):
    # TODO: Counter für einzelne Geste
    print("now saving...")
    file_exists = os.path.isfile(PATH)
    df = pd.DataFrame(data_dict)
    if not file_exists:
        df.to_csv(PATH, mode="a", index=False)
    else:
        df.to_csv(PATH, mode="a", index=False, header=False)
    # TODO: Warum kommen nicht alle gesendeten Reihen an?
    print(f"done saving {len(data_dict['timestamp'])} rows")


def handle_sensor_data(data):
    print(f"recieved data: {data}")
    sensor_data["timestamp"].append(time.time())
    sensor_data["gesture"] = GESTURE
    for index, sensor in enumerate(data):
        sensor_data[f"sensor_{index}"].append(sensor)


def on_press(key):
    global started, listener
    if key == keyboard.Key.esc:
        print("exit...")
        bela.disconnect()
        listener.join()
        os._exit(0)
    elif key == keyboard.Key.page_down and not started:
        print("starting!")
        started = True
        bela.register_callback("touch-sensors", handle_sensor_data)


def on_release(key):
    global started, sensor_data
    if key == keyboard.Key.page_down:
        print("stopping!")
        started = False
        bela.unregister_callback("touch-sensors", handle_sensor_data)
        save_data(sensor_data)
        clear_dict()


if __name__ == "__main__":
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
