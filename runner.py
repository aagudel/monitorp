# Takes care of starting and stopping stuff
import sys
import threading
import importlib

import numpy as np

import utils.comm as comm
import utils.shared as shared

name = ""
mod = ""
modobj = None
command = ""
runnode = None
runthread = None
shared_states = set()

def _thread_helper(object):
    print("runner.py: Starting runnode")
    object.start()

def _listener_callback(msg):
    global runnode, runthread
    print("runner.py:",name,"received",msg.data)

    msg = msg.data.decode()

    if msg == 'start':
        importlib.reload(modobj)
        runnode = eval(command)
        # TODO can this be done without the helper function?
        runthread = threading.Thread(target=_thread_helper, args=(runnode,), daemon=True)
        runthread.start()
    elif msg == 'stop':
        print("runner.py: Stopping runnode")
        runnode.stop()
        #del runnode
    else:
        print("runner.py: Setting variable",msg)
        k,v = msg.split()
        setattr(runnode,k,v)

def _timeout_callback():
    sn = _utilnode.sock.getsockname();
    # if runnode.state == 'Stopped':
    #     up = "0"
    # elif runnode.state == 'Running':
    #     up = "1"
    if runthread is not None:
        if runthread.is_alive():
            up = "1"
        else:
            up = "0"
    else:
        up = "0"
    #This returns "0.0.0.0" but that cannot be used
    #alive = name+" "+up+" "+str(sn[0])+" "+str(sn[1])
    alive = name+" up="+up+" ip=127.0.0.1 port="+str(sn[1])
    for s in shared_states:
        alive += " "+s+"="+str(getattr(runnode,s))
    _utilnode.sock.sendto(alive.encode(), ("127.0.0.255",16000))
    #print("runner.py: sent "+alive)

_utilnode = comm.Node()
_utilnode.listener_callback = _listener_callback
_utilnode.timeout_callback = _timeout_callback
_utilnode._stablish_connection()

if __name__ == "__main__":

    print("runner.py: runner was called",sys.argv[1],sys.argv[2],sys.argv[3])

    name = sys.argv[1]
    mod = sys.argv[2]
    command = sys.argv[3]

    # TODO Ugly hack
    if name == 'neuro':
        shared_states.add('mode')
        shared_states.add('log')

    exec("import rt2."+mod+" as "+mod)
    modobj = importlib.import_module("rt2."+mod)
    runnode = eval(command)

    #while True:
        #time.sleep(1)
    _utilnode.start()
