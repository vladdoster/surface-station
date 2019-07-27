import json

import wx


# Networking panel
class NetworkingControlPanel(wx.StaticBox):

    def __init__(self, *args, **kwargs):
        super(NetworkingControlPanel, self).__init__(*args, **kwargs)
        self.panel = wx.StaticBoxSizer(self, wx.VERTICAL)
        self.networking_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.ws_status = wx.StaticText(self.GetParent(), -1, label='Socket messages')
        self.networking_input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.send_test_message = wx.Button(self.GetParent(), label='Test message')
        self.send_test_message.Bind(wx.EVT_BUTTON, self.on_test_message_btn_click)

        self.messages = wx.TextCtrl(self.GetParent(), size=(450, 75), style=wx.TE_MULTILINE)
        self.networking_input_sizer.Add(self.ws_status, 0, wx.ALL | wx.ALIGN_TOP | wx.CENTER, 5)
        self.networking_input_sizer.Add(self.send_test_message, 0, wx.ALL | wx.CENTER, 5)

        # networking_sizer.Add(ws_status, 0, wx.ALL | wx.TOP, 5)
        self.networking_sizer.Add(self.networking_input_sizer, 0, wx.ALL | wx.CENTER, 5)
        self.networking_sizer.Add(self.messages, 0, wx.ALL | wx.CENTER, 5)
        self.panel.Add(self.networking_sizer, 0, wx.ALL | wx.CENTER, 10)

    def on_test_message_btn_click(self, event):
        if self.GetParent().GetParent().GetParent()._app._joystick_factory:
            proto = self.GetParent().GetParent().GetParent()._app._joystick_factory._proto
            if proto:
                # Send message to server
                evt = {'x': 1, 'y': 1, 'z': .5, 'r': -.1, 'p': .2, 'c': -1,
                       'button': 17, 'checksum': 987}
                msg = json.dumps(evt).encode('utf8')
                proto.sendMessage(msg)
                # Update UI
                self.messages.AppendText("Sending to server: {}\n".format(msg))
            else:
                self.messages.AppendText("Check websocket connection\n")
