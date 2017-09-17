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
from gettext import gettext as _

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio

from ..models import Logger, Settings
from .change_password import PasswordWindow


class SettingsBox(Gtk.ListBox):
    def __init__(self):
        Gtk.ListBox.__init__(self)
        self.get_style_context().add_class("settings-listbox")
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)
        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.connect("realize", self._resize_childs)

    def _resize_childs(self, listbox):
        """Make sure that all the childs have the same height."""
        max_height = 0
        for row in listbox.get_children():
            height = row.get_allocated_height()
            if height > max_height:
                max_height = height
        for row in listbox.get_children():
            row.props.height_request = max_height

    def append(label, widget):
        """Setup a listbox from a list of (label, widget)."""
        # Setup the listbox

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                      spacing=6)
        label_ = Gtk.Label(label)
        label_.get_style_context().add_class("settings-listbox-label")

        box.pack_start(label_, False, False, 12)
        box.pack_end(widget, False, False, 12)

        listboxrow = Gtk.ListBoxRow()
        listboxrow.get_style_context().add_class("settings-listbox-row")
        listboxrow.add(box)

        self.add(listboxrow)


class SettingsWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_destroy_with_parent(True)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_resizable(False)
        self.set_size_request(500, 300)
        self.set_title(_("Settings"))
        self._build_widgets()

    def _build_widgets(self):
        """Build the Settings Window widgets."""
        # Stack Switcher
        stack_switcher = Gtk.StackSwitcher()

        # HeaderBar
        headerbar = Gtk.HeaderBar()
        headerbar.set_title(_("Settings"))
        headerbar.set_show_close_button(True)
        headerbar.set_custom_title(stack_switcher)
        self.set_titlebar(headerbar)

        # Main window container
        self.main = Gtk.Stack()
        stack_switcher.set_stack(self.main)
        self._build_behaviour_settings()
        self._build_account_settings()
        self.add(self.main)

        """
        self.builder = Gtk.Builder.new_from_resource('/org/gnome/Authenticator/settings.ui')
        self.builder.connect_signals({
            "on_change_password" : self.__new_password_window,
            'on_password_toggle': self.__on_password_activated,
            "on_change_auto_lock_time" : self.__on_auto_lock_time_changed,
            "on_key_press": self.__on_key_press,
            "on_close_window": self._close_window
        })
        self.window = self.builder.get_object("SettingsWindow")
        self.window.set_transient_for(parent)
        logging.debug("Settings Window created")

        self.auto_lock_check = self.builder.get_object("AutoLockCheck")
        self.auto_lock_spin = self.builder.get_object("AutoLockSpin")
        self.password_check = self.builder.get_object("PasswordCheck")
        self.password_button = self.builder.get_object("PasswordButton")
        settings = Settings.get_default()

        settings.bind('state', self.password_check, 'active', Gio.SettingsBindFlags.DEFAULT)
        settings.bind('state', self.password_button, 'sensitive', Gio.SettingsBindFlags.INVERT_BOOLEAN)

        settings.bind('state', self.auto_lock_check, 'sensitive', Gio.SettingsBindFlags.GET)
        settings.bind('auto-lock', self.auto_lock_check, 'active', Gio.SettingsBindFlags.DEFAULT)

        settings.bind('auto-lock', self.auto_lock_spin, 'sensitive', Gio.SettingsBindFlags.GET)
        # Restore settings
        _auto_lock_time = settings.get_auto_lock_time()
        self.auto_lock_spin.set_value(_auto_lock_time)
        """

    def _build_behaviour_settings(self):
        """Build the Behaviour settings container."""
        container = SettingsBox()

        self.main.add_titled(container, "behaviour", _("Behaviour"))

    def _build_account_settings(self):
        """Build the Account settings container."""
        container = SettingsBox()

        self.main.add_titled(container, "account", _("Account"))

    def show_window(self):
        """Show the settings window."""
        self.show_all()
        self.present()

    def __on_key_press(self, key, key_event):
        """
            Keyboard Listener handler
        """
        key_name = Gdk.keyval_name(key_event.keyval)
        if key_name.lower() == "escape":
            self._close_window()

    def __new_password_window(self, *args):
        """
            Show a new password window
        """
        password_win = PasswordWindow()
        password_win.set_attached_to(self)
        password_win.show_window()

    def __on_auto_lock_time_changed(self, spin_btn):
        """
            Update auto lock time
        """
        Settings.get_default().auto_lock_time = spin_btn.get_value_as_int()
        Logger.info("[SettingsWindow] Auto lock time updated")

    def __on_password_activated(self, checkbutton, *args):
        """Update password state : enabled/disabled"""
        settings = Settings.get_default()
        checkbutton_status = checkbutton.get_active()
        # Show the password setting window
        # If no password was set before
        if checkbutton_status and not settings.password:
            self.__new_password_window()
        if checkbutton_status:
            Logger.info("[SettingsWindow] Password enabled")
        else:
            Logger.info("[SettingsWindow] Password disabled")

    def _close_window(self, *args):
        """Close the window"""
        Logger.debug("[SettingsWindow] Closed")
        self.destroy()
