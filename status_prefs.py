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
    
    self.time_style = self.settings["time_style"]
    self.show_notifs = self.settings["show_notifs"]

  def do_create_configure_widget(self):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "discord-status-prefs.ui")
    self.builder = Gtk.Builder()
    self.builder.add_from_file(path)
    self.builder.connect_signals(self)

    self.builder.get_object("show_notif_checkbox").set_active(self.settings["show_notifs"])
    
    if self.settings["time_style"] == 0:
      self.builder.get_object("elapsed_radio_button").set_active(True)
    elif self.settings["time_style"] == 1:
      self.builder.get_object("remaining_radio_button").set_active(False)

    return self.builder.get_object("discord-status-prefs")

  def update_settings(self):
    self.settings["time_style"] = self.time_style
    self.settings["show_notifs"] = self.show_notifs
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "settings.json")

    with open(path, "w") as file:
      json.dump(self.settings, file)    

  def show_notifs_toggled(self, checkbox):
    self.show_notifs = checkbox.get_active()
    self.update_settings()

  def elapsed_radio_button_toggled(self, toggle_button):
    print("elapsed")
    if (toggle_button.get_active()):
      self.time_style = 0
      self.update_settings()

  def remaining_radio_button_toggled(self, toggle_button):
    print("remaining")
    if (toggle_button.get_active()):
      self.time_style = 1
      self.update_settings()

