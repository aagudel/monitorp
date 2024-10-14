# Main library utilitites
# TODO Once the library has a name this file can be renamed to it

import utils.comm as comm
import utils.kernel as kernel

# TODO this is going to be shared by all threads
# so it is not ideal. Find a better way.
_utilnode = comm.LocalNode(16001)
_utilnode.listener_callback = lambda: ...
_utilnode._stablish_connection()

# Execute call on kernel
def exec(command):
    command = kernel.name + " " + command
    #_utilnode.sock.sendto(command.encode(), ("192.168.1.255",16000))
    _utilnode.sock.sendto(command.encode(), ("127.0.0.1",16000))

