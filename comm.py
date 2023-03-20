import socket

__kill = False

class Message(object):
    pass

class Node:
    def __init__(self, port):
        self.callback = None
        self.port = port
        self.state = "Stopped"

    def start(self):        
        self._stablish_connection()
        self.state = "Running"
        # Do communications loop        
        self._spin()
    
    def stop(self):
        self.state = "Stopped"

    def _stablish_connection(self):
        self.callback = self.listener_callback
        self.sock = socket.socket(socket.AF_INET, # Internet
            socket.SOCK_DGRAM) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, 
            socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.settimeout(1)
    
    def _receive(self):
        # Checkout recv_into and recvmsg_into
        # https://stackoverflow.com/questions/13981541/recv-into-a-numpy-array
        data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
        msg = Message()
        msg.data = data
        self.callback(msg)

    def _spin(self):
        while self.state == "Running":
            try:
                self._receive()
            except socket.timeout:
                print('DEBUG: socket timeout')
                pass
        self.sock.close()


