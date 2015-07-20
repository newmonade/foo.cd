# -*- coding: utf-8 -*-


from gi.repository import GObject
from gi.repository import Gst
Gst.init(None)


class Player():
    '''
    def __init__(self):
        self.pipeline = Gst.Pipeline()
        self.playbin = Gst.ElementFactory.make('playbin', None)
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)       
        self.pipeline.add(self.playbin)
        
        equalizer = Gst.ElementFactory.make('equalizer-10bands', 'equalizer')
        self.playbin.link( equalizer );
        equalizer.set_property('band1', -24.0)
        equalizer.set_property('band2', -24.0)
        equalizer.set_property('band3', -24.0)
        equalizer.set_property('band4', -24.0)
        equalizer.set_property('band5', -24.0)
        equalizer.set_property('band6', 12.0)
        equalizer.link( self.playbin );
        self.pipeline.add(equalizer)
    '''   
        
    
    def __init__(self, configEqua):
        bandValues = eval(configEqua['settings'])[configEqua['default']]
        self.playbin = Gst.ElementFactory.make('playbin', 'player')
          
        # No video, is it needed ?
        self.playbin.set_property('video-sink', Gst.ElementFactory.make('fakesink', 'fakesink'))

        # Change the audio sink to our own bin, so that an equalizer/replay gain element can be added later on if needed
        self.audiobin  = Gst.Bin('audiobin')
        self.audiosink = Gst.ElementFactory.make('autoaudiosink', 'audiosink')

        self.audiobin.add(self.audiosink)
        self.audiobin.add_pad(Gst.GhostPad.new('sink', self.audiosink.get_static_pad('sink')))
        self.playbin.set_property('audio-sink', self.audiobin)

        # Add equalizer
        self.equalizer = Gst.ElementFactory.make('equalizer-10bands', 'equalizer')
        self.audiobin.add(self.equalizer)
        self.audiobin.get_static_pad('sink').set_target(self.equalizer.get_static_pad('sink'))
        self.equalizer.link(self.audiosink)
        
        # Somehow equalizer needs to have a band set to not null
        # otherwise doesnt respond afterwards
        if bandValues == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
            self.equalizer.set_property('band0', 0.01)
        else:
            for i, v in enumerate(bandValues):
                self.equalizer.set_property('band'+str(i), v)

    
        self.bus = self.playbin.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)
  
    
    def add(self, uri):
        #realUri = ''.join(['file://', uri])
        self.playbin.set_property('uri', uri)

    def play(self):
        #self.pipeline.set_state(Gst.State.PLAYING)
        self.playbin.set_state(Gst.State.PLAYING)
        
    def stop(self):
        #self.pipeline.set_state(Gst.State.NULL)
        self.playbin.set_state(Gst.State.NULL)

    def toggle(self):
        state = self.playbin.get_state(Gst.State.NULL)
        if state[1] == Gst.State.PLAYING:
            self.playbin.set_state(Gst.State.PAUSED)
        else:
            self.playbin.set_state(Gst.State.PLAYING)

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