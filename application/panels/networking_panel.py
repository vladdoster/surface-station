import json

import wx


class NetworkingControlPanel(wx.StaticBox):
    def __init__(self, *args, **kwargs):
        super(NetworkingControlPanel, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.panel = wx.StaticBoxSizer(self, wx.VERTICAL)

        # Display containers
        self.networking_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.networking_input_sizer = wx.BoxSizer(wx.VERTICAL)

        # Label
        self.ws_status = wx.StaticText(self.GetParent(), -1, label="Socket messages")

        # Send test message to AUV
        self.send_test_message = wx.Button(self.GetParent(), label="Test message")
        self.send_test_message.Bind(wx.EVT_BUTTON, self.on_test_message_btn_click)

        # Sent/Received messages appended here
        self.messages = wx.TextCtrl(
            self.GetParent(), size=(450, 75), style=wx.TE_MULTILINE
        )

        # Adding parts to respective sizer
        self.networking_input_sizer.Add(
            self.ws_status, 0, wx.ALL | wx.ALIGN_TOP | wx.CENTER, 5
        )
        self.networking_input_sizer.Add(
            self.send_test_message, 0, wx.ALL | wx.CENTER, 5
        )
        self.networking_sizer.Add(self.networking_input_sizer, 0, wx.ALL | wx.CENTER, 5)
        self.networking_sizer.Add(self.messages, 0, wx.ALL | wx.CENTER, 5)

        # Add display containers on panel
        self.panel.Add(self.networking_sizer, 0, wx.ALL | wx.CENTER, 10)

    def on_test_message_btn_click(self, event):
        """Bound on click event to attempt sending a test message to the Joystick ROS Node websocket server"""
        proto = self.GetParent().GetParent().GetParent()._app._joystick_factory._proto
        if proto:
            test_message = {
                "x": 1,
                "y": 1,
                "z": 0.5,
                "r": -0.1,
                "p": 0.2,
                "c": -1,
                "button": 17,
                "checksum": 987,
            }
            msg = json.dumps(test_message).encode("utf8")
            # Send message to server
            proto.sendMessage(msg)
            self.messages.AppendText("Sending to server: {}\n".format(msg))
        else:
            # Make user aware of possible connection issue
            self.messages.AppendText("Check websocket connection\n")
