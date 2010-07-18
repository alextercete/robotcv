import unittest
from robotcv.robots_detector import RobotsDetector as RD

class TestRobotsDetector(unittest.TestCase):

    def test_points_combination_single_element_lists(self):
        left_points = [(0, 0)]
        right_points = [(1, 1)]
        expected_result = [((0, 0), (1, 1))]

        self.verify_combination(left_points, right_points, expected_result)

    def test_points_combination_two_elements_lists(self):
        left_points = [(0, 0), (2, 4)]
        right_points = [(1, 1), (3, 4)]
        expected_result = [((0, 0), (1, 1)),
                           ((2, 4), (3, 4))]

        self.verify_combination(left_points, right_points, expected_result)

    def verify_combination(self, left_points, right_points, expected_result):
        self.assertEqual(expected_result,
                         RD.combine_points(left_points, right_points))


if __name__ == '__main__':
    unittest.main()
