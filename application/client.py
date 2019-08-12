import os
import sys

import config
import wx.html
from networking.factories import ClientFactory
from networking.protocols import CameraStreamProtocol, JoystickExecutorProtocol
from panels.root_panel import RootFrame
from twisted.internet import wxreactor
from twisted.python import log


def start_surface_station():
    log.startLogging(sys.stdout)
    wxreactor.install()
    print(
        """

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

                """
    )
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_application_credentials_path
    except OSError as e:
        print("Error setting GOOGLE_APPLICATION_CREDENTIALS\n{}".format(e))

    app = wx.App(False)
    app._camera_factory = None
    app._joystick_factory = None

    app._frame = RootFrame(app, log)

    from twisted.internet import reactor
    reactor.registerWxApp(app)
    if config.sim_mode:
        print("Note: Simulation mode is true, we're running locally!")
        app._camera_factory = ClientFactory(
            config.dev_camera_ws_url, app, protocol=CameraStreamProtocol
        )
        app._joystick_factory = ClientFactory(
            config.dev_joystick_ws_url, app, protocol=JoystickExecutorProtocol
        )
        # Connect to host
        reactor.connectTCP(config.dev_robot_url, config.dev_camera_ws_port, app._camera_factory)
        reactor.connectTCP(config.dev_robot_url, config.dev_joystick_ws_port, app._joystick_factory)
    else:
        print("Note: Simulation mode is false, we're looking for the actual robot!")
        app._camera_factory = ClientFactory(
            config.live_camera_ws_url, app, protocol=CameraStreamProtocol
        )
        app._joystick_factory = ClientFactory(
            config.live_joystick_ws_url, app, protocol=JoystickExecutorProtocol
        )
        # Connect to host
        reactor.connectTCP(config.live_robot_url, config.live_camera_ws_port, app._camera_factory)
        reactor.connectTCP(config.live_robot_url, config.live_joystick_ws_port, app._joystick_factory)

    # Start twisted event loop
    reactor.run()


if __name__ == "__main__":
    start_surface_station()
