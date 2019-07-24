import json
import os
import time
from subprocess import Popen, PIPE

import wx
import wx.html
from wx.adv import SPLASH_CENTRE_ON_SCREEN, SPLASH_TIMEOUT, SplashScreen, Joystick

from joystick import InfoPanel, JoyPanel, POVPanel, AxisPanel, JoyButtons
from networking.factories import MyClientFactory
from networking.protocols import CameraStreamProtocol, JoystickExecutorProtocol


class AUVPanel(wx.Panel):

    def __init__(self, parent, ):
        wx.Panel.__init__(self, parent, -1)


class ROVPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""
        super(ROVPanel, self).__init__(parent)

        try:
            self.stick = Joystick()
            self.stick.SetCapture(self)
            # Calibrate our controls
            wx.CallAfter(self.Calibrate)
            wx.CallAfter(self.OnJoystick)
        except NotImplementedError as v:
            wx.MessageBox(str(v), "Exception Message")
            self.stick = None

        panel = wx.Panel(self)
        panel_vbox = wx.BoxSizer(wx.VERTICAL)
        websocket_and_networking_hbox = wx.BoxSizer(wx.HORIZONTAL)
        ######################################
        ## Websocket status information panel
        ######################################
        websocket_status_static_box = wx.StaticBox(panel, -1, 'Websockets info:')
        websocket_status_sizer = wx.StaticBoxSizer(websocket_status_static_box, wx.HORIZONTAL)

        ws_camera_sizer = wx.BoxSizer(wx.VERTICAL)
        camera_connection_title = wx.StaticText(panel, -1, "Camera")
        # set color addressable panel
        self.camera_status_pnl_col = wx.Colour(0, 0, 0)
        self.camera_status_pnl = wx.Panel(panel, size=(20, 20))
        self.camera_status_pnl.SetBackgroundColour(self.camera_status_pnl_col)
        ws_camera_sizer.Add(camera_connection_title, 0, wx.ALL | wx.TOP, 5)
        ws_camera_sizer.Add(self.camera_status_pnl, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        ws_joystick_sizer = wx.BoxSizer(wx.VERTICAL)
        joystick_connection_title = wx.StaticText(panel, -1, "Joystick")
        self.joystick_status_pnl_col = wx.Colour(0, 0, 0)
        self.joystick_status_pnl = wx.Panel(panel, size=(20, 20))
        self.joystick_status_pnl.SetBackgroundColour(self.joystick_status_pnl_col)
        ws_joystick_sizer.Add(joystick_connection_title, 0, wx.ALL | wx.TOP, 5)
        ws_joystick_sizer.Add(self.joystick_status_pnl, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        websocket_status_sizer.Add(ws_joystick_sizer, 0, wx.ALL | wx.TOP, 5)
        websocket_status_sizer.Add(ws_camera_sizer, 0, wx.ALL | wx.TOP, 5)

        ######################################
        ## Networking panel
        ######################################
        networking_controls = wx.StaticBox(panel, -1, 'Networking:')
        networking_io_sizer = wx.StaticBoxSizer(networking_controls, wx.VERTICAL)
        networking_sizer = wx.BoxSizer(wx.HORIZONTAL)

        ws_status = wx.StaticText(panel, -1, "Socket messages")
        networking_input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.send_test_message = wx.Button(panel, -1, 'Test message')
        self.send_test_message.Bind(wx.EVT_BUTTON, self.OnClick)

        self.messages = wx.TextCtrl(panel, size=(450, 75), style=wx.TE_MULTILINE)
        networking_input_sizer.Add(ws_status, 0, wx.ALL | wx.ALIGN_TOP | wx.CENTER, 5)
        networking_input_sizer.Add(self.send_test_message, 0, wx.ALL | wx.CENTER, 5)

        # networking_sizer.Add(ws_status, 0, wx.ALL | wx.TOP, 5)
        networking_sizer.Add(networking_input_sizer, 0, wx.ALL | wx.CENTER, 5)
        networking_sizer.Add(self.messages, 0, wx.ALL | wx.CENTER, 5)
        networking_io_sizer.Add(networking_sizer, 0, wx.ALL | wx.CENTER, 10)

        ######################################
        ## Image panel
        ######################################
        image_viewing_static_box = wx.StaticBox(panel, -1, 'Image info:')
        image_viewing_sizer = wx.StaticBoxSizer(image_viewing_static_box, wx.HORIZONTAL)
        img = wx.Image(320, 240)
        self.raw_camera_stream = wx.StaticBitmap(panel, wx.ID_ANY,
                                         wx.BitmapFromImage(img))
        processed_img = wx.Image(320, 240)
        self.processed_image_stream = wx.StaticBitmap(panel, wx.ID_ANY,
                                                 wx.BitmapFromImage(processed_img))
        image_viewing_sizer.Add(self.raw_camera_stream, 0, wx.ALL)
        image_viewing_sizer.Add(self.processed_image_stream, 0, wx.ALL)


        ######################################
        ## Joystick panel
        ######################################
        joystick_controls = wx.StaticBox(panel, -1, 'Joystick Controls:')
        joystick_main_sizer = wx.StaticBoxSizer(joystick_controls, wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        joystick_grid_sizer = wx.GridBagSizer(2, 2)
        self.info = InfoPanel(self, self.stick)
        joystick_grid_sizer.Add(self.info, (0, 0), (1, 3), wx.ALL | wx.GROW, 2)
        self.info.Bind(wx.EVT_BUTTON, self.Calibrate)
        self.joy = JoyPanel(self, self.stick)
        joystick_grid_sizer.Add(self.joy, (1, 0), (1, 1), wx.ALL | wx.GROW, 2)
        self.pov = POVPanel(self, self.stick)
        joystick_grid_sizer.Add(self.pov, (1, 1), (1, 2), wx.ALL | wx.GROW, 2)
        self.axes = AxisPanel(self, self.stick)
        joystick_grid_sizer.Add(self.axes, (2, 0), (1, 3), wx.ALL | wx.GROW, 2)
        self.buttons = JoyButtons(self, self.stick)
        joystick_grid_sizer.Add(self.buttons, (3, 0), (1, 3),
                                wx.ALL | wx.EXPAND | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL, 1)
        # Capture Joystick events (if they happen)
        self.Bind(wx.EVT_JOYSTICK_EVENTS, self.OnJoystick)
        self.stick.SetMovementThreshold(10)
        joystick_main_sizer.Add(joystick_grid_sizer)

        # Add everything to main panel
        websocket_and_networking_hbox.Add(websocket_status_sizer, 0, wx.ALL | wx.CENTER, 5)
        websocket_and_networking_hbox.Add(networking_io_sizer, 0, wx.ALL | wx.CENTER, 5)
        panel_vbox.Add(websocket_and_networking_hbox, 0, wx.ALL | wx.CENTER, 5)
        panel_vbox.Add(image_viewing_sizer, 0, wx.ALL | wx.CENTER, 5)
        panel_vbox.Add(joystick_main_sizer, 0, wx.ALL | wx.CENTER, 5)
        panel.SetSizer(panel_vbox)
        self.Centre()
        panel.Fit()

    def add_networking_panel(self, evt=None):
        pass

    def Calibrate(self, evt=None):
        # Do not try this without a stick
        if not self.stick:
            return

        self.info.Calibrate()
        self.axes.Calibrate()
        self.pov.Calibrate()
        self.buttons.Calibrate()

    def OnJoystick(self, evt=None):
        if not self.stick:
            return

        self.axes.Update()
        self.joy.Update()
        self.pov.Update()
        if evt is not None and evt.IsButton():
            self.buttons.Update()

    def ShutdownDemo(self):
        if self.stick:
            self.stick.ReleaseCapture()
        self.stick = None

    def OnClick(self, event):
        if self.GetParent()._app._joystick_factory:
            proto = self.GetParent()._app._joystick_factory._proto
            if proto:
                # Send message to server
                evt = {'x': 1, 'y': 1, 'z': .5, 'r': -.1, 'p': .2, 'c': -1,
                       'button': 17, 'checksum': 987}
                msg = json.dumps(evt).encode('utf8')
                proto.sendMessage(msg)
                # Update UI
                self.messages.AppendText("Sending to server: {}\n".format(msg))


class MenuBar(wx.MenuBar):
    def __init__(self, parent):
        wx.MenuBar.__init__(self, parent=parent)
        fileMenu = wx.Menu()
        switch_panels_menu_item = fileMenu.Append(wx.ID_ANY,
                                                  "Switch modes")
        parent.Bind(wx.EVT_MENU, self.onSwitchPanels,
                    switch_panels_menu_item)
        self.Append(fileMenu, '&File')


class MainFrame(wx.Frame):

    # ----------------------------------------------------------------------
    def __init__(self, app):
        self.frame_number = 1
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Enbarr")
        self._app = app
        # Loading screen
        bmp = wx.Image("enbarr.png").ConvertToBitmap()
        SplashScreen(bmp, SPLASH_CENTRE_ON_SCREEN | SPLASH_TIMEOUT,
                     5000, None, -1)

        wx.SafeYield()
        self.auv_panel = AUVPanel(self)
        self.rov_panel = ROVPanel(self)
        self.auv_panel.Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.auv_panel, 1, wx.EXPAND)
        self.sizer.Add(self.rov_panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.createMenuBar()

    def menuData(self):
        return (("&File",
                 ("&Switch Mode", "Switch operation mode", self.onSwitchPanels),
                 ("&Quit", "Quit", self.OnCloseWindow)),
                ("&Options",
                 ("&Upload Model", "Upload a ML model", self.UploadModel),
                 ("", "", ""),
                 ("&Documentation", "Show documentation", self.OnDocumentation)))

    def createMenuBar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1:]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)

    def createMenu(self, menuData):
        menu = wx.Menu()
        for eachLabel, eachStatus, eachHandler in menuData:
            if not eachLabel:
                menu.AppendSeparator()
                continue
            menuItem = menu.Append(-1, eachLabel, eachStatus)
            self.Bind(wx.EVT_MENU, eachHandler, menuItem)
        return menu

    # ----------------------------------------------------------------------
    def onSwitchPanels(self, event):
        """"""
        if self.auv_panel.IsShown():
            self.SetTitle("ROV Controls Showing")
            self.auv_panel.Hide()
            self.rov_panel.Show()
        else:
            self.SetTitle("AUV Controls Showing")
            self.auv_panel.Show()
            self.rov_panel.Hide()
        self.Layout()

    # Empty event handlers needs to compile
    def UploadModel(self, event):
        pass

    def OnOptions(self, event):
        pass

    def OnCloseWindow(self, event):
        self.Destroy()

    def OnDocumentation(self, event):
        try:
            browser = os.environ.get('BROWSER')
            doc_url = 'https://vdoster.com'
            process = Popen([browser, doc_url], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            print(stdout)
        except KeyError as e:
            print("No browser env var set, creating popup")


if __name__ == "__main__":
    import sys
    from twisted.internet import wxreactor
    import sys

    from twisted.python import log

    wxreactor.install()
    from twisted.internet import reactor
    from twisted.python import log

    log.startLogging(sys.stdout)
    print("""

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

                """)
    app = wx.App(False)
    app._camera_factory = None
    app._joystick_factory = None

    app._frame = MainFrame(app)
    timer = wx.Timer()
    time.sleep(5)
    app._frame.Show()
    reactor.registerWxApp(app)

    # Create factory (singleton connection pattern)
    app._camera_factory = MyClientFactory(u"ws://127.0.0.1:9000", app, protocol=CameraStreamProtocol)
    app._joystick_factory = MyClientFactory(u"ws://127.0.0.1:9001", app, protocol=JoystickExecutorProtocol)
    # Connect to host
    reactor.connectTCP("127.0.0.1", 9000, app._camera_factory)
    reactor.connectTCP("127.0.0.1", 9001, app._joystick_factory)
    # Start twisted event loop
    reactor.run()
