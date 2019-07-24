import json

import wx


class WebsocketStatusPanel(wx.StaticBox):
    def __init__(self, *args, **kwargs):
        super(WebsocketStatusPanel, self).__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        # container
        websocket_status_sizer = wx.StaticBoxSizer(self, wx.VERTICAL)
        # horizontal container
        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ws_status = wx.StaticText()
        horizontal_sizer.Add(ws_status, 0, wx.ALL | wx.TOP, 5)
        pnl = wx.Panel(self)
        # set color addressable panel
        self.col = wx.Colour(0, 0, 0)
        self.cpnl  = wx.Panel(self, size=(20, 20))
        self.cpnl.SetBackgroundColour(self.col)
        horizontal_sizer.Add(self.cpnl, 0, wx.ALL | wx.CENTER, 5)
        websocket_status_sizer.Add(horizontal_sizer, 0, wx.ALL | wx.CENTER, 10)
