import cv
from sys import argv

from color_detector import ColorDetector

# Constants
KEY_ESC = 27
WINDOW_MAIN = 'Camera'

if __name__ == '__main__':

    # Gets the camera index from the command line argument
    camera_index = int(argv[1]) if len(argv) > 1 else 0
    capture = cv.CaptureFromCAM(camera_index)

    # Creates the window
    cv.NamedWindow(WINDOW_MAIN)

    while True:
        image = cv.QueryFrame(capture)

        detector = ColorDetector(image)
        detector.add_color(green=33, blue=86)
        detector.add_color(red=112, green=4, blue=1)
        detector.run()

        cv.ShowImage(WINDOW_MAIN, detector.get_image())

        if cv.WaitKey(10) == KEY_ESC:
            break
