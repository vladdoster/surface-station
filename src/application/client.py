"""	 This file is part of Enbarr.
     Enbarr is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 3 of the License, or
     (at your option) any later version.
     Enbarr is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.
     You should have received a copy of the GNU General Public License
     along with Enbarr.  If not, see <https://www.gnu.org/licenses/>.
 """

import json
import os
import time
from subprocess import Popen, PIPE

import wx
import wx.html
########################################################################
from autobahn.twisted import WebSocketClientProtocol, WebSocketClientFactory
from wx.adv import SPLASH_CENTRE_ON_SCREEN, SPLASH_TIMEOUT, SplashScreen, Joystick

from src.application.Joystick import InfoPanel, JoyPanel, POVPanel, AxisPanel, JoyButtons


class AUVPanel(wx.Panel):
    """
    """

    def __init__(self, parent, ):
        wx.Panel.__init__(self, parent, -1)
        #
        # # Try to grab the control. If we get it, capture the stick.
        # # Otherwise, throw up an exception message and play stupid.
        # try:
        #     self.stick = Joystick()
        #     self.stick.SetCapture(self)
        #     # Calibrate our controls
        #     wx.CallAfter(self.Calibrate)
        #     wx.CallAfter(self.OnJoystick)
        # except NotImplementedError as v:
        #     wx.MessageBox(str(v), "Exception Message")
        #     self.stick = None
        #
        # # One Sizer to Rule Them All...
        # sizer = wx.GridBagSizer(2, 2)
        #
        # self.info = InfoPanel(self, self.stick)
        # sizer.Add(self.info, (0, 0), (1, 3), wx.ALL | wx.GROW, 2)
        #
        # self.info.Bind(wx.EVT_BUTTON, self.Calibrate)
        #
        # self.joy = JoyPanel(self, self.stick)
        # sizer.Add(self.joy, (1, 0), (1, 1), wx.ALL | wx.GROW, 2)
        #
        # self.pov = POVPanel(self, self.stick)
        # sizer.Add(self.pov, (1, 1), (1, 2), wx.ALL | wx.GROW, 2)
        #
        # self.axes = AxisPanel(self, self.stick)
        # sizer.Add(self.axes, (2, 0), (1, 3), wx.ALL | wx.GROW, 2)
        #
        # self.buttons = JoyButtons(self, self.stick)
        # sizer.Add(self.buttons, (3, 0), (1, 3), wx.ALL | wx.EXPAND | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL, 1)
        #
        # self.SetSizer(sizer)
        # sizer.Fit(self)
        #
        # # Capture Joystick events (if they happen)
        # self.Bind(wx.EVT_JOYSTICK_EVENTS, self.OnJoystick)
        # self.stick.SetMovementThreshold(10)

    # def Calibrate(self, evt=None):
    #     # Do not try this without a stick
    #     if not self.stick:
    #         return
    #
    #     self.info.Calibrate()
    #     self.axes.Calibrate()
    #     self.pov.Calibrate()
    #     self.buttons.Calibrate()
    #
    # def OnJoystick(self, evt=None):
    #     if not self.stick:
    #         return
    #
    #     self.axes.Update()
    #     self.joy.Update()
    #     self.pov.Update()
    #     if evt is not None and evt.IsButton():
    #         self.buttons.Update()
    #
    # def ShutdownDemo(self):
    #     if self.stick:
    #         self.stick.ReleaseCapture()
    #     self.stick = None


class ROVPanel(wx.Panel):
    """
    """

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
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Networking panel
        networking_controls = wx.StaticBox(panel, -1, 'Networking:')
        nmSizer = wx.StaticBoxSizer(networking_controls, wx.VERTICAL)

        networking_sizer = wx.BoxSizer(wx.HORIZONTAL)

        socket_messages = wx.StaticText(panel, -1, "Socket messages")

        networking_sizer.Add(socket_messages, 0, wx.ALL | wx.TOP, 5)
        self.messages = wx.TextCtrl(panel, size=(300, 150), style=wx.TE_MULTILINE)
        networking_sizer.Add(self.messages, 0, wx.ALL | wx.CENTER, 5)
        self.send_test_message = wx.Button(panel, -1, 'Test message')
        self.send_test_message.Bind(wx.EVT_BUTTON, self.OnClick)

        networking_sizer.Add(self.send_test_message, 0, wx.ALL | wx.CENTER, 5)

        nmSizer.Add(networking_sizer, 0, wx.ALL | wx.CENTER, 10)

        joystick_controls = wx.StaticBox(panel, -1, 'Joystick Controls:')
        sboxSizer = wx.StaticBoxSizer(joystick_controls, wx.VERTICAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(panel, -1, 'ok')

        hbox.Add(okButton, 0, wx.ALL | wx.LEFT, 10)
        cancelButton = wx.Button(panel, -1, 'cancel')

        hbox.Add(cancelButton, 0, wx.ALL | wx.LEFT, 10)

        sizer = wx.GridBagSizer(2, 2)

        self.info = InfoPanel(self, self.stick)
        sizer.Add(self.info, (0, 0), (1, 3), wx.ALL | wx.GROW, 2)

        self.info.Bind(wx.EVT_BUTTON, self.Calibrate)

        self.joy = JoyPanel(self, self.stick)
        sizer.Add(self.joy, (1, 0), (1, 1), wx.ALL | wx.GROW, 2)

        self.pov = POVPanel(self, self.stick)
        sizer.Add(self.pov, (1, 1), (1, 2), wx.ALL | wx.GROW, 2)

        self.axes = AxisPanel(self, self.stick)
        sizer.Add(self.axes, (2, 0), (1, 3), wx.ALL | wx.GROW, 2)

        self.buttons = JoyButtons(self, self.stick)
        sizer.Add(self.buttons, (3, 0), (1, 3), wx.ALL | wx.EXPAND | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL, 1)

        # Capture Joystick events (if they happen)
        self.Bind(wx.EVT_JOYSTICK_EVENTS, self.OnJoystick)
        self.stick.SetMovementThreshold(10)

        # sboxSizer.Add(hbox, 0, wx.ALL | wx.LEFT, 10)
        sboxSizer.Add(sizer)
        vbox.Add(nmSizer, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(sboxSizer, 0, wx.ALL | wx.CENTER, 5)
        panel.SetSizer(vbox)
        self.Centre()
        panel.Fit()

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
        if self.GetParent()._app._factory:
            proto = self.GetParent()._app._factory._proto
            if proto:
                # Send message to server
                evt = {'x': 1, 'y': 1}
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
        self.rov_panel.Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.auv_panel, 1, wx.EXPAND)
        self.sizer.Add(self.rov_panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.createMenuBar()

        # menubar = wx.MenuBar()
        # fileMenu = wx.Menu()
        # switch_panels_menu_item = fileMenu.Append(wx.ID_ANY,
        #                                           "Switch modes")
        # self.Bind(wx.EVT_MENU, self.onSwitchPanels,
        #           switch_panels_menu_item)
        # menubar.Append(fileMenu, '&File')
        # self.SetMenuBar(menubar)

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


class MyClientProtocol(WebSocketClientProtocol):
    """
    Our protocol for WebSocket client connections.
    """

    def onOpen(self):
        print("WebSocket connection open.")

        # the WebSocket connection is open. we store ourselves on the
        # factory object, so that we can access this protocol instance
        # from wxPython, e.g. to use sendMessage() for sending WS msgs
        ##
        self.factory._proto = self
        self._received = 0

    def onMessage(self, payload, isBinary):
        # a WebSocket message was received. now interpret it, possibly
        # accessing the wxPython app `self.factory._app` or our
        # single UI frame `self.factory._app._frame`
        ##
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        self._received += 1
        frame = self.factory._app._frame
        # frame.rov_panel.messages.AppendText("{}\n".format(self._received))
        frame.rov_panel.messages.AppendText("{}\n".format(payload))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

        # the WebSocket connection is gone. clear the reference to ourselves
        # on the factory object. when accessing this protocol instance from
        # wxPython, always check if the ref is None. only use it when it's
        # not None (which means, we are actually connected)
        ##
        self.factory._proto = None


class MyClientFactory(WebSocketClientFactory):
    """
    Our factory for WebSocket client connections.
    """
    protocol = MyClientProtocol

    def __init__(self, url, app):
        WebSocketClientFactory.__init__(self, url)
        self._app = app
        self._proto = None


if __name__ == "__main__":
    import sys
    from twisted.internet import wxreactor

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
    app._factory = None

    app._frame = MainFrame(app)
    timer = wx.Timer()
    time.sleep(5)
    app._frame.Show()
    # app.MainLoop()

    reactor.registerWxApp(app)
    app._factory = MyClientFactory(u"ws://127.0.0.1:9000", app)
    reactor.connectTCP("127.0.0.1", 9000, app._factory)
    reactor.run()