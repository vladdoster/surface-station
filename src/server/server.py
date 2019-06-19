"""	 This file is part of Enbarr.
     Enbarr is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 3 of the License, or
     (at your option) any later version.
     Enbarr is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.
     You should have received a copy of the GNU General Public License
     along with Enbarr.  If not, see <https://www.gnu.org/licenses/>.
 """

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
