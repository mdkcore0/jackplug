"""
Copyright (c) 2016 BYNE. All rights reserved.

This example subclass PlugBase to act as a plug ("server").
"""

import sys
from jackplug.plug import PlugBase
from jackplug.utils import IPCEndpoint
from jackplug.utils import TCPEndpoint


class PlugTest(PlugBase):
    def __init__(self, *args, **kwargs):
        super(PlugTest, self).__init__(*args, **kwargs)

        self.on_timeout(self._timeout_occurred)
        self.start()

    def _timeout_occurred(self, service):
        print("Timeout occurred on service (plug) %s!" % service)

    def recv(self, service, message):

        print("Recv (%s): %s" % (message, service))
        print("Ok, answering :)")

        self.send(service, message)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Thou shalt run as: %s [ipc | tcp]" % sys.argv[0])
        sys.exit()

    use_ipc = False
    use_tcp = False

    if sys.argv[1] == "ipc":
        print("Using IPC transport")
        use_ipc = True
    elif sys.argv[1] == "tcp":
        print("Using TCP transport")
        use_tcp = True
    else:
        print("Unknown argument: %s" % sys.argv[1])
        sys.exit()

    print("Acting as Plug")

    endpoint = None
    if use_ipc:
        endpoint = IPCEndpoint(pathname="/tmp/jack.plug.test")
    elif use_tcp:
        endpoint = TCPEndpoint(address="*", port="1234")

    plug = PlugTest(endpoint=endpoint)
    print("Exiting Plug...")
