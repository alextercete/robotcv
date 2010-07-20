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

    def test_points_combination_two_elements_lists_with_left_switched(self):
        left_points = [(2, 4), (0, 0)]
        right_points = [(1, 1), (3, 4)]
        expected_result = [((0, 0), (1, 1)),
                           ((2, 4), (3, 4))]

        self.verify_combination(left_points, right_points, expected_result)

    def test_points_combination_two_elements_lists_with_right_switched(self):
        left_points = [(0, 0), (2, 4)]
        right_points = [(3, 4), (1, 1)]
        expected_result = [((0, 0), (1, 1)),
                           ((2, 4), (3, 4))]

        self.verify_combination(left_points, right_points, expected_result)

    def test_coordinates_calculation_one_point(self):
        pairs = [((0, 0), (1, 1))]
        expected_result = [(0.5, 0.5, 45)]

        self.verify_calculation(pairs, expected_result)

    def test_coordinates_calculation_two_points(self):
        pairs = [((0, 0), (1, 1)),
                 ((2, 4), (3, 4))]
        expected_result = [(0.5, 0.5, 45), (2.5, 4, 0)]

        self.verify_calculation(pairs, expected_result)

    def test_coordinates_calculation_three_points(self):
        pairs = [((4, 2), (3, 2)),
                 ((1, 3), (2, 2)),
                 ((5, 2), (5, 1))]
        expected_result = [(3.5, 2, 180), (1.5, 2.5, 315), (5, 1.5, 270)]

        self.verify_calculation(pairs, expected_result)

    def verify_combination(self, left_points, right_points, expected_result):
        self.assertEqual(expected_result,
                         RD.combine_points(left_points, right_points))

    def verify_calculation(self, pairs, expected_result):
        self.assertEqual(expected_result, RD.calculate_coordinates(pairs))


if __name__ == '__main__':
    unittest.main()
