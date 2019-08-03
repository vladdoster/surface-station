import os

import wx


class ImageStreamPanel(wx.StaticBox):

    def __init__(self, *args, **kwargs):
        super(ImageStreamPanel, self).__init__(*args, **kwargs)
        self.Init_UI()

    def Init_UI(self):
        # Image Stream info box
        ######################################
        self.panel = wx.StaticBoxSizer(self, wx.HORIZONTAL)

        # Stream options input
        ######################################
        self.data_set_creator_input_panel = wx.StaticBox(self.GetParent(), label="Dataset Creator")
        self.data_set_creator_input_sizer = wx.StaticBoxSizer(self.data_set_creator_input_panel, wx.VERTICAL)
        self.start_data_set_creator = wx.Button(self.GetParent().GetParent(), label='Start recording', pos=(10, 50))
        self.start_data_set_creator.Bind(wx.EVT_BUTTON, self.button_browse_path_click)
        self.save_data_set_to_dir = wx.StaticText(self.GetParent(), -1)

        self.images_capture_rate_label = wx.StaticText(self.GetParent(), -1, "Images captured per second")
        self.images_capture_rate = wx.SpinCtrl(self.GetParent(), min=1)
        self.save_data_set_to_dir.Wrap(width=10)
        self.data_set_creator_input_sizer.Add(self.start_data_set_creator, 0, wx.ALL | wx.CENTER, 5)
        self.data_set_creator_input_sizer.Add(self.save_data_set_to_dir, 0, wx.ALL, 5)
        self.data_set_creator_input_sizer.Add(self.images_capture_rate_label, 0, wx.ALL | wx.CENTER, 5)
        self.data_set_creator_input_sizer.Add(self.images_capture_rate, 0, wx.ALL | wx.CENTER, 5)

        ######################################

        # Image stream from AUV
        ######################################
        self.raw_image_sizer = wx.BoxSizer(wx.VERTICAL)
        # This can be checked in project/camera_publisher.py
        self.blank_img = wx.Image(320, 240)
        self.raw_camera_stream = wx.StaticBitmap(self.GetParent(), wx.ID_ANY,
                                                 wx.Bitmap(self.blank_img))
        self.current_image_stream_title = wx.StaticText(self.GetParent(), -1, "Raw image stream")
        self.raw_image_sizer.Add(self.raw_camera_stream, 0, wx.ALL)
        self.raw_image_sizer.Add(self.current_image_stream_title, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        ######################################

        self.panel.Add(self.data_set_creator_input_sizer, 0, wx.ALL, 5)
        self.panel.Add(self.raw_image_sizer, 0, wx.ALL, 5)

    def button_browse_path_click(self, event):
        print("Starting to record image dataset")
        print(os.listdir("captured_datasets"))

        self.save_data_set_to_dir.Wrap(width=10)
        self.save_data_set_to_dir.Update()
