# -*- coding: utf-8 -*-

import sys
import os

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QWidget, QApplication, QFileDialog, QMessageBox)

from PyQt4 import QtCore
from PyQt4 import QtGui

from gi.repository import GObject
from gi.repository import Gst

from configparser import RawConfigParser

import song
from song import Song

import thread
from thread import WorkThread, WorkThreadPipe

from player import Player, ReplayGain

import widget
from widget import PlaybackButtons, SearchArea, VolumeSlider, ScrollSlider, Image, Equalizer, Retagging

from tree import Tree
from table_playlist import Table
from table_radio import TableRadio



from PyQt4.QtWebKit import *

class Foo(QtGui.QMainWindow):

	def __init__(self):
		super(Foo, self).__init__()
		self.initUI()

	def initUI(self):
		config = Foo.readConfig('options')
		self.timeOut = -1
		self.radio = False
		self.statusBar().showMessage('Ready')
		self.createMenu()
		self.setWindowTitle("Foo.cd")

		self.player = Player(Foo.readConfig('audio'))
		self.player.bus.connect('message::eos', self.stop)
		self.player.bus.connect('message::duration-changed', self.onDurationChanged)

		self.tree = Tree(self, config['tree_order'])
		self.tree.addSongs.connect(self.addSongsFromTree)
		self.tree.customContextMenuRequested.connect(self.tmpTag)

		if not self.radio:
			self.table=Table( self, config)
			self.handlerATF = self.player.playbin.connect("about-to-finish", self.onAboutToFinish)
			self.table.runAction.connect(self.tableAction)
		else:
			configRadio = Foo.readConfigRadios()
			self.table=TableRadio( self, configRadio)
			self.table.runAction.connect(self.tableAction)
			self.handlerT = self.player.bus.connect('message::tag', self.table.onTag)

		self.playbackButtons = PlaybackButtons(None)
		self.playbackButtons.buttonPlay.clicked.connect(self.toggleSong)
		self.playbackButtons.buttonStop.clicked.connect(self.stop)
		self.playbackButtons.buttonPrev.clicked.connect(self.previous)
		self.playbackButtons.buttonNext.clicked.connect(self.next)

		self.volumeSlider = VolumeSlider(self)
		self.volumeSlider.sliderMoved.connect(self.player.setVolume)
		self.scrollSlider = ScrollSlider(self)
		self.scrollSlider.sliderPressed.connect(self.player.toggle)
		self.scrollSlider.sliderReleased.connect(self.player.toggle)
		self.scrollSlider.sliderMoved.connect(self.player.seek)

		self.pixmap = Image(self, config['cover_names'], config['extensions'])

		# Album cover connections
		self.tree.selectionModel().selectionChanged.connect(lambda: self.pixmap.onSelectionChanged(self.tree.getChildren()[0].get('file', None)))
		self.table.selectionModel().selectionChanged.connect(lambda:  self.pixmap.onSelectionChanged(self.table.getSelection().get('file', None)))

		self.searchArea = SearchArea(self)
		self.searchArea.searchLine.returnPressed.connect(self.startSearch)

		self.playbackButtons.addWidget(self.volumeSlider)
		self.playbackButtons.addWidget(self.scrollSlider)

		splitterLeftRight = QtGui.QSplitter()
		self.splitterTopBottom = QtGui.QSplitter(Qt.Vertical, self)

		self.infoFrame = QtGui.QFrame()
		infoLayout = QtGui.QVBoxLayout()
		infoLayout.setContentsMargins(0,0,0,0)
		infoLayout.addLayout(self.playbackButtons)
		infoLayout.addWidget(self.pixmap)
		self.infoFrame.setLayout(infoLayout)

		libLayout = QtGui.QVBoxLayout()
		libLayout.setContentsMargins(0,0,0,0)
		libLayout.addWidget(self.tree)
		libLayout.addLayout(self.searchArea)
		libFrame = QtGui.QFrame()
		libFrame.setLayout(libLayout)

		self.splitterTopBottom.addWidget(self.table)
		self.splitterTopBottom.addWidget(self.infoFrame)
		self.splitterTopBottom.setStretchFactor(0,1)
		#self.splitterTopBottom.setStretchFactor(1,0)

		splitterLeftRight.addWidget(libFrame)
		splitterLeftRight.addWidget(self.splitterTopBottom)
		splitterLeftRight.setStretchFactor(0,2)
		splitterLeftRight.setStretchFactor(1,3)

		mainLayout = QtGui.QGridLayout()
		mainLayout.setContentsMargins(4, 4, 4, 4)
		mainLayout.addWidget(splitterLeftRight)

		dummyWidget = QtGui.QWidget()
		dummyWidget.setLayout(mainLayout)
		self.setCentralWidget(dummyWidget)

		self.setTabOrder(self.tree, self.table)

		dictShortcuts = self.readConfig('shortcuts')
		modifier = dictShortcuts['modifier']+'+'
		self.shortQuit = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['quit']), self, self.close)
		self.shortStop = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['stop']), self, self.stop)
		self.shortPlayPause = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['play_pause']), self, self.toggleSong)
		self.shortSongPrevious = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['previous']), self, self.previous)
		self.shortSongNext = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['next']), self, self.next)
		self.shortVolDown = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['volume_down']), self, self.volumeSlider.decr)
		self.shortVolUp = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['volume_up']), self, self.volumeSlider.incr)
		self.shortRadioMode = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['radio_mode']), self, self.toggleRadio)
		self.shortEqualizer = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['equalizer']), self, self.openEqualizer)

		thread = QtCore.QThread(self)
		thread.worker = WorkThreadPipe()
		thread.worker.moveToThread(thread);
		thread.started.connect(thread.worker.process)
		thread.worker.hotKey.connect(self.onHotKey)
		thread.worker.finished.connect(thread.quit)
		thread.worker.finished.connect(thread.worker.deleteLater)
		thread.finished.connect(thread.deleteLater)
		thread.start()






		self.show()

	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Alt:
			self.menuBar().setVisible(not self.menuBar().isVisible())
		else:
			QWidget.keyPressEvent(self, event)

	# Triggered by player end of stream event
	# or called by hand to stop the stream
	def stop(self, bus=None, msg=None):
		self.player.stop()
		self.scrollSlider.setValue(0)
		self.table.displayPlayToStop()
		self.stopStatusEmission('Ready')

	def previous(self):
		if self.table.playingId > 0:
			self.player.stop()
			self.table.playingId-=1
			self.player.add(self.table.model().item(self.table.playingId,0).data()['file'])
			self.player.play()

	def next(self):
		if self.table.model().rowCount()-1 > self.table.playingId:
			self.player.stop()
			self.table.playingId+=1
			self.player.add(self.table.model().item(self.table.playingId,0).data()['file'])
			self.player.play()

	def toggleSong(self):
		state = self.player.playbin.get_state(Gst.State.NULL)
		if state[1] == Gst.State.PLAYING:
			self.table.displayPlayToPause()
			self.player.toggle()

			status = self.statusBar().currentMessage().replace('Playing', 'Paused')
			self.stopStatusEmission(status)
		else:
			self.table.displayPauseToPlay(self.table.playingId)
			self.player.toggle()
			#self.onDurationChanged(0,0)
			status = self.table.getStatus()
			self.setStatusEmission(status)

	# Triggered by player when a song starts
	def onDurationChanged(self, bus, msg):
		self.table.displayNext()
		print('Duration changed signal !')

	# Triggered by player at the end of a song
	def onAboutToFinish(self, bus):
		if self.table.model().rowCount()-1 > self.table.playingId:
			print('About to finish !')
			self.table.playingId+=1
			self.player.add(self.table.model().item(self.table.playingId,0).data()['file'])

	def addSongsFromTree(self, list, play):
		if not self.radio:
			i = self.table.model().rowCount()
			for l in  list:
				self.table.addRow(l)
			self.table.resizeRowsToContents()
			if play:
				self.stop()
				self.player.add(list[0]['file'])
				self.player.play()
				self.table.displayStopToPlay(i)
				status = self.table.getStatus()
				self.setStatusEmission(status)

	def setStatusEmission(self, status):
		if self.timeOut > 0:
			GObject.source_remove(self.timeOut)
		self.timeOut =  GObject.timeout_add(1000, self.update, status)

	def stopStatusEmission(self, status):
		if self.timeOut > 0:
			GObject.source_remove(self.timeOut)
		self.timeOut = GObject.timeout_add(0, self.update, status)
		self.timeOut=-1

	def update(self, status):
		print('.')
		try:
			duration_nanosecs = self.player.getDuration()
			duration = float(duration_nanosecs) / 1000000000
			self.scrollSlider.setRange(0, duration)

			nanosecs = self.player.getPosition()
			position = float(nanosecs) // 1000000000
			self.scrollSlider.setValue(position)
			m, s = divmod(position, 60)
			self.statusBar().showMessage(status.replace('%',"%02d:%02d" % (m, s)))
		except Exception as e:
			print(e)
			pass
		if 'Playing' in status:
			return True
		else:
			return False


	def tableAction(self, str):
		if str == 'stop':
			self.stop()
		elif str == 'play':
			if self.table.selectedIndexes():
				index = self.table.selectedIndexes()[0]
			else:
				index= self.table.model().index(self.table.selectionModel().currentIndex().row(),0)
			songURI = index.model().itemFromIndex(index).data()['file']

			self.player.stop()
			self.player.add(songURI)
			self.player.play()
			self.table.displayStopToPlay(index.row())
			status = self.table.getStatus()
			self.setStatusEmission(status)

	@staticmethod
	def readConfig(section):
		parser = RawConfigParser()
		if getattr(sys, 'frozen', False):
			# frozen
			parser.read(os.path.dirname(os.path.realpath(sys.executable))+'/config')
		else:
			# unfrozen
			parser.read(os.path.dirname(os.path.realpath(__file__))+'/config')

		return dict(parser.items(section))

	#Create menu bar
	def createMenu(self):
		self.menuBar()
		self.menuBar().setVisible(False)
		actionMenu = self.menuBar().addMenu('&Action')
		scanMusicFolderAction = QtGui.QAction('Scan Music Folder', self)
		showShortcutAction = QtGui.QAction('Show Shortcut',self)
		addFolderToLibraryAction = QtGui.QAction('Add Folder to Library',self)
		self.toggleRadioAction= QtGui.QAction('Switch to Radio mode',self)
		if not self.radio:
			self.toggleRadioAction.setText('Switch to Radio mode')
		else:
			self.toggleRadioAction.setText('Switch to Library mode')
		#scanMusicFolderAction.setShortcut('Ctrl+N')
		#scanMusicFolderAction.setStatusTip('Create new file')
		scanMusicFolderAction.triggered.connect(self.scanMusicFolder)
		actionMenu.addAction(scanMusicFolderAction)
		showShortcutAction.triggered.connect(self.showShortcut)
		actionMenu.addAction(showShortcutAction)
		addFolderToLibraryAction.triggered.connect(self.addFolderToLibrary)
		actionMenu.addAction(addFolderToLibraryAction)
		self.toggleRadioAction.triggered.connect(self.toggleRadio)
		actionMenu.addAction(self.toggleRadioAction)


	# Menu Action 1
	def scanMusicFolder(self):
		thread = QtCore.QThread(self)
		thread.worker = WorkThread(Foo.readConfig('options')['music_folder'], False)
		thread.worker.moveToThread(thread)
		thread.started.connect(thread.worker.process)
		thread.worker.finished.connect(thread.quit)
		thread.worker.finished.connect(thread.worker.deleteLater)
		thread.finished.connect(thread.deleteLater)
		thread.finished.connect(self.tree.initUI)
		thread.start()

	# Menu Action 2
	def showShortcut(self):
		dictSC = Foo.readConfig('shortcuts')
		message = '''<b>'''+dictSC['modifier']+'''+'''+dictSC['stop']+'''</b> : Stop<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['quit']+'''</b> : Quit<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['play_pause']+'''</b> : Play/Pause    <br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['previous']+'''</b> : Previous<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['next']+'''</b> : Next<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['volume_down']+'''</b> : Volume down<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['volume_up']+'''</b> : Volume up<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['radio_mode']+'''</b> : Toggle radio mode<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['equalizer']+'''</b> : Equalizer<br/>'''
		print(len(self.findChildren(QtCore.QObject)))
		box = QMessageBox.about(self, 'About Shortcuts',
		message)
		print(len(self.findChildren(QtCore.QObject)))
		print('must delete')

	# Menu Action3
	# Must be subdirectory of music folder otherwise wont be rescanned
	def addFolderToLibrary(self):
		dir = QFileDialog.getExistingDirectory(None,
				"Open Directory",
				Foo.readConfig('options')['music_folder'],
				QFileDialog.ShowDirsOnly
				| QFileDialog.DontResolveSymlinks)
		self.thread = WorkThread(dir, True)
		self.thread.finished.connect(self.tree.initUI)
		self.thread.start()

	# Menu Action4
	def toggleRadio(self):
		self.table.deleteLater()
		self.table.close()
		if not self.radio:
			configRadio = Foo.readConfig('radios')
			self.table=TableRadio(self.tree, configRadio)
			self.toggleRadioAction.setText('Switch to Library mode')
			self.radio=True
			self.player.playbin.disconnect(self.handlerATF)
			self.handlerT=self.player.bus.connect('message::tag', self.table.onTag)
		else:
			config = Foo.readConfig('options')
			self.table=Table( self.tree, config)
			self.toggleRadioAction.setText('Switch to Radio mode')
			self.radio=False
			self.handlerATF = self.player.playbin.connect("about-to-finish",self.onAboutToFinish)
			self.player.bus.disconnect(self.handlerT)

		self.splitterTopBottom.addWidget(self.table)
		# Since the frame is already attached to the splitter,
		# it only moves it to the new position
		self.splitterTopBottom.addWidget(self.infoFrame)
		self.table.runAction.connect(self.tableAction)
		self.setTabOrder(self.tree, self.table)
		self.splitterTopBottom.setStretchFactor(0,10)
		#self.splitterTopBottom.setStretchFactor(3,1)

	@QtCore.pyqtSlot()
	def startSearch(self):
		input = self.searchArea.searchLine.text()

		db = thread.load()
		songList = []
		songGenerator = (Song(self.tree.comm, **dict) for dict in db)
		self.tree.model().removeRows(0, self.tree.model().rowCount())

		if self.searchArea.searchExact.isChecked():
			songList = [ e for e in songGenerator if e.exactMatch(input) ]
		elif self.searchArea.searchPrecise.isChecked():
			songList = [ e for e in songGenerator if e.preciseMatch(input) ]
		else:
			songList = [ e for e in songGenerator if e.fuzzyMatch(input) ]

		del db[:]
		songList.sort(key=self.tree.sortFunc)
		self.tree.populateTree(songList)

	@QtCore.pyqtSlot(str)
	def onHotKey(self, key):
		print('Hotkey was pressed', key)
		if key == 'quit':
			self.shortQuit.activated.emit()
		if key == 'stop':
			self.shortStop.activated.emit()
		if key == 'play_pause':
			self.shortPlayPause.activated.emit()
		if key == 'volume_up':
			self.shortVolUp.activated.emit()
		if key == 'volume_down':
			self.shortVolDown.activated.emit()
		if key == 'song_next':
			self.shortSongNext.activated.emit()
		if key == 'song_prev':
			self.shortSongPrev.activated.emit()
		if key == 'tree_up':
			if self.radio:
				self.table.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Up, Qt.KeyboardModifier(), ''))
			else:
				self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Up, Qt.KeyboardModifier(), ''))
		if key == 'tree_down':
			if self.radio:
				self.table.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Down, Qt.KeyboardModifier(), ''))
			else:
				self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Down, Qt.KeyboardModifier(), ''))
		if key == 'tree_left':
			if not self.radio:
				self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Left, Qt.KeyboardModifier(), ''))
		if key == 'tree_right':
			if not self.radio:
				self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Right, Qt.KeyboardModifier(), ''))
		if key == 'tree_validate':
			if self.radio:
				self.table.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Return, Qt.KeyboardModifier(), ''))
			else:
				self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Return, Qt.KeyboardModifier(), ''))
		if key == 'tree_append':
			if not self.radio:
				self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Return, Qt.KeyboardModifier(QtCore.Qt.ShiftModifier), ''))
		if key == 'radio_mode':
			self.shortRadioMode.activated.emit()

	def tmpTag(self, position):
		menu = QtGui.QMenu()
		tagging = QtGui.QAction('Tagging',self)
		replayGain = QtGui.QAction('ReplayGain',self)

		tagging.triggered.connect(self.openTagging)
		replayGain.triggered.connect(self.startReplayGain)
		menu.addAction(tagging)
		menu.addAction(replayGain)
		menu.exec_(self.tree.viewport().mapToGlobal(position))

	def startReplayGain(self):
		children = self.tree.getChildren()
		self.RG = ReplayGain([x['file'] for x in children])
		self.RG.exec_()

	def openTagging(self):
		children = self.tree.getChildren()
		#[7:] to drop the 'file://' appended for gstreamer
		retag = Retagging([x['file'][7:] for x in children])
		res = retag.exec_()
		if res:
			self.tree.initUI()
		print(res)

	def openEqualizer(self):
		from configparser import RawConfigParser
		equa = Equalizer(self, Foo.readConfig('audio'))
		equa.equalize.connect(self.applyEqua)
		if equa.exec_():
			parser = RawConfigParser()
			parser.read(os.path.dirname(os.path.realpath(__file__))+'/config')
			parser['audio']['settings']= str(equa.config)
			with open(os.path.dirname(os.path.realpath(__file__))+'/config', 'w') as configfile:
				parser.write(configfile)

	def applyEqua(self,band, value):
		print('receiving equa', str(band), value)
		if str(band) == 'band0' and value == 0:
			self.player.equalizer.set_property('band0', 0.01)
		else:
			self.player.equalizer.set_property(str(band), value)

def main():
	app = QApplication(sys.argv)
	ex = Foo()
	sys.exit(app.exec_())

if __name__ == '__main__':
	'''import cProfile, pstats, io
	pr = cProfile.Profile()
	pr.enable()
	main()
	pr.disable()
	s = io.StringIO()
	sortby = 'cumulative'
	ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
	ps.print_stats()
	print(s.getvalue())
	'''
	main()

