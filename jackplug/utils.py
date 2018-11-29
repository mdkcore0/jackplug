#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class Configuration(object):
    """Configuration class for Jack and Plug"""
    _instance = None

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
