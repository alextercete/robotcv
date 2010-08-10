import wx

from common import GenericPanel, WarningDialog
from .commands_manager import CommandsManager
from .commands import *

LABEL_START = 'Start'
LABEL_STOP = 'Stop'

class MainWindow(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title='RobotCV', size=(550, 450))

        # Initializes the webcam timer
        self.webcam_timer = WebcamTimer(self)

        # Initializes the commands manager
        self.commands_manager = CommandsManager()

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

        parent.Bind(wx.EVT_TIMER, self.main_loop, self)

    def start(self):
        self.parent.commands_manager.log('Starting webcam timer...')
        self.Start(self.polling_time)
        self.parent.webcam_timer_panel.btn_toggle_webcam.SetLabel(LABEL_STOP)

    def stop(self):
        self.Stop()
        self.parent.webcam_timer_panel.btn_toggle_webcam.SetLabel(LABEL_START)
        self.parent.commands_manager.log('Webcam timer stopped!')

    def main_loop(self, event):
        self.parent.commands_manager.run_iteration()


class ConfigPanel(GenericPanel):

    def __init__(self, parent, label=''):
        GenericPanel.__init__(self, parent, label)

        self.commands_manager = parent.commands_manager
        self.webcam_timer = parent.webcam_timer

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
        self.commands_manager.set_webcam_capture(camera_index)

    def enable_communication(self, event=None):
        checked_state = self.chk_enable_communication.GetValue()
        self.commands_manager.send_messages = checked_state

    def update_port_name(self, event=None):
        port_name = self.txt_port_name.GetValue()
        self.commands_manager.set_serial_port(port_name)

    def update_polling_time(self, event=None):
        value = self.spn_polling_time.GetValue()
        self.webcam_timer.polling_time = value

    def enable_log(self, event=None):
        checked_state = self.chk_enable_log.GetValue()
        self.commands_manager.show_log_in_console = checked_state


class WebcamTimerPanel(GenericPanel):

    def __init__(self, parent, label=''):
        GenericPanel.__init__(self, parent, label)

        self.parent = parent

        self.create_controls()
        self.do_layout()
        self.bind_events()

    def create_controls(self):
        self.btn_toggle_webcam = wx.Button(self, label=LABEL_START)

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

        self.parent = parent

        self.create_controls()
        self.do_layout()
        self.bind_events()

    def create_controls(self):
        self.cbo_commands = wx.ComboBox(self, choices=[
            'Lock engines',
            'Unlock engines',
        ])
        self.btn_run_command = wx.Button(self, label='Run')

    def do_layout(self):
        self.add_labeled_field('Commands', self.cbo_commands)
        self.add_button(self.btn_run_command)

    def bind_events(self):
        self.btn_run_command.Bind(wx.EVT_BUTTON, self.run_command)

    def run_command(self, event):
        try:
            command = {
                0: LOCK_ENGINES,
                1: UNLOCK_ENGINES,
            }[self.cbo_commands.GetCurrentSelection()]
        except KeyError:
            WarningDialog('You must select a command')
        else:
            if self.parent.webcam_timer.IsRunning():
                self.parent.commands_manager.add_command(command)
            else:
                WarningDialog('Webcam timer must be running!')


class RunModePanel(GenericPanel):

    def __init__(self, parent, label=''):
        GenericPanel.__init__(self, parent, label)

        self.parent = parent

        self.create_controls()
        self.do_layout()
        self.bind_events()

    def create_controls(self):
        self.cbo_run_modes = wx.ComboBox(self, choices=[
            'Send robots positions',
            'Acquire control data',
        ])
        self.btn_toggle_run_mode = wx.Button(self, label=LABEL_START)

    def do_layout(self):
        self.add_labeled_field('Mode', self.cbo_run_modes)
        self.add_button(self.btn_toggle_run_mode)

    def bind_events(self):
        self.btn_toggle_run_mode.Bind(wx.EVT_BUTTON, self.toggle_run_mode)

    def toggle_run_mode(self, event):
        commands_manager = self.parent.commands_manager
        combobox = self.cbo_run_modes
        button = self.btn_toggle_run_mode

        if commands_manager.continuous_run_mode == IDLE:
            try:
                run_mode = {
                    0: SEND_ROBOTS_POSITIONS,
                    1: ACQUIRE_CONTROL_DATA,
                }[combobox.GetCurrentSelection()]
            except KeyError:
                WarningDialog('You must select a run mode')
            else:
                commands_manager.set_run_mode(run_mode)
                combobox.Enable(False)
                button.SetLabel(LABEL_STOP)
        else:
            commands_manager.set_run_mode(IDLE)
            combobox.Enable(True)
            button.SetLabel(LABEL_START)
