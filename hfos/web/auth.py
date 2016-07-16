"""

Module: Auth
============

Authentication (and later Authorization) system

:copyright: (C) 2011-2015 riot@hackerfleet.org
:license: GPLv3 (See LICENSE)

"""

from uuid import uuid4
from circuits import handler
from hfos.database import userobject, profileobject, clientconfigobject
from hfos.events import authentication, send
from hfos.logger import error, warn, debug, verbose
from hfos.component import ConfigurableComponent

__author__ = "Heiko 'riot' Weinen <riot@hackerfleet.org>"


class Authenticator(ConfigurableComponent):
    """
    Authenticates users against the database.
    """

    channel = "hfosweb"

    configprops = {}

    def __init__(self, *args):
        super(Authenticator, self).__init__('AUTH', *args)

    @handler("authenticationrequest", channel="auth")
    def authenticationrequest(self, event):
        """Handles authentication requests from clients
        :param event: AuthenticationRequest with user's credentials
        """

        # TODO: Refactor to simplify

        if event.auto:
            self.log("Automatic login request:")

            e = None
            try:
                clientconfig = clientconfigobject.find_one({'uuid':
                                                                event.requestedclientuuid})
            except Exception as e:
                clientconfig = None

            if clientconfig == None or clientconfig.autologin == False:
                self.log("Autologin failed:", e, lvl=error)
                return

            if clientconfig.autologin == True:

                try:
                    useraccount = userobject.find_one({'uuid':
                                                           clientconfig.useruuid})
                    self.log("Account: %s" % useraccount._fields, lvl=debug)
                except Exception as e:
                    self.log("No userobject due to error: ", e, type(e),
                             lvl=error)

                try:
                    userprofile = profileobject.find_one(
                        {'uuid': str(useraccount.uuid)})
                    self.log("Profile: ", userprofile,
                             useraccount.uuid, lvl=debug)

                    useraccount.passhash = ""
                    self.fireEvent(
                        authentication(useraccount.name, (
                            useraccount, userprofile, clientconfig),
                                       event.clientuuid,
                                       useraccount.uuid,
                                       event.sock),
                        "auth")
                    self.log("Autologin successful!", lvl=error)
                except Exception as e:
                    self.log("No profile due to error: ", e, type(e),
                             lvl=error)
        else:
            self.log("Auth request for ", event.username,
                     event.clientuuid)

            if (len(event.username) < 3) or (len(event.passhash) < 3):
                self.log("Illegal username or password received, "
                         "login cancelled",
                         lvl=warn)
                return

            useraccount = None
            clientconfig = None
            userprofile = None

            try:
                useraccount = userobject.find_one({'name': event.username})
                self.log("Account: %s" % useraccount._fields, lvl=debug)
            except Exception as e:
                self.log("No userobject due to error: ", e, type(e),
                         lvl=error)

            if useraccount:
                self.log("User found.")

                if useraccount.passhash == event.passhash:
                    self.log("Passhash matches, checking client and "
                             "profile.",
                             lvl=debug)

                    requestedclientuuid = event.requestedclientuuid

                    # Client requests to get an existing client
                    # configuration or has none

                    clientconfig = clientconfigobject.find_one(
                        {'uuid': requestedclientuuid})

                    if clientconfig:
                        self.log("Checking client configuration permissions",
                                 lvl=debug)
                        if clientconfig.useruuid != useraccount.uuid:
                            clientconfig = None
                            self.log("Unauthorized client configuration "
                                     "requested",
                                     lvl=warn)
                    else:
                        self.log("Unknown client configuration requested: ",
                                 requestedclientuuid, event.__dict__,
                                 lvl=warn)

                    if not clientconfig:
                        self.log("Creating new default client configuration")
                        # Either no configuration was found or requested
                        # -> Create a new client configuration

                        clientconfig = clientconfigobject()
                        clientconfig.uuid = event.clientuuid
                        clientconfig.name = "New client"
                        clientconfig.description = "New client configuration " \
                                                   "" \
                                                   "from " + useraccount.name
                        clientconfig.useruuid = useraccount.uuid
                        # TODO: Make sure the profile is only saved if the
                        # client could store it, too
                        clientconfig.save()

                    try:
                        userprofile = profileobject.find_one(
                            {'uuid': str(useraccount.uuid)})
                        self.log("Profile: ", userprofile,
                                 useraccount.uuid, lvl=debug)

                        useraccount.passhash = ""
                        self.fireEvent(
                            authentication(useraccount.name, (
                                useraccount, userprofile, clientconfig),
                                           event.clientuuid,
                                           useraccount.uuid,
                                           event.sock),
                            "auth")
                    except Exception as e:
                        self.log("No profile due to error: ", e, type(e),
                                 lvl=error)
                else:
                    self.log("Password was wrong!", lvl=warn)

                self.log("Done with Login request", lvl=debug)

            else:
                self.createuser(event)

    def createuser(self, event):
        self.log("Creating user")
        try:
            newuser = userobject(
                {'name': event.username, 'passhash': event.passhash,
                 'uuid': str(uuid4())})
            newuser.save()
        except Exception as e:
            self.log("Problem creating new user: ", type(e), e,
                     lvl=error)
            return
        try:
            newprofile = profileobject({'uuid': str(newuser.uuid)})
            self.log("New profile uuid: ", newprofile.uuid,
                     lvl=verbose)

            newprofile.components = {
                'enabled': ["dashboard", "map", "weather", "settings"]}
            newprofile.save()
        except Exception as e:
            self.log("Problem creating new profile: ", type(e),
                     e, lvl=error)
            return

        try:
            # TODO: Clone or reference systemwide default configuration
            newclientconfig = clientconfigobject()
            newclientconfig.uuid = event.clientuuid
            newclientconfig.name = "New client"
            newclientconfig.description = "New client configuration " \
                                          "from " + newuser.name
            newclientconfig.useruuid = newuser.uuid
            newclientconfig.save()
        except Exception as e:
            self.log("Problem creating new clientconfig: ",
                     type(e), e, lvl=error)
            return

        try:
            self.fireEvent(
                authentication(newuser.name,
                               (newuser, newprofile, newclientconfig),
                               event.clientuuid,
                               newuser.uuid,
                               event.sock),
                "auth")
            self.fireEvent(send(event.clientuuid, {'component': 'auth',
                                                   'action': 'new',
                                                   'data': 'registration '
                                                           'successful'
                                                   },
                                sendtype="client"), "hfosweb")
        except Exception as e:
            self.log("Error during new account confirmation transmission",
                     e, lvl=error)

    def profilerequest(self, event):
        """Handles client profile actions
        :param event:
        """

        self.log("Profile update %s" % event)

        if event.action != "update":
            self.log("Unsupported profile action: ", event, lvl=warn)
            return

        try:
            newprofile = event.data
            self.log("Updating with %s " % newprofile, lvl=debug)

            userprofile = profileobject.find_one({'uuid': event.user.uuid})

            self.log("Updating %s" % userprofile, lvl=debug)

            userprofile.update(newprofile)
            userprofile.save()

            self.log("Profile stored.")
            # TODO: Give client feedback
        except Exception as e:
            self.log("General profile request error %s %s" % (type(e), e),
                     lvl=error)
