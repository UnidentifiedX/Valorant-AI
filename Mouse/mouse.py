import serial

class ArduinoMouse():
    def __init__(self, port, baud: int):
        self.port = port
        self.baud = baud
        self.arduino = serial.Serial(port, baud)

    # We use a letter 'x' to indicate the end of a message
    def moveRel(self, x: int, y: int):
        self.arduino.write(f"{x}:{y}x".encode())


    # def moveTo(self, x: int, y: int):
    #     self.arduino.write(f"{x}:{y}x".encode())