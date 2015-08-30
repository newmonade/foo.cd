#!/usr/bin/env python


import subprocess as sp
import sys
import os

from PyQt4.QtGui import QImage, qRgba
from PyQt4.QtCore import QObject, pyqtSignal

import struct
import sqlite3
import json
import multiprocessing
from functools import reduce

WIDTH=1024
HEIGHT=720



def normalize(li, width = WIDTH, height = HEIGHT):
	mymax = max(li)
	mymin = min(li)
	sampling = len(li)//width
	amplitude = height
	li= [int(amplitude * ((x-mymin)/(mymax-mymin))) for x in li]
	
	res = [(0,0) for x in range(width)]
	
	for i in range(width):
		sub = li[i*sampling:(i+1)*sampling]
		sub.append(amplitude//2)
		mymin = min(sub)
		mymax = max(sub)
		bottom = [x for x in sub if x >= amplitude//2]
		top = [x for x in sub if x <= amplitude//2]
		myavpos = reduce(lambda x, y: x + y, bottom) // len(bottom)
		myavneg = reduce(lambda x, y: x + y, top) // len(top)
		res[i]=(mymin,myavneg, myavpos, mymax)
	return res

def computeWave(filename):
	command = [ 'ffmpeg',
		'-loglevel', 'quiet',
		'-i', filename,
		'-ac', '1', # mono (set to '2' for stereo)
		'-filter:a', 'aresample=8000',
		'-map', '0:a',
		'-c:a', 'pcm_s16le',
		'-f', 'data',
		'-']
	pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)
	array = pipe.communicate()[0]
	array = [struct.unpack('<h', array[i:i+2])[0] for i in range(0, len(array), 2)]
	return (filename, normalize(array))
	
def createDB():
	conn = sqlite3.connect('wave.db')	
	c = conn.cursor()
	c.execute('''DROP TABLE IF EXISTS wave''')
	c.execute('''CREATE TABLE IF NOT EXISTS wave
	             (file text, data text)''')
	conn.commit()

def insertDB(data):
	conn = sqlite3.connect('wave.db')
	c = conn.cursor()
	data = [(x[0], json.dumps(x[1])) for x in data]
	c.executemany('INSERT INTO wave VALUES (?,?)', data)
	conn.commit()
	

def getDBData(filename):
	conn = sqlite3.connect('wave.db')
	c = conn.cursor()
	c.execute('SELECT data FROM wave WHERE file=?', (filename,))
	res = c.fetchone()
	res = res[0]
	return json.loads(res)

def scan(folder):
	data = []
	pool = multiprocessing.Pool(4)
	for (root, dirs, files) in os.walk(folder):
		filenames = [os.path.join(root, x) for x in files if (x.endswith(".flac") or x.endswith(".mp3"))]
		
		filenames, waves = zip(*pool.map(computeWave, filenames))
		res = zip(list(filenames),list(waves))
		res = list(res)
		
		data.extend(res)
	return data


def createImg(data):
	img = QImage(WIDTH, HEIGHT, QImage.Format_ARGB32_Premultiplied)
	for i in range(WIDTH):
		fore = qRgba(255, 255, 255,255)
		foreInside = qRgba(127, 127, 127,127)
		back = qRgba(0, 0, 0, 0)
		for j in range(HEIGHT):
			if data[i][0] <= j < data[i][1]:
				img.setPixel(i, j, fore)
			if data[i][1] <= j < data[i][2]:
				img.setPixel(i, j, foreInside)
			if data[i][2] <= j < data[i][3]:
				img.setPixel(i, j, fore)
	img.save('wave.png', 'png')

class Wave(QObject):

	finished = pyqtSignal()
   
	def __init__(self, musicFolder):
		QtCore.QObject.__init__(self)
		self.musicFolder = musicFolder
		
	def processScan(self):
		createDB()
		data = scan(self.musicFolder)
		insertDB(data)
		print("finished wave db creation")
		self.finished.emit()



	
#ffmpeg -i "/mnt/Data/Documents/Boogie Bones/2001 - Duke Ellington - Love Songs [FLAC]/01 - Satin Doll.flac" -ac 1 -filter:a aresample=8000 -map 0:a -c:a pcm_s16le -f data -