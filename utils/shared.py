# Module for shared variables
# For the moment, only numpy arrays of dim>1 are supported as they can nicely
# use arbitrary memory blocks as data container
# TODO: 
# - At the moment we catch shared.x = y. See if we can also catch
#   y = shared.x, when x is not yet declared.
import sys
from multiprocessing import shared_memory
import numpy as np

import utils.kernel as kernel

modself = sys.modules[__name__]

class CatchAssignOp(type(modself)):
    # Catches shared.var = x
    def __setattr__(self, attr, val):
        exists = getattr(self, attr, None)        
        if exists is None:
            print('shared.py: Catched creation',attr,val[0])
            super().__setattr__(attr, create(attr,val))
        else:
            #
            # This is called all the time !!!
            #
            #print('Catched write',attr,val[0])
            # To reuse the shared buffer, we do not assign the pointer
            # to the object but copy each element.
            # This should aso take care of size differences
            modself.__dict__[attr][:] = val[:]
            #print(modself.__dict__[attr])
    
    # Catches x = shared.var or just shared.var in an expression
    #
    # We could catch this, but if does not exist in shared mem, who 
    # knows how to initialize? Maybe we could wait? Would this be called
    # every time?    
    #def __getattr__(self, attr):
    #    print('Wanna get ', attr)
    #    ...

modself.__class__ = CatchAssignOp

shms = []

def create(attr,val):
    try:
        shm = shared_memory.SharedMemory(name=kernel.share_name+"_"+attr)        
        print("shared.py: Shared variable", shm.name, "was found")
        print(shm)
    except FileNotFoundError:
        # Not created yet
        shm = shared_memory.SharedMemory(name=kernel.share_name+"_"+attr, create=True, size=val.nbytes)
        print("shared.py: Shared variable", shm.name, "was not yet created")
        print(shm)
    # Shared memory objects have to be kept, otherwise they are garbage collected
    # and the memory area is taken away
    shms.append(shm)
    return np.ndarray(val.shape, dtype=val.dtype, buffer=shm.buf)

#def assign(attr,val):
#    modself.__dict__[attr][:] = val[:]

"""
Test code
Process 1:
    shared.z_current = np.zeros((30,1),dtype=np.float32)
    shared.z_current[0] = 1.0
    shared.x_current = np.array([[0.0,0.0,0.0]],dtype=np.float32).T
    shared.x_current = np.array([[1.0,2.0,3.0]],dtype=np.float32).T

Process 2:
    shared.z_current = np.zeros((30,1),dtype=np.float32)
    print(shared.z_current.T)
    shared.x_current = np.array([[0.0,0.0,0.0]],dtype=np.float32).T
    print(shared.x_current.T)
"""