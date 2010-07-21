from sys import argv

from computer_vision import ComputerVision as CV, Color
from robots_detector import RobotsDetector

if __name__ == '__main__':

    # Gets the camera index from the command line argument
    camera_index = int(argv[1]) if len(argv) > 1 else 0

    #color = Color(red=225, green=160, blue=34)  # Yellow
    #color = Color(red=41, green=87, blue=193)   # Blue
    #color = Color(red=30, green=112, blue=68)   # Green
    #color = Color(red=228, green=46, blue=39)   # Red
    color = Color(red=90, green=249, blue=211)   # Green (lab)
    detector = RobotsDetector(color)

    capture = CV.get_capture(camera_index)
    CV.create_window()

    while True:
        image = CV.grab_frame(capture)
        coordinates = detector.get_robots_coordinates(image)

        CV.draw_robots(coordinates, image)
        CV.show_window(image)

        if CV.esc_key_was_pressed():
            break
