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

Provisioning: Layers
====================

Contains
--------

Predefined open layers.


"""

from hfos.provisions.base import provisionList
from hfos.database import objectmodels
from hfos.logger import hfoslog

layers = [
    {
        "name": "OpenStreetMap",
        "uuid": "2837298e-a3e8-4a2e-8df2-f475554d2f23",
        "shared": True,
        "description": "Open Street Map",
        "baselayer": True,
        "url": "http://hfoshost/tilecache/a.tile.osm.org/{z}/{x}/{y}.png",
        "layerOptions": {
            "continuousWorld": False,
            "attribution": "&copy; <a "
                           "href=\"http://osm.org/copyright\">OpenStreetMap"
                           "</a> contributors"
        },
        "type": "xyz"
    },
    {
        "name": "OpenStreetMap-Overlay",
        "uuid": "3a4cceaa-3e8b-4f65-85ee-2ff9f6de6a71",
        "shared": True,
        "description": "Open Street Map Overlay",
        "baselayer": False,
        "url": "http://hfoshost/tilecache/a.tile.osm.org/{z}/{x}/{y}.png",
        "layerOptions": {
            "opacity": 0.5,
            "continuousWorld": False,
            "attribution": "&copy; <a "
                           "href=\"http://osm.org/copyright\">OpenStreetMap"
                           "</a> contributors"
        },
        "type": "xyz"
    },
    {
        "name": "OpenTopographyMap",
        "uuid": "958b1006-2688-44b0-99be-a67728228e08",
        "shared": True,
        "description": "Open Topography Map",
        "url": 'http://hfoshost/tilecache/{s}.tile.opentopomap.org/{z}/{x}/{'
               'y}.png',
        "layerOptions": {
            "maxZoom": 16,
            "attribution": '<a '
                           'href="http://viewfinderpanoramas.org">SRTM</a> | '
                           'Map style: &copy;\
<a href="https://opentopomap.org">OpenTopoMap</a>'
        },
        "type": "xyz"
    },
    {
        "name": "ESRI-Sat-Shaded",
        "uuid": "19e5704e-68a2-435e-9f21-ac389973cc7a",
        "shared": True,
        "description": "Shaded Satellite relief image data from ESRI",
        "baselayer": True,
        "url": 'http://hfoshost/tilecache/server.arcgisonline.com/ArcGIS/rest'
               '/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}',
        "layerOptions": {
            "attribution": 'Tiles &copy; Esri &mdash; Source: Esri',
            "maxZoom": 13
        },
        "type": "xyz"
    },
    {
        "name": "OpenCycleMap",
        "uuid": "4e4809c8-111f-4910-838f-62fd7eb0c038",
        "shared": True,
        "baselayer": True,
        "description": "Open Cycle Map",
        "url": "http://hfoshost/tilecache/a.tile.opencyclemap.org/cycle/{"
               "z}/{x}/{y}.png",
        "layerOptions": {
            "continuousWorld": True,
            "attribution": "&copy; <a "
                           "href=\"http://www.opencyclemap.org/copyright"
                           "\">OpenCycleMap</a> contributors"
        },
        "type": "xyz"
    },
    {
        "name": "OpenSeaMapBase",
        "uuid": "ab3f1d76-cb26-4ddf-9811-05527e0d3640",
        "shared": True,
        "description": "Open Sea Map Baselayer",
        "baselayer": True,
        "url": "http://hfoshost/tilecache/tiles.openseamap.org/seamark/{z}/{"
               "x}/{y}.png",
        "layerOptions": {
            "attribution": "&copy; OpenSeaMap contributors",
            "minZoom": 7
        },
        "type": "xyz"
    },
    {
        "name": "OpenSeaMap",
        "uuid": "2bedb0d2-be9f-479c-9516-256cd5a0baae",
        "shared": True,
        "description": "Open Sea Map",
        "baselayer": False,
        "url": "http://hfoshost/tilecache/tiles.openseamap.org/seamark/{z}/{"
               "x}/{y}.png",
        "layerOptions": {
            "attribution": "&copy; OpenSeaMap contributors",
            "minZoom": 7
        },
        "type": "xyz"
    },
    {
        "name": "Hillshade-Europe",
        "uuid": "fefa0221-850c-4e35-9d5d-04244521c32a",
        "shared": True,
        "description": "Hillshade layer for Europe from GIScience",
        "baselayer": False,
        "visible": False,
        "url": "http://hfoshost/tilecache/129.206.228.72/cached/hillshade",
        "layerOptions": {
            "crs": {
                "code": "EPSG:900913",
                "Simple": {
                    "transformation": {
                        "_d": 0,
                        "_b": 0,
                        "_a": 1,
                        "_c": -1
                    },
                    "projection": {}
                },
                "transformation": {
                    "_d": 0.5,
                    "_b": 0.5,
                    "_a": 0.15915494309189535,
                    "_c": -0.15915494309189535
                },
                "projection": {
                    "MAX_LATITUDE": 85.0511287798
                }
            },
            "attribution": "Hillshade layer by GIScience "
                           "http://www.osm-wms.de",
            "layers": "europe_wms:hs_srtm_europa",
            "format": "image/png",
            "opacity": 0.25
        },
        "type": "wms"
    },
    {
        "name": "ESRI-Sat-Shaded-Base",
        "uuid": "582d2ef3-759e-49f7-81ab-8dbe224d618a",
        "shared": True,
        "description": "Shaded Satellite relief image data from ESRI as "
                       "base layer",
        "baselayer": True,
        "visible": False,
        "url": "http://hfoshost/tilecache/server.arcgisonline.com/ArcGIS"
               "/rest/services/World_Imagery/MapServer/\
tile/{z}/{y}/{x}",
        "layerOptions": {
            "continuousWorld": True,
            "opacity": 1,
            "attribution": "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, "
                           "USDA, USGS, AEX, GeoEye, Getmapping,\
Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
        },
        "type": "xyz"
    },
    {
        "name": "ESRI-Sat-Shaded-Overlay",
        "uuid": "72611470-39b3-4982-8991-2ad467b06fc9",
        "shared": True,
        "description": "Shaded Satellite relief image data from ESRI as "
                       "Overlay",
        "baselayer": False,
        "visible": False,
        "url": "http://hfoshost/tilecache/server.arcgisonline.com/ArcGIS"
               "/rest/services/World_Imagery/MapServer/\
tile/{z}/{y}/{x}",
        "layerOptions": {
            "continuousWorld": True,
            "opacity": 0.25,
            "attribution": "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, "
                           "USDA, USGS, AEX, GeoEye, Getmapping,\
Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
        },
        "type": "xyz"
    },
    {
        "name": "OpenFireMap",
        "uuid": "06a6b913-039a-4638-b495-748b042002df",
        "shared": True,
        "description": "Open Fire Map containing data about local fire safety",
        "baselayer": False,
        "visible": False,
        "url": "http://hfoshost/tilecache/openfiremap.org/hytiles/{z}/{x}/{"
               "y}.png",
        "layerOptions": {
            "continuousWorld": True,
            "attribution": "&copy; <a "
                           "href=\"http://www.openfiremap.org\">OpenFireMap"
                           "</a> contributors"
        },
        "type": "xyz"
    },
    {
        "name": "OpenWeatherMap-Clouds",
        "uuid": "7b73024e-9ede-4c90-821d-9c24c0cc0ff6",
        "shared": True,
        "description": "Open Weather Map showing clouds",
        "baselayer": False,
        "url": "http://hfoshost/tilecache/a.tile.openweathermap.org/map"
               "/clouds/{z}/{x}/{y}.png",
        "layerOptions": {
            "continuousWorld": True,
            "attribution": "&copy; OpenWeatherMap"
        },
        "type": "xyz"
    }
]


def provision(**kwargs):
    provisionList(layers, objectmodels['layer'], **kwargs)
    hfoslog('Provisioning: Layers: Done.', emitter='PROVISIONS')


if __name__ == "__main__":
    provision()
