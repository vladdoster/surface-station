import os
import time

import wx
import wx.html
from wx.adv import SPLASH_CENTRE_ON_SCREEN, SPLASH_TIMEOUT, SplashScreen

from networking.factories import ClientFactory
from networking.protocols import CameraStreamProtocol, JoystickExecutorProtocol
from panels.menu_bar import MenuBar
from panels.rov_panel import ROVPanel
from wx.adv import SPLASH_CENTRE_ON_SCREEN, SPLASH_TIMEOUT, SplashScreen

global container_id, log


class MainFrame(wx.Frame):
    def __init__(self, app):
        self.frame_number = 1
        frame = wx.Frame.__init__(self, None, wx.ID_ANY, "Enbarr")
        self._app = app
        # Loading screen
        bmp = wx.Image("images/enbarr.png").ConvertToBitmap()
        SplashScreen(bmp, SPLASH_CENTRE_ON_SCREEN | SPLASH_TIMEOUT, 1000, None, -1)

        wx.SafeYield()
        global log

        # Menu bar
        menu_bar = MenuBar()
        self.SetMenuBar(menu_bar)

        # ROV panel
        self.rov_panel = ROVPanel(self, log=log)

        # Frame sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.rov_panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)


if __name__ == "__main__":
    import sys
    from twisted.internet import wxreactor
    import sys

    global log
    from twisted.python import log

    log.startLogging(sys.stdout)

    wxreactor.install()
    from twisted.internet import reactor

    print(
        """

                ######## ##    ## ########     ###    ########  ########
                ##       ###   ## ##     ##   ## ##   ##     ## ##     ##
                ##       ####  ## ##     ##  ##   ##  ##     ## ##     ##
                ######   ## ## ## ########  ##     ## ########  ########
                ##       ##  #### ##     ## ######### ##   ##   ##   ##
                ##       ##   ### ##     ## ##     ## ##    ##  ##    ##
                ######## ##    ## ########  ##     ## ##     ## ##     ##

                                 ######   ##     ## ####
                                ##    ##  ##     ##  ##
                                ##        ##     ##  ##
                                ##   #### ##     ##  ##
                                ##    ##  ##     ##  ##
                                ##    ##  ##     ##  ##
                                 ######    #######  ####

                """
    )
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/vlad/Downloads/Enbarr-9a739a9422cc.json"
    app = wx.App(False)
    app._camera_factory = None
    app._joystick_factory = None

    app._frame = MainFrame(app)
    timer = wx.Timer()
    time.sleep(1)
    app._frame.Show()
    reactor.registerWxApp(app)

    simmode = False
    if simmode:
        print("Note: Simulation mode is true, we're running locally!")
        # Create factory (singleton connection pattern)
        app._camera_factory = ClientFactory(
            "ws://127.0.0.1:9000", app, protocol=CameraStreamProtocol
        )
        app._joystick_factory = ClientFactory(
            "ws://127.0.0.1:9001", app, protocol=JoystickExecutorProtocol
        )
        # Connect to host
        reactor.connectTCP("127.0.0.1", 9000, app._camera_factory)
        reactor.connectTCP("127.0.0.1", 9001, app._joystick_factory)
    else:
        print("Note: Simulation mode is false, we're looking for the actual robot!")
        # Create factory (singleton connection pattern)
        app._camera_factory = ClientFactory(
            "ws://enbarr.local:9000", app, protocol=CameraStreamProtocol
        )
        app._joystick_factory = ClientFactory(
            "ws://enbarr.local:9001", app, protocol=JoystickExecutorProtocol
        )
        # Connect to host
        reactor.connectTCP("enbarr.local", 9000, app._camera_factory)
        reactor.connectTCP("enbarr.local", 9001, app._joystick_factory)

    # Start twisted event loop
    reactor.run()
