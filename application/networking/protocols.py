import base64
import io
from datetime import datetime

import cv2
import numpy as np
import wx
from autobahn.twisted import WebSocketClientProtocol
from google.cloud import automl_v1beta1
from google.protobuf.json_format import MessageToDict


class CameraStreamProtocol(WebSocketClientProtocol):

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory._proto = self
        self.received_images_count = 0
        print("updated ui color")
        # Update websocket info color
        frame = self.factory._app._frame
        frame.rov_panel.camera_status_pnl.SetBackgroundColour("#228B22")

    def get_prediction(self, content, project_id, model_id):
        prediction_client = automl_v1beta1.PredictionServiceClient()
        name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
        payload = {'image': {'image_bytes': base64.b64decode(content)}}
        params = {}
        request = prediction_client.predict(name, payload, params)
        return request

    def process_image_cloud_ml(self, content, project_id, model_id):
        try:
            predictions = self.get_prediction(content, project_id, model_id)
            response = MessageToDict(predictions, preserving_proto_field_name=True)
            ref_point = []
            # content = base64.b64decode(content)
            content = base64.b64decode(content)
            im_arr = np.asarray(content)
            # convert rgb array to opencv's bgr format
            im_arr_bgr = cv2.cvtColor(im_arr, cv2.COLOR_RGB2BGR)
            # pts1 and pts2 are the upper left and bottom right coordinates of the rectangle
            cv2.rectangle(im_arr_bgr, pts1, pts2,
                          color=(0, 255, 0), thickness=3)
            im_arr = cv2.cvtColor(im_arr_bgr, cv2.COLOR_BGR2RGB)
            # convert back to Image object
            im = Image.fromarray(im_arr)
            for x in response["payload"]:
                print(x["display_name"])
                print(x["image_object_detection"]["bounding_box"]["normalized_vertices"])
            #     # coords = []
            #     # for coordinates in x["image_object_detection"]["bounding_box"]["normalized_vertices"]:
            #     #     try:
            #     #         x = int(coordinates["x"] * 320)
            #     #     except Exception as e:
            #     #         x = 0
            #     #     try:
            #     #         y = int(coordinates["y"] * 280)
            #     #     except Exception as e:
            #     #         y = 0
            #     #     coords.append((int(x), int(y)))
            #     # print(coords)
            #     # cv2.circle(content, (18, 123), 3, (0, 255, 0), -1)
            #     # cv2.rectangle(content, (384, 0), (510, 128), (0, 255, 0), 3)
            #     # cv2.rectangle(content, coords[0], coords[1], (0, 255, 0), 2)
            #     cv2.rectangle(img, 15, 200, 5, 15)
            return content
        except Exception as e:
            print("No coral detected, is your camera pointing the right way?")
            print("{}".format(e))
            return content

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
                # print("Dataset generator active at {} with {} images received".format(
                #     frame.rov_panel.image_viewer.record_dataset_to_dir, self.received_images_count))
            else:
                self.received_images_count = 0
            # image_np = cv2.imdecode(payload, cv2.IMREAD_COLOR)
            # f = self.process_image_cloud_ml(payload, 1070726212812, "IOD8268142722922053632")
            frame = self.factory._app._frame
            # frame.rov_panel.messages.AppendText("{}\n".format(self._received))
            # frame.rov_panel.networking_io.messages.AppendText("Image written to disk\n")

            # Srt image panel with camera stream
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
