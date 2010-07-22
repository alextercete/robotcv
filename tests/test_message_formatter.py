import unittest
from robotcv.message_formatter import *

class TestMessageFormatter(unittest.TestCase):

    def test_robot_position_message_for_one_robot(self):
        message = (689, 342)
        self.verify_formatting(SEND_ROBOTS_POSITIONS, message)

    def test_robot_position_message_for_two_robots(self):
        message = (689, 342, 110, 55)
        self.verify_formatting(SEND_ROBOTS_POSITIONS, message)

    def test_robot_position_message_for_three_robots(self):
        message = (689, 342, 110, 55, 13, 519)
        self.verify_formatting(SEND_ROBOTS_POSITIONS, message)

    def test_malformed_robot_position_message(self):
        message = (437,)
        self.verify_failing_encoding_attempt(SEND_ROBOTS_POSITIONS, message)

    def test_malformed_robot_position_message_for_two_robots(self):
        message = (43, 201, 34)
        self.verify_failing_encoding_attempt(SEND_ROBOTS_POSITIONS, message)

    def verify_formatting(self, message_type, message):
        formatter = MessageFormatter

        encoded_message = formatter.encode_data(message_type, message)
        decoded_message = formatter.decode_data(message_type, encoded_message)

        self.assertEqual(message, decoded_message)

    def verify_failing_encoding_attempt(self, message_type, message):
        self.assertRaises(BadFormatError,
                          MessageFormatter.encode_data,
                          SEND_ROBOTS_POSITIONS, message)


if __name__ == '__main__':
    unittest.main()
