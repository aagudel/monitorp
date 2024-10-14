import time,threading
import numpy as np

import utils.comm as comm
import utils.shared as shared

import rt2.vars as vars

# Lists are way faster than growing a numpy array
# See https://stackoverflow.com/a/49363524
# TODO: is this the best place for globals?
vars.Z_list = []
vars.X_list = []

# W is needed in advance so force shared to get the shared variable
# TODO: probably is clearer and cleaner if all used variables are declared and
# initialized 
shared.x_current = np.array([[0.0,0.0,0.0]],dtype=np.float32).T
shared.W = np.zeros([3,30],dtype=np.float32)

class NeuroDataCapture(comm.Node):
    """Captures spike activity from device/simulator for the current 
    process/node.
    """
    def __init__(self,port):
        super().__init__(port)
        self.mode = vars.IDLE
        self.switch_to = ""
        self.log = ""
        self.t0 = time.time()

    def start(self):
        print("Running neuro capture loop", threading.get_ident())
        super().start()
    
    def stop(self):
        print("Stopping neuro capture loop")
        super().stop()
    
    def listener_callback(self, msg):
        
        shared.z_current = np.frombuffer(msg.data, dtype=np.uint8).reshape(-1,1)

        #print('neuro.py: NeuroDataCapture: received array', str(shared.z_current.shape))
        #print('neuro.py: NeuroDataCapture: switch_to='+self.switch_to)

        # TODO Should this be moved to an independent process/thread? 
        # We are not saving data here anymore so there is nothing else to do ...?
        # Anything -> Idle: train decoder
        if self.switch_to == "idle":
            # Simplest decoder, least squares regression
            # https://stackoverflow.com/a/15739248
            Z = np.hstack(vars.Z_list)
            X = np.hstack(vars.X_list)            
            shared.W = np.linalg.lstsq(Z.T, X.T, rcond=None)[0].T.astype(np.float32)
            self.log = f'Decoder_ready!' #:X{X.shape} = W{shared.W.shape}*Z{Z.shape}'
            print(self.log)
            print("MinMax X:", X.dtype, X.min(), X.max())
            print("MinMax Z:", Z.dtype, Z.min(), Z.max())
            print("MinMax W:", shared.W.dtype, shared.W.min(), shared.W.max())
            self.mode = vars.IDLE
            self.switch_to = ""
            
            # Send parameters to independent decoder
            #self.sock.sendto(shared.W.tobytes(),("192.168.1.255",4200))
            #self.sock.sendto(shared.W.tobytes(),("127.0.0.1",4200))
            
            #__import__("IPython").embed()
        
        t1 = time.time()
        # shared.p_neuro[0] = t1 - self.t0 ... works only when shared.p_neuro exists
        # TODO: ideally this should not require calling np, but no other way for the
        # moment
        shared.p_neuro = np.array([t1 - self.t0],dtype=np.float32)
        self.t0 = t1

        # Anything -> Collect: reset vars to start capure
        if self.switch_to == "collect":
            vars.Z_list = []
            vars.X_list = []
            self.log = "Collecting_data..."
            self.mode = vars.COLLECT
            self.switch_to = ""

        # Anything -> Collect and decode: reset vars to start capure
        if self.switch_to == "collect_and_decode":
            vars.Z_list = []
            vars.X_list = []
            self.log = "Collecting_and_Decoding..."
            self.mode = vars.COLLECT_AND_DECODE
            self.switch_to = ""

        if self.mode == vars.IDLE:
            ...
        elif self.mode == vars.COLLECT or self.mode == vars.COLLECT_AND_DECODE:            
            vars.Z_list.append(np.copy(shared.z_current))
            vars.X_list.append(np.copy(shared.x_current))
            if len(vars.Z_list) > 100: # Restrict to a certain length
                vars.Z_list.pop(0)
                vars.X_list.pop(0)
            self.log = str(len(vars.Z_list))+"_samples"
        
        if self.mode == vars.COLLECT_AND_DECODE: # Decoding
            # Local prediction just for comparison with that of the
            # remote decoder
            shared.x_pred_local = shared.W @ shared.z_current

class DecoderParam(comm.Node):
    def __init__(self,port):
        super().__init__(port)

    def start(self):
        print("Running decoder parameters loop", threading.get_ident())
        super().start()
    
    def stop(self):
        print("Stopping decoder parameters loop")
        super().stop()
    
    def listener_callback(self, msg):
        W = np.frombuffer(msg.data, dtype=np.float32)
        n = shared.z_current.shape[0]
        vars.W = W.reshape((-1,n))
        print("Decoder params. received", vars.W.shape)
        print(vars.W[0:2,0:2])

class NeuroDecode(comm.Node):
    def __init__(self,port):
        super().__init__(port)        

    def start(self):
        print("Running neuro decode loop", threading.get_ident())        
        super().start()

    def stop(self):        
        print("Stopping neuro decode loop")
        # TODO Stop ROS
        super().stop()

    def listener_callback(self, msg):

        shared.z_current = np.frombuffer(msg.data, dtype=np.uint8).reshape(-1,1)

        # To keep things simple, always predict even if parameters
        # are not upto date
        vars.x_pred = vars.W @ shared.z_current
        
        # Send output to robot and monitor
        # TODO send


