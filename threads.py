

import os, sys

from PyQt4 import QtCore

import song
from song import Song



class WorkThread(QtCore.QThread):
	def __init__(self, mF, appenD):
		QtCore.QThread.__init__(self)
		self.musicFolder = mF
		self.append = appenD
		
	def run(self):
		db = song.exploreMusicFolder(self.musicFolder, self.append)




class WorkThreadPipe(QtCore.QThread):

	hotKey = QtCore.pyqtSignal(str)
   
	def __init__(self):
		QtCore.QThread.__init__(self)

	def run(self):
		#constantly read a pipe and emit a signal avery time there is something to read
		print(os.path.join(sys.path[0], "pipe_test"))
		pipein = open(os.path.join(sys.path[0], "pipe_test"), 'r')
		#pipein = open('/mnt/Data/Documents/Projets/Python/pipe_test', 'r')
		while True:
			line = pipein.read()
			if line != '':
				#print('line:', line)
				self.hotKey.emit(line.replace('\n', ''))
				#reopen because is kind of blocking and waiting for a new input
				pipein = open(os.path.join(sys.path[0], "pipe_test"), 'r')
				
