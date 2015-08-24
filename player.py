# -*- coding: utf-8 -*-


from gi.repository import GObject
from gi.repository import Gst
Gst.init(None)

# For ReplayGain
import thread

from PyQt4 import QtGui

class Player():
	def __init__(self, configEqua):

		bandValues = eval(configEqua['settings'])[configEqua['default']]
		self.playbin = Gst.ElementFactory.make('playbin', 'player')


		# No video, is it needed ?
		self.playbin.set_property('video-sink', Gst.ElementFactory.make('fakesink', 'fakesink'))

		# Change the audio sink to our own bin,
		# so that an equalizer/replay gain element can be added later on if needed
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

		# Add ReplayGain
		self.replayGain = Gst.ElementFactory.make('rgvolume', 'rgvolume')
		self.audiobin.add(self.replayGain)
		self.audiobin.get_static_pad('sink').set_target(self.replayGain.get_static_pad('sink'))
		self.replayGain.link(self.equalizer)
		self.replayGain.set_property("album-mode", configEqua['replay_gain_album_mode'])

		self.bus = self.playbin.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect('message::error', self.on_error)
		self.bus.connect('message::tag', self.onTag)

	def onTag(self, bus, msg):
		taglist = msg.parse_tag()
		tags = {}
		#print(taglist.to_string())
		if 'replaygain' in taglist.to_string():
			print(taglist.to_string())

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
		self.index = 0
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
		self.bus.connect('message::eos', self.onEOS)

	def onTag(self, bus, msg):
		taglist = msg.parse_tag()
		#print(taglist.to_string())
		tags = {}

		if 'replaygain' in taglist.to_string():
			def handle_tag(tagslist, tag, userdata):
				if tag == Gst.TAG_TRACK_GAIN:
					_, tags['REPLAYGAIN_TRACK_GAIN'] = tagslist.get_double(tag)
					tags['REPLAYGAIN_TRACK_GAIN'] = "{:.2f}".format(tags['REPLAYGAIN_TRACK_GAIN'])  +' dB'
				elif tag == Gst.TAG_TRACK_PEAK:
					_, tags['REPLAYGAIN_TRACK_PEAK'] = tagslist.get_double(tag)
					tags['REPLAYGAIN_TRACK_PEAK'] = "{:.6f}".format(tags['REPLAYGAIN_TRACK_PEAK'])
				elif tag == Gst.TAG_REFERENCE_LEVEL:
					_, tags['REPLAYGAIN_REFERENCE_LEVEL'] = tagslist.get_double(tag)
					tags['REPLAYGAIN_REFERENCE_LEVEL'] = str(tags['REPLAYGAIN_REFERENCE_LEVEL'])
				elif tag == Gst.TAG_ALBUM_GAIN:
					_, tags['REPLAYGAIN_ALBUM_GAIN'] = tagslist.get_double(tag)
				elif tag == Gst.TAG_ALBUM_PEAK:
					_, tags['REPLAYGAIN_ALBUM_PEAK'] = tagslist.get_double(tag)
					tags['REPLAYGAIN_ALBUM_PEAK'] =tags['REPLAYGAIN_ALBUM_PEAK']

			taglist.foreach(handle_tag, None)
			self.tags.append(tags)

	def process(self):
		print('aboutToFinish')
		if self.index < len(self.files) :
			#head, *tail = self.files
			#print(head, tail)
			#self.files = tail

			self.playbin.set_property('uri', self.files[self.index])
			self.playbin.set_state(Gst.State.PLAYING)
			self.replaygain.set_locked_state(False)
			pad = self.replaygain.get_static_pad("src")
			pad.send_event(Gst.Event.new_flush_start())
			pad.send_event(Gst.Event.new_flush_stop(True))

			self.index += 1
		else:
			self.playbin.set_state(Gst.State.NULL)
			albumData = self.tags[-1]
			for i, t in enumerate(self.tags):
				t['FILE'] = self.files[i][7:]
				t['REPLAYGAIN_ALBUM_PEAK'] = "{:.6f}".format(albumData['REPLAYGAIN_ALBUM_PEAK'])
				t['REPLAYGAIN_ALBUM_GAIN'] = "{:.2f}".format(albumData['REPLAYGAIN_ALBUM_GAIN']) +" dB"

			for tags in self.tags:
				print(tags)
			'''
			fileList = []
			for tags in self.tags:
				modified = thread.modifyTags(tags)
				if modified:
					fileList.append(tags['FILE'])
			thread.updateDB(fileList)
			'''
			self.deleteLater()
			self.close()

	def onEOS(self, dummy, dummy2):
		self.replaygain.set_locked_state(True)
		self.playbin.set_state(Gst.State.READY)
		self.process()


	def exec_(self):
		self.process()
		if QtGui.QDialog.exec_(self) == QtGui.QDialog.Accepted:
			return  1
		else:
			return 0
