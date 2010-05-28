import cv
from sys import argv

# Constants
KEY_ESC = 27

WINDOW_MAIN = 'Camera'
WINDOW_PROCESSED = 'Processed'

RED_MIN = 10
RED_MAX = 70
GREEN_MIN = 70
GREEN_MAX = 130
BLUE_MIN = 170
BLUE_MAX = 230


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

        cv.ShowImage(WINDOW_MAIN, img)
        cv.ShowImage(WINDOW_PROCESSED, processed_img)

        if cv.WaitKey(10) == KEY_ESC:
            break
