# -*- coding: utf-8 -*-

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from time import sleep
from threading import Thread, Event

from image_view import ImageView


class StoppableThread(Thread):

    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.stop_event = Event()

    def stop(self):
        if self.isAlive():
            self.stop_event.set()
            self.join()


class IntervalTimer(StoppableThread):

    def __init__(self, interval, worker_func):
        StoppableThread.__init__(self)
        self._interval = interval
        self._worker_func = worker_func

    def run(self):
        while not self.stop_event.is_set():
            self._worker_func()
            sleep(self._interval)


class VideoView(ImageView):

    def __init__(self, parent, callback=None,
                 size=(-1, -1), black=False):
        ImageView.__init__(self, parent, size=size, black=black)

        self.callback = callback
        self.interval = IntervalTimer(0.07, self.player)

    def player(self):
        if self.callback is not None:
            frame = self.callback()
            wx.CallAfter(self.set_frame, frame)

    def start(self):
        self.interval.start()

    def stop(self):
        self.interval.stop()
        self.hide = True
        self.set_default_image()
