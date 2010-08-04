import wx
from controls import MainWindow

def main():
    app = wx.App()
    frame = MainWindow()
    frame.Centre()
    frame.Show(True)
    app.MainLoop()
