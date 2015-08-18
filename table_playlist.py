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
		#super(QtGui.QTableView, self).__init__(parent)
		super().__init__(parent)
		self.playlistOrder = configOption['playlist_order']
		self.extensions = configOption['extensions'].replace(' ', '').split('|')
		self.coverNames = configOption['cover_names'].replace(' ', '').split('|')
		self.initUI()

	def initUI(self):
		self.playingId = -1
		model = QStandardItemModel()
		self.setModel(model)

		#self.selectionModel().selectionChanged.connect(self.selectionChanged)

		# Dummy line to display headers
		self.addRow(Song(self.playlistOrder))
		self.model().removeRow(0)

		# Fill headers, with first capital letter using title()
		headers = self.playlistOrder.title().replace('%','').split('|')
		model.setHeaderData(0,QtCore.Qt.Horizontal,'')
		for i,h in enumerate(headers):
			model.setHeaderData(i+1,QtCore.Qt.Horizontal,h)
		# One liner which is slower start1 = time.perf_counter()
		#map(lambda (i, h): model.setHeaderData(i+1,QtCore.Qt.Horizontal,h), enumerate(headers))

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
		status = str(song['bitrate'])+' kbps | '+str(song['samplerate'])+' Hz | '
		if song['samplerate'] == 1:
			status+='Mono'
		else:
			status+='Stereo'
		m, s = divmod(song['length'], 60)
		status+= ' | %/'+"%02d:%02d" % (m, s)+' - Playing'

		return status

	def getSelection(self):
		try:
			return self.model().itemFromIndex(self.selectedIndexes()[0]).data()
		except:
			return {}
