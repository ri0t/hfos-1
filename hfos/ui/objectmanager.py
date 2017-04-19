"""

Module: OM
==========

OM manager

:copyright: (C) 2011-2016 riot@c-base.org
:license: GPLv3 (See LICENSE)

"""

from uuid import uuid4

from hfos.events.system import objectcreation, objectchange, objectdeletion
from hfos.events.client import send
from hfos.component import ConfigurableComponent
from hfos.database import objectmodels, collections, ValidationError, \
    schemastore
from hfos.logger import verbose, debug, error, warn, critical, hilight

__author__ = "Heiko 'riot' Weinen <riot@c-base.org>"

WARNSIZE = 500


class ObjectManager(ConfigurableComponent):
    """
    Handles object requests and updates.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(ObjectManager, self).__init__('OM', *args)

        self.subscriptions = {}

        self.log("Started")

    def _check_permissions(self, subject, action, obj):
        if 'owner' in obj.perms[action]:
            try:
                if subject.uuid == obj.owner:
                    return True
            except AttributeError as e:
                self.log('Schema has ownership permission but no owner:',
                         obj._schema['name'], obj._fields, e, type(e), \
                         lvl=warn, exc=True)

        for role in subject.roles:
            if role in obj.perms[action]:
                return True
        return False

    def objectmanagerrequest(self, event):
        """OM event handler for incoming events
        :param event: OMRequest with incoming OM pagename and pagedata
        """

        self.log("Event: ", event.user.account.name, event.action,
                 event.data, lvl=verbose)

        self.log('Roles of user:', event.user.account.roles, lvl=hilight)

        action = event.action
        data = event.data

        if action not in ['subscribe', 'unsubscribe']:
            if 'schema' not in data or data['schema'] not in \
                    objectmodels.keys():
                thing = data['schema'] if 'schema' in data else None
                self.log("Schemata: ", objectmodels.keys())
                self.log("List for unavailable schema requested: ",
                         thing,
                         lvl=warn)
                result = {
                    'component': 'objectmanager',
                    'action': "noschema",
                    'data': thing
                }
                self.fireEvent(send(event.client.uuid, result))
                return
            else:
                schema = data['schema']

        if 'filter' in data:
            objectfilter = data['filter']
        else:
            objectfilter = {}

        result = None
        notification = None

        if action == "list":

            if 'fields' in data:
                fields = data['fields']
            else:
                fields = []

            objlist = []

            opts = schemastore[schema].get('options', {})
            hidden = opts.get('hidden', [])

            if objectmodels[schema].count(objectfilter) > WARNSIZE:
                self.log("Getting a very long list of items for ", schema,
                         lvl=warn)

            for item in objectmodels[schema].find(objectfilter):
                try:

                    if fields in ('*', ['*']):
                        itemfields = item.serializablefields()
                        for field in hidden:
                            itemfields.pop(field, None)
                        objlist.append(itemfields)
                    else:
                        listitem = {'uuid': item.uuid}

                        if 'name' in item._fields:
                            listitem['name'] = item._fields['name']

                        for field in fields:
                            if field in item._fields and not field in \
                                    hidden:
                                listitem[field] = item._fields[field]
                            else:
                                listitem[field] = None

                        objlist.append(listitem)
                except Exception as e:
                    self.log("Faulty object or field: ", e, type(e),
                             item._fields, fields, lvl=result,
                             exc=True)
            # self.log("Generated object list: ", objlist)

            result = {'component': 'objectmanager',
                      'action': 'list',
                      'data': {'schema': schema,
                               'list': objlist
                               }
                      }
        elif action == "search":
            # objectfilter['$text'] = {'$search': str(data['search'])}
            if 'fulltext' in data:
                objectfilter = {
                    'name': {
                        '$regex': str(data['search']),
                        '$options': '$i'
                    }
                }
            else:
                if isinstance(data['search'], dict):
                    objectfilter = data['search']
                else:
                    objectfilter = {}

            if 'fields' in data:
                fields = data['fields']
            else:
                fields = []

            reqid = data['req']

            objlist = []

            if collections[schema].count() > WARNSIZE:
                self.log("Getting a very long list of items for ", schema,
                         lvl=warn)

            opts = schemastore[schema].get('options', {})
            hidden = opts.get('hidden', [])

            self.log("Objectfilter: ", objectfilter, ' Schema: ', schema,
                     "Fields: ", fields,
                     lvl=warn)
            # for item in collections[schema].find(objectfilter):
            for item in collections[schema].find(objectfilter):
                self.log("Search found item: ", item, lvl=verbose)
                try:
                    # TODO: Fix bug in warmongo that needs this workaround:
                    item = objectmodels[schema](item)
                    listitem = {'uuid': item.uuid}
                    if fields in ('*', ['*']):
                        itemfields = item.serializablefields()
                        for field in hidden:
                            itemfields.pop(field, None)
                        objlist.append(itemfields)
                    else:
                        if 'name' in item._fields:
                            listitem['name'] = item.name

                        for field in fields:
                            if field in item._fields and field not in \
                                    hidden:
                                listitem[field] = item._fields[field]
                            else:
                                listitem[field] = None

                        objlist.append(listitem)
                except Exception as e:
                    self.log("Faulty object or field: ", e, type(e),
                             item._fields, fields, lvl=result)
            # self.log("Generated object search list: ", objlist)

            result = {'component': 'objectmanager',
                      'action': 'search',
                      'data': {'schema': schema,
                               'list': objlist,
                               'req': reqid
                               }
                      }

        elif action == "get":
            if 'subscribe' in data:
                subscribe = data['subscribe'] is True
            else:
                subscribe = False

            try:
                uuid = str(data['uuid'])
            except (KeyError, TypeError):
                uuid = ""

            opts = schemastore[schema].get('options', {})
            hidden = opts.get('hidden', [])

            if objectfilter == {}:
                if uuid == "":
                    self.log('Object with no filter/uuid requested:', schema,
                             data,
                             lvl=warn)
                    return
                objectfilter = {'uuid': uuid}

            storageobject = None

            storageobject = objectmodels[schema].find_one(objectfilter)

            if not storageobject:
                if uuid.upper == "CREATE":
                    # TODO: Fix this, a request for an existing object is a
                    # request for an existing object, a creation request is
                    # not.

                    self.log("Object not found, creating: ", data)

                    storageobject = objectmodels[schema](
                        {'uuid': str(uuid4())})

                    if "owner" in schemastore[schema]['schema'][
                        'properties']:
                        storageobject.owner = event.user.uuid
                        self.log("Attached initial owner's id: ",
                                 event.user.uuid)
                else:
                    self.log("Object not found and not willing to create.",
                             lvl=warn)
                    result = {
                        'component': 'objectmanager',
                        'action': 'noobject',
                        'data': {
                            'schema': schema,
                        }
                    }

            if storageobject:
                self.log(storageobject.perms, lvl=hilight)
                self.log("Object found, checking permissions: ", data)

                if not self._check_permissions(event.user.account, 'read',
                                               storageobject):
                    self._cancel_by_permission(schema, data, event.client)
                    return

                for field in hidden:
                    storageobject._fields.pop(field, None)

                if subscribe and uuid != "":
                    self.log('Updating subscriptions', lvl=debug)
                    if uuid in self.subscriptions:
                        if not event.client.uuid in self.subscriptions[uuid]:
                            self.subscriptions[uuid].append(event.client.uuid)
                    else:
                        self.subscriptions[uuid] = [event.client.uuid]

                result = {'component': 'objectmanager',
                          'action': 'get',
                          'data': storageobject.serializablefields()
                          }

        elif action == "subscribe":
            uuid = data

            if uuid in self.subscriptions:
                if not event.client.uuid in self.subscriptions[uuid]:
                    self.subscriptions[uuid].append(event.client.uuid)
            else:
                self.subscriptions[uuid] = [event.client.uuid]

            result = {'component': 'objectmanager',
                      'action': 'subscribe',
                      'data': {'uuid': uuid, 'success': True}
                      }

        elif action == "unsubscribe":
            # TODO: Automatic Unsubscription
            uuid = data

            if uuid in self.subscriptions:
                self.subscriptions[uuid].remove(event.client.uuid)

                if len(self.subscriptions[uuid]) == 0:
                    del (self.subscriptions[uuid])

            result = {'component': 'objectmanager',
                      'action': 'unsubscribe',
                      'data': {'uuid': uuid, 'success': True}
                      }

        elif action == "put":
            result, notification = self._put(schema, data, event.user,
                                             event.client)

        elif action == 'delete':
            result, notification = self._delete(schema, data, event.user,
                                                event.client)

        elif action == 'change':
            result, notification = self._change(schema, data, event.user,
                                                event.client)

        else:
            self.log("Unsupported action: ", action, event, event.__dict__,
                     lvl=warn)
            return

        if notification:
            try:
                self.fireEvent(notification)
            except Exception as e:
                self.log("Transmission error during notification: %s" % e,
                         lvl=result)

        if result:
            try:
                self.fireEvent(send(event.client.uuid, result))
            except Exception as e:
                self.log("Transmission error during response: %s" % e,
                         lvl=result)

    def updatesubscriptions(self, event):
        """OM event handler for to be stored and client shared objectmodels
        :param event: OMRequest with uuid, schema and object data
        """

        self.log("Event: '%s'" % event.__dict__)
        try:
            data = event.data
            self._updateSubscribers(data)

        except Exception as e:
            self.log("Error during subscription update: ", type(e), e,
                     exc=True)

    def _updateSubscribers(self, updateobject):
        # Notify frontend subscribers

        self.log('Notifying subscribers about update.', lvl=debug)
        if updateobject.uuid in self.subscriptions:
            update = {'component': 'objectmanager',
                      'action': 'update',
                      'data': updateobject.serializablefields()
                      }

            for recipient in self.subscriptions[updateobject.uuid]:
                self.log('Notifying subscriber: ', recipient, lvl=verbose)
                self.fireEvent(send(recipient, update))

    def _cancel_by_permission(self, schema, data, client):
        self.log('No permission!', lvl=error)

        msg = {
            'component': 'objectmanager',
            'action': 'Fail',
            'data': (False, 'No permission.', data)
        }
        self.fire(send(client.uuid, msg))

    def _change(self, schema, data, user, client):
        try:
            uuid = data['uuid']

            change = data['change']
            field = change['field']
            newdata = change['value']

        except KeyError as e:
            self.log("Update request with missing arguments!", data, e,
                     lvl=critical)

        storageobject = None

        try:
            storageobject = objectmodels[schema].find_one({'uuid': uuid})
        except Exception as e:
            self.log('Change for unknown object requested:', schema,
                     data, lvl=warn)

        if storageobject is not None:
            if not self._check_permissions(user, 'write', storageobject):
                self._cancel_by_permission(schema, data, client)
                return

            self.log("Changing object:", storageobject._fields, lvl=debug)
            storageobject._fields[field] = newdata

            self.log("Storing object:", storageobject._fields, lvl=debug)
            try:
                storageobject.validate()
            except ValidationError:
                self.log("Validation of changed object failed!",
                         storageobject, lvl=warn)

            storageobject.save()

            self.log("Object stored.")
            return True, None
        else:
            self.log("Object update failed. No object.", lvl=warn)
            return False, None

    def _put(self, schema, data, user, client):
        try:
            clientobject = data['obj']
            uuid = clientobject['uuid']
        except KeyError:
            self.log("Put request with missing arguments!", data, lvl=critical)
            return

        try:
            if uuid != 'create':
                storageobject = objectmodels[schema].find_one({'uuid': uuid})
            else:
                clientobject['uuid'] = str(uuid4())
                clientobject['owner'] = user.uuid
                storageobject = objectmodels[schema](clientobject)

            if storageobject:
                self.log("Updating object:", storageobject._fields, lvl=debug)
                storageobject.update(clientobject)

            else:
                storageobject = objectmodels[schema](clientobject)
                self.log("Storing object:", storageobject._fields, lvl=debug)
                try:
                    storageobject.validate()
                except ValidationError:
                    self.log("Validation of new object failed!", clientobject,
                             lvl=warn)

            storageobject.save()

            self.log("Object stored.")

            # Notify backend listeners

            if uuid == 'create':
                notification = objectcreation(storageobject.uuid, schema,
                                              client)
            else:
                notification = objectchange(storageobject.uuid, schema, client)

            self._updateSubscribers(storageobject)

            result = {'component': 'objectmanager',
                      'action': 'put',
                      'data': (True, storageobject.uuid),
                      }

            return result, notification

        except Exception as e:
            self.log("Error during object storage:", e, type(e), data,
                     lvl=error, exc=True)

    def _delete(self, schema, data, user, client):
        if True:  # try:
            uuid = data['uuid']

            if schema in objectmodels.keys():
                self.log("Looking for object to be deleted.", lvl=debug)
                storageobject = objectmodels[schema].find_one({'uuid': uuid})
                self.log("Found object.", lvl=debug)

                if not self._check_permissions(user, 'write', storageobject):
                    self._cancel_by_permission(schema, data, client)
                    return

                self.log("Fields:", storageobject._fields, "\n\n\n",
                         storageobject.__dict__)
                storageobject.delete()

                self.log("Preparing notification.", lvl=debug)
                notification = objectdeletion(uuid, schema, client)

                if uuid in self.subscriptions:
                    deletion = {'component': 'objectmanager',
                                'action': 'deletion',
                                'data': uuid
                                }
                    for recipient in self.subscriptions[uuid]:
                        self.fireEvent(send(recipient, deletion))

                    del (self.subscriptions[uuid])

                result = {'component': 'objectmanager',
                          'action': 'delete',
                          'data': (True, schema, storageobject.uuid),
                          }
                return result, notification
            else:
                self.log("Unknown schema encountered: ", schema, lvl=warn)
                # except Exception as e:
                #    self.log("Error during delete request: ", e, type(e),
                # lvl=error)
