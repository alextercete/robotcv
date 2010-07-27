import math
import cv

KEY_ESC = 27
WINDOW_MAIN = 'Camera'

class ComputerVision:

    @classmethod
    def get_capture(cls, camera_index):
        return cv.CaptureFromCAM(camera_index)

    @classmethod
    def create_window(cls):
        cv.NamedWindow(WINDOW_MAIN)

    @classmethod
    def grab_frame(cls, capture):
        return cv.QueryFrame(capture)

    @classmethod
    def convert_to_RGB(cls, image):
        cv.CvtColor(image, image, cv.CV_BGR2RGB)

    @classmethod
    def split_into_channels(cls, image):
        red = cv.CreateImage(cv.GetSize(image), cv.IPL_DEPTH_8U, 1)
        green = cv.CloneImage(red)
        blue = cv.CloneImage(red)

        # Split the BGR image into separate channels
        cv.Split(image, blue, green, red, None)

        return red, green, blue

    @classmethod
    def find_color_blob(cls, color, image_channels):
        processed_image = cls.do_processing(color, image_channels)

        return cls.find_center_of_mass(processed_image)

    @classmethod
    def do_processing(cls, color, image_channels):
        red, green, blue = image_channels

        processed_image = cv.CloneImage(red)
        thresholded_red = cv.CloneImage(red)
        thresholded_green = cv.CloneImage(red)
        thresholded_blue = cv.CloneImage(red)

        # Threshold the channels with the color ranges
        limits = ColorLimits(color)
        cv.InRangeS(red, limits.R_min, limits.R_max, thresholded_red)
        cv.InRangeS(green, limits.G_min, limits.G_max, thresholded_green)
        cv.InRangeS(blue, limits.B_min, limits.B_max, thresholded_blue)

        # And the images together to find the desired color
        cv.And(thresholded_red, thresholded_green, processed_image)
        cv.And(processed_image, thresholded_blue, processed_image)

        # Erode and dilate the image, to decrease noise
        #cv.Erode(processed_image, processed_image)
        #cv.Dilate(processed_image, processed_image)

        return processed_image

    @classmethod
    def find_center_of_mass(cls, image):
        moments = cv.Moments(image)
        M00 = cv.GetSpatialMoment(moments, 0, 0)

        try:
            x = int(cv.GetSpatialMoment(moments, 1, 0) / M00)
            y = int(cv.GetSpatialMoment(moments, 0, 1) / M00)
        except ZeroDivisionError:
            return None
        else:
            return x, y

    @classmethod
    def draw_robots(cls, coordinates, image):
        if coordinates:
            x, y = map(int, map(round, coordinates))

            cv.Circle(image, (x, y), 5, cv.RGB(0, 0, 0), thickness=-1)

    @classmethod
    def show_window(cls, image):
        cv.ShowImage(WINDOW_MAIN, image)

    @classmethod
    def esc_key_was_pressed(cls, time_to_wait=10):
        key_code = cv.WaitKey(time_to_wait) % 0x100
        return key_code == KEY_ESC


class Color:

    def __init__(self, red=0, green=0, blue=0):
        self.R = red
        self.G = green
        self.B = blue


class ColorLimits:

    def __init__(self, color, delta=30):
        self.R_min, self.R_max = self.get_limits(color.R, delta)
        self.G_min, self.G_max = self.get_limits(color.G, delta)
        self.B_min, self.B_max = self.get_limits(color.B, delta)

    def get_limits(self, component_value, delta):
        minimum_limit = component_value - delta
        maximum_limit = component_value + delta

        if minimum_limit < 0:
            return 0, 2 * delta
        elif maximum_limit > 255:
            return 255 - 2 * delta, 255

        return minimum_limit, maximum_limit
