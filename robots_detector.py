from __future__ import division

import math
from computer_vision import ComputerVision as CV

class RobotsDetector:

    def __init__(self, left_color, right_color):
        '''Initializes the robots detector.

        Left and right colors of the robots are given as arguments.
        '''
        self.left_color = left_color
        self.right_color = right_color

    def get_robots_coordinates(self, image):
        '''Gets the robots position and rotation list.'''

        image_channels = CV.split_into_channels(image)

        left_points = CV.find_color_blobs(self.left_color, image_channels)
        right_points = CV.find_color_blobs(self.right_color, image_channels)
        pairs = self.combine_points(left_points, right_points)

        return self.calculate_coordinates(pairs)

    @staticmethod
    def combine_points(left_points, right_points):
        '''Combines two lists of points that represents left and right
           sides of a robot.

        Finds the closest two points that can be paired from each list.
        '''
        return zip(sorted(left_points), sorted(right_points))

    @staticmethod
    def calculate_coordinates(pairs):
        '''Calculates the robots position and rotation based on the
           its two points representation.

        The coordinates are returned as tuples (x, y, theta). The angle
        is given in degrees
        '''
        points = []

        for pair in pairs:
            (x_left, y_left), (x_right, y_right) = pair
            delta_x, delta_y = x_right - x_left, y_right - y_left

            x, y = x_left + delta_x / 2, y_left + delta_y / 2

            if delta_y == 0:
                theta = 0 if delta_x > 0 else 180
            elif delta_x == 0:
                theta = 90 if delta_y > 0 else 270
            else:
                theta = math.atan(delta_y / delta_x) * 180 / math.pi

                if theta < 0:
                    theta += 360

            points.append((x, y, theta))

        return points
