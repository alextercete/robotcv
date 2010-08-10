import wx

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


class WarningDialog(wx.MessageDialog):

    def __init__(self, message):
        wx.MessageDialog.__init__(self, None, message, caption='Warning',
                                  style=wx.OK|wx.ICON_EXCLAMATION)

        self.ShowModal()
