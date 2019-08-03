import docker
import wx
import wx.html
from panels.image_panel import ImageStreamPanel
from panels.joystick import JoystickPanel
from panels.networking_panel import NetworkingControlPanel

global container_id

class ROVPanel(wx.Panel):

    def __init__(self, parent, container_id=None, log=None):
        super(ROVPanel, self).__init__(parent)
        self.container_id = container_id
        self.log = log

        panel = wx.Panel(self)
        panel_vbox = wx.BoxSizer(wx.VERTICAL)

        websocket_and_networking_hbox = wx.BoxSizer(wx.HORIZONTAL)

        ######################################
        ## Websocket status information panel
        ######################################

        websocket_status_static_box = wx.StaticBox(panel, -1, 'Websocket Status')
        websocket_status_sizer = wx.StaticBoxSizer(websocket_status_static_box, wx.HORIZONTAL)

        # auv camera websocket connection indicator
        ws_camera_sizer = wx.BoxSizer(wx.VERTICAL)
        camera_connection_title = wx.StaticText(panel, -1, "Camera")
        # set color addressable panel
        self.camera_status_pnl_col = wx.Colour(0, 0, 0)
        self.camera_status_pnl = wx.Panel(panel, size=(20, 20))
        self.camera_status_pnl.SetBackgroundColour(self.camera_status_pnl_col)
        ws_camera_sizer.Add(camera_connection_title, 0, wx.ALL | wx.TOP, 5)
        ws_camera_sizer.Add(self.camera_status_pnl, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # auv joystick websocket connection indicator
        ws_joystick_sizer = wx.BoxSizer(wx.VERTICAL)
        joystick_connection_title = wx.StaticText(panel, -1, "Joystick")
        self.joystick_status_pnl_col = wx.Colour(0, 0, 0)
        self.joystick_status_pnl = wx.Panel(panel, size=(20, 20))
        self.joystick_status_pnl.SetBackgroundColour(self.joystick_status_pnl_col)
        ws_joystick_sizer.Add(joystick_connection_title, 0, wx.ALL | wx.TOP, 5)
        ws_joystick_sizer.Add(self.joystick_status_pnl, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # ML image classification docker container running indicator
        ml_docker_container_sizer = wx.BoxSizer(wx.VERTICAL)
        ml_docker_container_title = wx.StaticText(panel, -1, "ML")
        self.ml_docker_container_status_pnl_col = wx.Colour(0, 0, 0)
        self.ml_docker_container_status_pnl = wx.Panel(panel, size=(20, 20))
        self.ml_docker_container_status_pnl.SetBackgroundColour(self.ml_docker_container_status_pnl_col)
        ml_docker_container_sizer.Add(ml_docker_container_title, 0, wx.ALL | wx.TOP, 5)
        ml_docker_container_sizer.Add(self.ml_docker_container_status_pnl, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        websocket_status_sizer.Add(ws_joystick_sizer, 0, wx.ALL | wx.TOP, 5)
        websocket_status_sizer.Add(ws_camera_sizer, 0, wx.ALL | wx.TOP, 5)
        websocket_status_sizer.Add(ml_docker_container_sizer, 0, wx.ALL | wx.TOP, 5)

        ######################################
        ## Networking panel
        ######################################

        self.networking_io = NetworkingControlPanel(parent=panel, label="Networking", id=-1)

        ######################################
        ## Image panel
        ######################################

        self.image_viewer = ImageStreamPanel(parent=panel, label="Vision Processing", id=-1)

        ######################################
        ## Joystick panel
        ######################################

        # TODO: Refactor to reduce to singular call
        joystick_controls = wx.StaticBox(panel, -1, 'Joystick Controls:')
        joystick_main_sizer = wx.StaticBoxSizer(joystick_controls, wx.VERTICAL)
        joystick_panel = JoystickPanel(panel, self.log)
        joystick_main_sizer.Add(joystick_panel)

        ######################################
        ## Panel construction
        ######################################

        websocket_and_networking_hbox.Add(websocket_status_sizer, 0, wx.ALL | wx.CENTER, 5)
        websocket_and_networking_hbox.Add(self.networking_io.panel, 0, wx.ALL | wx.CENTER, 5)
        panel_vbox.Add(websocket_and_networking_hbox, 0, wx.ALL | wx.CENTER, 5)
        panel_vbox.Add(self.image_viewer.panel, 0, wx.ALL | wx.CENTER, 5)
        panel_vbox.Add(joystick_main_sizer, 0, wx.ALL | wx.CENTER, 5)
        panel.SetSizer(panel_vbox)
        self.Centre()
        panel.Fit()
        # Start docker status check
        self.check_docker_status()

    def check_docker_status(self):
        # Boo globals but....
        if self.container_id:
            try:
                client = docker.client.from_env()
                status = client.containers.get(self.container_id).status
                if status == "running":
                    self.ml_docker_container_status_pnl.SetBackgroundColour("#228B22")
                else:
                    self.ml_docker_container_status_pnl.SetBackgroundColour("#FF0000")
            except Exception as e:
                print("Error getting ml container status\n{}".format(e))
                self.ml_docker_container_status_pnl.SetBackgroundColour("#FF0000")
        else:
            print("Error getting ml container status\n{}".format(e))
            self.ml_docker_container_status_pnl.SetBackgroundColour("#FF0000")
        wx.CallLater(10000, self.check_docker_status)