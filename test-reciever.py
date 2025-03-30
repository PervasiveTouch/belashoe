import time
from DIPPID import SensorUDP

PORT_RIGHT = 5701
bela = SensorUDP(PORT_RIGHT)

data = []
new_data = False
counter = 0


def printDataToConsole(data):
    print(f"recieved data: {data}, type: {type(data[0])}")


def register(sensor: SensorUDP):
    print("Registering...")
    sensor.register_callback("touch-sensors", handle_dippid)
    print("Sensor registered!")


def handle_dippid(_):
    global new_data
    new_data = True


def receive_data(sensor):
    global data, new_data
    if new_data == False:
        return False
    new_data = False

    sensors = sensor.get_value("touch-sensors")
    data.append({"timestamp": sensors.pop(0), "sensors": [value for value in sensors]})

    return True


if __name__ == "__main__":
    register(bela)
    print(f"Capabilities: {bela.get_capabilities()}")

    start_time = time.time()
    while True:
        has_logged = receive_data(bela)
        if has_logged:
            counter += 1
        if time.time() - start_time >= 1:
            print(f"Counter: {counter}")
            start_time = time.time()
            counter = 0
