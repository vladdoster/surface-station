import time

import docker
import wx
import wx.html
from networking.factories import ClientFactory
from networking.protocols import CameraStreamProtocol, JoystickExecutorProtocol
from panels.menu_bar import MenuBar
from panels.rov_panel import ROVPanel
from wx.adv import SPLASH_CENTRE_ON_SCREEN, SPLASH_TIMEOUT, SplashScreen

global container_id, log


class MainFrame(wx.Frame):

    def __init__(self, app):
        self.frame_number = 1
        frame = wx.Frame.__init__(self, None, wx.ID_ANY,
                                  "Enbarr")
        self._app = app
        # Loading screen
        bmp = wx.Image("images/enbarr.png").ConvertToBitmap()
        SplashScreen(bmp, SPLASH_CENTRE_ON_SCREEN | SPLASH_TIMEOUT,
                     5000, None, -1)

        wx.SafeYield()
        global container_id, log

        # Menu bar
        menu_bar = MenuBar()
        self.SetMenuBar(menu_bar)

        # ROV panel
        self.rov_panel = ROVPanel(self, container_id=container_id, log=log)

        # Frame sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.rov_panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)


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

    global log
    from twisted.python import log

    log.startLogging(sys.stdout)

    wxreactor.install()
    from twisted.internet import reactor

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
    app._camera_factory = ClientFactory(u"ws://127.0.0.1:9000", app, protocol=CameraStreamProtocol)
    app._joystick_factory = ClientFactory(u"ws://127.0.0.1:9001", app, protocol=JoystickExecutorProtocol)
    # Connect to host
    reactor.connectTCP("127.0.0.1", 9000, app._camera_factory)
    reactor.connectTCP("127.0.0.1", 9001, app._joystick_factory)

    # Start twisted event loop
    reactor.run()
