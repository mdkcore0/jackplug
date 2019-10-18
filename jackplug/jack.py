#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Copyright (c) 2016 BYNE. All rights reserved.

Use JackBase to create a new class or subclass it.

We are calling ZMQ's 'identity' as 'service', to ease the understanding of
services.
"""

import signal
import uuid

import zmq
from zmq.utils import jsonapi
from zmq.eventloop import ioloop, zmqstream

from .utils import Configuration
from .utils import IPCEndpoint

from simb.pilsner import log as logging

log = logging.getLogger('Service')


class JackBase(object):
    """Base Jack class

    This handles low level communication (plus heartbeat), server side"""
    _timeout = None

    def __init__(self, service, endpoint=IPCEndpoint()):
        """Class contructor

        :param service: name (or identifier) of this jack
        :param endpoint: IPCEndpoint(pathname) or TCPEndpoint(address, port) to
        connect (default pathname: /tmp/jack.plug, default port: 3559)
        """
        self.context = zmq.Context.instance()

        self.socket = self.context.socket(zmq.DEALER)
        self._identity = str(uuid.uuid4())
        self.socket.identity = service.encode()

        # use with flags=zmq.DONTWAIT on send; also, any new message sent after
        # reaching HWM will be discarded (dealer)
        self.socket.setsockopt(zmq.SNDHWM, 3)

        # use with close to discard all messages
        # self.socket.setsockopt(zmq.LINGER, 0)

        # return immediately if message cannot be sent
        self.socket.setsockopt(zmq.SNDTIMEO, 0)

        # do not queue message if connection not completed (zmq level)
        self.socket.setsockopt(zmq.IMMEDIATE, 1)

        self.socket.connect(endpoint.endpoint)

        self.socket_stream = zmqstream.ZMQStream(self.socket)
        self.socket_stream.on_recv(self._recv)

        self._conf = Configuration.instance()
        self._liveness = self._conf.ping_max_liveness

        self._heartbeat_loop = ioloop.PeriodicCallback(
            self.heartbeat, self._conf.ping_interval)

        self._heartbeat_loop.start()

    def close(self):
        """Do close Jack with its socket and loopers

        Can be reimplemented on the inherited class, but do not forget to call
        this base function to proper cleanup.
        """
        self._heartbeat_loop.stop()

        ioloop.IOLoop.instance().stop()
        self.socket_stream.close()
        self.socket.close()

    def heartbeat(self):
        """Send a ping message to the other endpoint"""
        JackBase.send(self, {"event": "ping", "data": {'id': self._identity}})

    def _recv(self, message):
        self.recv(jsonapi.loads(message[0]))

    def recv(self, message):
        """Receive a message

        Should be reimplemented on the derived class.

        :param message: received message
        """
        raise NotImplementedError

    def send(self, message):
        """Send a message

        Tries to send a message to the other endpoint. Also, check service
        liveness.
        :param message: message to be sent
        """
        try:
            self.socket.send_json(message)
        except zmq.Again as e:
            if message.get('event', None) == 'ping':
                self._liveness = self._liveness - 1

                max_str = ""
                if self._liveness + 1 == self._conf.ping_max_liveness:
                    max_str = " (MAX) | interval: %sms" %\
                            self._conf.ping_interval

                if self._liveness >= 0:
                    log.info("Jack: liveness: %s%s", self._liveness, max_str)

                if self._liveness == 0:
                    log.error("Jack: Plug seems unavailable now")
                    if self._timeout:
                        self._timeout()
            else:
                log.error("Jack: Could not send message: %s", e)
        except Exception as e:
            log.error("Jack: Error: %s", e)
        else:
            self._liveness = self._conf.ping_max_liveness

    def start(self):
        """Initialize all service loopers"""
        loop = ioloop.IOLoop.instance()

        signal.signal(signal.SIGINT, lambda sig, frame:
                      loop.add_callback_from_signal(self.close))

        try:
            loop.start()
        except RuntimeError as e:
            log.debug("Jack: %s", e)
        except zmq.ZMQError as e:
            if e.errno != zmq.ENOTSOCK:
                log.error("Error starting IOLoop: %s", e)

    def on_timeout(self, timeout_callback=None):
        """Register a callback to be called when a timeout occurs


        :param timeout_callback: function to be set as callback. If 'None', it
        will unregister the callback.
        """

        self._timeout = timeout_callback
