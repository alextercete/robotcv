from computer_vision import ComputerVision as CV

class RobotsDetector:

    def __init__(self, color):
        '''Initializes the robots detector.

        The color of the robots is given as argument.
        '''
        self.color = color

    def get_robots_coordinates(self, image):
        '''Gets the robots position and rotation list.'''

        image_channels = CV.split_into_channels(image)

        return CV.find_color_blob(self.color, image_channels)
