# -*- coding: utf-8 -*-
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QStandardItemModel, QAbstractItemView, QStandardItem,
			QItemSelection, QItemSelectionModel, QTableView)

from PyQt4 import QtCore
from PyQt4 import QtGui

class TableMother(QtGui.QTableView):

	runAction = QtCore.pyqtSignal(str)

	def addRow(self, song):
		raise NotImplementedError( "Should have implemented this" )

	def __init__(self, parent):
		raise NotImplementedError( "Should have implemented this" )
        
	def initUI(self):
		raise NotImplementedError( "Should have implemented this" )

	def focusOutEvent(self, e):
		self.selectionModel().clearSelection()

	def focusInEvent(self, e):
		currentIndex= self.model().index(self.selectionModel().currentIndex().row(),0)
		currentIndex2=self.model().index(currentIndex.row(),self.model().columnCount()-1)
		#If we never entered the widget
		if currentIndex.row()<0:
			currentIndex= self.model().index(0,0)
			currentIndex2=self.model().index(0,self.model().columnCount()-1)
			self.selectionModel().setCurrentIndex(currentIndex,QItemSelectionModel.Rows)
		self.selectionModel().select(QItemSelection(currentIndex,currentIndex2),QItemSelectionModel.Select)

	#Update signs '[ ]' and '>'
	#Is called by enter key from the tree or a line of the table
	def displayStopToPlay(self, indice):
		if self.playingId > -1:
			self.model().item(self.playingId,0).setText('')
		else:
			oldPlayingId = -1
			for i in range(0, self.model().rowCount()):
				if self.model().item(i,0).text()=='[ ]':
					oldPlayingId = i
				self.model().item(i,0).setText('')
		
		self.model().item(indice,0).setText('>')
		self.playingId = indice

	#Update signs '[ ]' and '>'
	#Different than stoptoplay because can be called by a shortcut
	#Thus not having a positive indice 
	def displayPauseToPlay(self, indice):
		if self.playingId > -1:
			self.model().item(self.playingId,0).setText('')
			self.model().item(indice,0).setText('>')
			self.playingId = indice
		else:
			oldPlayingId = -1
			for i in range(0, self.model().rowCount()):
				if self.model().item(i,0).text()=='[ ]':
					oldPlayingId = i
				self.model().item(i,0).setText('')
			self.model().item(oldPlayingId,0).setText('>')
			self.playingId = oldPlayingId

	#Update signs '[ ]' and '>'
	def displayNext(self):
		if self.playingId > 0:
			print(self.playingId)
			self.model().item(self.playingId-1,0).setText('')
			self.model().item(self.playingId,0).setText('>')
			print(self.playingId)
		if self.model().rowCount()-1 > self.playingId:
			self.model().item(self.playingId+1,0).setText('')
		if self.playingId == 0:
			self.model().item(self.playingId,0).setText('>')
			

	#Update signs '[ ]' and '>'
	def displayPlayToStop(self):
		if self.playingId > -1:
			self.model().item(self.playingId,0).setText('[ ]')
			self.playingId = -1
	
	#Update signs '||' and '>'
	def displayPlayToPause(self):
		if self.playingId > -1:
			self.model().item(self.playingId,0).setText('||')
			#self.playingId = -1

	def getStatus(self):
		raise NotImplementedError( "Should have implemented this" )
	
	
	
	
