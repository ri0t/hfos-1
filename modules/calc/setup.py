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

from setuptools import setup, find_packages

# This snippet needs to be inserted into nginx' configuration
# """
# # EtherCalc Module
# location /ethercalc/ {
#       proxy_pass      http://127.0.0.1:8000/;
# include         proxy_params;
# }
#
# location /zappa/socket/__local/ {
#       rewrite (.*) /ethercalc/$1;
# }
# """

setup(name="hfos-calc",
      version="0.0.1",
      description="hfos-calc",
      author="Hackerfleet Community",
      author_email="riot@c-base.org",
      url="https://github.com/hackerfleet/hfos-calc",
      license="GNU General Public License v3",
      packages=find_packages(),
      long_description="""HFOS - Calc
===========

A module to seamlessly integrate EtherCalc into HFOS.

This software package is a plugin module for HFOS.
""",
      dependency_links=[
      ],
      install_requires=[
          'hfos>=1.2.0',
      ],
      entry_points="""[hfos.components]
    spreadsheetwatcher=hfos.calc.spreadsheetwatcher:SpreadsheetWatcher
    [hfos.schemata]
    spreadsheet=hfos.calc.schemata.spreadsheet:Spreadsheet
    """,
      test_suite="tests.main.main",
      )
