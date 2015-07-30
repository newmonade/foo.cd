# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

import thread

class PlaybackButtons(QtGui.QHBoxLayout):

	def __init__(self, parent):
		super().__init__(parent)
		self.initUI()
        
	def initUI(self):
		
		self.buttonPlay = QtGui.QPushButton(">")
		self.buttonPlay.setMaximumSize(25,25)
		self.buttonPlay.setFocusPolicy(QtCore.Qt.NoFocus)
		self.buttonPlay.setFont(QtGui.QFont('TypeWriter', 9))
		self.buttonStop = QtGui.QPushButton("[ ]")
		self.buttonStop.setMaximumSize(25,25)
		self.buttonStop.setFocusPolicy(QtCore.Qt.NoFocus)
		self.buttonStop.setFont(QtGui.QFont('TypeWriter', 9))
		self.buttonPrev = QtGui.QPushButton("|<<")
		self.buttonPrev.setMaximumSize(25,25)
		self.buttonPrev.setFocusPolicy(QtCore.Qt.NoFocus)
		self.buttonPrev.setFont(QtGui.QFont('TypeWriter', 9))
		self.buttonNext = QtGui.QPushButton(">>|")
		self.buttonNext.setMaximumSize(25,25)
		self.buttonNext.setFocusPolicy(QtCore.Qt.NoFocus)
		self.buttonNext.setFont(QtGui.QFont('TypeWriter', 9))
		self.setContentsMargins(0, 0, 0, 0)
        
		
		self.addWidget(self.buttonPrev)
		self.addWidget(self.buttonStop)
		self.addWidget(self.buttonPlay)
		self.addWidget(self.buttonNext)

		#self.addStrut(10)
		#self.show()
        
        
class VolumeSlider(QtGui.QSlider):

	def __init__(self, parent):
		super().__init__(QtCore.Qt.Horizontal, parent)
		self.initUI()
        
	def initUI(self):
		self.setFocusPolicy(QtCore.Qt.NoFocus)
		self.setTickInterval(1)
		self.setTracking(False)
		self.setMaximumWidth(70)
		self.setMinimum(0)
		self.setMaximum(200)
		self.setSliderPosition(100)
		self.setValue(100)
		
	def incr(self):
		position = self.value()
		if position < 210:
			self.setValue(position+10)
			self.sliderMoved.emit(position+10)
			
	
	def decr(self):
		position = self.value()
		if position > 0:
			self.setValue(position-10)
			self.sliderMoved.emit(position-10)

def createScrollSlider(parent):
    
	slider = QtGui.QSlider(QtCore.Qt.Horizontal, parent)
	slider.setFocusPolicy(QtCore.Qt.NoFocus)
	slider.setPageStep(1)
	slider.setTracking(False)
	return slider



class Image(QtGui.QLabel):

	def __init__(self, parent):
		#QtGui.QLabel.__init__(self)
		super().__init__(parent)
		self._pixmap = None #QtGui.QPixmap(1,1)
		self.initUI()
        
	def initUI(self):
		#self._pixmap.fill(Qt.darkGray)
		self.setText('[No Cover]')
		
		self.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
		#self.setFixedSize(200,200)
		#self.setAlignment(QtCore.Qt.AlignCenter)

	def resizeEvent(self, event):
		if self._pixmap != None:
			self.setPixmap(self._pixmap.scaled(
				self.width(), self.height(),
				QtCore.Qt.KeepAspectRatio))
            
	def onSelectionChanged(self, file):
		print("selection changed", file)
		'''
		import os
		if not selected.isEmpty():
			index = self.selectedIndexes()[0]
			crawler = index.model().itemFromIndex(index)
			dir = os.path.dirname(crawler.data().tags['file'])
			
			#fileNames = ['cover', 'Cover', 'Folder']
			#extensions = ['jpg', 'png','jpeg']
			allPossibilities = [(x +'.'+ y) for x in self.coverNames for y in self.extensions]
			
			myPixmap = QtGui.QPixmap(200,200)
			
			for file in allPossibilities : 
				if os.path.isfile(dir+'/'+file):
					myPixmap = QtGui.QPixmap(dir+'/'+file)
					break

			
			myScaledPixmap = myPixmap.scaled(200, 200, Qt.KeepAspectRatio)
			self.label.setPixmap(myScaledPixmap)
		'''
		
class SearchArea(QtGui.QGridLayout):

	def __init__(self, parent):
		QtGui.QGridLayout.__init__(self)
		# Why does it print an error 
		#super().__init__(parent)
		self.initUI()
        
	def initUI(self):
		self.searchLine = QtGui.QLineEdit()
		self.searchExact = QtGui.QRadioButton('Exact')
		self.searchPrecise = QtGui.QRadioButton('Precise')
		self.searchFuzzy = QtGui.QRadioButton('Fuzzy')
		self.searchPrecise.setChecked(True);    
    
		self.setContentsMargins(0, 0, 0, 0)
		self.addWidget(self.searchLine,0,0,1,3)	
		self.addWidget(self.searchFuzzy,1,0)
		self.addWidget(self.searchPrecise,1,1)
		self.addWidget(self.searchExact,1,2)
		


class Equalizer(QtGui.QDialog):
	equalize = QtCore.pyqtSignal(str, int) 

	def __init__(self, parent, config):
		super().__init__(parent)
		self.setWindowModality(QtCore.Qt.ApplicationModal)
		self.config = eval(config['settings'])
		self.modified = False
		bandValues = self.config[config['default']]
		frequencies = [ "29Hz", "59Hz", "119Hz", "237Hz", "474Hz", 
			"947Hz", "1.8kHz", "3.7kHz", "7.5kHz", "15kHz"]
        
		self.layout = QtGui.QGridLayout()
        
		self.configList = QtGui.QComboBox()
		self.configList.addItems([x for x in self.config.keys()])
		self.configList.setCurrentIndex(list(self.config.keys()).index(config['default']))
		self.configList.activated[str].connect(self.listActivated)    
 
		self.addButton = QtGui.QPushButton('Add')
		self.addButton.clicked.connect(self.addPreset)
        
		self.removeButton = QtGui.QPushButton('Remove')
		#self.removeButton.setMaximumWidth(40)
		self.removeButton.clicked.connect(self.removePreset)
        
		self.saveButton = QtGui.QPushButton('Save')
		self.saveButton.setMaximumWidth(40)
		self.saveButton.clicked.connect(self.savePreset)
        
		self.closeButton = QtGui.QPushButton('Quit')
		self.closeButton.setMaximumWidth(40)
		self.closeButton.clicked.connect(self.close)
        
		self.layout.addWidget(self.configList, 0, 0, 1, 3)
		self.layout.addWidget(self.addButton, 0, 3, 1, 2, QtCore.Qt.AlignCenter)
		self.layout.addWidget(self.removeButton, 0, 5, 1, 2, QtCore.Qt.AlignCenter)
		self.layout.addWidget(self.saveButton, 0, 8, 1, 1, QtCore.Qt.AlignCenter)
		self.layout.addWidget(self.closeButton, 0, 9, 1, 1, QtCore.Qt.AlignCenter)
        
		for index, val in enumerate(bandValues):
			band = QtGui.QLabel(frequencies[index], self)
			slider = QtGui.QSlider(QtCore.Qt.Vertical, self)
			slider.setMinimum(-24)
			slider.setMaximum(12)
			slider.setSliderPosition(val)
			slider.valueChanged.connect(self.updateLabel)
			# Make that work...
			#labelValue = QtGui.QLabel(str(val).rjust(3, ' ')+"dB", self)
			labelValue = QtGui.QLabel('', self)
   
			self.layout.addWidget(band, 1 , index, 1, 1, QtCore.Qt.AlignCenter)
			self.layout.addWidget(slider, 2 , index, 1, 1, QtCore.Qt.AlignCenter)
			self.layout.addWidget(labelValue, 3 , index, 1, 1, QtCore.Qt.AlignCenter)
			band.setAlignment(QtCore.Qt.AlignCenter)
            
			slider.valueChanged.emit(val)
        
		self.setLayout(self.layout)


	def updateLabel(self, val):
		position = self.layout.getItemPosition(self.layout.indexOf(self.sender()))[1]
		self.layout.itemAtPosition(3, position).widget().setText(str(val) + 'dB')
		print('emiting equa')
		self.equalize.emit('band'+str(position), val)

	def listActivated(self, confName):
		bandValues = self.config[confName]
		for index, val in enumerate(bandValues):
			self.layout.itemAtPosition(2, index).widget().setValue(val)
    
	def addPreset(self):
		name, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
			'Name of this new preset:')
		if ok:
			if name in self.config.keys():
				box = QtGui.QMessageBox.about(self, 'About Message', 'Already exist')
			else:
				newConf = [self.layout.itemAtPosition(2, index).widget().value() for index in range(0,10)]
				self.config[name] = newConf
				self.configList.addItem(name)
				self.configList.setCurrentIndex(self.configList.count()-1)
				# To save the presets to config file when closing the dialog
				self.modified = True
    
	def savePreset(self):
		newConf = [self.layout.itemAtPosition(2, index).widget().value() for index in range(0,10)]
		self.config[self.configList.currentText()] = newConf
		self.modified = True
    
	def removePreset(self):
		if len(self.config) > 1:
			self.config.pop(self.configList.currentText())
			self.configList.removeItem(self.configList.currentIndex())
			self.listActivated(self.configList.currentText())
			self.modified = True
    
	def exec_(self):
		QtGui.QDialog.exec_(self)
		return self.modified
        
        
        
class Retagging(QtGui.QDialog):
	def __init__(self, fileList):
		super().__init__()
		self.columnsToRemove = {}
		self.setWindowModality(QtCore.Qt.ApplicationModal)
		self.setSizeGripEnabled(True)
	  
		allRepr = thread.getRepresentationAllTags(fileList)
		self.layout = QtGui.QGridLayout()
		
		self.buttonAdd = QtGui.QPushButton('Add')
		self.buttonOk = QtGui.QPushButton('Ok')
		self.buttonCancel = QtGui.QPushButton('Cancel')
		self.layout.addWidget(self.buttonAdd, 0, 0)
		self.layout.addWidget(self.buttonCancel, 0, 1)
		self.layout.addWidget(self.buttonOk, 0, 2)

		formLayout = QtGui.QFormLayout()
		self.artistLine = QtGui.QLineEdit(self)
		self.artistLine.setText(allRepr.get('ARTIST', ''))
		self.albumLine = QtGui.QLineEdit(self)
		self.albumLine.setText(allRepr.get('ALBUM', ''))
		self.yearLine = QtGui.QLineEdit(self)
		self.yearLine.setText(allRepr.get('DATE', ''))
		self.genreLine = QtGui.QLineEdit(self)
		self.genreLine.setText(allRepr.get('GENRE', ''))
		
		formLayout.addRow('Artist', self.artistLine)
		formLayout.addRow('Album', self.albumLine)
		formLayout.addRow('Year', self.yearLine)
		formLayout.addRow('Genre', self.genreLine)
		
		self.layout.addLayout(formLayout, 1, 0, 1, 3)
		
		self.tagTable = QtGui.QTableView()
		self.model = QtGui.QStandardItemModel()
		self.tagTable.setModel(self.model)
		
		# Add rows
		listKeys = [ x for x in thread.getAllKeys(fileList) 
				if x not in  ['ARTIST', 'ALBUM', 'DATE', 'GENRE'] ]
		allTags = thread.getAllTags(fileList)
		
		attribs = [[allTags[key][file] for key in listKeys] 
				for file in range(len(fileList))]
		nodes = [[QtGui.QStandardItem(x) for x in attrList]
				for attrList in attribs ]
		for n in nodes:
			self.model.appendRow(n)
		
		# Add the headers to the list of values
		attribs.append(listKeys)
		fontMetric = QtGui.QFontMetrics(QtGui.QFont())
		colWidth = [[fontMetric.width(x) for x in l] for l in attribs]
		maxWidth = [max(x) for x in zip(*colWidth)]
		# Fill headers
		for i,h in enumerate(listKeys):
			self.model.setHeaderData(i,QtCore.Qt.Horizontal,h.title())
			self.tagTable.horizontalHeader().resizeSection(i, maxWidth[i])
			
		self.tagTable.setAlternatingRowColors(True)
		self.tagTable.setWordWrap(False)
		self.tagTable.verticalHeader().hide()
		self.tagTable.horizontalHeader().setHighlightSections(False)
		self.tagTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
		self.tagTable.horizontalHeader().setStretchLastSection(True)
		
		self.layout.addWidget(self.tagTable, 2, 0, 1, 3)
		
		self.setLayout(self.layout)
		self.buttonOk.clicked.connect(self.saveChanges)
		self.buttonCancel.clicked.connect(self.refuse)
		self.buttonAdd.clicked.connect(self.addColumn)
		
		self.tagTable.horizontalHeader().sectionDoubleClicked.connect(self.changeHorizontalHeader)
		screen = QtGui.QDesktopWidget().screenGeometry()
		self.resize(min(sum(maxWidth)+10, screen.width()-10), self.sizeHint().height())
		
	def addColumn(self):
		name, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
            			'Name of this new tag:')
		if ok:
			name = name.upper()
			headers = [self.model.horizontalHeaderItem(x).text().upper() 
					for x in range(self.model.columnCount())]
			
			if name not in headers:
				emptyColumn = [QtGui.QStandardItem('') for x in range(self.model.rowCount())]
				self.model.appendColumn(emptyColumn)
				self.model.setHeaderData(self.model.columnCount()-1,
					QtCore.Qt.Horizontal,name.title())
				
	
	
	def saveChanges(self):
		headers = [self.model.horizontalHeaderItem(x).text().upper() 
				for x in range(self.model.columnCount())]
		generalTags = {'ARTIST':self.artistLine.text().strip(), 
				'ALBUM':self.albumLine.text().strip(), 
				'DATE':self.yearLine.text().strip(), 
				'GENRE':self.genreLine.text().strip()}
		fileList = []
		for r in range(self.model.rowCount()):
			values = [x.text().strip() for x in self.model.takeRow(0)]
			
			tags = dict(zip(headers, values))
			tags.update({k: v for k, v in generalTags.items() if v != 'Multiple Values'})
			tags.update(self.columnsToRemove)
			
			# This dict contains the tags to write and '' tags to be deleted
			modified = thread.modifyTags(tags)
			if modified:
				fileList.append(tags['FILE'])
		thread.updateDB(fileList)
		self.accept()

	def changeHorizontalHeader(self, index):
		oldHeader = self.tagTable.model().horizontalHeaderItem(index).text()
		newHeader, ok = QtGui.QInputDialog.getText(self,
						'Change tag name', 'New tag name:',
						QtGui.QLineEdit.Normal, oldHeader)
		if ok:
			self.tagTable.model().horizontalHeaderItem(index).setText(newHeader.title())
			self.columnsToRemove[oldHeader.upper()]=''
	
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Delete:
			index = self.tagTable.selectedIndexes()
			for i in index:
				self.tagTable.model().itemFromIndex(i).setText('')

	def refuse(self):
		self.close()

	def exec_(self):
		if QtGui.QDialog.exec_(self) == QtGui.QDialog.Accepted:
			return  1
		else:
			return 0
			
