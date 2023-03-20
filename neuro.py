import numpy as np
import comm, kernel

class NeuroDataCapture(comm.Node):
    def __init__(self,port):
        super().__init__(port)
        self.mode = "Decoding"
        self.message = ""
        self.log = ""

    def start(self):
        print("Running neuro capture loop")
        super().start()
    
    def stop(self):
        print("Stopping neuro capture loop")
        super().stop()
    
    def listener_callback(self, msg):
        
        z = np.frombuffer(msg.data, dtype=np.uint8).reshape(-1,1)

        # TODO Do not query the ui here, use some sort of state

        # Training -> Decoding: train decoder
        if self.message == "SwitchToDecode" and self.mode == "Training":
            # Simplest decoder, least squares regression
            # https://stackoverflow.com/a/15739248
            Z = np.hstack(kernel.state.Z_list)
            X = np.hstack(kernel.state.X_list)            
            kernel.state.W = np.linalg.lstsq(Z.T, X.T, rcond=None)[0].T
            self.log = f'Trained decoder: X{X.shape} = W{kernel.state.W.shape}*Z{Z.shape}'
            print(self.log)
            print("MinMax X:", X.min(), X.max())
            print("MinMax Z:", Z.min(), Z.max())
            print("MinMax W:", kernel.state.W.min(), kernel.state.W.max())
            self.mode = "Decoding"
            self.message = ""
            #__import__("IPython").embed()

        # Decoding -> Training
        # TODO: do not ask the ui here use some sorf of state
        if self.message == "SwitchToTrain" and self.mode == "Decoding":
            kernel.state.Z_list = []
            kernel.state.X_list = []
            self.log = "Capturing data..."
            self.mode = "Training"
            self.message = ""

        if self.mode == "Training":
            kernel.state.Z_list.append(z)
            kernel.state.X_list.append(kernel.state.x_current)
            if len(kernel.state.Z_list) > 100: # Restrict to a certain length
                kernel.state.Z_list.pop(0)
                kernel.state.X_list.pop(0)
            self.log = str(len(kernel.state.Z_list))+" samples"
        else: # Decoding
            if kernel.state.W.size == 0: kernel.state.W = np.zeros([3,z.shape[0]])
            kernel.state.x_pred = kernel.state.W @ z            
