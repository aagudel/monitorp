import numpy as np
import comm, kernel

class KinemDataCapture(comm.Node):
    def __init__(self,port):
        super().__init__(port)

    def start(self):
        print("Running kinem capture loop")
        super().start()

    def stop(self):
        print("Stopped kinem capture loop")
        super().stop()

    def listener_callback(self, msg):
        global x_current
        # Extra 1.0 is required for the offset in the regression
        x = np.frombuffer(msg.data, dtype=">f4").reshape(-1,1)
        kernel.state.x_current = np.vstack([x,1.0])
        #print("x:", kernel.state.x_current)