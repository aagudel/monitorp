import time,threading
import inspect

class State:
    pass

state = State()
_command = (None,None)

# TODO In the future consider this instead:
# https://docs.python.org/3/library/queue.html
def exec(name,param):
    global _command
    _command = (name,param)

def _thread_helper(object):
    object.start()

def start():
    global _command
    while True:
        if _command[0] == "start":            
            # TODO Maybe the way start() works should be the responsibility of the
            # object? either to start a process or thread or whatever ...
            module = state.modules[_command[1]]
            if inspect.ismodule(module):
                threading.Thread(target=module.start, daemon=True).start()
            else:
                # TODO can this be done without the helper function?
                threading.Thread(target=_thread_helper, args=(module,), daemon=True).start()
            
        elif _command[0] == "stop":
            module = state.modules[_command[1]]
            module.stop()
        
        _command = (None,None)
        time.sleep(0.1)