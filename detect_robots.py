from computer_vision import ComputerVision as CV, Color
from robot_detector import RobotDetector

if __name__ == '__main__':

    # Gets the camera index from the command line argument
    camera_index = int(argv[1]) if len(argv) > 1 else 0

    left_color = Color(red=225, green=160, blue=34)  # Yellow
    right_color = Color(red=41, green=87, blue=193)  # Blue
    detector = RobotDetector(left_color, right_color)

    capture = CV.get_capture(camera_index)
    CV.create_window()

    while True:
        image = CV.grab_frame(capture)
        coordinates = detector.get_robots_coordinates(image)

        CV.draw_robots(coordinates, image)
        CV.show_window(image)
