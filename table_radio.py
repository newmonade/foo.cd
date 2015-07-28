from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QStandardItemModel, QAbstractItemView, QStandardItem,
			QItemSelection, QItemSelectionModel, QTableView)

from PyQt4 import QtCore
from PyQt4 import QtGui

import song
from song import Song
from table_mother import TableMother


#temporarily
import time

'''
Table interface
signal runAction(str) connected to Foo.tableAction
playingID
displays...
getStatus
'''

class TableRadio(TableMother):

	def addRow(self, song):
		attribs = song.getOptionalValues('%name%|'+self.radioConfig['prefered_informations'])
		nodes = [QStandardItem(x) for x in attribs]
		map(lambda x : x.setData(song), nodes)
		
		n = QStandardItem('')
		n.setData(song)
		nodes.insert(0, n)
		self.model().appendRow(nodes)
		
	def onTag(self, bus, msg):
		song = self.model().item(self.playingId, 0).data()
		(emptiedStr, tagNames) = Song.getTagName(self.radioConfig['prefered_informations'])

		taglist = msg.parse_tag()
		print(taglist.to_string())

		def handle_tag(tagslist, tag, userdata):
			# Look http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/GstTagList.html
			# for list of available tags
			if tag == "bitrate":
				_, song['bitrate'] = tagslist.get_uint(tag)
				song['bitrate'] = song['bitrate']//1000
			elif tag == "title":
				_, tmp = tagslist.get_string(tag)
				song['title'], song['artist'] = tmp.split("-")
				song['title'] = song['title'].strip()
				song['artist'] = song['artist'].strip()
			elif tag == "genre":
				_, song['genre'] = tagslist.get_string(tag)
			elif tag == "channel-mode":
				_, song['channels'] = tagslist.get_string(tag)
					
		taglist.foreach(handle_tag, None)
		#print(song)
		attribs = song.getOptionalValues(self.radioConfig['prefered_informations'])
		self.model().item(self.playingId, 2).setText(attribs[0])
		

	def __init__(self, parent, radioConfig):
		super().__init__(parent)
		self.radioConfig = radioConfig
		self.initUI()
        
	def initUI(self):
		self.playingId = -1
		model = QStandardItemModel()
		self.setModel(model)
		
		#self.selectionModel().selectionChanged.connect(self.selectionChangedCustom)
 
		stations = self.radioConfig['stations'].split('|')
		for station in stations:
			tags = dict(zip(['NAME','FILE'], [st.strip() for st in station.split('!')]))	 
			self.addRow(Song('%name%'+self.radioConfig['prefered_informations'], **tags))

		#Fill in the header, with capital for the first letter(title())
		headers = ['Name','Informations']
		model.setHeaderData(0,QtCore.Qt.Horizontal,'')
		for i,h in enumerate(headers):
			model.setHeaderData(i+1,QtCore.Qt.Horizontal,h)
		# One liner generator expression which is actually slower
		#map(lambda (i, h): model.setHeaderData(i+1,QtCore.Qt.Horizontal,h), enumerate(headers))

		self.resizeColumnsToContents()
		self.resizeRowsToContents()
		self.show()
		
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Return:
			self.runAction.emit('play')
		QTableView.keyPressEvent(self, event)

	def getStatus(self):
		radioName = self.model().item(self.playingId, 0).data()['name']
		status = 'Radio '+ radioName +' - Playing'
		return status


