# -*- coding: utf-8 -*-

import sys
import os

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QWidget, QApplication, QFileDialog, QMessageBox)

from PyQt4 import QtCore
from PyQt4 import QtGui

import song
from song import Song
from tree import Tree

import thread
from thread import WorkThread
from thread import WorkThreadPipe
from table_playlist import Table

from player import Player
import widget
from widget import PlaybackButtons, SearchArea, VolumeSlider, Image

from table_radio import TableRadio

from gi.repository import GObject
from gi.repository import Gst


class Foo(QtGui.QMainWindow):

	#songUpdate = QtCore.pyqtSignal(str)

	def __init__(self):
		super(Foo, self).__init__()
		self.initUI()
        
	def initUI(self):
		config = Foo.readConfig()
		self.timeOut = -1
		self.radio = True
		self.statusBar().showMessage('Ready')
		self.createMenu()
		self.setWindowTitle("Foo.cd")
        
		self.player = Player()
		self.player.bus.connect('message::eos', self.stop)
		self.player.bus.connect('message::duration-changed', self.onDurationChanged)
		#self.player.playbin.connect("about-to-finish", self.onAboutToFinish)      
        
		
		
		
		
		
		self.tree = Tree(self, config['tree_order'])
		
		
		
		self.playbackButtons = PlaybackButtons(None)
		
		self.playbackButtons.buttonPlay.clicked.connect(self.toggleSong)
		self.playbackButtons.buttonStop.clicked.connect(self.stop)
		self.playbackButtons.buttonPrev.clicked.connect(self.previous)
		self.playbackButtons.buttonNext.clicked.connect(self.next)
		
		
		self.volumeSlider = VolumeSlider(self)
		self.scrollSlider = widget.createScrollSlider(self)
		self.scrollSlider.sliderMoved.connect(self.player.seek)
		self.scrollSlider.sliderPressed.connect(self.player.toggle)
		self.scrollSlider.sliderReleased.connect(self.player.toggle)
		self.volumeSlider.sliderMoved.connect(self.player.setVolume)
        
        
		self.pixmap = Image(self)
		self.searchArea = SearchArea(self)
		
		
		self.playbackButtons.addWidget(self.volumeSlider)
		self.playbackButtons.addWidget(self.scrollSlider)	
		
		

		if not self.radio:
			self.table=Table( self.tree, config)
			self.tree.addSongs.connect(self.addSongsFromTree)
			
			
			self.searchArea.searchLine.returnPressed.connect(self.startSearch)
			self.table.runAction.connect(self.tableAction)
		else:
			configRadio = Foo.readConfigRadios()
			self.table=TableRadio( self.tree, configRadio)
			self.table.runAction.connect(self.tableAction)
			self.player.bus.connect('message::tag', self.table.onTag)
		
		
		splitterLeftRight = QtGui.QSplitter()
		self.splitterTopBottom = QtGui.QSplitter(Qt.Vertical, self)
		
		
		self.frameInfo = QtGui.QFrame()
		tmpLayout = QtGui.QVBoxLayout()
		tmpLayout.setContentsMargins(0,0,0,0)
		tmpFrame = QtGui.QFrame()
		tmpFrame.setLayout(self.playbackButtons)
		tmpLayout.addWidget(tmpFrame)
		tmpLayout.addWidget(self.pixmap)
		tmpFrame2 = QtGui.QFrame()
		tmpFrame2.setLayout(self.searchArea)
		tmpLayout.addWidget(tmpFrame2)
		self.frameInfo.setLayout(tmpLayout)
		
		self.splitterTopBottom.addWidget(self.table)
		self.splitterTopBottom.addWidget(self.frameInfo)
		self.splitterTopBottom.setStretchFactor(0,3)
		self.splitterTopBottom.setStretchFactor(1,1)
		
		
		
		
		splitterLeftRight.addWidget(self.tree)
		splitterLeftRight.addWidget(self.splitterTopBottom)
		splitterLeftRight.setStretchFactor(0,2)
		splitterLeftRight.setStretchFactor(1,3)


		mainLayout = QtGui.QGridLayout()
		mainLayout.setContentsMargins(4, 4, 4, 4)
		mainLayout.addWidget(splitterLeftRight)
		
		dummyWidget = QtGui.QWidget()
		dummyWidget.setLayout(mainLayout)  
		self.setCentralWidget(dummyWidget)


		dictShortcuts = self.readConfigShortcuts()
		
		modifier = dictShortcuts['modifier']+'+'
		
		self.shortQuit = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['quit']), self, self.close)
		self.shortStop = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['stop']), self, self.stop)
		self.shortPlayPause = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['play_pause']), self, self.toggleSong)
		self.shortSongPrevious = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['previous']), self, self.previous)
		self.shortSongNext = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['next']), self, self.next)
		self.shortVolDown = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['volume_down']), self, self.volumeSlider.decr)
		self.shortVolUp = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['volume_up']), self, self.volumeSlider.incr)
		self.shortRadioMode = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['radio_mode']), self, self.toggleRadio)
		
		pipeWorker = WorkThreadPipe()   
		pipeWorker.hotKey.connect(self.onHotKey)
		pipeWorker.start()
		
		self.show()
	
	
	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Alt:
			self.menuBar().setVisible(not self.menuBar().isVisible())
		else:
			QWidget.keyPressEvent(self, event)
		
	#Triggered by player end of stream event
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
			self.player.add(self.table.model().item(self.table.playingId,0).data().tags['file'])
			self.player.play()
			
	def next(self):
		if self.table.model().rowCount()-1 > self.table.playingId:
			self.player.stop()
			self.table.playingId+=1
			self.player.add(self.table.model().item(self.table.playingId,0).data().tags['file'])
			self.player.play()
	
	def toggleSong(self):			
		state = self.player.pipeline.get_state(Gst.State.NULL)
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
			
	#triggered by player when a song starts
	def onDurationChanged(self, bus, msg):
		self.table.displayNext()
		print('Duration changed signal !')
		#status = self.table.getStatus()
		#self.setStatusEmission(status)

	#triggered by player at the end of a song
	def onAboutToFinish(self, bus):
		if self.table.model().rowCount()-1 > self.table.playingId:
			print('About to finish !')
			self.table.playingId+=1
			#print('finish',self.playingId)
			self.player.add(self.table.model().item(self.table.playingId,0).data().tags['file'])




	def addSongsFromTree(self, list, play):
		i = self.table.model().rowCount()
		for l in  list:
			self.table.addRow(l)
		self.table.resizeRowsToContents()
		if play:
			self.stop()
			self.player.add(list[0].tags['file'])
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
			#print(index.row())
			songURI = index.model().itemFromIndex(index).data().tags['file']
			
			self.player.stop()
			self.player.add(songURI)
			self.player.play()
			self.table.displayStopToPlay(index.row())
			status = self.table.getStatus()
			self.setStatusEmission(status)

	@staticmethod
	def readConfig():
		from configparser import RawConfigParser
		parser = RawConfigParser()
		parser.read(os.path.dirname(os.path.realpath(__file__))+'/config')
		return dict(parser.items('options'))
	
	@staticmethod
	def readConfigShortcuts():
		from configparser import RawConfigParser
		parser = RawConfigParser()
		parser.read(os.path.dirname(os.path.realpath(__file__))+'/config')
		return dict(parser.items('shortcuts'))

	@staticmethod
	def readConfigRadios():
		from configparser import RawConfigParser
		parser = RawConfigParser()
		parser.read(os.path.dirname(os.path.realpath(__file__))+'/config')
		return dict(parser.items('radios'))



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
		self.thread = WorkThread(Foo.readConfig()['music_folder'], False)
		self.thread.start()
	
	# Menu Action 2
	def showShortcut(self):
		dictSC = Foo.readConfigShortcuts()
		message = '''<b>'''+dictSC['modifier']+'''+'''+dictSC['stop']+'''</b> : Stop<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['quit']+'''</b> : Quit<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['play_pause']+'''</b> : Play/Pause    <br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['previous']+'''</b> : Previous<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['next']+'''</b> : Next<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['volume_down']+'''</b> : Volume down<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['volume_up']+'''</b> : Volume up<br/>'''
		print(len(self.findChildren(QtCore.QObject)))
		for ittt in self.findChildren(QtCore.QObject):
			print(ittt)
		box = QMessageBox.about(self, 'About Message',
		message)
		print(len(self.findChildren(QtCore.QObject)))
		print('must delete')

	# Menu Action3
	#Must be subdirectory of music folder otherwise wont be rescanned
	def addFolderToLibrary(self):
		dir = QFileDialog.getExistingDirectory(None,
				"Open Directory",
				Foo.readConfig()['music_folder'],
				QFileDialog.ShowDirsOnly
				| QFileDialog.DontResolveSymlinks)
		self.thread = WorkThread(dir, True)
		self.thread.start()
		print(dir)

	# Menu Action4
	def toggleRadio(self):
		self.table.deleteLater()
		self.table.close()
		if not self.radio:
			configRadio = Foo.readConfigRadios()
			self.table=TableRadio( self.tree, configRadio)
			self.player.bus.connect('message::tag', self.table.onTag)
			self.toggleRadioAction.setText('Switch to Library mode')
			self.radio=True
		else:
			config = Foo.readConfig()
			self.table=Table( self.tree, config)
			self.toggleRadioAction.setText('Switch to Radio mode')
			self.radio=False

		self.splitterTopBottom.addWidget(self.table)
		# Since the frame is already attached to the splitter, 
		# it only moves it to the new position
		self.splitterTopBottom.addWidget(self.frameInfo)
		self.splitterTopBottom.setStretchFactor(0,3)
		self.splitterTopBottom.setStretchFactor(1,1)
		self.table.runAction.connect(self.tableAction)
		


	@QtCore.pyqtSlot()
	def startSearch(self):
		input = self.searchArea.searchLine.text()
		
		db = thread.load()

		songList = []
		for dict in db:
			songList.append(Song(dict,self.tree.comm))
		
		self.tree.model().removeRows(0, self.tree.model().rowCount())
		
		if self.searchArea.searchExact.isChecked():
			songList = [ e for e in songList if e.exactMatch(input) ]
		elif self.searchArea.searchPrecise.isChecked():
			songList = [ e for e in songList if e.preciseMatch(input) ]
		else:
			songList = [ e for e in songList if e.fuzzyMatch(input) ]	

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
			self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Up, Qt.KeyboardModifier(), ''))
		if key == 'tree_down':
			self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Down, Qt.KeyboardModifier(), ''))
		if key == 'tree_left':
			self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Left, Qt.KeyboardModifier(), ''))
		if key == 'tree_right':
			self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Right, Qt.KeyboardModifier(), ''))
		if key == 'tree_validate':
			self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Return, Qt.KeyboardModifier(), ''))
		if key == 'tree_append':
			self.tree.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Return, Qt.KeyboardModifier(QtCore.Qt.ShiftModifier), ''))
		if key == 'radio_mode':
			self.shortRadioMode.activated.emit()
		

def main():

	app = QApplication(sys.argv)
	ex = Foo()
	sys.exit(app.exec_())
	

if __name__ == '__main__':
	main()



