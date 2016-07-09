"""

Schema: User
============

Account credentials and administrativa

Contains
--------

User: Useraccount object

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""
from hfos.schemata.defaultform import noform

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"

UserSchema = {
    'id': '#user',
    'type': 'object',
    'name': 'user',
    'properties': {
        'name': {'type': 'string'},
        'passhash': {'type': 'string'},
        'groups': {'type': 'array',
                   'items': {
                       'type': 'number'
                   },
                   },
        'uuid': {'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$',
                 'type': 'string',
                 'title': 'Unique User ID'
                 }
    }
}

User = {'schema': UserSchema, 'form': noform}
