"""
Copyright (c) 2016 BYNE. All rights reserved.

Use PlugBase to create a new class and use as an object, or subclass Plug.

We are calling ZMQ's 'identity' as 'service', to ease the understanding of the
services.
"""

import logging
import signal
import threading
import time

import zmq
from zmq.utils import jsonapi
from zmq.eventloop import ioloop, zmqstream

from .utils import Configuration
from .utils import IPCEndpoint


log = logging.getLogger("JackPlug")


class PlugBase(object):
    """Base Plug class

    This handles low level communication (plus hearbeat), microservice side"""
    _services_ping = dict()
    _timeout_callback = None
    _connection_callback = None

    def __init__(self, endpoint=IPCEndpoint()):
        """Class constructor

        :param pathname: IPC pathname to be used (default: /tmp/jack.plug)
        """
        self.context = zmq.Context.instance()

        self.socket = self.context.socket(zmq.ROUTER)

        self.socket.bind(endpoint.endpoint)

        # XXX check zmq.asyncio.Socket with recv_multipart
        self.socket_stream = zmqstream.ZMQStream(self.socket)
        self.socket_stream.on_recv(self._recv)

        self._conf = Configuration.instance()
        self._heartbeat_loop = ioloop.PeriodicCallback(
            self.heartbeat, self._conf.ping_interval)

        self._heartbeat_loop.start()

    def close(self):
        """Do close Plug with its socket and loopers"""
        ioloop.IOLoop.instance().stop()

        try:
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket_stream.close()
            self.socket.close()
        except Exception as e:
            log.error("An error occurred while closing socket: %s", e)

    @staticmethod
    def set_logger(logger):
        global log

        log.propagate = False
        log = logger

    def heartbeat(self):
        """Check if known jacks are alive (pinging us)"""
        services = list(self._services_ping.keys())
        for service in services:
            last_ping = self._services_ping[service]['last_ping']
            liveness = self._services_ping[service]['liveness']

            now = self._now()
            if now - last_ping > self._conf.ping_interval:
                liveness = liveness - 1
                max_str = ""
                if liveness + 1 == self._conf.ping_max_liveness:
                    max_str = " (MAX) | interval: %sms" %\
                            self._conf.ping_interval

                log.debug("Plug: Service '%s' liveness: %s%s", service,
                          liveness, max_str)

                if liveness == 0:
                    if self._services_ping[service]['alive']:
                        log.debug("Plug: Service '%s' seems unavailable now",
                                  service)

                        self._services_ping[service]['last_ping'] = now
                        self._services_ping[service]['liveness'] = liveness
                        self._services_ping[service]['alive'] = False

                        if self._timeout_callback:
                            self._timeout_callback(service.decode())
                elif liveness < 0:
                    del self._services_ping[service]
                else:
                    self._services_ping[service]['last_ping'] = now
                    self._services_ping[service]['liveness'] = liveness

    def _recv(self, message):
        """Receive a message from any jack

        Internally handles messages from jacks and prepare them to be consumed
        by the application.
        :param message: received raw message
        """
        service, message = tuple(message)
        message = jsonapi.loads(message)

        # setup heartbeat settings for this service (or update it)
        # any message is treated as ping
        service_ping = {
            'last_ping': self._now(),
            'liveness': self._conf.ping_max_liveness,
        }

        if service in self._services_ping:
            self._services_ping[service].update(service_ping)
        else:
            service_ping['alive'] = False
            service_ping['id'] = -1
            self._services_ping[service] = service_ping

        # do not propagate ping messages
        if message.get('event', None) == 'ping':
            identity = message.get('data')['id']

            if 'alive' in self._services_ping[service] and\
               not self._services_ping[service]['alive']:
                self._services_ping[service]['alive'] = True

            if 'id' in self._services_ping[service] and\
               self._services_ping[service]['id'] != identity:
                self._services_ping[service]['id'] = identity

                if self._connection_callback:
                    self._connection_callback(service.decode(), True)

            return

        self.recv(service, message)

    def recv(self, service, message):
        """Receive a message

        Should be reimplemented on the derived class.
        :param service: which jack sent this message
        :param message: received message
        """
        raise NotImplementedError

    def send(self, service, message):
        """Send a message

        Tries to send a message to a given service.
        :param service: destination jack
        :param message: message to be sent
        """
        if self.socket.closed:
            return

        self.socket.send_multipart([service, jsonapi.dumps(message)])

    def start(self):
        """Initialize all plug loopers"""
        loop = ioloop.IOLoop.instance()

        # handle signal if, and only, if we are running on the main thread
        if isinstance(threading.current_thread(), threading._MainThread):
            signal.signal(signal.SIGINT, lambda sig, frame:
                          loop.add_callback_from_signal(self.close))

        try:
            loop.start()
        except RuntimeError as e:
            log.debug("Plug: %s", e)
        except zmq.ZMQError as e:
            if e.errno != zmq.ENOTSOCK:
                log.error("Error starting IOLoop: %s", e)

    def restart(self):
        del self.socket_stream
        self._heartbeat_loop.stop()

        self.socket_stream = zmqstream.ZMQStream(self.socket)
        self.socket_stream.on_recv(self._recv)

        self._heartbeat_loop = ioloop.PeriodicCallback(
            self.heartbeat, self._conf.ping_interval)

        self._heartbeat_loop.start()

        self.start()

    # apocalypse
    def _now(self):
        """Helper function to get current time as milliseconds"""
        return time.time() * 1000.0

    def on_connection(self, connection_callback=None):
        """Register a callback to be called when a connection occurs

        :param connection_callback: function to be set as callback. If 'None',
        it will unregister the callback.
        """
        self._connection_callback = connection_callback

    def on_timeout(self, timeout_callback=None):
        """Register a callback to be called when a timeout occurs

        :param timeout_callback: function to be set as callback. If 'None', it
        will unregister the callback.
        """
        self._timeout_callback = timeout_callback


class Plug(PlugBase):
    """Plug class, ready for use python object"""
    _listener = None

    def __init__(self, listener=None, **kwargs):
        """Class constructor

        :param listener: callback function to be called when a new message is
        received
        """
        super(Plug, self).__init__(**kwargs)

        self._listener = listener
        self.start()

    def recv(self, service, message):
        """PlugBase.recv reimplementation

        Show how to handle received messages
        :param service: which jack sent this message
        :param message: received message
        """
        if self._listener:
            self._listener(service, message)
        else:
            log.debug("Plug: Listener not set for service %s", service)
