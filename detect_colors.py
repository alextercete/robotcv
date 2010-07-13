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
        detector.add_color(red=225, green=160, blue=34) # Yellow
        detector.add_color(red=239, green=47, blue=44)  # Red
        detector.add_color(red=34, green=112, blue=70)  # Green
        detector.add_color(red=41, green=87, blue=193)  # Blue
        detector.run()

        cv.ShowImage(WINDOW_MAIN, detector.get_image())

        if cv.WaitKey(10) == KEY_ESC:
            break
