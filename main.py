#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QWidget, QApplication, QFileDialog, QMessageBox)

from PyQt4 import QtCore
from PyQt4 import QtGui

#import song
#from song import Song
from tree import Tree

from threads import WorkThread
from threads import WorkThreadPipe
from table import Table







class Foo(QtGui.QMainWindow):

	def __init__(self):
		super(Foo, self).__init__()
		self.initUI()
        
	def initUI(self):
		config = Foo.readConfig()

		self.statusBar().showMessage('Ready')
		self.createMenu()
		self.setWindowTitle("Foo.cd")

		layout = QtGui.QGridLayout()
		mainLayout = QtGui.QGridLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		mainLayout.setContentsMargins(4, 4, 4, 4)

		splitterLeftRight = QtGui.QSplitter()
		splitterTopBottom = QtGui.QSplitter(Qt.Vertical, self)
		dummyWidget = QtGui.QWidget()
		frameInfo = QtGui.QFrame()
		self.tree = Tree(splitterLeftRight, config['tree_order'])
		
		self.table=Table( self.tree, config)
		
		
		
		self.tree.addAndPlaySongs.connect(self.table.addAndPlaySongsFromTree)
		self.tree.addSongs.connect(self.table.addSongsFromTree)
		self.table.songUpdate.connect(self.update)
		self.table.searchLine.returnPressed.connect(self.startSearch)
		
		
		
		#label is in box 2,0, spanning 1 line, 4 columns
		layout.addWidget(self.table.buttonPrev,1,0)
		layout.addWidget(self.table.buttonStop,1,1)
		layout.addWidget(self.table.buttonPlay,1,2)
		layout.addWidget(self.table.buttonNext,1,3)
		layout.addWidget(self.table.volumeSlider,1,4)
		layout.addWidget(self.table.slider,1,5)	
		layout.addWidget(self.table.label,2,0,1,5)
		layout.addWidget(self.table.tabs, 2,5,1,1)
		
		
		
		searchLayout = QtGui.QGridLayout(self.table.searchExactFuzzyGroup)
		searchLayout.setContentsMargins(0, 0, 0, 0)
		searchLayout.addWidget(self.table.searchLine,0,0,1,3)	
		searchLayout.addWidget(self.table.searchFuzzy,1,0)
		searchLayout.addWidget(self.table.searchPrecise,1,1)
		searchLayout.addWidget(self.table.searchExact,1,2)
		
		tabLayout = QtGui.QVBoxLayout(self.table.tabs.widget(0))
		tabLayout.setContentsMargins(0, 0, 0, 0)
		tabLayout.addWidget(self.table.searchExactFuzzyGroup)
		
	
			
		frameInfo.setLayout(layout)
		splitterTopBottom.addWidget(self.table)
		splitterTopBottom.addWidget(frameInfo)
		splitterTopBottom.setStretchFactor(0,3)
		splitterTopBottom.setStretchFactor(1,1)
		
		
		
		
		splitterLeftRight.addWidget(self.tree)
		splitterLeftRight.addWidget(splitterTopBottom)
		splitterLeftRight.setStretchFactor(0,2)
		splitterLeftRight.setStretchFactor(1,3)

		mainLayout.addWidget(splitterLeftRight)
		dummyWidget.setLayout(mainLayout)  
		self.setCentralWidget(dummyWidget)


		dictShortcuts = self.readConfigShortcuts()
		
		modifier = dictShortcuts['modifier']+'+'
		
		self.shortQuit = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['quit']), self, self.close)
		self.shortStop = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['stop']), self, self.table.stop)
		self.shortPlayPause = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['play_pause']), self, self.table.toggleSongFromTable)
		self.shortSongPrevious = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['previous']), self, self.table.previous)
		self.shortSongNext = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['next']), self, self.table.next)
		self.shortVolDown = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['volume_down']), self, self.table.volumeSliderDecr)
		self.shortVolUp = QtGui.QShortcut(QtGui.QKeySequence(modifier+dictShortcuts['volume_up']), self, self.table.volumeSliderIncr)
		
		
		pipeWorker = WorkThreadPipe()   
		pipeWorker.hotKey.connect(self.onHotKey)
		pipeWorker.start()
		
		self.show()
	
	
	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Alt:
			self.menuBar().setVisible(not self.menuBar().isVisible())
		else:
			QWidget.keyPressEvent(self, event)
	

	

	def update(self, status):
		print('.')
		try:
			nanosecs = self.table.pgetPosition()
			position = float(nanosecs) // 1000000000	
			self.table.slider.setValue(position)
			m, s = divmod(position, 60)
			self.statusBar().showMessage(status.replace('%',"%02d:%02d" % (m, s)))
		except Exception as e:
			print(e)
			pass




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


	#Create menu bar
	def createMenu(self):
		self.menuBar()
		self.menuBar().setVisible(False)
		actionMenu = self.menuBar().addMenu('Action')
		scanMusicFolderAction = QtGui.QAction('Scan Music Folder', self) 
		showShortcutAction = QtGui.QAction('Show Shortcut',self)
		addFolderToLibraryAction = QtGui.QAction('Add Folder to Library',self) 
		#scanMusicFolderAction.setShortcut('Ctrl+N') 
		#scanMusicFolderAction.setStatusTip('Create new file') 
		scanMusicFolderAction.triggered.connect(self.scanMusicFolder)
		actionMenu.addAction(scanMusicFolderAction)
		showShortcutAction.triggered.connect(Foo.showShortcut)
		actionMenu.addAction(showShortcutAction)
		addFolderToLibraryAction.triggered.connect(self.addFolderToLibrary)
		actionMenu.addAction(addFolderToLibraryAction)


	#Action 1 du menu
	def scanMusicFolder(self):
		self.thread = WorkThread(Foo.readConfig()['music_folder'], False)
		self.thread.start()
	
	#Action 2 du menu
	def showShortcut():
		dictSC = Foo.readConfigShortcuts()
		message = '''<b>'''+dictSC['modifier']+'''+'''+dictSC['stop']+'''</b> : Stop<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['quit']+'''</b> : Quit<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['play_pause']+'''</b> : Play/Pause    <br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['previous']+'''</b> : Previous<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['next']+'''</b> : Next<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['volume_down']+'''</b> : Volume down<br/>''' + '''
		<b>'''+dictSC['modifier']+'''+'''+dictSC['volume_up']+'''</b> : Volume up<br/>'''
		QMessageBox.about(None, 'About Message',
		message)

	#Action3 du menu
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


	@QtCore.pyqtSlot()
	def startSearch(self):
		input = self.table.searchLine.text()
		
		db = song.load()

		songList = []
		for dict in db:
			songList.append(Song(dict,self.tree.comm))
		
		self.tree.model().removeRows(0, self.tree.model().rowCount())
		
		if self.table.searchExact.isChecked():
			songList = song.filter(songList, song2.exactMatch, input)
		elif self.table.searchPrecise.isChecked():
			songList = song.filter(songList, song2.preciseMatch, input)
		else:
			songList = song.filter(songList, song2.fuzzyMatch, input)	

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
		

def main():

	app = QApplication(sys.argv)
	ex = Foo()
	sys.exit(app.exec_())
	

if __name__ == '__main__':
	main()