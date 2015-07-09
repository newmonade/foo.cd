from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QStandardItemModel, QAbstractItemView, QStandardItem,
			QItemSelection, QItemSelectionModel, QTableView)

from PyQt4 import QtCore
from PyQt4 import QtGui


from song import Song



#------Player---------------------
from gi.repository import GObject
from gi.repository import Gst
Gst.init(None)
#---------------------------------



class TableRadio(QtGui.QTableView):

	#songUpdate = QtCore.pyqtSignal(str)

	def addRow(self, listTags):
		nodes = [QStandardItem('')]
		nodes[-1].setData(listTags) #[-1] is last element
		for i in listTags:
			nodes.append(QStandardItem(i))
			#nodes[-1].setData(song) #[-1] is last element
		self.model().appendRow(nodes) 

	def on_tag(self, bus, msg):
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
		super(TableRadio, self).__init__(parent)
		self.radioConfig = radioConfig
		
		self.initUI()
        
	def initUI(self):

		self.pipeline = Gst.Pipeline()
		self.playbin = Gst.ElementFactory.make('playbin', None)
		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		#self.bus.connect('message::eos', self.onStop)
		self.bus.connect('message::error', self.on_error)
		#self.bus.connect('message::duration-changed', self.onDurationChanged)
		#self.playbin.connect("about-to-finish", self.onAboutToFinish)
		self.bus.connect('message::tag', self.on_tag)
		self.bus.enable_sync_message_emission()	
		self.pipeline.add(self.playbin)
		
	
	



	
		
		
		
		self.playingId = -1
		self.timeOut = -1
		

		
		self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.slider.setFocusPolicy(QtCore.Qt.NoFocus)
		self.slider.setPageStep(1)
		self.slider.setTracking(False)
		
		#self.slider.sliderMoved.connect(self.sliderMoved)
		#self.slider.sliderPressed.connect(self.sliderAction)
		#self.slider.sliderReleased.connect(self.sliderAction)

		self.volumeSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.volumeSlider.setFocusPolicy(QtCore.Qt.NoFocus)
		self.volumeSlider.setTickInterval(1)
		self.volumeSlider.setTracking(False)
		self.volumeSlider.setMaximumWidth(70)
		self.volumeSlider.setMinimum(0)
		self.volumeSlider.setMaximum(100)
		self.playbin.set_property('volume',0.5)
		self.volumeSlider.setSliderPosition(50)

		self.volumeSlider.sliderMoved.connect(self.volumeSliderMoved)

		
		
		

		self.buttonPlay = QtGui.QPushButton(">", self)
		self.buttonPlay.setMaximumSize(25,25)
		self.buttonPlay.setFocusPolicy(QtCore.Qt.NoFocus)
		self.buttonPlay.setFont(QtGui.QFont('TypeWriter', 9))
		self.buttonStop = QtGui.QPushButton("[ ]", self)
		self.buttonStop.setMaximumSize(25,25)
		self.buttonStop.setFocusPolicy(QtCore.Qt.NoFocus)
		self.buttonStop.setFont(QtGui.QFont('TypeWriter', 9))
		self.buttonPrev = QtGui.QPushButton("|<<", self)
		self.buttonPrev.setMaximumSize(25,25)
		self.buttonPrev.setFocusPolicy(QtCore.Qt.NoFocus)
		self.buttonPrev.setFont(QtGui.QFont('TypeWriter', 9))
		self.buttonNext = QtGui.QPushButton(">>|", self)
		self.buttonNext.setMaximumSize(25,25)
		self.buttonNext.setFocusPolicy(QtCore.Qt.NoFocus)
		self.buttonNext.setFont(QtGui.QFont('TypeWriter', 9))
		
		self.buttonPlay.clicked.connect(self.toggleSongFromTable)
		self.buttonStop.clicked.connect(self.stop)
		self.buttonPrev.clicked.connect(self.previous)
		self.buttonNext.clicked.connect(self.next)

		myPixmap = QtGui.QPixmap(200, 200)
		myPixmap.fill(Qt.darkGray)
		myScaledPixmap = myPixmap.scaled(200, 200, Qt.KeepAspectRatio)
		
		self.label = QtGui.QLabel()
		self.label.setPixmap(myScaledPixmap)


		
		tab1 = QtGui.QWidget()	
		tab2 = QtGui.QWidget()
		self.tabs = QtGui.QTabWidget()
		self.tabs.addTab(tab1,"Search")
		self.tabs.addTab(tab2,"Tab 2")
		
		self.searchLine = QtGui.QLineEdit()
		self.searchExactFuzzyGroup = QtGui.QGroupBox()
		self.searchExact = QtGui.QRadioButton('Exact')
		self.searchPrecise = QtGui.QRadioButton('Precise')
		self.searchFuzzy = QtGui.QRadioButton('Fuzzy')
		self.searchPrecise.setChecked(True);
		



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
		
		self.addRow(self.radioConfig['column_order'].split('|'))
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
			print(station)
			self.addRow([st.strip() for st in station.split('!')])
		
		self.resizeColumnsToContents()
		self.resizeRowsToContents()

		self.show()
		
		

		

#----------PLAYER FUNCTIONS----------------------------------------
	def padd(self, uri):
		#realUri = ''.join(['file://', uri])
		self.playbin.set_property('uri', uri)

	def pplay(self):
		self.pipeline.set_state(Gst.State.PLAYING)
		
	def pstop(self):
		self.pipeline.set_state(Gst.State.NULL)

	def ptoggle(self):
		state = self.pipeline.get_state(Gst.State.NULL)
		if state[1] == Gst.State.PLAYING:
			self.pipeline.set_state(Gst.State.PAUSED)
		else:
			self.pipeline.set_state(Gst.State.PLAYING)
	'''
	def pseek(self, val):
		self.playbin.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, val * Gst.SECOND)

	def pgetPosition(self):
		return self.playbin.query_position(Gst.Format.TIME)[1]
	
	def pgetDuration(self):
		return self.playbin.query_duration(Gst.Format.TIME)[1]
	'''

	def psetVolume(self, vol):
		self.playbin.set_property('volume', vol)
		print( self.playbin.get_property('volume'))

	def on_error(self, bus, msg):
		print('on_error():', msg.parse_error())
#------------------------------------------------------------------------------------

	def play(self, url):
		self.pstop()
		self.padd(url)
		self.pplay()

	#Wrapper for event trigger
	def onStop(self,bus, msg):
		self.stop()

	def stop(self):
		self.pstop()
		self.slider.setValue(0)
		self.displayPlayToStop()
		self.stopStatusEmission('Ready')


	def previous(self):
		if self.playingId > 0:
			self.pstop()
			self.playingId-=1
			print('finish',self.playingId)
			self.padd(self.model().item(self.playingId,0).data().tags['file'])
			self.pplay()
			

	def next(self):
		if self.model().rowCount()-1 > self.playingId:
			self.pstop()
			self.playingId+=1
			print('finish',self.playingId)
			self.padd(self.model().item(self.playingId,0).data().tags['file'])
			self.pplay()

	def playSongFromTable(self):
		if self.selectedIndexes():
			index = self.selectedIndexes()[0]
		else:
			index= self.model().index(self.selectionModel().currentIndex().row(),0)
		print(index.row())
		nameAndURL = index.model().itemFromIndex(index).data()
		print(nameAndURL)
		self.play(nameAndURL[1])
		self.displayStopToPlay(index.row())

	def toggleSongFromTable(self):			
		state = self.pipeline.get_state(Gst.State.NULL)
		if state[1] == Gst.State.PLAYING:
			self.displayPlayToPause()
			self.ptoggle()	
			self.onPause()
		else:
			print(self.playingId)
			self.displayPauseToPlay(self.playingId)
			self.ptoggle()
			self.onDurationChanged(0,0)




	'''
	def addAndPlaySongsFromTree(self,list):
		i = self.model().rowCount()
		for l in  list:
			self.addRow(l)
		self.resizeRowsToContents()
		self.play(list[0])
		self.displayStopToPlay(i)
	
	def addSongsFromTree(self,list):
		i = self.model().rowCount()
		for l in  list:
			self.addRow(l)
		self.resizeRowsToContents()

	'''	
	
		
		
	def setStatusEmission(self, status):
		try:
			duration_nanosecs = self.pgetDuration()
			duration = float(duration_nanosecs) / 1000000000
			self.slider.setRange(0, duration)
		except Exception as e:
			print(e)
			pass
		
		def signalEmiting():
			self.songUpdate.emit(status)
			return True
		if self.timeOut > 0:
			GObject.source_remove(self.timeOut)

		self.timeOut = GObject.timeout_add(1000,signalEmiting)
		
		
	def stopStatusEmission(self, status):
		if self.timeOut > 0:
			GObject.source_remove(self.timeOut)
		def signalEmiting():
			self.songUpdate.emit(status)
			return False
		self.timeOut = GObject.timeout_add(0,signalEmiting)
		self.timeOut=-1
	
		
	#when song starts to play
	def onDurationChanged(self,bus, msg):
		self.displayNext()
		song = self.model().item(self.playingId, 0).data()
		status = str(song.tags['bitrate'])+' kbps | '+str(song.tags['samplerate'])+' Hz | '
		if song.tags['samplerate'] == 1:
			status+='Mono'
		else:
			status+='Stereo'
		m, s = divmod(song.tags['length'], 60)
		status+= ' | %/'+"%02d:%02d" % (m, s)+' - Playing'
		
		self.setStatusEmission(status)
		
	
	#when song is paused
	def onPause(self):
		song = self.model().item(self.playingId, 0).data()
		status = str(song.tags['bitrate'])+' kbps | '+str(song.tags['samplerate'])+' Hz | '
		if song.tags['samplerate'] == 1:
			status+='Mono'
		else:
			status+='Stereo'
		m, s = divmod(song.tags['length'], 60)
		status+= ' | %/'+"%02d:%02d" % (m, s)+' - Paused'
		
		self.stopStatusEmission(status)
	
	
	def onAboutToFinish(self, bus):
		if self.model().rowCount()-1 > self.playingId:
			print('finish',self.playingId)
			self.playingId+=1
			print('finish',self.playingId)
			self.padd(self.model().item(self.playingId,0).data().tags['file'])
		

	#Update artwork on selectionChanged
	def selectionChangedCustom(self,selected, deselected):
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


	def focusOutEvent(self, e):
		self.selectionModel().clearSelection()

	def focusInEvent(self, e):
		currentIndex= self.model().index(self.selectionModel().currentIndex().row(),0)
		currentIndex2=self.model().index(currentIndex.row(),self.model().columnCount()-1)
		if currentIndex.row()<0:	#Si on n'est jamais entré dans le widget
			currentIndex= self.model().index(0,0)
			currentIndex2=self.model().index(0,self.model().columnCount()-1)
			self.selectionModel().setCurrentIndex(currentIndex,QItemSelectionModel.Rows)
		
		self.selectionModel().select(QItemSelection(currentIndex,currentIndex2),QItemSelectionModel.Select)


	#met a jour les signes '[ ]' et '>'
	#est forcement appellé par la touche entré venant de l'arbre ou 
	# d'une ligne de la table
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

	
	#met a jour les signes '||' et '>'
	#différent du précédent car peut etre appelé par shortcut
	#et donc ne pas avoir d'indice 
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

	#met a jour les signes '[ ]' et '>'
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
			

	
	#met a jour les signes '[ ]' et '>'
	def displayPlayToStop(self):
		if self.playingId > -1:
			self.model().item(self.playingId,0).setText('[ ]')
			self.playingId = -1
	
	#met a jour les signes '||' et '>'
	def displayPlayToPause(self):
		if self.playingId > -1:
			self.model().item(self.playingId,0).setText('||')
			#self.playingId = -1

	def sliderMoved(self, val):
		self.pseek(val)

	def sliderAction(self):
		self.ptoggle()
	
	def volumeSliderMoved(self, val):
		self.psetVolume(val/100)
		
	def volumeSliderIncr(self):
		incrVol = self.playbin.get_property('volume')*100+10
		if incrVol < 110:
			self.volumeSlider.setSliderPosition(incrVol)
			self.psetVolume(incrVol/100)
	
	def volumeSliderDecr(self):
		decrVol = self.playbin.get_property('volume')*100-10
		self.volumeSlider.setSliderPosition(decrVol)
		self.psetVolume(decrVol/100)
		

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_A and int(event.modifiers()) == (QtCore.Qt.ShiftModifier):
			print('should not happen as it is in shortcuts now')
		elif event.key() == Qt.Key_Delete:
			index = self.selectedIndexes()[0]
			crawler = index.model().itemFromIndex(index)
			row=crawler.row()
			childIndex=self.model().index(row+1,0)
			childIndex2=self.model().index(row+1,self.model().columnCount()-1)
			self.selectionModel().clearSelection()
			self.selectionModel().select(QItemSelection(childIndex,childIndex2), QItemSelectionModel.Select)
			self.selectionModel().setCurrentIndex(childIndex,QItemSelectionModel.Rows)
			if self.playingId == row:
				self.stop()
			self.model().removeRow(row)
		elif event.key() == Qt.Key_Return:
			self.playSongFromTable()
		QTableView.keyPressEvent(self, event)



		
		


