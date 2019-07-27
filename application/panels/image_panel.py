import wx


class ImageStreamPanel(wx.StaticBox):

    def __init__(self, *args, **kwargs):
        super(ImageStreamPanel, self).__init__(*args, **kwargs)
        self.Init_UI()

    def Init_UI(self):
        self.panel = wx.StaticBoxSizer(self, wx.HORIZONTAL)
        self.choices_sizer = wx.BoxSizer(wx.VERTICAL)
        self.raw_stream_choice = wx.RadioButton(self.GetParent(), label='Raw', pos=(10, 10),
                                                style=wx.RB_GROUP)
        self.classification_choice = wx.RadioButton(self.GetParent(), label='Image classification', pos=(10, 30))
        self.obj_detection_choice = wx.RadioButton(self.GetParent(), label='Object detection', pos=(10, 50))

        self.raw_stream_choice.Bind(wx.EVT_RADIOBUTTON, self.SetVal)
        self.classification_choice.Bind(wx.EVT_RADIOBUTTON, self.SetVal)
        self.obj_detection_choice.Bind(wx.EVT_RADIOBUTTON, self.SetVal)

        self.raw_image_sizer = wx.BoxSizer(wx.VERTICAL)
        self.blank_img = wx.Image(320, 240)
        self.raw_camera_stream = wx.StaticBitmap(self.GetParent(), wx.ID_ANY,
                                                 wx.Bitmap(self.blank_img))

        self.choices_sizer.Add(self.raw_stream_choice, 0, wx.ALL, 5)
        self.choices_sizer.Add(self.classification_choice, 0, wx.ALL, 5)
        self.choices_sizer.Add(self.obj_detection_choice, 0, wx.ALL, 5)

        self.panel.Add(self.choices_sizer, 0, wx.ALL, 5)
        self.current_image_stream_title = wx.StaticText(self.GetParent(), -1, "Raw image stream")
        self.raw_image_sizer.Add(self.raw_camera_stream, 0, wx.ALL)
        self.raw_image_sizer.Add(self.current_image_stream_title, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.raw_image_sizer.Hide(self.current_image_stream_title)
        self.panel.Add(self.raw_image_sizer, 0, wx.ALL, 5)

    def SetVal(self, e):
        if str(self.raw_stream_choice.GetValue()):
            self.current_image_stream_title.SetLabel("Raw stream")
        if str(self.classification_choice.GetValue()):
            self.current_image_stream_title.SetLabel("Image classification")
        if str(self.obj_detection_choice.GetValue()):
            self.current_image_stream_title.SetLabel("Object detection")
