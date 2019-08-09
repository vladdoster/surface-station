import base64
import io
from datetime import datetime

import wx
from autobahn.twisted import WebSocketClientProtocol


class CameraStreamProtocol(WebSocketClientProtocol):

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory._proto = self
        self.received_images_count = 0
        print("updated ui color")
        # Update websocket info color
        frame = self.factory._app._frame
        frame.rov_panel.camera_status_pnl.SetBackgroundColour("#228B22")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            frame = self.factory._app._frame
            f = io.BytesIO(base64.b64decode(payload))
            if frame.rov_panel.image_viewer.currently_recording_dataset:
                self.received_images_count += 1
                if self.received_images_count % frame.rov_panel.image_viewer.dataset_record_rate == 0:
                    print("Saving image #{}".format(self.received_images_count))
                    # decode the image and save locally
                    with open("{}/{}.jpg".format(frame.rov_panel.image_viewer.record_dataset_to_dir,
                                                 datetime.now().strftime('%Y_%m_%d_%H_%M_%S')),
                              "wb") as image_file:
                        image_file.write(base64.b64decode(payload))
            else:
                self.received_images_count = 0
            frame = self.factory._app._frame

            try:
                img = wx.Image(f, wx.BITMAP_TYPE_ANY)
                frame.rov_panel.image_viewer.raw_camera_stream.SetBitmap(wx.Bitmap(img))
                frame.rov_panel.Refresh()
            except Exception as e:
                pass

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.factory._proto = None
        frame = self.factory._app._frame
        frame.rov_panel.camera_status_pnl.SetBackgroundColour("#ff0000")


class JoystickExecutorProtocol(WebSocketClientProtocol):

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory._proto = self
        # Update websocket info color
        frame = self.factory._app._frame
        frame.rov_panel.joystick_status_pnl.SetBackgroundColour("#228B22")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received, saving to a file")
        frame = self.factory._app._frame
        frame.rov_panel.networking_io.messages.AppendText("{}\n".format(payload))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.factory._proto = None
        frame = self.factory._app._frame
        frame.rov_panel.joystick_status_pnl.SetBackgroundColour("#ff0000")
