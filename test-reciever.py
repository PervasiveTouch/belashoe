import time
from DIPPID import SensorUDP

PORT = 5700
bela = SensorUDP(PORT)

data_dic = []
counter = 0


def register(sensor: SensorUDP):
    print("Registering...")
    sensor.register_callback("shoe_data", handle_bela)
    sensor.register_callback("shoe_baseline", handle_bela_baseline)
    print("Sensor registered!")


def handle_bela(data):
    global data_dic, counter
    data_dic.append({"timestamp": data.pop(0), "sensors": [value for value in data]})
    try:
        diff_to_prev = data_dic[-1]["timestamp"] - data_dic[-2]["timestamp"]
        if (diff_to_prev) != 1:
            print(f"{diff_to_prev-1} PACKET(S) LOST!!!")
    except IndexError:
        print("Could not yet compare to sencond to last timestamp.")
    counter += 1

def handle_bela_baseline(data):
    print(f"Current basline: {data}")


if __name__ == "__main__":
    register(bela)
    print(f"Capabilities: {bela.get_capabilities()}")

    start_time = time.time()
    while True:
        if time.time() - start_time >= 1:
            print(f"Counter: {counter}")
            start_time = time.time()
            counter = 0
