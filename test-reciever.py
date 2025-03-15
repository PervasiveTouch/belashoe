from time import sleep
from DIPPID import SensorUDP

PORT_RIGHT = 5701
bela = SensorUDP(PORT_RIGHT)

def printDataToConsole(data):
    print(f'recieved data: {data}, type: {type(data[0])}')

bela.register_callback('touch-sensors', printDataToConsole)
