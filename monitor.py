import numpy as np

import kernel, neuro, kinem, uiimgui

def main():

    neurodc = neuro.NeuroDataCapture(4300)
    kinemdc = kinem.KinemDataCapture(4600)
    
    kernel.state.modules = {
        "imgui": uiimgui,
        "Neuro": neurodc,
        "Kinem": kinemdc,
    }
    
    # Init important vars
    kernel.state.x_current = np.array([[0.0,0.0,0.0]],dtype=np.float32).T
    kernel.state.x_pred = np.array([[0.0,0.0,0.0]],dtype=np.float32).T
    # Lists are way faster than growing a numpy array
    # See https://stackoverflow.com/a/49363524
    kernel.state.Z_list = []
    kernel.state.X_list = []
    kernel.state.W = np.array([],dtype=np.float32)

    # Start gui
    kernel.exec("start","imgui")
    kernel.start()

if __name__ == '__main__':
    main()
