import wx

from computer_vision import ComputerVision as CV, Color
from robots_detector import RobotsDetector
from message_formatter import MessageFormatter as MF, SEND_ROBOTS_POSITIONS
from serial_communicator import SerialCommunicator

class MainWindow(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='RobotCV', size=(900, 480))

        self.webcam_panel = WebcamPanel(self)
        self.image_panel = ImagePanel(self)
        self.webcam_timer = WebcamTimer(self)

        # Initializes the robot detector
        left_color = Color(red=30, green=112, blue=68)   # Green
        right_color = Color(red=228, green=46, blue=39)  # Red
        self.detector = RobotsDetector(left_color, right_color)

        # Initializes the serial communicator
        self.communicator = SerialCommunicator()

        self.do_layout()
        self.set_defaults()
        self.bind_events()

    def do_layout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.webcam_panel, 1, wx.EXPAND, 0)
        sizer.Add(self.image_panel, 0, wx.EXPAND, 0)
        self.SetSizer(sizer)

    def set_defaults(self):
        self.update_capture()
        self.enable_sending_data()
        self.update_port_name()
        self.update_polling_time()
        self.enable_log()

    def bind_events(self):
        panel = self.webcam_panel
        panel.spn_camera_index.Bind(wx.EVT_SPINCTRL, self.update_capture)
        panel.chk_send_data.Bind(wx.EVT_CHECKBOX, self.enable_sending_data)
        panel.txt_port_name.Bind(wx.EVT_TEXT, self.update_port_name)
        panel.spn_polling_time.Bind(wx.EVT_SPINCTRL, self.update_polling_time)
        panel.chk_enable_log.Bind(wx.EVT_CHECKBOX, self.enable_log)
        panel.btn_toggle_webcam.Bind(wx.EVT_BUTTON, self.toggle_webcam)

        self.Bind(wx.EVT_CLOSE, self.close)

    def update_capture(self, event=None):
        camera_index = self.webcam_panel.spn_camera_index.GetValue()
        self.capture = CV.get_capture(camera_index)

    def enable_sending_data(self, event=None):
        checked_state = self.webcam_panel.chk_send_data.GetValue()
        self.webcam_timer.send_messages = checked_state

    def update_port_name(self, event=None):
        port_name = self.webcam_panel.txt_port_name.GetValue()
        #self.communicator.set_port(port_name)
        pass

    def update_polling_time(self, event=None):
        value = self.webcam_panel.spn_polling_time.GetValue()
        self.webcam_timer.polling_time = value

    def enable_log(self, event=None):
        checked_state = self.webcam_panel.chk_enable_log.GetValue()
        self.webcam_timer.show_log_in_console = checked_state

    def toggle_webcam(self, event):
        timer = self.webcam_timer

        if timer.IsRunning():
            timer.stop()
        else:
            timer.start()

    def close(self, event):
        timer = self.webcam_timer

        if timer.IsRunning():
            timer.stop()

        self.Destroy()


class ImagePanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        empty_bitmap = wx.EmptyBitmap(640, 480)
        self.webcam_image = wx.StaticBitmap(self, bitmap=empty_bitmap)


class WebcamPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.spn_camera_index = wx.SpinCtrl(self, max=10, initial=0)
        self.chk_send_data = wx.CheckBox(self, label='Send data through serial port')
        self.txt_port_name = wx.TextCtrl(self, value='/dev/usb/ttyUSB0')
        self.spn_polling_time = wx.SpinCtrl(self, min=50, max=1000, initial=200)
        self.chk_enable_log = wx.CheckBox(self, label='Enable console log')
        self.btn_toggle_webcam = wx.Button(self, label='Start')

        sizer = WebcamSizer(self)
        sizer.add_form_field('Camera index', self.spn_camera_index)
        sizer.add_separator()
        sizer.add(self.chk_send_data, 0, wx.ALL, 5)
        sizer.add_form_field('Port name', self.txt_port_name)
        sizer.add_form_field('Polling time', self.spn_polling_time)
        sizer.add_separator()
        sizer.add(self.chk_enable_log, 0, wx.ALL, 5)
        sizer.add(self.btn_toggle_webcam, 0, wx.ALL|wx.CENTER, 15)

        self.SetSizer(sizer)


class WebcamSizer(wx.BoxSizer):

    def __init__(self, panel):
        wx.BoxSizer.__init__(self, wx.VERTICAL)

        self.panel = panel

        container = wx.StaticBox(panel, label='Robots detection through webcam')
        self.main_sizer = wx.StaticBoxSizer(container, wx.VERTICAL)
        self.Add(self.main_sizer, 0, wx.ALL|wx.EXPAND, 10)

    # XXX: Can't override 'Add'! See: http://wiki.wxpython.org/OverridingMethods
    def add(self, *args, **kwargs):
        self.main_sizer.Add(*args, **kwargs)

    def add_form_field(self, label_text, form_field):
        lbl_form_field = wx.StaticText(self.panel, label=label_text)

        inner_sizer = wx.BoxSizer(wx.HORIZONTAL)
        inner_sizer.Add(lbl_form_field, 1, wx.CENTER, 0)
        inner_sizer.Add(form_field, 1, wx.CENTER, 0)

        self.main_sizer.Add(inner_sizer, 0, wx.ALL|wx.EXPAND, 5)

    def add_separator(self):
        separator = wx.StaticLine(self.panel)
        self.main_sizer.Add(separator, 0, wx.ALL|wx.EXPAND, 3)


class WebcamTimer(wx.Timer):

    def __init__(self, parent):
        wx.Timer.__init__(self, parent)

        self.parent = parent

        self.polling_time = 200
        self.show_log_in_console = False
        self.send_messages = False

        parent.Bind(wx.EVT_TIMER, self.detect_robots, self)

    def start(self):
        self.log('Starting robots detection...')
        self.Start(self.polling_time)
        self.parent.webcam_panel.btn_toggle_webcam.SetLabel('Stop')

    def stop(self):
        self.Stop()
        self.parent.webcam_panel.btn_toggle_webcam.SetLabel('Start')
        self.log('Robots detection stopped!')

    def detect_robots(self, event):
        image = CV.grab_frame(self.parent.capture)
        coordinates = self.parent.detector.get_robots_coordinates(image)

        self.show_image(image, coordinates)
        self.send_message(coordinates)
        self.log(coordinates)

    def show_image(self, image, robots_coordinates):
        image_panel = self.parent.image_panel

        CV.draw_robots(robots_coordinates, image)
        CV.convert_to_RGB(image)

        bitmap = wx.BitmapFromBuffer(image.width, image.height, image.tostring())
        image_panel.webcam_image.SetBitmap(bitmap)
        image_panel.Refresh()

    def log(self, message):
        if self.show_log_in_console:
            print message

    def send_message(self, message_data):
        if self.send_messages:
            message = MF.encode(SEND_ROBOTS_POSITIONS, data)
            self.parent.communicator.send_command(message)


def main():
    app = wx.App()
    frame = MainWindow()
    frame.Centre()
    frame.Show(True)
    app.MainLoop()
