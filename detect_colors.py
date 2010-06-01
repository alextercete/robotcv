import cv
from sys import argv

# Constants
KEY_ESC = 27

WINDOW_MAIN = 'Camera'
WINDOW_PROCESSED = 'Processed'

RED_MIN = 0
RED_MAX = 60
GREEN_MIN = 35
GREEN_MAX = 95
BLUE_MIN = 75
BLUE_MAX = 135


if __name__ == '__main__':

    # Gets the camera index from the command line argument
    camera_index = int(argv[1]) if len(argv) > 1 else 0
    capture = cv.CaptureFromCAM(camera_index)

    # Creates the windows
    cv.NamedWindow(WINDOW_MAIN)
    cv.NamedWindow(WINDOW_PROCESSED)

    while True:
        img = cv.QueryFrame(capture)
        size = cv.GetSize(img)

        red = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        green = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        blue = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        processed_img = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)

        # Split the BGR image into separate channels
        cv.Split(img, blue, green, red, None)

        # Threshold the channels with the color ranges
        cv.InRangeS(red, RED_MIN, RED_MAX, red)
        cv.InRangeS(green, GREEN_MIN, GREEN_MAX, green)
        cv.InRangeS(blue, BLUE_MIN, BLUE_MAX, blue)

        # And the images together to find the desired color
        cv.And(red, green, processed_img)
        cv.And(processed_img, blue, processed_img)

        # Erode and dilate the image, to decrease noise
        cv.Erode(processed_img, processed_img)
        #cv.Dilate(processed_img, processed_img)

        # Get the center of mass
        moments = cv.Moments(processed_img)
        M00 = cv.GetSpatialMoment(moments, 0, 0)
        
        if M00 != 0:
            x = int(cv.GetSpatialMoment(moments, 1, 0) / M00)
            y = int(cv.GetSpatialMoment(moments, 0, 1) / M00)

            # Draws the center of mass to the image
            cv.Circle(img, (x, y), 5, cv.Scalar(0, 0, 255), thickness=-1)

        cv.ShowImage(WINDOW_MAIN, img)
        cv.ShowImage(WINDOW_PROCESSED, processed_img)

        if cv.WaitKey(10) == KEY_ESC:
            break
