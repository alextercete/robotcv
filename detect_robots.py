import wx
from sys import argv

from computer_vision import ComputerVision as CV, Color
from robots_detector import RobotsDetector
#from message_formatter import MessageFormatter as MF, SEND_ROBOTS_POSITIONS
#message = MF.encode(SEND_ROBOTS_POSITIONS, coordinates)
from serial_communicator import SerialCommunicator

class MainWindow(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='RobotCV', size=(250, 350))

        self.webcam_panel = WebcamPanel(self)
        self.webcam_timer = WebcamTimer(self)

        self.set_defaults()
        self.bind_events()

        # Initializes the robot detector
        #color = Color(red=225, green=160, blue=34)  # Yellow
        #color = Color(red=41, green=87, blue=193)   # Blue
        color = Color(red=30, green=112, blue=68)   # Green
        #color = Color(red=228, green=46, blue=39)   # Red
        #color = Color(red=90, green=249, blue=211)   # Green (lab)
        self.detector = RobotsDetector(color)

    def set_defaults(self):
        self.update_capture()
        self.update_polling_time()
        self.enable_log()

    def bind_events(self):
        panel = self.webcam_panel
        panel.spn_camera_index.Bind(wx.EVT_SPINCTRL, self.update_capture)
        panel.chk_enable_log.Bind(wx.EVT_CHECKBOX, self.enable_log)
        panel.spn_polling_time.Bind(wx.EVT_SPINCTRL, self.update_polling_time)
        panel.btn_toggle_webcam.Bind(wx.EVT_BUTTON, self.toggle_webcam)

    def update_capture(self, event=None):
        camera_index = self.webcam_panel.spn_camera_index.GetValue()
        self.capture = CV.get_capture(camera_index)

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


class WebcamPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.spn_camera_index = wx.SpinCtrl(self, max=10, initial=1)
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
        lbl_form_field = wx.StaticText(self.panel, wx.ID_ANY, label_text)

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

        self.log(coordinates)

    def log(self, message):
        if self.show_log_in_console:
            print message


if __name__ == '__main__':

    app = wx.App()
    frame = MainWindow().Show()
    app.MainLoop()
