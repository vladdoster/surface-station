#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import time
from subprocess import Popen, PIPE

import wx
import wx.html
from autobahn.twisted import WebSocketClientProtocol, WebSocketClientFactory
from joystick import POVPanel, JoyButtons, InfoPanel, AxisPanel, JoyPanel
from wx.adv import SPLASH_CENTRE_ON_SCREEN, SPLASH_TIMEOUT, SplashScreen, Joystick
from auv_panel import AUVPanel
from rov_panel import ROVPanel


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
            self.rov_panel.Show()
            self.auv_panel.Hide()
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
