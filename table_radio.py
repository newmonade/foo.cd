from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QStandardItemModel, QAbstractItemView, QStandardItem,
			QItemSelection, QItemSelectionModel, QTableView)

from PyQt4 import QtCore
from PyQt4 import QtGui


from song import Song
from table_mother import TableMother

'''
Interface de table
signal runAction(str) qui est connecté a Foo.tableAction
playingID
displays...
getStatus
'''

class TableRadio(TableMother):

	def addRow(self, song):
		attribs = song.getFormatedValues(self.radioConfig['column_order'])
		nodes = [QStandardItem('')]
		nodes[-1].setData(song) #[-1] is last element
		for i in attribs:
			nodes.append(QStandardItem(i))
			nodes[-1].setData(song) #[-1] is last element
		self.model().appendRow(nodes) 

	def onTag(self, bus, msg):
		taglist = msg.parse_tag()
		print(taglist.to_string())
		tags = {}
		
		for i in range(0, taglist.n_tags()):
			tag_name = taglist.nth_tag_name(i)	
			if taglist.get_string(tag_name)[0]:
				tags[tag_name] = taglist.get_string(tag_name)[1]
			
				'''(success, value) = taglist.get_int(tag_name)
				
				if success:
					tags[tag_name] = value
				'''
		print(tags)

	def __init__(self, parent, radioConfig):
		super(QtGui.QTableView, self).__init__(parent)
		self.radioConfig = radioConfig
		
		self.initUI()
        
	def initUI(self):
		
		self.playingId = -1

		model = QStandardItemModel()
		self.setModel(model)
		
		#self.selectionModel().selectionChanged.connect(self.selectionChangedCustom)
		


		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.setTabKeyNavigation(False)		#Pas de changement de cellules avec tab
		self.setShowGrid(False)			#pas de traits entre les celules
		self.setAlternatingRowColors(True)	#Alternance des couleurs de lignes
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)	#Cellules pas editables
		self.setWordWrap(False)		#Pas de retour a la ligne
		
		#Creer une ligne bidon pour afficher les headers
		#self.addRow(self.radioConfig['column_order'].split('|'))
		#self.addRow( dict(zip(['name','file'], self.radioConfig['column_order'].split('|') )))
		self.addRow(Song({'FILE': '', 'LENGTH': '','CHANNELS': '', 'SAMPLERATE': '','BITRATE': ''}, self.radioConfig['column_order'].split('|')))
		self.model().removeRow(0)

		#Remplis le titre des headers, avec des majuscules (title())
		headers = self.radioConfig['column_order'].title().replace('%','').split('|')
		model.setHeaderData(0,QtCore.Qt.Horizontal,'')
		for i,h in enumerate(headers):
			model.setHeaderData(i+1,QtCore.Qt.Horizontal,h)

				
		#Don't bold header when get focus
		self.horizontalHeader().setHighlightSections(False)
		self.verticalHeader().hide()
		self.horizontalHeader().setStretchLastSection(True)
		self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive) #Interactive, ResizeToContents, Stretch
		
		
		stations = self.radioConfig['stations'].split('|')
		for station in stations:
			tags = dict(zip(['NAME','FILE'], [st.strip() for st in station.split('!')]))
			tags['LENGTH']=''
			tags['CHANNELS']=''
			tags['SAMPLERATE']=''
			tags['BITRATE']=''
			 
			self.addRow(Song(tags, self.radioConfig['column_order']))
		
		self.resizeColumnsToContents()
		self.resizeRowsToContents()

		self.show()
		
		

	def keyPressEvent(self, event):
		
		if event.key() == Qt.Key_Return:
			self.runAction.emit('play')
		QTableView.keyPressEvent(self, event)



		
	def getStatus(self):
		print(self.model().item(self.playingId, 0).data().toString())
		radioName = self.model().item(self.playingId, 0).data().tags['name']
		status = 'Radio '+ radioName +' - Playing'
		return status


