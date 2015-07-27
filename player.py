# -*- coding: utf-8 -*-


from gi.repository import GObject
from gi.repository import Gst
Gst.init(None)

from PyQt4 import QtGui

class Player():
        
    
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
        '''
        '''
    	# Add ReplayGain
        self.replayGain = Gst.ElementFactory.make('rgvolume', 'rgvolume')
        self.audiobin.add(self.replayGain)
        self.audiobin.get_static_pad('sink').set_target(self.replayGain.get_static_pad('sink'))
        self.replayGain.link(self.equalizer)
        
        self.bus = self.playbin.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)
  
    
    def add(self, uri):
        self.playbin.set_property('uri', uri)

    def play(self):
        self.playbin.set_state(Gst.State.PLAYING)
        
    def stop(self):
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


class ReplayGain(QtGui.QDialog):
	def __init__(self, children):
		super().__init__()
		self.tags = []
		self.files = children
		self.playbin = Gst.ElementFactory.make('playbin', 'player')
	          
	        # No video, is it needed ?
		self.playbin.set_property('video-sink', Gst.ElementFactory.make('fakesink', 'fakesink'))
	
	        # Change the audio sink to our own bin, so that an equalizer/replay gain element can be added later on if needed
		self.audiobin  = Gst.Bin('audiobin')
		self.audiosink = Gst.ElementFactory.make('fakesink', 'audiosink')
		self.audiobin.add(self.audiosink)
		self.audiobin.add_pad(Gst.GhostPad.new('sink', self.audiosink.get_static_pad('sink')))
		self.playbin.set_property('audio-sink', self.audiobin)
	

	        
	        
		self.replaygain = Gst.ElementFactory.make('rganalysis', 'replaygain')

		self.audiobin.add(self.replaygain)
		self.audiobin.get_static_pad('sink').set_target(self.replaygain.get_static_pad('sink'))
		self.replaygain.link(self.audiosink)
		
		self.replaygain.set_property("num-tracks", len(self.files))
		
		self.bus = self.playbin.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect('message::tag', self.onTag)
		#self.playbin.connect('about-to-finish', self.process)
		self.bus.connect('message::eos', self.onEOS)
		
	def onTag(self, bus, msg):
		taglist = msg.parse_tag()
		tags = {}
		#print(taglist.to_string())
		
		if 'replaygain' in taglist.to_string():
			#print(taglist.to_string())
			#self.tags.append(taglist.to_string())
			def handle_tag(tagslist, tag, userdata):
				if tag == Gst.TAG_TRACK_GAIN:
					_, tags['trackGain'] = tagslist.get_double(tag)
				elif tag == Gst.TAG_TRACK_PEAK:
					_, tags['trackPeak'] = tagslist.get_double(tag)
				elif tag == Gst.TAG_REFERENCE_LEVEL:
					_, tags['trackLevel'] = tagslist.get_double(tag)
				elif tag == Gst.TAG_ALBUM_GAIN:
					_, tags['albumGain'] = tagslist.get_double(tag)
				elif tag == Gst.TAG_ALBUM_PEAK:
					_, tags['albumPeak'] = tagslist.get_double(tag)
        
			taglist.foreach(handle_tag, None)
			self.tags.append(tags)
			#print(tags)
			
	def process(self, file):
		#self.replaygain.set_property("num-tracks", len(self.files))
		print('aboutToFinish')
		if len(self.files) >0 :
			head, *tail = self.files
			#print(head, tail)
			self.files = tail
			
			
		
			self.playbin.set_property('uri', head)
			self.playbin.set_state(Gst.State.PLAYING)
			#pad = self.replaygain.get_static_pad("src")
			#pad.send_event(Gst.Event.new_flush_start())
			#pad.send_event(Gst.Event.new_flush_stop(True))
			self.replaygain.set_locked_state(False)
			
		else:
			self.playbin.set_state(Gst.State.NULL)
			print(self.tags)
			self.deleteLater()
			
			
	def onEOS(self, dummy, dummy2):
		self.replaygain.set_locked_state(True)
		self.playbin.set_state(Gst.State.NULL)
		
		self.process('')
		'''ret = self._next_file()
		if ret:
			self.pipe.set_state(Gst.State.PLAYING)
			#For some reason, GStreamer 1.0's rganalysis element produces
			#an error here unless a flush has been performed.
			pad = self.rg.get_static_pad("src")
			pad.send_event(Gst.Event.new_flush_start())
			pad.send_event(Gst.Event.new_flush_stop(True))
		self.rg.set_locked_state(False)
		'''
		
	'''
	def process(self, fileD, dummy):
		for file in self.files:
			self.current_song = file
			
			#self.filesrc.set_property("location", realpath(file))
			self.playbin.set_property('uri', file['file'])
			
			self.playbin.set_state(Gst.State.PLAYING)
			self.replaygain.set_locked_state(False)

			while True:
				# Pure evil ! 
				message = self.bus.poll(Gst.MessageType.EXTENDED, 0)
				if message != None and message.type == gst.MESSAGE_EOS:
					self.analysis.set_locked_state(True)
					self.pipe.set_state(gst.STATE_NULL)
					break

			self.analysis.set_locked_state(False)
	'''


	def exec_(self):
		self.process('')
		if QtGui.QDialog.exec_(self) == QtGui.QDialog.Accepted:
			return  1
		else:
			return 0

'''			
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2009-2014 Felix Krull <f_krull@gmx.de>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""Replay Gain analysis using GStreamer. See ``ReplayGain`` class for full
documentation or use the ``calculate`` function.
"""

import os.path
import sys

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

#from rgain import GainData, GSTError, util

# Initialise threading.
GObject.threads_init()
# Also initialise threading. This hack is necessary because while threads_init
# was originally deprecated in pygobject 3.10 and turned into a no-op, that
# wouldn't initialise Python threading properly when an introspection-loaded
# library used threading, but the Python program didn't (see
# https://bugzilla.gnome.org/show_bug.cgi?id=710447). Therefore, we create a
# dummy thread to force Python to initialise threading to accomodate these
# broken pygobject versions.
import threading
threading.Thread(target=lambda: None).start()

class ReplayGain(GObject.GObject):
    
    """Perform a Replay Gain analysis on some files.
    
    This class doesn't actually write any Replay Gain information - that is left
    as an exercise to the user. It only analyzes the files and presents the
    result.
    Basic usage is as follows:
     - instantiate the class, passing it a list of file names and optionally the
       reference loudness level to use (defaults to 89 dB),
     - connect to the signals the class provides,
     - get yourself a glib main loop (e.g. ``GObject.MainLoop`` or the one from
       GTK),
     - call ``replaygain_instance.start()`` to start processing,
     - start your main loop to dispatch events and
     - wait.
    Once you've done that, you can retrieve the data from ``track_data`` (which
    is a dict: keys are file names, values are ``GainData`` instances) and
    ``album_data`` (a 'GainData' instance, even though it may contain only
    ``None`` values if album gain isn't calculated). Note that the values don't
    contain any kind of unit, which might be needed.
    """
    
    __gsignals__ = {
        "all-finished": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
            (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
        "track-started": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
            (GObject.TYPE_STRING,)),
        "track-finished": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
            (GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)),
        "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
            (GObject.TYPE_PYOBJECT,)),
    }
    
    
    def __init__(self, files, force=False, ref_lvl=89):
        GObject.GObject.__init__(self)
        self.files = files
        print(files)
        self.force = force
        self.ref_lvl = ref_lvl
        
        self._setup_pipeline()
        self._setup_rg_elem()
        
        self._files_iter = iter(self.files)
        
        # this holds all track gain data
        self.track_data = {}
        #self.album_data = GainData(0)
        self.album_data = {}
    
    def start(self):
        """Start processing.
        
        For it to work correctly, you'll need to run some GObject main loop
        (e.g. the Gtk one) or process any events manually (though I have no
        idea how or if that works).
        """
        if not self._next_file():
            raise ValueError("do never, ever run this thing without any files")
        self.pipe.set_state(Gst.State.PLAYING)
        print("playing")
    
    def pause(self, pause):
        if pause:
            self.pipe.set_state(Gst.State.PAUSED)
        else:
            self.pipe.set_state(Gst.State.PLAYING)
    
    def stop(self):
        self.pipe.set_state(Gst.State.NULL)
    
    
    # internal stuff
    def _check_elem(self, elem):
        if elem is None:
            # that element couldn't be created, maybe because plugins are
            # missing?
            raise Exception(u"failed to construct pipeline (did you install "
                            u"all necessary GStreamer plugins?)")
        else:
            return elem
    def _setup_pipeline(self):
        """Setup the pipeline."""
        self.pipe = Gst.Pipeline()
        
        # elements
        self.src = self._check_elem(Gst.ElementFactory.make("filesrc", "src"))
        self.pipe.add(self.src)
        self.decbin = self._check_elem(Gst.ElementFactory.make("decodebin",
                                                               "decbin"))
        self.pipe.add(self.decbin)
        self.conv = self._check_elem(Gst.ElementFactory.make("audioconvert",
                                                             "conv"))
        self.pipe.add(self.conv)
        self.res = self._check_elem(Gst.ElementFactory.make("audioresample",
                                                            "res"))
        self.pipe.add(self.res)
        self.rg = self._check_elem(Gst.ElementFactory.make("rganalysis", "rg"))
        self.pipe.add(self.rg)
        self.sink = self._check_elem(Gst.ElementFactory.make("fakesink",
                                                             "sink"))
        self.pipe.add(self.sink)
        
        # Set num-tracks to the number of files we have to process so they're
        # all treated as one album. Fixes #8.
        self.rg.set_property("num-tracks", len(self.files))
        
        # link
        self.src.link(self.decbin)
        self.conv.link(self.res)
        self.res.link(self.rg)
        self.rg.link(self.sink)
        self.decbin.connect("pad-added", self._on_pad_added)
        self.decbin.connect("pad-removed", self._on_pad_removed)
        
        bus = self.pipe.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_message)
    
    def _setup_rg_elem(self):
        # there's no way to specify 'forced', as it's usually useless
        self.rg.set_property("forced", True)
        self.rg.set_property("reference-level", self.ref_lvl)
    
    def _next_file(self):
        """Load the next file to analyze.
        
        Returns False if everything is done and the pipeline shouldn't be
        started again; True otherwise.
        """
        # get the next file
        try:
            fname = self._files_iter.__next__()
        except StopIteration:
            self.emit("all-finished", self.track_data, self.album_data)
            return False

        # By default, GLib (and therefore GStreamer) assume any filename to be
        # UTF-8 encoded, regardless of locale settings (though most Unix
        # systems, Linux at least, should be configured for UTF-8 anyways these
        # days). The file name we pass to GStreamer is encoded with the system
        # default encoding here: if that's UTF-8, everyone's happy, if it isn't,
        # GLib's UTF-8 assumption needs to be overridden using the
        # G_FILENAME_ENCODING environment variable (set to locale to tell GLib
        # that all file names passed to it are encoded in the system encoding).
        # That way, people on non-UTF-8 systems or with non-UTF-8 file names can
        # still force all file name processing into a different encoding.
        
        #self.src.set_property("location",
        #                     fname.encode(util.getfilesystemencoding()))
        self.src.set_property("location", fname)
        self._current_file = fname
        self.emit("track-started", fname)
        
        print("track-startes")
        
        return True
    
    def _process_tags(self, msg):
        """Process a tag message."""
        tags = msg.parse_tag()
        trackdata = self.track_data.setdefault(self._current_file, GainData(0))

        def handle_tag(taglist, tag, userdata):
            if tag == Gst.TAG_TRACK_GAIN:
                _, trackdata.gain = taglist.get_double(tag)
            elif tag == Gst.TAG_TRACK_PEAK:
                _, trackdata.peak = taglist.get_double(tag)
            elif tag == Gst.TAG_REFERENCE_LEVEL:
                _, trackdata.ref_level = taglist.get_double(tag)
            
            elif tag == Gst.TAG_ALBUM_GAIN:
                _, self.album_data.gain = taglist.get_double(tag)
            elif tag == Gst.TAG_ALBUM_PEAK:
                _, self.album_data.peak = taglist.get_double(tag)
        
        tags.foreach(handle_tag, None)
        print(tags)
    
    # event handlers
    def _on_pad_added(self, decbin, new_pad):
        sinkpad = self.conv.get_compatible_pad(new_pad, None)
        if sinkpad is not None:
            new_pad.link(sinkpad)
    
    def _on_pad_removed(self, decbin, old_pad):
        peer = old_pad.get_peer()
        if peer is not None:
            old_pad.unlink(peer)
    
    def _on_message(self, bus, msg):
        print("mg!")
        if msg.type == Gst.MessageType.TAG:
            self._process_tags(msg)
        elif msg.type == Gst.MessageType.EOS:
            self.emit("track-finished", self._current_file,
                      self.track_data[self._current_file])
            # Preserve rganalysis state
            self.rg.set_locked_state(True)
            self.pipe.set_state(Gst.State.NULL)
            ret = self._next_file()
            if ret:
                self.pipe.set_state(Gst.State.PLAYING)
                # For some reason, GStreamer 1.0's rganalysis element produces
                # an error here unless a flush has been performed.
                pad = self.rg.get_static_pad("src")
                pad.send_event(Gst.Event.new_flush_start())
                pad.send_event(Gst.Event.new_flush_stop(True))
            self.rg.set_locked_state(False)
        elif msg.type == Gst.MessageType.ERROR:
            self.pipe.set_state(Gst.State.NULL)
            err, debug = msg.parse_error()
            self.emit("error", GSTError(err, debug))


def calculate(*args, **kwargs):
    """Analyze some files.
    
    This is only a convenience interface to the ``ReplayGain`` class: it takes
    the same arguments, but setups its own main loop and returns the results
    once everything's finished.
    """
    exc_slot = [None]

    def on_finished(evsrc, trackdata, albumdata):
        # all done
        loop.quit()

    def on_error(evsrc, exc):
        exc_slot[0] = exc
        loop.quit()
    rg = ReplayGain(*args, **kwargs)
    #with util.gobject_signals(rg, ("all-finished", on_finished),  ("error", on_error),):
    rg.connect("all-finished", on_finished)
    rg.connect("error", on_error)
    
    loop = GObject.MainLoop()
    rg.start()
    loop.run()

    if exc_slot[0] is not None:
        raise exc_slot[0]
    print("end")
    return (rg.track_data, rg.album_data)

'''


