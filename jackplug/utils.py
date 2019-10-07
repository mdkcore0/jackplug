#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class Configuration(object):
    """Configuration class for Jack and Plug"""
    _instance = None

    DEFAULT_PATHNAME = "/tmp/jack.plug"
    DEFAULT_TCP_PORT = "3559"

    # XXX read from config file
    ping_interval = 3000.0
    ping_max_liveness = 3

    def __init__(self):
        pass

    @classmethod
    def instance(self):
        if self._instance is None:
            self._instance = self()

        return self._instance


class IPCEndpoint():
    """IPCEndpoint

    A IPC transport wrapper
    """
    pathname = ""
    endpoint = ""

    # on linux, len(pathname) == 107
    def __init__(self, pathname=Configuration.DEFAULT_PATHNAME):
        """Class constructor

        :param pathname: IPC pathname to connect (default: /tmp/jack.plug)
        """
        self.pathname = pathname

        self.endpoint = "ipc://%s" % self.pathname


class TCPEndpoint():
    """TCPEndpoint

    A TCP transport wrapper
    """
    address = ""
    port = ""
    endpoint = ""

    def __init__(self, address, port=Configuration.DEFAULT_TCP_PORT):
        """Class constructor

        :param address: TCP IP address or interface to connect. Example:
            "127.0.0.1"
            "eth0"
            "*"
        A wildcard will bind the socket to all available interfaces.
        :param port: TCP PORT number to connect (default: 3559)
        """
        self.address = address
        self.port = port

        self.endpoint = "tcp://%s:%s" % (self.address, self.port)
