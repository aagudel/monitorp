import time, threading
import numpy as np

import utils.kernel as kernel
import utils.comm as comm
import utils.shared as shared

class KinemDataCapture(comm.Node):
    """Captures kinematics from device/simulator for the current 
    process.
    """
    def __init__(self,port):
        super().__init__(port)
        self.t0 = time.time()

    def start(self):
        print("Running kinem capture loop")
        super().start()

    def stop(self):
        print("Stopped kinem capture loop")
        super().stop()

    def listener_callback(self, msg):        
        # Using big endian here as this is the network standard
        # TODO little endian is probably more efficent as Protobuf does
        x = np.frombuffer(msg.data, dtype=">f4").reshape(-1,1)
        #print('kinem.py: KinemDataCapture: received array', str(x))
        # Extra 1.0 is required for the offset in the regression        
        shared.x_current = np.vstack([x,1.0],dtype=np.float32)
        #print("x:", shared.x_current.dtype)
        t1 = time.time()
        shared.p_kinem = np.array([t1 - self.t0],dtype=np.float32)
        self.t0 = t1

class KinemDecodeCapture(comm.Node):
    """Captures decoded kinematics produced by other process"""
    def __init__(self,port):
        super().__init__(port)

    def start(self):
        print("Running kinem decode loop", threading.get_ident())
        self.state = "Running"     
        super().start()

    def stop(self):
        print("Stopped kinem decode loop")
        self.state = "Stopped"
        super().stop()

    def listener_callback(self, msg):
        pass
        # TODO receive
        #print(threading.get_ident())
        # Received prediction from remote decoder
        # shared.x_pred = np.array(msg.data).reshape(3,1)
        #print(shared.x_pred)
