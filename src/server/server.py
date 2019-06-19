from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol


class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        payload = b"Server response: " + payload
        self.factory.broadcast(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):

    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """
    protocol = BroadcastServerProtocol

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []

    def register(self, client):
        if client not in self.clients:
            self.clients.append(client)
            print("registered client {}".format(client.peer))

    def unregister(self, client):
        if client in self.clients:
            self.clients.remove(client)
            print("unregistered client {}".format(client.peer))

    def broadcast(self, payload, isBinary):
        for c in self.clients:
            c.sendMessage(payload, isBinary)
        print("broadcasted message to {} clients".format(len(self.clients)))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)
    print("""
    
         ######## ##    ## ########     ###    ########  ########   
         ##       ###   ## ##     ##   ## ##   ##     ## ##     ##  
         ##       ####  ## ##     ##  ##   ##  ##     ## ##     ##  
         ######   ## ## ## ########  ##     ## ########  ########   
         ##       ##  #### ##     ## ######### ##   ##   ##   ##    
         ##       ##   ### ##     ## ##     ## ##    ##  ##    ##   
         ######## ##    ## ########  ##     ## ##     ## ##     ##
           
          ######  ######## ########  ##     ## ######## ########    
         ##    ## ##       ##     ## ##     ## ##       ##     ##   
         ##       ##       ##     ## ##     ## ##       ##     ##   
          ######  ######   ########  ##     ## ######   ########    
               ## ##       ##   ##    ##   ##  ##       ##   ##     
         ##    ## ##       ##    ##    ## ##   ##       ##    ##    
          ######  ######## ##     ##    ###    ######## ##     ##
                       
            """)
    factory = BroadcastServerFactory(u"ws://127.0.0.1:9000")

    reactor.listenTCP(9000, factory)
    reactor.run()
