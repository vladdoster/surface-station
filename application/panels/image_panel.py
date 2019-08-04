import glob
import os

import cv2
import wx
from cv2 import rectangle
from google.cloud import automl_v1beta1
from google.protobuf.json_format import MessageToDict


class ImageStreamPanel(wx.StaticBox):

    def __init__(self, *args, **kwargs):
        super(ImageStreamPanel, self).__init__(*args, **kwargs)
        self.currently_recording_dataset = False
        self.init_ui()

    def init_ui(self):

        # Image Stream info box
        ######################################
        self.panel = wx.StaticBoxSizer(self, wx.HORIZONTAL)

        # Stream options input
        ######################################
        self.data_set_creator_input_panel = wx.StaticBox(self.GetParent(), label="Dataset Creator")
        self.data_set_creator_input_sizer = wx.StaticBoxSizer(self.data_set_creator_input_panel, wx.VERTICAL)

        # Start recording btn
        self.start_data_set_creator_btn = wx.Button(self.GetParent().GetParent(), label='Start recording')
        self.start_data_set_creator_btn.Bind(wx.EVT_BUTTON, self.start_dataset_creation)

        # Process latest dataset
        self.process_latest_dataset_btn = wx.Button(self.GetParent().GetParent(), label="Process dataset")
        self.process_latest_dataset_btn.Bind(wx.EVT_BUTTON, self.batch_process)
        # Disabled by default
        self.process_latest_dataset_btn.Disable()
        self.dir_to_process_label = wx.StaticText(self.GetParent(), -1, "Dataset to process")
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        font.SetUnderlined(True)
        self.dir_to_process_label.SetFont(font=font)
        self.dir_to_process_value = wx.StaticText(self.GetParent(), -1, "N/A")

        self.num_images_to_process_label = wx.StaticText(self.GetParent(), -1, "Number of images")
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        font.SetUnderlined(True)
        self.num_images_to_process_label.SetFont(font=font)
        self.num_images_to_process_value = wx.StaticText(self.GetParent(), -1, "N/A")

        # Image save to disk rate spinctl
        self.images_capture_rate_label = wx.StaticText(self.GetParent(), -1, "Image saved every N second(s)")
        self.images_capture_rate_spin_ctrl = wx.SpinCtrl(self.GetParent(), min=1)
        self.images_capture_rate_spin_ctrl.Bind(wx.EVT_SPINCTRL, self.update_dataset_images_capture_rate)

        # Adding to sizer
        self.data_set_creator_input_sizer.Add(self.start_data_set_creator_btn, 0, wx.ALL | wx.CENTER, 5)
        self.data_set_creator_input_sizer.Add(self.images_capture_rate_label, 0, wx.ALL | wx.CENTER, 5)
        self.data_set_creator_input_sizer.Add(self.images_capture_rate_spin_ctrl, 0, wx.ALL | wx.CENTER, 5)
        self.data_set_creator_input_sizer.Add(self.process_latest_dataset_btn, 0, wx.ALL | wx.CENTER, 5)
        self.data_set_creator_input_sizer.Add(self.dir_to_process_label, 0, wx.ALL | wx.CENTER, 2)
        self.data_set_creator_input_sizer.Add(self.dir_to_process_value, 0, wx.ALL | wx.CENTER, 2)
        self.data_set_creator_input_sizer.Add(self.num_images_to_process_label, 0, wx.ALL | wx.CENTER, 2)
        self.data_set_creator_input_sizer.Add(self.num_images_to_process_value, 0, wx.ALL | wx.CENTER, 2)
        ######################################

        ######################################
        # Image stream from AUV
        ######################################
        self.raw_image_sizer = wx.BoxSizer(wx.VERTICAL)

        # This can be checked in project/camera_publisher.py
        self.blank_img = wx.Image(320, 240)
        self.raw_camera_stream = wx.StaticBitmap(self.GetParent(), wx.ID_ANY,
                                                 wx.Bitmap(self.blank_img))
        self.current_image_stream_title = wx.StaticText(self.GetParent(), -1, "Raw image stream")

        # Adding to sizer
        self.raw_image_sizer.Add(self.raw_camera_stream, 0, wx.ALL)
        self.raw_image_sizer.Add(self.current_image_stream_title, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        ######################################

        self.panel.Add(self.data_set_creator_input_sizer, 0, wx.ALL, 5)
        self.panel.Add(self.raw_image_sizer, 0, wx.ALL, 5)

    def get_num_images_in_dataset(self):
        print([f for f in glob.glob(str(self.record_dataset_to_dir))])
        return len([f for f in glob.glob(str(self.record_dataset_to_dir) + "/*")])

    def get_prediction(self, content, project_id, model_id):
        prediction_client = automl_v1beta1.PredictionServiceClient()
        name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
        payload = {'image': {'image_bytes': content}}
        params = {}
        request = prediction_client.predict(name, payload, params)
        return request

    def process_image_cloud_ml(self, content, project_id, model_id, image_name):
        print("Calling Google Cloud ML API")
        try:
            predictions = self.get_prediction(content, project_id, model_id)
            print(predictions)
            response = MessageToDict(predictions, preserving_proto_field_name=True)
            # Convert RGB to BGR
            content = cv2.UMat(cv2.imread(image_name, cv2.IMREAD_COLOR))
            print(len(response["payload"]))
            for x in response["payload"]:
                # Check for type
                if x["display_name"] == "bleached":
                    rect_color = (0,0,0)
                if x["display_name"] == "healthy":
                    rect_color = (255, 255, 255)
                print(x)
                x1, x2, y1, y2 = 0, 0, 0, 0
                for i, coordinates in enumerate(x["image_object_detection"]["bounding_box"]["normalized_vertices"]):
                    print("Adding prediction coordinates to image with i={}".format(i))
                    print(type(coordinates))
                    try:
                        print(coordinates["x"])
                        x = coordinates["x"] * 320
                    except Exception as e:
                        x = 0
                    try:
                        y = coordinates["y"] * 280
                    except Exception as e:
                        y = 0
                    if i == 0:
                        x1 = int(x)
                        y1 = int(y)
                    if i == 1:
                        x2 = int(x)
                        y2 = int(y)
                print("Adding rectangle")
                rectangle(img=content, pt1=(x1, y1), pt2=(x2, y2), color=rect_color, thickness=3)
            return content
        except Exception as e:
            print("No coral detected, is your camera pointing the right way?")
            print("{}".format(e))
            return content

    def batch_process(self, event):
        print("Starting batch processing. . .")
        for i, image in enumerate([f for f in glob.glob(str(self.record_dataset_to_dir) + "/*.jpg")]):
            with open(image, 'rb') as image_file:
                content = image_file.read()
                # img = base64.b64encode(content)
            # img = base64.b64encode(img)
            # Pass the image data to an encoding function.
            new_img = self.process_image_cloud_ml(content, 1070726212812, "IOD8268142722922053632", image)
            cv2.imwrite(str(self.record_dataset_to_dir) + "/processed_{}.jpg".format(i), new_img)

    def start_dataset_creation(self, event):
        if self.currently_recording_dataset:
            print("Recording stopped for dataset")
            # Let rest of app know
            self.currently_recording_dataset = False
            self.process_latest_dataset_btn.Enable()
            self.dir_to_process_value.SetLabel(label=str(self.record_dataset_to_dir))
            self.num_images_to_process_value.SetLabel(label=str(self.get_num_images_in_dataset()))
            self.start_data_set_creator_btn.SetLabel("Start Recording")
            self.panel.Layout()
        else:
            print("Starting to record image dataset")
            # Let rest of app know
            self.currently_recording_dataset = True
            self.process_latest_dataset_btn.Disable()
            # Figure out what to name dataset
            dataset_dir = sorted([f for f in glob.glob("captured_datasets/*")])
            # dataset name null check
            if len(dataset_dir) == 0:
                self.record_dataset_to_dir = "captured_datasets/1"
                os.mkdir(path="captured_datasets/1")
            else:
                self.record_dataset_to_dir = "captured_datasets/{}".format(1 + len(dataset_dir))
                os.mkdir(path=self.record_dataset_to_dir)
            self.dataset_record_rate = int(self.images_capture_rate_spin_ctrl.Value * 30)
            self.start_data_set_creator_btn.SetLabel("Stop Recording")

    def update_dataset_images_capture_rate(self, event):
        self.dataset_record_rate = int(self.images_capture_rate_spin_ctrl.Value * 30)

    def process_last_recorded_data_set(self):
        pass
