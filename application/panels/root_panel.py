import time

import config
import wx
import wx.html
from panels.menu_bar import MenuBar
from panels.rov_panel import ROVPanel
from wx.adv import SPLASH_CENTRE_ON_SCREEN, SPLASH_TIMEOUT, SplashScreen


class RootFrame(wx.Frame):
    def __init__(self, app, log):
        self.frame_number = 1
        frame = wx.Frame.__init__(self, None, wx.ID_ANY, "Enbarr")
        self._app = app
        self.display_splash_screen()
        wx.SafeYield()

        # Menu bar
        menu_bar = MenuBar()
        self.SetMenuBar(menu_bar)

        # ROV panel
        self.rov_panel = ROVPanel(self, log=log)

        # Frame sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.rov_panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

    def display_splash_screen(self):
        bmp = wx.Image("assets/enbarr.png").ConvertToBitmap()
        SplashScreen(bmp, SPLASH_CENTRE_ON_SCREEN | SPLASH_TIMEOUT, config.splash_screen_timeout, None, -1)
        time.sleep(config.splash_screen_timeout / 1000)
        self.Show()
