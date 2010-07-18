import cv

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
    def split_into_channels(cls, image):
        red = cv.CreateImage(cv.GetSize(image), cv.IPL_DEPTH_8U, 1)
        green = cv.CloneImage(red)
        blue = cv.CloneImage(red)

        # Split the BGR image into separate channels
        cv.Split(image, blue, green, red, None)

        return red, green, blue

    @classmethod
    def find_color_blobs(cls, color, image_channels):
        processed_image = cls.do_processing(color, image_channels)
        contours = cls.find_contours(processed_image)
        color_blobs_positions = []

        while contours:
            color_blob_center = cls.find_center_of_mass(contours)

            if color_blob_center:
                color_blobs_positions.append(color_blob_center)

            contours.h_next()

        return color_blobs_positions

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
    def find_contours(cls, image):
        return cv.FindContours(image,
                               cv.CreateMemStorage(),
                               cv.CV_RETR_CCOMP,
                               cv.CV_CHAIN_APPROX_SIMPLE)

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
        pass

    @classmethod
    def show_window(cls, image):
        cv.ShowImage(WINDOW_MAIN, image)


class Color:

    def __init__(self, red=0, green=0, blue=0):
        self.R = red
        self.G = green
        self.B = blue


class ColorLimits:

    def __init__(self, color, delta=30):

        self.R_min = self.get_minimum_limit(color.R, delta)
        self.R_max = self.get_maximum_limit(color.R, delta)
        self.G_min = self.get_minimum_limit(color.G, delta)
        self.G_max = self.get_maximum_limit(color.G, delta)
        self.B_min = self.get_minimum_limit(color.B, delta)
        self.B_max = self.get_maximum_limit(color.B, delta)

    def get_minimum_limit(self, component_value, delta):
        minimum_limit = component_value - delta
        return minimum_limit if minimum_limit >= 0 else 0

    def get_maximum_limit(self, component_value, delta):
        minimum_limit = component_value + delta
        return minimum_limit if minimum_limit <= 255 else 255
