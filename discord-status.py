import rb
import gi
import time
import os
from gi.repository import Gio, GLib, GObject, Peas
from gi.repository import RB
from pypresence import Presence

class discord_status (GObject.Object, Peas.Activatable):
  RPC = Presence('415207119642689544')
  RPC.connect()
  __gtype_name__ = 'IMStatusPlugin'
  object = GObject.property(type=GObject.Object)

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
      info = self.get_info(sp)
      album = info[0]
      title = info[1]
      artist = info[2]
      duration = info[3]
      details="%s - %s" %(title, artist)

      start_time = int(time.time())
      pos = sp.get_playing_time().time
      end_time = start_time + duration - pos

      self.RPC.update(state=album, details=details[0:127], large_image="rhythmbox", small_image="play", small_text="Playing", start=start_time, end=end_time)

  def playing_changed(self, sp, playing):
    print("[discord-status] Playing chaned to: %s" %(playing))
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

    if playing:
      print("Playing chaned to: playing")
      self.RPC.update(state=album, details="%s - %s" %(title, artist)[0:127], large_image="rhythmbox", small_image="play", small_text="Playing", start=start_time, end=end_time)
    elif not playing and not sp.get_playing_entry():
      print("Playing chaned to: stopped")
      self.RPC.update(state="Playback Stopped", details="Rhythmbox Status Plugin", large_image="rhythmbox", small_image="stop", small_text="Stopped")
    else:
      print("Playing chaned to: paused")
      self.RPC.update(state=album, details=details, large_image="rhythmbox", small_image="pause", small_text="Paused")

  def elapsed_changed(self, sp, entry):
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

      self.RPC.update(state=album, details=details[0:127], large_image="rhythmbox", small_image="play", small_text="Playing", start=start_time, end=end_time)