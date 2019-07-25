import json
import os
import time
from subprocess import PIPE, Popen

import docker
import wx
import wx.html
from joystick import JoystickPanel
from networking.factories import MyClientFactory
from networking.protocols import CameraStreamProtocol, JoystickExecutorProtocol
from wx.adv import SPLASH_CENTRE_ON_SCREEN, SPLASH_TIMEOUT, SplashScreen

global container_id, log


class AUVPanel(wx.Panel):

    def __init__(self, parent, ):
        wx.Panel.__init__(self, parent, -1)


class ROVPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""
        super(ROVPanel, self).__init__(parent)

        panel = wx.Panel(self)
        panel_vbox = wx.BoxSizer(wx.VERTICAL)

        websocket_and_networking_hbox = wx.BoxSizer(wx.HORIZONTAL)
        ######################################
        ## Websocket status information panel
        ######################################
        websocket_status_static_box = wx.StaticBox(panel, -1, 'Websockets info:')
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
        networking_controls = wx.StaticBox(panel, -1, 'Networking:')
        networking_io_sizer = wx.StaticBoxSizer(networking_controls, wx.VERTICAL)
        networking_sizer = wx.BoxSizer(wx.HORIZONTAL)

        ws_status = wx.StaticText(panel, -1, "Socket messages")
        networking_input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.send_test_message = wx.Button(panel, -1, 'Test message')
        self.send_test_message.Bind(wx.EVT_BUTTON, self.on_test_message_btn_click)

        self.messages = wx.TextCtrl(panel, size=(450, 75), style=wx.TE_MULTILINE)
        networking_input_sizer.Add(ws_status, 0, wx.ALL | wx.ALIGN_TOP | wx.CENTER, 5)
        networking_input_sizer.Add(self.send_test_message, 0, wx.ALL | wx.CENTER, 5)

        # networking_sizer.Add(ws_status, 0, wx.ALL | wx.TOP, 5)
        networking_sizer.Add(networking_input_sizer, 0, wx.ALL | wx.CENTER, 5)
        networking_sizer.Add(self.messages, 0, wx.ALL | wx.CENTER, 5)
        networking_io_sizer.Add(networking_sizer, 0, wx.ALL | wx.CENTER, 10)

        ######################################
        ## Image panel
        ######################################
        image_viewing_static_box = wx.StaticBox(panel, -1, 'Image info:')
        image_viewing_sizer = wx.StaticBoxSizer(image_viewing_static_box, wx.HORIZONTAL)
        img = wx.Image(320, 240)
        self.raw_camera_stream = wx.StaticBitmap(panel, wx.ID_ANY,
                                                 wx.BitmapFromImage(img))
        processed_img = wx.Image(320, 240)
        self.processed_image_stream = wx.StaticBitmap(panel, wx.ID_ANY,
                                                      wx.BitmapFromImage(processed_img))
        image_viewing_sizer.Add(self.raw_camera_stream, 0, wx.ALL, 5)
        image_viewing_sizer.Add(self.processed_image_stream, 0, wx.ALL, 5)

        ######################################
        ## Joystick panel
        ######################################
        joystick_controls = wx.StaticBox(panel, -1, 'Joystick Controls:')
        joystick_main_sizer = wx.StaticBoxSizer(joystick_controls, wx.VERTICAL)
        global log
        joystick_panel = JoystickPanel(panel, log)
        joystick_main_sizer.Add(joystick_panel)

        # Add everything to main panel
        websocket_and_networking_hbox.Add(websocket_status_sizer, 0, wx.ALL | wx.CENTER, 5)
        websocket_and_networking_hbox.Add(networking_io_sizer, 0, wx.ALL | wx.CENTER, 5)
        panel_vbox.Add(websocket_and_networking_hbox, 0, wx.ALL | wx.CENTER, 5)
        panel_vbox.Add(image_viewing_sizer, 0, wx.ALL | wx.CENTER, 5)
        panel_vbox.Add(joystick_main_sizer, 0, wx.ALL | wx.CENTER, 5)
        panel.SetSizer(panel_vbox)
        self.Centre()
        panel.Fit()
        # Start docker status check
        self.check_docker_status()

    def on_test_message_btn_click(self, event):
        if self.GetParent()._app._joystick_factory:
            proto = self.GetParent()._app._joystick_factory._proto
            if proto:
                # Send message to server
                evt = {'x': 1, 'y': 1, 'z': .5, 'r': -.1, 'p': .2, 'c': -1,
                       'button': 17, 'checksum': 987}
                msg = json.dumps(evt).encode('utf8')
                proto.sendMessage(msg)
                # Update UI
                self.messages.AppendText("Sending to server: {}\n".format(msg))

    def check_docker_status(self):
        global container_id
        if container_id:
            try:
                client = docker.client.from_env()
                status = client.containers.get(container_id).status
                if status == "running":
                    self.ml_docker_container_status_pnl.SetBackgroundColour("#228B22")
                else:
                    self.ml_docker_container_status_pnl.SetBackgroundColour("#FF0000")
            except Exception as e:
                print("Error getting ml container status")
                self.ml_docker_container_status_pnl.SetBackgroundColour("#FF0000")
        wx.CallLater(10000, self.check_docker_status)


class MainFrame(wx.Frame):

    def __init__(self, app):
        self.frame_number = 1
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Enbarr")
        self._app = app
        # Loading screen
        bmp = wx.Image("enbarr.png").ConvertToBitmap()
        SplashScreen(bmp, SPLASH_CENTRE_ON_SCREEN | SPLASH_TIMEOUT,
                     5000, None, -1)

        wx.SafeYield()
        self.auv_panel = AUVPanel(self)
        self.rov_panel = ROVPanel(self)
        self.auv_panel.Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.auv_panel, 1, wx.EXPAND)
        self.sizer.Add(self.rov_panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.create_menu_bar()

    def menu_data(self):
        return (("&File",
                 ("&Switch Mode", "Switch operation mode", self.on_panel_switch),
                 ("&Quit", "Quit", self.close_window)),
                ("&Options",
                 ("&Upload Model", "Upload a ML model", self.upload_model),
                 ("", "", ""),
                 ("&Documentation", "Show documentation", self.documentation)))

    def create_menu_bar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menu_data():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1:]
            menuBar.Append(self.create_menu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)

    def create_menu(self, menuData):
        menu = wx.Menu()
        for eachLabel, eachStatus, eachHandler in menuData:
            if not eachLabel:
                menu.AppendSeparator()
                continue
            menuItem = menu.Append(-1, eachLabel, eachStatus)
            self.Bind(wx.EVT_MENU, eachHandler, menuItem)
        return menu

    def on_panel_switch(self, event):
        """"""
        if self.auv_panel.IsShown():
            self.SetTitle("ROV Controls Showing")
            self.auv_panel.Hide()
            self.rov_panel.Show()
        else:
            self.SetTitle("AUV Controls Showing")
            self.auv_panel.Show()
            self.rov_panel.Hide()
        self.Layout()

    # Empty event handlers needs to compile
    def upload_model(self, event):
        pass

    def options(self, event):
        pass

    def close_window(self, event):
        self.Destroy()

    def documentation(self, event):
        try:
            browser = os.environ.get('BROWSER')
            doc_url = 'https://vdoster.com'
            process = Popen([browser, doc_url], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            print(stdout)
        except KeyError as e:
            print("No browser env var set, creating popup\n\n{}".format(e))


def start_ml_docker_container():
    client = docker.from_env()
    # kill all running containers
    running_containers = client.containers.list()
    for container in running_containers:
        container.kill()
    try:
        global container_id
        container_id = client.containers.run(image="gcr.io/automl-vision-ondevice/gcloud-container-1.12.0:latest",
                                             detach=True).id
    except docker.errors.APIError as e:
        print("Error starting ml container\n\n{}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    import sys
    from twisted.internet import wxreactor
    import sys

    from twisted.python import log

    wxreactor.install()
    from twisted.internet import reactor
    from twisted.python import log

    global log
    log.startLogging(sys.stdout)
    start_ml_docker_container()
    print("""

                ######## ##    ## ########     ###    ########  ########  
                ##       ###   ## ##     ##   ## ##   ##     ## ##     ## 
                ##       ####  ## ##     ##  ##   ##  ##     ## ##     ## 
                ######   ## ## ## ########  ##     ## ########  ########  
                ##       ##  #### ##     ## ######### ##   ##   ##   ##   
                ##       ##   ### ##     ## ##     ## ##    ##  ##    ##  
                ######## ##    ## ########  ##     ## ##     ## ##     ##

                                 ######   ##     ## ####                                  
                                ##    ##  ##     ##  ##                                   
                                ##        ##     ##  ##                                   
                                ##   #### ##     ##  ##                                   
                                ##    ##  ##     ##  ##                                   
                                ##    ##  ##     ##  ##                                   
                                 ######    #######  ####

                """)
    app = wx.App(False)
    app._camera_factory = None
    app._joystick_factory = None

    app._frame = MainFrame(app)
    timer = wx.Timer()
    time.sleep(5)
    app._frame.Show()
    reactor.registerWxApp(app)

    # Create factory (singleton connection pattern)
    app._camera_factory = MyClientFactory(u"ws://127.0.0.1:9000", app, protocol=CameraStreamProtocol)
    app._joystick_factory = MyClientFactory(u"ws://127.0.0.1:9001", app, protocol=JoystickExecutorProtocol)
    # Connect to host
    reactor.connectTCP("127.0.0.1", 9000, app._camera_factory)
    reactor.connectTCP("127.0.0.1", 9001, app._joystick_factory)

    # Start twisted event loop
    reactor.run()
