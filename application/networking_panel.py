import json

import wx
# Networking panel


class NetworkingControlPanel(wx.StaticBox):
    def __init__(self, *args, **kwargs):
        super(NetworkingControlPanel, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        network_controls_sizer = wx.StaticBoxSizer(self, wx.VERTICAL)
        messages_sizer = wx.BoxSizer(wx.HORIZONTAL)
        socket_messages = wx.StaticText()
        messages_sizer.Add(socket_messages, 0, wx.ALL | wx.TOP, 5)
        self.messages = wx.TextCtrl(size=(960, 1280), style=wx.TE_MULTILINE)
        messages_sizer.Add(self.messages, 0, wx.ALL | wx.CENTER, 5)

        self.send_test_message = wx.Button()
        self.send_test_message.Bind(wx.EVT_BUTTON, self.on_click)

        messages_sizer.Add(self.send_test_message, 0, wx.ALL | wx.CENTER, 5)
        network_controls_sizer.Add(messages_sizer, 0, wx.ALL | wx.CENTER, 10)

    def on_click(self, event):
        if self.GetParent()._app._factory:
            proto = self.GetParent()._app._factory._proto
            if proto:
                # Send message to server
                evt = {'roll': 1.0, 'pitch': 1.0, 'yaw': 1.0, 'x': 1, 'y': 1, 'z': 1}
                msg = json.dumps(evt).encode('utf8')
                proto.sendMessage(msg)
                # Update UI
                self.messages.AppendText("Sending to server: {}\n".format(msg))