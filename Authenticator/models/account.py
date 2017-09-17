"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Gnome Authenticator.

 Gnome Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 TwoFactorAuth is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Gnome Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""
from threading import Thread
from time import sleep

from gi.repository import GObject

from .code import Code
from .database import Database
from .keyring import Keyring
from .logger import Logger


class Account(GObject.GObject, Thread):
    __gsignals__ = {
        'code_updated': (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'name_updated': (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'counter_updated': (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'removed': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self, app):
        Thread.__init__(self)
        GObject.GObject.__init__(self)
        self.counter_max = 30
        self._alive = True
        self.counter = self.counter_max
        self._id = app[0]
        self.name = app[1]
        self._secret_code_id = app[2]
        self._secret_code = Keyring.get_by_id(self._secret_code_id)
        if self._secret_code:
            self._code = Code(self._secret_code)
            self._code_generated = True
        else:
            self._code = None
            self._code_generated = False
            Logger.error("Could not read the secret code,"
                         "the keyring keys were reset manually")
        self.logo = app[3]
        self.start()

    @property
    def secret_code(self):
        if self._code_generated:
            return self._code.secret_code
        return None

    def run(self):
        while self._code_generated and self._alive:
            self.counter -= 1
            if self.counter == 0:
                self.counter = self.counter_max
                self._code.update()
                self.emit("code_updated", self.secret_code)
            self.emit("counter_updated", self.counter)
            sleep(1)

    def kill(self):
        """
            Kill the row thread once it's removed
        """
        self._alive = False

    def remove(self):
        Database.get_default().remove(self._id)
        Keyring.remove(self._secret_code_id)
        self.emit("removed", True)
        Logger.debug("Account '{}' with id {} was removed".format(self.name,
                                                                  self._id))

    def set_name(self, name):
        Database.get_default().update(self._id, name, self.logo)
        self.name = name
        self.emit("name_updated", self.name)
