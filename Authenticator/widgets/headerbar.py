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
from abc import abstractmethod, ABCMeta
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio
from gettext import gettext as _

from ..models import Logger, Settings, Database
from ..utils import is_gnome


class HeaderBarBtn:
    __metaclass__ = ABCMeta

    def __init__(self, icon_name, tooltip):
        self._build(icon_name, tooltip)

    @abstractmethod
    def set_image(self, image):
        """Set an image"""

    @abstractmethod
    def set_tooltip_text(self, tooltip):
        """Set the tooltip text"""

    def _build(self, icon_name, tooltip):
        """
        :param icon_name:
        :param tooltip:
        """
        icon = Gio.ThemedIcon(name=icon_name)
        image = Gtk.Image.new_from_gicon(icon,
                                         Gtk.IconSize.BUTTON)
        self.set_tooltip_text(tooltip)
        self.set_image(image)

    def hide(self):
        """Set a button visible or not?."""
        self.set_visible(False)
        self.set_no_show_all(True)

    def show(self):
        self.set_visible(True)
        self.set_no_show_all(False)


class HeaderBarButton(Gtk.Button, HeaderBarBtn):
    """HeaderBar Button widget"""

    def __init__(self, icon_name, tooltip):
        Gtk.Button.__init__(self)
        HeaderBarBtn.__init__(self, icon_name, tooltip)


class HeaderBarToggleButton(Gtk.ToggleButton, HeaderBarBtn):
    """HeaderBar Toggle Button widget"""

    def __init__(self, icon_name, tooltip):
        Gtk.ToggleButton.__init__(self)
        HeaderBarBtn.__init__(self, icon_name, tooltip)


class HeaderBar(Gtk.HeaderBar):
    """
    HeaderBar widget
    """
    instance = None

    def __init__(self):
        Gtk.HeaderBar.__init__(self)

        self.search_btn = HeaderBarToggleButton("system-search-symbolic",
                                                _("Search"))
        self.add_btn = HeaderBarButton("list-add-symbolic",
                                       _("Add a new account"))
        self.settings_btn = HeaderBarButton("open-menu-symbolic",
                                            _("Settings"))
        self.select_btn = HeaderBarButton("object-select-symbolic",
                                          _("Selection mode"))
        self.lock_btn = HeaderBarButton("changes-prevent-symbolic",
                                        _("Lock the application"))
        self.popover = None

        self._build_widgets()

    @staticmethod
    def get_default():
        """
        :return: Default instance of HeaderBar
        """
        if HeaderBar.instance is None:
            HeaderBar.instance = HeaderBar()
        return HeaderBar.instance

    def _build_widgets(self):
        """
        Generate the HeaderBar widgets
        """
        self.set_show_close_button(True)

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Hide the search button if nothing is found
        if Database.get_default().count > 0:
            self.search_btn.show()
        else:
            self.search_btn.hide()

        Settings.get_default().connect('changed', self.bind_status)

        left_box.add(self.add_btn)
        left_box.add(self.lock_btn)

        right_box.add(self.search_btn)
        right_box.add(self.select_btn)

        if not is_gnome():
            # add settings menu
            self.generate_popover(right_box)

        self.pack_start(left_box)
        self.pack_end(right_box)
        self.refresh()

    def generate_popover(self, box):
        self.settings_btn.connect("clicked", self.toggle_popover)
        self.popover = Gtk.Popover.new_from_model(self.settings_btn,
                                                  self.app.menu)
        self.popover.props.width_request = 200
        box.add(self.settings_btn)

    def bind_status(self, settings, key_name):
        if key_name == "locked":
            settings.bind("locked", self.lock_btn, "visible",
                          Gio.SettingsBindFlags.INVERT_BOOLEAN)
            settings.unbind(self.lock_btn, "visible")
        elif key_name == "state":
            settings.bind("state", self.lock_btn, "visible",
                          Gio.SettingsBindFlags.GET)
            settings.unbind(self.lock_btn, "visible")

    def toggle_popover(self, *args):
        if self.popover:
            if self.popover.get_visible():
                self.popover.hide()
            else:
                self.popover.show_all()

    def toggle_select_mode(self):
        is_select_mode = self.window.is_select_mode
        pass_enabled = Settings.get_default().is_locked

        self.set_show_close_button(not is_select_mode)
        self.settings_btn.set_visible(not is_select_mode)

        self.lock_btn.set_visible(not is_select_mode and pass_enabled)
        self.add_btn.set_visible(not is_select_mode)
        self.select_btn.set_visible(not is_select_mode)

        if is_select_mode:
            self.get_style_context().add_class("selection-mode")
        else:
            self.get_style_context().remove_class("selection-mode")

    def toggle_search(self):
        self.search_btn.set_active(not self.search_btn.get_active())

    def toggle_settings_button(self, visible):
        if not is_gnome():
            self.settings_button.set_visible(visible)
            self.settings_button.set_no_show_all(not visible)

    def refresh(self):
        return True
