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

Module: Event Playback
======================

A controllable event playback utility component


"""

from hfos.component import ConfigurableComponent

# from hfos.logger import error, warn
# from time import time


class Playback(ConfigurableComponent):
    """
    Event Playback

    Produces
    * outgoing events, that have previously been recorded to a readable json
    file
    """

    configprops = {}

    def __init__(self, *args):
        super(Playback, self).__init__("PLAY", *args)

        self.log("Started")
