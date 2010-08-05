from computer_vision import ComputerVision as CV, Color
from robots_detector import RobotsDetector
from message_formatter import MessageFormatter as MF
from serial_communicator import SerialCommunicator
from commands import *

class CommandsManager:

    def __init__(self):

        # Initializes the robot detector
        #color = Color(red=225, green=160, blue=34)  # Yellow
        #color = Color(red=41, green=87, blue=193)   # Blue
        color = Color(red=30, green=112, blue=68)    # Green
        #color = Color(red=228, green=46, blue=39)   # Red
        #color = Color(red=90, green=249, blue=211)  # Green (lab)
        self.detector = RobotsDetector(color)

        # Initializes the serial communicator
        self.communicator = SerialCommunicator()

        self.immediate_commands = []
        self.continuous_run_mode = IDLE
        self.show_log_in_console = False
        self.send_messages = False

    def set_webcam_capture(self, camera_index):
        # TODO: Create an empty 'capture' in the constructor
        self.capture = CV.get_capture(camera_index)

    def set_serial_port(self, port):
        self.communicator.set_port(port)

    def add_command(self, command):
        self.immediate_commands.insert(0, command)

    def set_run_mode(self, run_mode):
        self.continuous_run_mode = run_mode

    def run_iteration(self):
        if self.immediate_commands:
            command = self.immediate_commands.pop()
        else:
            command = self.continuous_run_mode

        self.run_command(command)

    def run_command(self, command):
        if command == IDLE:
            pass

        elif command == LOCK_ENGINES:
            self.log("I've locked the engines")

        elif command == UNLOCK_ENGINES:
            self.log("I've unlocked the engines")

        elif command == SEND_ROBOTS_POSITIONS:
            image = CV.grab_frame(self.capture)
            coordinates = self.detector.get_robots_coordinates(image)

            self.send_message(command, coordinates)
            self.log('Robots found at: {0}'.format(coordinates))

        elif command == ACQUIRE_CONTROL_DATA:
            self.log("I'm acquiring control data")

    def log(self, message):
        if self.show_log_in_console:
            print message

    def send_message(self, command, data):
        if self.send_messages:
            message = MF.encode(command, data)
            self.communicator.send_command(message)
