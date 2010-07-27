import time
from serial import Serial
from message_formatter import SOT

SLEEPING_TIME = 0.01

class SerialCommunicator:

    def __init__(self, port='/dev/usb/ttyUSB0', baudrate=19200):
        self.connection = Serial()
        self.connection.port = port
        self.connection.baudrate = baudrate

    def set_port(self, port_name):
        self.connection.port = port_name

    def send_command(self, message):
        self.connection.open()
        self.connection.write(message)

        # Waits until the robot starts the response
        while self.connection.read() != SOT:
            time.sleep(SLEEPING_TIME)

        message_length = self.connection.read()
        remaining_chars = ord(message_length) + 1
        message = self.connection.read(remaining_chars)
        message_type = message[0]
        encoded_data = message[1:-1]

        self.connection.close()

        return message_type, encoded_data
