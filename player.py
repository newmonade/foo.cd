# -*- coding: utf-8 -*-


from gi.repository import GObject
from gi.repository import Gst
Gst.init(None)


class Player():
    def __init__(self):
        self.pipeline = Gst.Pipeline()
        self.playbin = Gst.ElementFactory.make('playbin', None)
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)       
        self.pipeline.add(self.playbin)
  
    def add(self, uri):
        #realUri = ''.join(['file://', uri])
        self.playbin.set_property('uri', uri)

    def play(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        
    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)

    def toggle(self):
        state = self.pipeline.get_state(Gst.State.NULL)
        if state[1] == Gst.State.PLAYING:
            self.pipeline.set_state(Gst.State.PAUSED)
        else:
            self.pipeline.set_state(Gst.State.PLAYING)

    def seek(self, val):
        self.playbin.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, val * Gst.SECOND)

    def getPosition(self):
        return self.playbin.query_position(Gst.Format.TIME)[1]
    
    def getDuration(self):
        return self.playbin.query_duration(Gst.Format.TIME)[1]

    def setVolume(self, vol):
        self.playbin.set_property('volume', vol/100)

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())