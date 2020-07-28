#!/usr/bin/env python2

from __future__ import absolute_import

import sys, os, logging
import collections, types
import subprocess
import re
import gi

from .depsolver import *

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

LOG = logging.getLogger(__name__)

GstUtils = [
    '/usr/bin/gst-inspect-1.0',
    '/usr/bin/gst-launch-1.0',
    '/usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-ptp-helper',
    '/usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-plugin-scanner',
]
GstDefaultPlugins = [
    'coreelements'
]

class GstMinimize(object):
    def __init__(self):
        self.plugins = list()

        ## Init GObject and GStreamer libs
        Gst.init(None)
        GObject.threads_init()

        ## Read the gstreamer plugin list
        registry = Gst.Registry.get()
        plugins = Gst.Registry.get().get_plugin_list()
        keyfunc = lambda a: a.get_name()
        self.registry = dict( (keyfunc(p), p) for p in plugins)

        # Register the default plugins
        for plugin in GstDefaultPlugins:
            self.add_plugin(plugin)

    def add_plugin(self, plugin):
        if plugin not in self.registry:
            LOG.error('Plugin %s was not found.', plugin)
        else:
            self.plugins.append (plugin)

    def get_files(self):
        solver = DependencySolver()
        file_list = set()

        ## Add the GStreamer Utilities
        for path in GstUtils:
            file_list.add(path)
            solver.add(path)

        ## Add the plugin libraries
        for key in self.plugins:
            plugin_path = self.registry[key].get_filename()
            file_list.add(plugin_path)
            solver.add(plugin_path)

        ret = file_list.union(solver.deps)
        return sorted(ret)
