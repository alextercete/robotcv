import time
from serial import Serial

from message_formatter import MessageFormatter as MF, SOT, EOT
from commands import *

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

        response = self.get_response()

        self.connection.close()

        return response

    def get_response(self):
        # Waits until the robot starts the response
        while self.connection.read() != SOT:
            time.sleep(SLEEPING_TIME)

        message_length = self.connection.read()
        remaining_chars_count = ord(message_length) + len(EOT)
        message = self.connection.read(remaining_chars_count)
        command = message[0]

        if command == ACQUIRE_CONTROL_DATA:
            data = message[1:-1]
            return MF.decode_data(command, data)
