from gi.repository import PeasGtk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gio
import os
import json

class discord_status_prefs(GObject.Object, PeasGtk.Configurable):
  __gtype_name__ = "discord_status_prefs"
  object = GObject.property(type=GObject.Object)

  def __init__(self):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json")

    with open(path) as file:
      self.settings = json.load(file)

  def load_settings(self):
    return self.settings

  def do_create_configure_widget(self):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "discord-status-prefs.ui")
    builder = Gtk.Builder()
    builder.add_from_file(path)
    builder.connect_signals(self)

    builder.get_object("show_notif_checkbox").set_active(self.settings["show_notifs"])

    return builder.get_object("discord-status-prefs")

  def show_notifs_toggled(self, checkbox):
    print(checkbox)
    self.settings["show_notifs"] = checkbox.get_active()

    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json")

    with open(path, "w") as file:
      json.dump(self.settings, file)
