
import os, sys

from PyQt4 import QtCore
from PyQt4 import QtGui
import taglib
import json
from collections import defaultdict


#temp
import time


# Used a lot so just define that folder variable
if getattr(sys, 'frozen', False):
	localFolder = os.path.dirname(os.path.realpath(sys.executable))
else:
	localFolder = os.path.dirname(os.path.realpath(__file__))

# Return the list of all single tag present in all the files
def getAllKeys(fileList):
	return list({key for file in fileList for key in taglib.File(file).tags }) + ['FILE']

# Return a dict with a single key for every tag among the file list
# values are list with one element for every file, might be empty if tag doesnt exist in a file
def getAllTags(fileList):
	allKeys = {key for file in fileList for key in taglib.File(file).tags}

	allTags = defaultdict(list)
	for file in fileList:
		allTags['FILE'].append(file)
		for key in allKeys:
			allTags[key].append(', '.join(taglib.File(file).tags.get(key, '')))

	return allTags



def getRepresentationAllTags(fileList):
    allTags = getAllTags(fileList)
    return {key: value[0] if value.count(value[0]) == len(value) else 'Multiple Values' for (key, value) in allTags.items()}

# Modify the file tags 
def modifyTags(tags):
	modified=False
	file = taglib.File(tags['FILE'])
	for (k, v) in tags.items():
		if v == '':
			if file.tags.get(k, None) != None:
				del file.tags[k]
				modified=True
		elif k == 'FILE':
			pass
		else:
			if file.tags.get(k,None) != [v]:
				file.tags[k] = [v]
				modified = True
	file.save()
	return modified

def exploreMusicFolder(musicFolder, append):
	print("lets walk")
	allFiles = ((taglib.File(os.path.join(root, name)), os.path.join('file://'+root, name) )
		for root,dirs,files in os.walk(musicFolder, topdown=True) 
		for name in files 
		if name.lower().endswith(".flac") or name.lower().endswith(".mp3"))
	
	
	# Should try to replace with list comprehension
	# using dict merging : z = {**x, **y}
	# database = [{**{key:', '.join(value) for (key, value) in f.tags.items() }, 
	#		**{'FILE':p, 'LENGTH':f.length, 'SAMPLERATE': f.sampleRate, 'CHANNELS':f.channels, 'BITRATE':f.bitrate}}
	#			for (f,p) in allFiles]
	database =[]
	for (f, p) in allFiles:
		print(f)
		print(p)
		tags = {key:', '.join(value) for (key, value) in f.tags.items() }
		tags.update({'FILE':p, 'LENGTH':f.length, 'SAMPLERATE': f.sampleRate, 'CHANNELS':f.channels, 'BITRATE':f.bitrate})
		database.append(tags)

	sanitize(database)
	if append:
		db = load()
		database.extend(db)
		
	save(database)
	print('Finished scanning music folder')
	return database
	
''' Try with more music in folders
def exploreMusicFolder2(musicFolder, append):
	database =[]
	for root, dirs, files in os.walk(musicFolder, topdown=True):
		for name in files:
			if name.lower().endswith(".flac") or name.lower().endswith(".mp3"):
				path=os.path.join(root, name)
				file = taglib.File(path)
				dico = file.tags
				for key, value in dico.items():
					#if it's a list, concatenate, otherwise, take the value
					if len(dico[key]) == 1:
						dico[key]=value[0]
					else :
						dico[key]=', '.join(value)
				# Dict comprehension 1 liner
				# dico = {key: value[0] if len(file.tag[key]) == 1 else key: ', '.join(value) for (key, value) in file.tags.items()}
				dico['FILE'] = os.path.join('file://'+root, name)
				dico['LENGTH'] = file.length
				dico['SAMPLERATE'] = file.sampleRate
				dico['CHANNELS'] = file.channels
				dico['BITRATE'] = file.bitrate
				database.append(dico)

	sanitize(database)
	if append:
		db = load()
		database.extend(db)
		
	save(database)
	print('Finished scanning music folder')
	return database
'''

def save(database):
	with open(os.path.join(localFolder,'musicDatabase.json'), mode='w', encoding='utf-8') as f:
		json.dump(database, f, indent=2)
  

def load():
	try:
		with open(os.path.join(localFolder,'musicDatabase.json'), 'r', encoding='utf-8') as f:
			return json.load(f)
	except IOError:
   		return []

def sanitize(database):
	for dico in database:
		track = dico.get('TRACKNUMBER', None)
		if track != None:
			try: 
				track = str(int(dico['TRACKNUMBER']))
				if len(track) == 1:
					dico['TRACKNUMBER'] = track.rjust(2, '0')
				else:
					dico['TRACKNUMBER'] = track
			except ValueError:
				pass

# Update the database, replacing all dicts in listDictTags
def updateDB(fileList):
	taglibFiles = [taglib.File(f) for f in fileList]
	listTags = [{key:', '.join(value) for (key, value) in f.tags.items()}
			for f in taglibFiles]
	for index, f in enumerate(taglibFiles):
		listTags[index].update({'FILE':'file://'+f.path, 'LENGTH':f.length,
					'SAMPLERATE': f.sampleRate,
					'CHANNELS':f.channels, 'BITRATE':f.bitrate})

	database = load()
	for i in range(len(database)):
		for j in range(len(listTags)):
			if database[i]['FILE'] == listTags[j]['FILE']:
				print('found')
				database[i] = listTags[j]
	save(database)

class WorkThread(QtCore.QObject):
	finished = QtCore.pyqtSignal()
	def __init__(self, musicFolder, append):
		QtCore.QObject.__init__(self)
		self.musicFolder = musicFolder
		self.append = append
		
	def process(self):
		#start1 = time.perf_counter()
		exploreMusicFolder(self.musicFolder, self.append)
		#start2 = time.perf_counter()
		#print('time', start2-start1)
		#self.deleteLater()
		self.finished.emit()


class WorkThreadPipe(QtCore.QObject):

	hotKey = QtCore.pyqtSignal(str)
	finished = QtCore.pyqtSignal()
   
	def __init__(self):
		QtCore.QObject.__init__(self)

	def process(self):
		pipePath=localFolder+'/pipe'
		# Constantly read the pipe and emit a signal every time there is something to read
		pipein = open(pipePath, 'r')
		while True:
			line = pipein.read()
			if line != '':
				self.hotKey.emit(line.replace('\n', ''))				
				# Reopen because is kind of blocking and waiting for a new input
				pipein = open(pipePath, 'r')

		finished.emit()
