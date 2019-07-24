from autobahn.twisted import WebSocketClientFactory
from twisted.internet.protocol import ReconnectingClientFactory


class MyClientFactory(ReconnectingClientFactory, WebSocketClientFactory):
    """
    Our factory for WebSocket client connections.
    """
    # protocol = MyClientProtocol

    maxDelay = 10
    maxRetries = 5

    def __init__(self, url, app, protocol):
        WebSocketClientFactory.__init__(self, url)
        self.protocol = protocol
        self._app = app
        self._proto = None

    def startedConnecting(self, connector):
        print('Started to connect.')


    def clientConnectionLost(self, connector, reason):
        print('Lost connection. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
