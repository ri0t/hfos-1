#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# HFOS - Hackerfleet Operating System
# ===================================
# Copyright (C) 2011-2017 Heiko 'riot' Weinen <riot@c-base.org> and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Heiko 'riot' Weinen"
__license__ = "GPLv3"

"""


Module: Debugger
================

Debugger overlord


"""

import json
from uuid import uuid4

from circuits.core.events import Event
from circuits.core.handlers import reprhandler
from circuits.io import stdin

from hfos.component import ConfigurableComponent, handler
from hfos.events.client import send
from hfos.events.system import frontendbuildrequest, componentupdaterequest, \
    logtailrequest, debugrequest
from hfos.logger import hfoslog, critical, warn, debug, verbose

try:
    import objgraph
    from guppy import hpy
except ImportError:
    objgraph = None
    hpy = None
    hfoslog("Debugger couldn't import objgraph and/or guppy.", lvl=warn,
            emitter="DBG")


class HFDebugger(ConfigurableComponent):
    """
    Handles various debug requests.
    """
    configprops = {
        'notificationusers': {
            'type': 'array',
            'title': 'Notification receivers',
            'description': 'Users that should be notified about exceptions.',
            'default': [],
            'items': {'type': 'string'}
        }
    }
    channel = "hfosweb"

    def __init__(self, root=None, *args):
        super(HFDebugger, self).__init__("DBG", *args)

        if not root:
            from hfos.logger import root
            self.root = root
        else:
            self.root = root

        if hpy is not None:
            # noinspection PyCallingNonCallable
            self.heapy = hpy()
        else:
            self.log("Can't use heapy. guppy package missing?")

        self.log("Started. Notification users: ",
                 self.config.notificationusers)

    @handler("exception", channel="*", priority=100.0)
    def _on_exception(self, error_type, value, traceback,
                      handler=None, fevent=None):

        try:
            s = []

            if handler is None:
                handler = ""
            else:
                handler = reprhandler(handler)

            msg = "ERROR"
            msg += "{0:s} ({1:s}) ({2:s}): {3:s}\n".format(
                handler, repr(fevent), repr(error_type), repr(value)
            )

            s.append(msg)
            s.extend(traceback)
            s.append("\n")

            self.log("\n".join(s), lvl=critical)

            alert = {
                'component': 'hfos.alert.manager',
                'action': 'danger',
                'data': {
                    'message': "\n".join(s),
                    'title': 'Exception Monitor'
                }
            }
            for user in self.config.notificationusers:
                self.fireEvent(send(None, alert, username=user,
                                    sendtype='user'))

        except Exception as e:
            self.log("Exception during exception handling: ", e, type(e),
                     lvl=critical)

    @handler(debugrequest)
    def debugrequest(self, event):
        try:
            self.log("Event: ", event.__dict__, lvl=critical)

            if event.action == "storejson":
                self.log("Storing received object to /tmp", lvl=critical)
                fp = open('/tmp/hfosdebugger_' + str(
                    event.user.useruuid) + "_" + str(uuid4()), "w")
                json.dump(event.data, fp, indent=True)
                fp.close()
            if event.action == "memdebug":
                self.log("Memory hogs:", lvl=critical)
                objgraph.show_most_common_types(limit=20)
            if event.action == "growth":
                self.log("Memory growth since last call:", lvl=critical)
                objgraph.show_growth()
            if event.action == "graph":
                objgraph.show_backrefs([self.root], max_depth=42,
                                       filename='backref-graph.png')
                self.log("Backref graph written.", lvl=critical)
            if event.action == "exception":
                class TestException(BaseException):
                    pass

                raise TestException
            if event.action == "heap":
                self.log("Heap log:", self.heapy.heap(), lvl=critical)
            if event.action == "buildfrontend":
                self.log("Sending frontend build command")

                self.fireEvent(frontendbuildrequest(force=True), "setup")
            if event.action == "logtail":
                self.fireEvent(logtailrequest(event.user, None, None,
                                              event.client), "logger")

        except Exception as e:
            self.log("Exception during debug handling:", e, type(e),
                     lvl=critical)


class CLI(ConfigurableComponent):
    """
    Command Line Interface support
    """

    configprops = {}

    def __init__(self, *args):
        super(CLI, self).__init__("CLI", *args)

        self.hooks = {}

        self.log("Started")
        stdin.register(self)

    @handler("read", channel="stdin")
    def stdin_read(self, data):
        """read Event (on channel ``stdin``)
        This is the event handler for ``read`` events specifically from the
        ``stdin`` channel. This is triggered each time stdin has data that
        it has read.
        """

        data = data.strip().decode("utf-8")
        self.log("Incoming:", data, lvl=verbose)

        if len(data) == 0:
            return

        if data[0] == "/":
            cmd = data[1:].upper()
            args = []
            if ' ' in cmd:
                cmd, args = cmd.split(' ', maxsplit=1)
                args = args.split(' ')
            if cmd in self.hooks:
                self.log('Firing hooked event:', cmd, args, lvl=debug)
                self.fireEvent(self.hooks[cmd](args))
            # TODO: Move these out, so we get a simple logic here
            if cmd == 'FRONTEND':
                self.log("Sending %s frontend rebuild event" % ("(forced)"
                                                                if 'FORCE'
                                                                   in args
                                                                else ''))
                self.fireEvent(frontendbuildrequest(force='FORCE' in args,
                                                    install='INSTALL' in args),
                               "setup")
            if cmd == 'BACKEND':
                self.log("Sending backend reload event")
                self.fireEvent(componentupdaterequest(force=False), "setup")

    @handler('cli_register_event')
    def register_event(self, event):
        self.log('Registering event hook:', event.cmd, event.thing,
                 pretty=True, lvl=debug)
        self.hooks[event.cmd.upper()] = event.thing


class clicommand(Event):
    def __init__(self, cmd, cmdargs, *args, **kwargs):
        super(clicommand, self).__init__(*args, **kwargs)
        self.cmd = cmd
        self.args = cmdargs


class cli_register_event(Event):
    def __init__(self, cmd, thing, *args, **kwargs):
        super(cli_register_event, self).__init__(*args, **kwargs)
        self.cmd = cmd
        self.thing = thing
