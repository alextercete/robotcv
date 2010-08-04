import wx

from computer_vision import ComputerVision as CV, Color
from robots_detector import RobotsDetector
from message_formatter import MessageFormatter as MF, SEND_ROBOTS_POSITIONS
from serial_communicator import SerialCommunicator

class MainWindow(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='RobotCV', size=(550, 450))

        # Initializes the webcam timer
        self.webcam_timer = WebcamTimer(self)

        # Initializes the robot detector
        #color = Color(red=225, green=160, blue=34)  # Yellow
        #color = Color(red=41, green=87, blue=193)   # Blue
        color = Color(red=30, green=112, blue=68)    # Green
        #color = Color(red=228, green=46, blue=39)   # Red
        #color = Color(red=90, green=249, blue=211)  # Green (lab)
        self.detector = RobotsDetector(color)

        # Initializes the serial communicator
        self.communicator = SerialCommunicator()

        self.config_panel = ConfigPanel(self, 'Configuration')
        self.webcam_timer_panel = WebcamTimerPanel(self, 'Webcam timer')
        self.commands_panel = CommandsPanel(self, 'Immediate commands')
        self.run_mode_panel = RunModePanel(self, 'Continuous run mode')

        self.do_layout()
        self.bind_events()

    def do_layout(self):
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.config_panel, 0, wx.EXPAND, 0)
        left_sizer.Add(self.webcam_timer_panel, 0, wx.EXPAND, 0)

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.commands_panel, 0, wx.EXPAND, 0)
        right_sizer.Add(self.run_mode_panel, 0, wx.EXPAND, 0)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left_sizer, 1, wx.EXPAND, 0)
        sizer.Add(right_sizer, 1, wx.EXPAND, 0)
        self.SetSizer(sizer)

    def bind_events(self):
        self.Bind(wx.EVT_CLOSE, self.close)

    def close(self, event):
        timer = self.webcam_timer

        if timer.IsRunning():
            timer.stop()

        self.Destroy()


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
        self.parent.webcam_timer_panel.btn_toggle_webcam.SetLabel('Stop')

    def stop(self):
        self.Stop()
        self.parent.webcam_timer_panel.btn_toggle_webcam.SetLabel('Start')
        self.log('Robots detection stopped!')

    def detect_robots(self, event):
        image = CV.grab_frame(self.parent.capture)
        coordinates = self.parent.detector.get_robots_coordinates(image)

        self.send_message(coordinates)
        self.log(coordinates)

    def log(self, message):
        if self.show_log_in_console:
            print message

    def send_message(self, data):
        if self.send_messages:
            message = MF.encode(SEND_ROBOTS_POSITIONS, data)
            self.parent.communicator.send_command(message)


class GenericPanel(wx.Panel):

    def __init__(self, parent, label):
        wx.Panel.__init__(self, parent)

        self.sizer = FramedSizer(self, label)
        self.SetSizer(self.sizer)

    def add_field(self, form_field):
        self.sizer.add_field(form_field)

    def add_labeled_field(self, label, form_field):
        self.sizer.add_labeled_field(label, form_field)

    def add_button(self, button):
        self.sizer.add_button(button)

    def add_separator(self):
        self.sizer.add_separator()


class FramedSizer(wx.BoxSizer):

    def __init__(self, panel, label):
        wx.BoxSizer.__init__(self, wx.VERTICAL)

        self.panel = panel

        container = wx.StaticBox(panel, label=label)
        self.main_sizer = wx.StaticBoxSizer(container, wx.VERTICAL)
        self.Add(self.main_sizer, 0, wx.ALL|wx.EXPAND, 10)

    def add_field(self, form_field):
        self.main_sizer.Add(form_field, 0, wx.ALL, 5)

    def add_labeled_field(self, label, form_field):
        lbl_form_field = wx.StaticText(self.panel, label=label)

        inner_sizer = wx.BoxSizer(wx.HORIZONTAL)
        inner_sizer.Add(lbl_form_field, 3, wx.CENTER, 0)
        inner_sizer.Add(form_field, 4, wx.CENTER, 0)

        self.main_sizer.Add(inner_sizer, 0, wx.ALL|wx.EXPAND, 5)

    def add_button(self, button):
        self.main_sizer.Add(button, 0, wx.ALL|wx.CENTER, 15)

    def add_separator(self):
        separator = wx.StaticLine(self.panel)
        self.main_sizer.Add(separator, 0, wx.ALL|wx.EXPAND, 3)


class ConfigPanel(GenericPanel):

    def __init__(self, parent, label=''):
        GenericPanel.__init__(self, parent, label)

        self.parent = parent

        self.create_controls()
        self.do_layout()
        self.set_defaults()
        self.bind_events()

    def create_controls(self):
        self.spn_camera_index = wx.SpinCtrl(self, max=10, initial=0)
        self.chk_enable_communication = \
            wx.CheckBox(self, label='Enable serial communication')
        self.txt_port_name = wx.TextCtrl(self, value='/dev/usb/ttyUSB0')
        self.spn_polling_time = wx.SpinCtrl(self, min=50, max=1000, initial=200)
        self.chk_enable_log = wx.CheckBox(self, label='Enable console log')

    def do_layout(self):
        self.add_labeled_field('Camera index', self.spn_camera_index)
        self.add_separator()
        self.add_field(self.chk_enable_communication)
        self.add_labeled_field('Port name', self.txt_port_name)
        self.add_labeled_field('Polling time', self.spn_polling_time)
        self.add_separator()
        self.add_field(self.chk_enable_log)

    def set_defaults(self):
        self.update_capture()
        self.enable_communication()
        self.update_port_name()
        self.update_polling_time()
        self.enable_log()

    def bind_events(self):
        self.spn_camera_index.Bind(wx.EVT_SPINCTRL, self.update_capture)
        self.chk_enable_communication.Bind(wx.EVT_CHECKBOX, self.enable_communication)
        self.txt_port_name.Bind(wx.EVT_TEXT, self.update_port_name)
        self.spn_polling_time.Bind(wx.EVT_SPINCTRL, self.update_polling_time)
        self.chk_enable_log.Bind(wx.EVT_CHECKBOX, self.enable_log)

    def update_capture(self, event=None):
        camera_index = self.spn_camera_index.GetValue()
        self.parent.capture = CV.get_capture(camera_index)

    def enable_communication(self, event=None):
        checked_state = self.chk_enable_communication.GetValue()
        self.parent.webcam_timer.send_messages = checked_state

    def update_port_name(self, event=None):
        port_name = self.txt_port_name.GetValue()
        self.parent.communicator.set_port(port_name)

    def update_polling_time(self, event=None):
        value = self.spn_polling_time.GetValue()
        self.parent.webcam_timer.polling_time = value

    def enable_log(self, event=None):
        checked_state = self.chk_enable_log.GetValue()
        self.parent.webcam_timer.show_log_in_console = checked_state


class WebcamTimerPanel(GenericPanel):

    def __init__(self, parent, label=''):
        GenericPanel.__init__(self, parent, label)

        self.parent = parent

        self.create_controls()
        self.do_layout()
        self.bind_events()

    def create_controls(self):
        self.btn_toggle_webcam = wx.Button(self, label='Start')

    def do_layout(self):
        self.add_button(self.btn_toggle_webcam)

    def bind_events(self):
        self.btn_toggle_webcam.Bind(wx.EVT_BUTTON, self.toggle_webcam)

    def toggle_webcam(self, event):
        timer = self.parent.webcam_timer

        if timer.IsRunning():
            timer.stop()
        else:
            timer.start()


class CommandsPanel(GenericPanel):

    def __init__(self, parent, label=''):
        GenericPanel.__init__(self, parent, label)

        self.create_controls()
        self.do_layout()

    def create_controls(self):
        self.cbo_commands = wx.ComboBox(self, choices=[
            'Lock engines',
            'Unlock engines',
        ])
        self.btn_run_command = wx.Button(self, label='Run')

    def do_layout(self):
        self.add_labeled_field('Commands', self.cbo_commands)
        self.add_button(self.btn_run_command)


class RunModePanel(GenericPanel):

    def __init__(self, parent, label=''):
        GenericPanel.__init__(self, parent, label)

        self.create_controls()
        self.do_layout()

    def create_controls(self):
        self.cbo_run_mode = wx.ComboBox(self, choices=[
            'Send robots positions',
            'Acquire control data',
        ])
        self.btn_toggle_continuous_mode = wx.Button(self, label='Start')

    def do_layout(self):
        self.add_labeled_field('Mode', self.cbo_run_mode)
        self.add_button(self.btn_toggle_continuous_mode)


def main():
    app = wx.App()
    frame = MainWindow()
    frame.Centre()
    frame.Show(True)
    app.MainLoop()
