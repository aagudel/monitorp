import socket

__kill = False

class Message(object):
    pass
# TODO: an alternative name can be Loop
class Node:
    def __init__(self, port=0):
        self.receivecb = None
        self.timeoutcb = None
        self.port = port
        self.state = "Stopped"
        self.timeout = 1

    def start(self):        
        self._stablish_connection()
        self.state = "Running"
        # Do communications loop        
        self._spin()
    
    def stop(self):
        self.state = "Stopped"

    def listener_callback(self):
        ...
    
    def timeout_callback(self):
        ...

    def _stablish_connection(self):
        self.receivecb = self.listener_callback
        self.timeoutcb = self.timeout_callback
        self.sock = socket.socket(socket.AF_INET, # Internet
            socket.SOCK_DGRAM) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, 
            socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.settimeout(self.timeout)

    def _receive(self):
        # Checkout recv_into and recvmsg_into
        # https://stackoverflow.com/questions/13981541/recv-into-a-numpy-array
        data, _ = self.sock.recvfrom(1024) # buffer size is 1024 bytes
        msg = Message()
        # TODO: maybe decode() this already? ... No this can also be raw data
        msg.data = data
        self.listener_callback(msg)

    def _spin(self):
        while self.state == "Running":
            try:                
                self._receive()
                #print('comm.py: received message')
            except socket.timeout:                
                self.timeout_callback()
                #print('comm.py: socket on %d timed out'%self.port)
        self.sock.close()

"""
class LocalNode:
    def __init__(self, port=0):
        self.callback = None
        self.port = port
        self.state = "Stopped"
        self.timeout = 1

    def start(self):        
        self._stablish_connection()
        self.state = "Running"
        # Do communications loop        
        self._spin()
    
    def stop(self):
        self.state = "Stopped"

    def _stablish_connection(self):
        # TODO this migh change to a TCP message or pipe in the 
        # future. Google says pipes and local TCP are actually not
        # that different in performance
        self.callback = self.listener_callback
        self.timeoutcb = self.listener_timeoutcb
        self.sock = socket.socket(socket.AF_INET, # Internet
            socket.SOCK_DGRAM) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, 
            socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.settimeout(self.timeout)

    def _receive(self):
        data, _ = self.sock.recvfrom(1024) # buffer size is 1024 bytes
        msg = Message()
        msg.data = data
        self.callback(msg)

    def _spin(self):
        while self.state == "Running":
            try:
                print('DEBUG: received message')
                self._receive()
            except socket.timeout:
                print('DEBUG: socket timeout')
                self.timeoutcb()
                pass
        self.sock.close()
"""