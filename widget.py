# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

class PlaybackButtons(QtGui.QHBoxLayout):

	def __init__(self, parent):
		super(QtGui.QHBoxLayout, self).__init__(parent)
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

  
		#self.show()
        
        
class VolumeSlider(QtGui.QSlider):

	def __init__(self, parent):
		super(QtGui.QSlider, self).__init__(QtCore.Qt.Horizontal, parent)
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
		QtGui.QLabel.__init__(self)
		self._pixmap = QtGui.QPixmap(1,1)
		self.initUI()
        
	def initUI(self):
		self._pixmap.fill(Qt.darkGray)


	def resizeEvent(self, event):
		self.setPixmap(self._pixmap.scaled(
		self.width(), self.height(),
		QtCore.Qt.KeepAspectRatio))
            

class SearchArea(QtGui.QGridLayout):

	def __init__(self, parent):
		QtGui.QGridLayout.__init__(self)
		self.initUI()
        
	def initUI(self):
		self.searchLine = QtGui.QLineEdit()
		#searchExactFuzzyGroup = QtGui.QGroupBox(self)
		self.searchExact = QtGui.QRadioButton('Exact')
		self.searchPrecise = QtGui.QRadioButton('Precise')
		self.searchFuzzy = QtGui.QRadioButton('Fuzzy')
		self.searchPrecise.setChecked(True);    
    
		#searchLayout = QtGui.QGridLayout(searchExactFuzzyGroup)
		self.setContentsMargins(0, 0, 0, 0)
		self.addWidget(self.searchLine,0,0,1,3)	
		self.addWidget(self.searchFuzzy,1,0)
		self.addWidget(self.searchPrecise,1,1)
		self.addWidget(self.searchExact,1,2)
		#self.show()


class Equalizer(QtGui.QDialog):
    def __init__(self, config):
    
        QtGui.QDialog.__init__(self)
        self.config = eval(config['settings'])
        self.modified = False
        bandValues = self.config['default']
        frequencies = [ "29Hz", "59Hz", "119Hz", "237Hz", 
            "474Hz", "947Hz", "1.8kHz", "3.7kHz", "7.5kHz", "15kHz"]
        
        self.layout = QtGui.QGridLayout()
        
        self.configList = QtGui.QComboBox()
        self.configList.addItems([x for x in self.config.keys()])
        self.configList.activated[str].connect(self.listActivated)    
 
        self.addButton = QtGui.QPushButton('Add preset')
        self.addButton.clicked.connect(self.addPreset)
        
        self.saveButton = QtGui.QPushButton('Remove')
        self.saveButton.setMaximumWidth(40)
        self.saveButton.clicked.connect(self.removePreset)
        
        self.saveButton = QtGui.QPushButton('Save')
        self.saveButton.setMaximumWidth(40)
        self.saveButton.clicked.connect(self.savePreset)
        
        self.closeButton = QtGui.QPushButton('Quit')
        self.closeButton.setMaximumWidth(40)
        self.closeButton.clicked.connect(self.close)
        
        self.layout.addWidget(self.configList, 0, 0, 1, 3)
        self.layout.addWidget(self.addButton, 0, 3, 1, 2, QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.closeButton, 0, 9, 1, 1, QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.saveButton, 0, 8, 1, 1, QtCore.Qt.AlignCenter)
        
        for index, val in enumerate(bandValues):
            band = QtGui.QLabel(frequencies[index], self)
            slider = QtGui.QSlider(QtCore.Qt.Vertical, self)
            slider.setMinimum(-24)
            slider.setMaximum(12)
            slider.setSliderPosition(val)
            #slider.valueChanged.connect() # Connect to the gstreamer & to the label
            slider.valueChanged.connect(self.updateLabel)
            labelValue = QtGui.QLabel(str(val).rjust(3, ' ')+"dB", self)
            
            self.layout.addWidget(band, 1 , index, 1, 1, QtCore.Qt.AlignCenter)
            self.layout.addWidget(slider, 2 , index, 1, 1, QtCore.Qt.AlignCenter)
            
            self.layout.addWidget(labelValue, 3 , index, 1, 1, QtCore.Qt.AlignCenter)
            band.setAlignment(QtCore.Qt.AlignCenter)
        
        self.setLayout(self.layout)

    def updateLabel(self, val):
        position = self.layout.getItemPosition(self.layout.indexOf(self.sender()))[1]
        self.layout.itemAtPosition(3, position).widget().setText(str(val) + 'dB')

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
                # To save the presets to config file when closing the dialog
                self.modified = True
                print(name, newConf)
    
    def savePreset(self):
        newConf = [self.layout.itemAtPosition(2, index).widget().value() for index in range(0,10)]
        self.config[self.configList.currentText()] = newConf
        self.modified = True
    
    def removePreset(self):
        self.config.pop(self.configList.currentText())
    	self.modified = True
    
    def exec_(self):
        QtGui.QDialog.exec_(self)
        return self.modified
