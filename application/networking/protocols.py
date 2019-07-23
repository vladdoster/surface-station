import base64

from autobahn.twisted import WebSocketClientProtocol


class CameraStreamProtocol(WebSocketClientProtocol):

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory._proto = self

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received, saving to a file")

            # decode the image and save locally
            with open("image_received.jpg", "wb") as image_file:
                image_file.write(base64.b64decode(payload))

            frame = self.factory._app._frame
            # frame.rov_panel.messages.AppendText("{}\n".format(self._received))
            frame.rov_panel.messages.AppendText("Image written to disk\n")
        # try:
        #     f = io.BytesIO(base64.b64decode(payload))
        #     pilimage = Image.open(f)
        # except Exception as e:
        #     pass

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.factory._proto = None


class JoystickExecutorProtocol(WebSocketClientProtocol):

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory._proto = self

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received, saving to a file")

        frame = self.factory._app._frame
        # frame.rov_panel.messages.AppendText("{}\n".format(self._received))
        frame.rov_panel.messages.AppendText("{}\n".format(payload))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.factory._proto = None


