import cv

class ColorDetector:

    def __init__(self, image):
        self.image = image
        self.colors = []

    def add_color(self, red=0, green=0, blue=0):
        '''Adds a color to be detected, given its RGB value.

        Arguments should be between 0 (default) and 255.
        '''
        color = red, green, blue
        self.colors.append(color)

    def run(self):
        red, green, blue = self.get_components()

        processed = cv.CreateImage(cv.GetSize(self.image), cv.IPL_DEPTH_8U, 1)
        thresholded_red = cv.CloneImage(processed)
        thresholded_green = cv.CloneImage(processed)
        thresholded_blue = cv.CloneImage(processed)

        for color in self.colors:
            limits = ColorLimits(color)

            # Threshold the channels with the color ranges
            cv.InRangeS(red, limits.R_min, limits.R_max, thresholded_red)
            cv.InRangeS(green, limits.G_min, limits.G_max, thresholded_green)
            cv.InRangeS(blue, limits.B_min, limits.B_max, thresholded_blue)

            # And the images together to find the desired color
            cv.And(thresholded_red, thresholded_green, processed)
            cv.And(processed, thresholded_blue, processed)

            # Erode and dilate the image, to decrease noise (SLOW)
            #cv.Erode(processed, processed)
            #cv.Dilate(processed, processed)

            contours = cv.FindContours(processed,
                                       cv.CreateMemStorage(),
                                       cv.CV_RETR_CCOMP,
                                       cv.CV_CHAIN_APPROX_SIMPLE)

            while contours:

                # Get the center of mass
                moments = cv.Moments(contours)
                M00 = cv.GetSpatialMoment(moments, 0, 0)

                if M00 != 0:
                    x = int(cv.GetSpatialMoment(moments, 1, 0) / M00)
                    y = int(cv.GetSpatialMoment(moments, 0, 1) / M00)

                    # Draws the center of mass to the image
                    cv.Circle(self.image, (x, y), 5, cv.RGB(0, 0, 0), thickness=-1)

                # Get the next contour set
                contours = contours.h_next()

    def get_components(self):
        size = cv.GetSize(self.image)

        red = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        green = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        blue = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)

        # Split the BGR image into separate channels
        cv.Split(self.image, blue, green, red, None)

        return red, green, blue

    def get_image(self):
        return self.image


class ColorLimits:

    def __init__(self, colors, delta=30):
        red, green, blue = colors

        self.R_min = self.get_minimum_limit(red, delta)
        self.R_max = self.get_maximum_limit(red, delta)
        self.G_min = self.get_minimum_limit(green, delta)
        self.G_max = self.get_maximum_limit(green, delta)
        self.B_min = self.get_minimum_limit(blue, delta)
        self.B_max = self.get_maximum_limit(blue, delta)

    def get_minimum_limit(self, component_value, delta):
        minimum_limit = component_value - delta
        return minimum_limit if minimum_limit >= 0 else 0

    def get_maximum_limit(self, component_value, delta):
        minimum_limit = component_value + delta
        return minimum_limit if minimum_limit <= 255 else 255
