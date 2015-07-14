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
