import unittest
from robotcv.message_formatter import *

class TestMessageFormatter(unittest.TestCase):

    def test_robot_position_message_for_one_robot(self):
        message = ('A', 689, 342)
        self.verify_formatting(SEND_ROBOTS_POSITIONS, message)

    def test_robot_position_message_for_two_robots(self):
        message = ('A', 689, 342, 'B', 110, 55)
        self.verify_formatting(SEND_ROBOTS_POSITIONS, message)

    def test_robot_position_message_for_three_robots(self):
        message = ('A', 689, 342, 'B', 110, 55, 'C', 13, 519)
        self.verify_formatting(SEND_ROBOTS_POSITIONS, message)

    def test_malformed_robot_position_message(self):
        message = ('A', 437)
        self.verify_failing_encoding_attempt(SEND_ROBOTS_POSITIONS, message)

    def test_malformed_robot_position_message_for_two_robots(self):
        message = ('A', 43, 'B', 201)
        self.verify_failing_encoding_attempt(SEND_ROBOTS_POSITIONS, message)

    def verify_formatting(self, message_type, message):
        formatter = MessageFormatter

        encoded_message = formatter.encode(message_type, message)
        decoded_message = formatter.decode(message_type, encoded_message)

        self.assertEqual(message, decoded_message)

    def verify_failing_encoding_attempt(self, message_type, message):
        self.assertRaises(BadFormatError,
                          MessageFormatter.encode,
                          SEND_ROBOTS_POSITIONS, message)


if __name__ == '__main__':
    unittest.main()
