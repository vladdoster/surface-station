#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx

from camera import Camera
from video_view import VideoView


class Frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, size=(640, 480))

        self.camera = Camera(1)
        self.camera.set_resolution(960, 1280)

        self.video_view = VideoView(self, self.capture)
        self.video_view.start()

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.video_view, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(box)
        self.Centre()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def capture(self):
        return self.camera.capture_image(flush=0)

    def on_close(self, event):
        self.video_view.stop()
        event.Skip()


class MyApp(wx.App):
    def OnInit(self):
        frame = Frame(None)
        frame.Show(True)
        return True

app = MyApp(0)
app.MainLoop()
