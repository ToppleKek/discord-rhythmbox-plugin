import gi
import time
import os
gi.require_version('Notify', '0.7')
gi.require_version('Gtk', '3.0')
from gi.repository import Notify, Gtk
from gi.repository import Gio, GLib, GObject, Peas
from gi.repository import RB
from pypresence import Presence

class discord_status_dev (GObject.Object, Peas.Activatable):
  Notify.init("Rhythmbox")
  RPC = Presence("415207119642689544")
  connected = False
  gave_up = False
  try:
    RPC.connect()
    Notify.Notification.new("Rhythmbox Discord Status Plugin", "Connected to Discord").show()
    Notify.uninit()
    connected = True
  except ConnectionRefusedError:
    Notify.Notification.new("Rhythmbox Discord Status Plugin", "Failed to connect to discord: ConnectionRefused. Is discord open?").show()
    Notify.uninit()
    while not connected and not gave_up:
      dialog = Gtk.Dialog(title = "Discord Rhythmbox Status Plugin",
                          parent = None,
                          buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                     Gtk.STOCK_OK, Gtk.ResponseType.OK)
                         )

      hbox = Gtk.HBox()

      label = Gtk.Label("\nFailed to connect to the discord client. Make sure that discord is open. Retry?\n")
      hbox.pack_start(label, True, True, 0)

      dialog.vbox.pack_start(hbox, True, True, 0)
      dialog.vbox.show_all()

      response = dialog.run()

      if (response == Gtk.ResponseType.OK):
        try:
          RPC.connect()
          connected = True
        except ConnectionRefusedError:
          print('Failed to retry connection to discord')

      elif (response == Gtk.ResponseType.CANCEL):
        gave_up = True
        dialog.destroy()

      else:
        pass

      dialog.destroy()
  __gtype_name__ = 'DiscordStatusPlugin'
  object = GObject.property(type=GObject.Object)
  start_date = None
  playing_date = None
  is_playing = False
  def __init__ (self):
    GObject.Object.__init__ (self)

  def do_activate(self):
    shell = self.object
    sp = shell.props.shell_player
    self.psc_id  = sp.connect ('playing-song-changed',
                               self.playing_entry_changed)
    self.pc_id   = sp.connect ('playing-changed',
                               self.playing_changed)
    self.ec_id   = sp.connect ('elapsed-changed',
                               self.elapsed_changed)

    self.RPC.update(state="Playback Stopped", details="Rhythmbox Status Plugin", large_image="rhythmbox", small_image="stop", small_text="Stopped")

  def do_deactivate(self):
    shell = self.object
    sp = shell.props.shell_player
    sp.disconnect (self.psc_id)
    sp.disconnect (self.pc_id)
    sp.disconnect (self.ec_id)
    self.RPC.clear(pid=os.getpid())
    self.RPC.close()

  def get_info(self, sp):
      album = None
      title = None
      artist = None
      duration = None

      if not sp.get_playing_entry().get_string(RB.RhythmDBPropType.ALBUM):
        album = 'Unknown'
      else:
        album = sp.get_playing_entry().get_string(RB.RhythmDBPropType.ALBUM)

      if not sp.get_playing_entry().get_string(RB.RhythmDBPropType.TITLE):
        title = 'Unknown'
      else:
        title = sp.get_playing_entry().get_string(RB.RhythmDBPropType.TITLE)

      if not sp.get_playing_entry().get_string(RB.RhythmDBPropType.ARTIST):
        artist = 'Unknown'
      else:
        artist = sp.get_playing_entry().get_string(RB.RhythmDBPropType.ARTIST)

      if not sp.get_playing_entry().get_ulong(RB.RhythmDBPropType.DURATION):
        duration = 0
      else:
        duration = sp.get_playing_entry().get_ulong(RB.RhythmDBPropType.DURATION)

      return [album, title, artist, duration]

  def playing_entry_changed(self, sp, entry):
    if sp.get_playing_entry():
      self.start_date = int(time.time())
      self.playing_date = self.start_date
      info = self.get_info(sp)
      album = info[0]
      title = info[1]
      artist = info[2]
      duration = info[3]
      details="%s - %s" %(title, artist)
      self.is_playing = True

      start_time = int(time.time())
      pos = sp.get_playing_time().time
      end_time = start_time + duration - pos

      print("Updating RPC... (playing_entry_changed)")
      self.RPC.update(state=album[0:127], details=details[0:127], large_image="rhythmbox", small_image="play", small_text="Playing", start=start_time, end=end_time)

  def playing_changed(self, sp, playing):
    print("Playing chaned to: %s" %(playing))
    album = None
    title = None
    artist = None
    if sp.get_playing_entry():
      info = self.get_info(sp)
      album = info[0]
      title = info[1]
      artist = info[2]
      duration = info[3]
      details="%s - %s" %(title, artist)

      start_time = int(time.time())
      pos = sp.get_playing_time().time
      end_time = start_time + duration - pos

    print("Updating RPC... (playing_changed)")
    if playing:
      print("Playing chaned to: playing")
      self.is_playing = True
      self.RPC.update(state=album[0:127], details=details[0:127], large_image="rhythmbox", small_image="play", small_text="Playing", start=start_time, end=end_time)
    elif not playing and not sp.get_playing_entry():
      print("Playing chaned to: stopped")
      self.is_playing = False
      self.RPC.update(state="Playback Stopped", details="Rhythmbox Status Plugin", large_image="rhythmbox", small_image="stop", small_text="Stopped")
    else:
      print("Playing chaned to: paused")
      self.is_playing = False
      self.RPC.update(state=album[0:127], details=details[0:127], large_image="rhythmbox", small_image="pause", small_text="Paused")

  def elapsed_changed(self, sp, elapsed):
    print("[DEBUG] ELAPSED: %s" %(elapsed))
    if not self.playing_date or not self.is_playing:
      return
    else:
      self.playing_date += 1
    if self.playing_date - elapsed == self.start_date:
      return
    else:
      if sp.get_playing_entry() and self.is_playing and not elapsed == 0:
        self.playing_date = self.start_date + elapsed
        info = self.get_info(sp)
        album = info[0]
        title = info[1]
        artist = info[2]
        duration = info[3]
        details="%s - %s" %(title, artist)

        start_time = int(time.time())
        pos = sp.get_playing_time().time
        end_time = start_time + duration - pos

        print("Updating RPC... (elapsed_changed)")
        self.RPC.update(state=album[0:127], details=details[0:127], large_image="rhythmbox", small_image="play", small_text="Playing", start=start_time, end=end_time)