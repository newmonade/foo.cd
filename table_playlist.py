# -*- coding: utf-8 -*-
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QStandardItemModel, QAbstractItemView, QStandardItem,
			QItemSelection, QItemSelectionModel, QTableView)

from PyQt4 import QtCore
from PyQt4 import QtGui

import os
from song import Song
from table_mother import TableMother

#temporarily
import time

class Table(TableMother):

	def addRow(self, song):
		attribs = song.getFormatedValues(self.playlistOrder)
		nodes = [QStandardItem('')]
		nodes[-1].setData(song)
		for i in attribs:
			nodes.append(QStandardItem(i))
			nodes[-1].setData(song)
		self.model().appendRow(nodes) 

	def __init__(self, parent, configOption):
		super(QtGui.QTableView, self).__init__(parent)
		self.playlistOrder = configOption['playlist_order']
		self.extensions = configOption['extensions'].replace(' ', '').split('|')
		self.coverNames = configOption['cover_names'].replace(' ', '').split('|')
		self.initUI()
        
	def initUI(self):
		self.playingId = -1
		model = QStandardItemModel()
		self.setModel(model)
		
		self.selectionModel().selectionChanged.connect(self.selectionChanged)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.setTabKeyNavigation(False)
       		# No lines between cells	
		self.setShowGrid(False)			
		self.setAlternatingRowColors(True)
		# Not editable cells
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)	
		self.setWordWrap(False)
		
		# Dummy line to display headers
		self.addRow(Song({}, self.playlistOrder))
		self.model().removeRow(0)

        	#Fill headers, with first capital letter using title()
		headers = self.playlistOrder.title().replace('%','').split('|')
		model.setHeaderData(0,QtCore.Qt.Horizontal,'')
		for i,h in enumerate(headers):
			model.setHeaderData(i+1,QtCore.Qt.Horizontal,h)
		# One liner which is slower start1 = time.perf_counter()
		#map(lambda (i, h): model.setHeaderData(i+1,QtCore.Qt.Horizontal,h), enumerate(headers))
				
		#Don't bold header when get focus
		self.horizontalHeader().setHighlightSections(False)
		self.verticalHeader().hide()
		self.horizontalHeader().setStretchLastSection(True)
		self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive) #Interactive, ResizeToContents, Stretch
		
		self.resizeColumnsToContents()
		self.resizeRowsToContents()

		self.show()


	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Delete:
			index = self.selectedIndexes()[0]
			row = index.model().itemFromIndex(index).row()
			
			childIndex=self.model().index(row+1,0)
			childIndex2=self.model().index(row+1,self.model().columnCount()-1)
			self.selectionModel().clearSelection()
			self.selectionModel().select(QItemSelection(childIndex,childIndex2), QItemSelectionModel.Select)
			self.selectionModel().setCurrentIndex(childIndex,QItemSelectionModel.Rows)
			if self.playingId == row:
				self.runAction.emit('stop')
			self.model().removeRow(row)
		elif event.key() == Qt.Key_Return:
			self.runAction.emit('play')
		QTableView.keyPressEvent(self, event)

	def getStatus(self):
		song = self.model().item(self.playingId, 0).data()
		status = str(song.tags['bitrate'])+' kbps | '+str(song.tags['samplerate'])+' Hz | '
		if song.tags['samplerate'] == 1:
			status+='Mono'
		else:
			status+='Stereo'
		m, s = divmod(song.tags['length'], 60)
		status+= ' | %/'+"%02d:%02d" % (m, s)+' - Playing'
	
		return status
	
	
	
	
  		
