#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import wx

from joystick import POVPanel, JoyButtons, InfoPanel, AxisPanel, JoyPanel, Joystick


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
        # TODO: Refactor this to individual panels to compose together
        # Networking panel
        # networking_controls = NetworkingControlPanel(panel, -1, 'Networking')
        networking_controls = wx.StaticBox(panel, -1, 'Networking:')
        network_sizer = wx.StaticBoxSizer(networking_controls, wx.VERTICAL)

        networking_internal_sizer = wx.BoxSizer(wx.HORIZONTAL)

        socket_messages = wx.StaticText(panel, -1, "Socket messages")

        networking_internal_sizer.Add(socket_messages, 0, wx.ALL | wx.TOP, 5)
        self.messages = wx.TextCtrl(panel, size=(300, 150), style=wx.TE_MULTILINE)
        networking_internal_sizer.Add(self.messages, 0, wx.ALL | wx.CENTER, 5)
        self.send_test_message = wx.Button(panel, -1, 'Test message')
        self.send_test_message.Bind(wx.EVT_BUTTON, self.OnClick)

        networking_internal_sizer.Add(self.send_test_message, 0, wx.ALL | wx.CENTER, 5)

        network_sizer.Add(networking_internal_sizer, 0, wx.ALL | wx.CENTER, 10)

        # Joystick
        joystick_controls = wx.StaticBox(panel, -1, 'Joystick Controls:')
        joystick_main_sizer = wx.StaticBoxSizer(joystick_controls, wx.VERTICAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
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

        joystick_main_sizer.Add(sizer)

        # vbox.Add(network_sizer, 0, wx.ALL | wx.CENTER, 5)

        vbox.Add(network_sizer, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(joystick_main_sizer, 0, wx.ALL | wx.CENTER, 5)


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
        # Socket logic
        if self.GetParent()._app._factory:
            proto = self.GetParent()._app._factory._proto
            if proto:
                # Send message to server
                evt = {'roll': 1.0, 'pitch': 1.0, 'yaw': 1.0, 'x': 1.0, 'y': 1.0, 'z': 1.0}
                msg = json.dumps(evt).encode('utf8')
                proto.sendMessage(msg)
                # Update UI
                self.messages.AppendText("Sending to server: {}\n".format(msg))

    def ShutdownDemo(self):
        if self.stick:
            self.stick.ReleaseCapture()
        self.stick = None

    def OnClick(self, event):
        if self.GetParent()._app._factory:
            proto = self.GetParent()._app._factory._proto
            if proto:
                # Send message to server
                evt = {'roll': 1.0, 'pitch': 1.0, 'yaw': 1.0, 'x': 1, 'y': 1, 'z': 1}
                msg = json.dumps(evt).encode('utf8')
                proto.sendMessage(msg)
                # Update UI
                self.messages.AppendText("Sending to server: {}\n".format(msg))
