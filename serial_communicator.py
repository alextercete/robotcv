import time
from serial import Serial, SerialException

from message_formatter import MessageFormatter as MF, SOT, EOT
from commands import *

SLEEPING_TIME = 0.01
NUMBER_OF_TRIES = 10

class CommunicationError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class SerialCommunicator:

    def __init__(self, port='/dev/usb/ttyUSB0', baudrate=19200):
        self.connection = Serial()
        self.connection.port = port
        self.connection.baudrate = baudrate

    def set_port(self, port_name):
        self.connection.port = port_name

    def send_command(self, message):
        try:
            self.connection.open()
        except SerialException:
            raise CommunicationError('Failed to establish serial connection')

        self.connection.write(message)
        response = self.get_response()
        self.connection.close()

        return response

    def get_response(self):
        tries = 0
        while self.connection.read() != SOT:
            tries += 1

            if tries >= NUMBER_OF_TRIES:
                raise CommunicationError('Could not get the robot response!')

            time.sleep(SLEEPING_TIME)

        message_length = self.connection.read()
        remaining_chars_count = ord(message_length) + len(EOT)
        message = self.connection.read(remaining_chars_count)
        command = message[0]

        if command == SEND_ROBOTS_POSITIONS:
            data = message[1:-1]
            # FIXME: Don't decode messages here
            return MF.decode_data(command, data)

        elif command == ACQUIRE_CONTROL_DATA:
            data = message[1:-1]
            # FIXME: Don't decode messages here
            return MF.decode_data(command, data)
