#import sys, pprint, time

import json

import taglib
import os
#mapping de albumartist vers artist si albumartist n'est pas renseigné


class Song:

	def __init__(self, dict, commDisp):
		self.tags={}
		self.tags['file'] = dict['FILE']
		self.tags['length'] = dict['LENGTH']
		self.tags['samplerate'] = dict['SAMPLERATE']
		self.tags['channels'] = dict['CHANNELS']
		self.tags['bitrate'] = dict['BITRATE']
		(str, fields) = Song.getTagName(commDisp)
		for f in fields:
			if f.upper() in dict:
				self.tags[f]=dict[f.upper()]
			else:
				if f == 'albumartist' and 'ARTIST' in dict:
					self.tags[f]=dict['ARTIST']
				elif f == 'trackartist' and 'ARTIST' in dict and 'ALBUMARTIST' in dict and dict['ARTIST'] != dict['ALBUMARTIST']:
					self.tags[f]=dict['ARTIST']
				else:
					self.tags[f]='???'

	def to_string(self):
		return str(self.tags)


	@staticmethod
	#ajoute les tag contenue dans 'str' a la liste 'tags'
	#et retourne 'str' vidé de ses tags
	def getTagName(str, optionalTags=False): #(str,tags):
		if optionalTags == True:
			separator="$"
		else:
			separator="%"
		indices = [i for i, x in enumerate(str) if x == separator]
		length = len(indices)//2
		tags = []
		for i in range(0, length):
			tags.append(str[indices[2*i]+1:indices[2*i+1]])
		for t in tags:
			str = str.replace(t, '')	
		return (str, tags)


	#get all attributes in attrList in a list
	def getAttribs(self, attrList):
		attribs = []
		for attr in attrList:
			if attr in self.tags:
				attribs.append(self.tags[attr])
			else:
				if attr == 'artist' and 'albumartist' in self.tags:
					attribs.append(self.tags['albumartist'])
				else:
					attribs.append("foiragefonctiongetAttribs")
					print(self.tags)

		return attribs

	#get all attributes in attrList in a list
	def getAttribsSort(self, attrList):
		#print('called')
		attribs = []
		for attr in attrList:
			if attr == 'tracknumber':
				#print('	VV')
				try: 
					int(self.tags['tracknumber'])
					isInt = True
				except ValueError:
					isInt = False
				if isInt:
					attribs.append("%05d" % int(self.tags['tracknumber']))
			elif attr in self.tags:
				attribs.append(self.tags[attr])
			else:
				if attr == 'albumartist' and 'artist' in self.tag:
					attribs.append(self.tags['artist'])
				else:
					attribs.append("foiragefonctiongetAttribs")
			
		return attribs

	
	#get attributes customized with string around
	# '[%date%] - %artist%' will give '[1998] - DaftPunk'
	def getAttribsCustom(self, comm, sort=False):
		comms = [x.strip() for x in comm.split('|')]
		customAttribs = []
		for comm in comms:
			(commEmptied,tags) = Song.getTagName(comm)
			if sort:
				attribs = self.getAttribsSort(tags)
			else:
				attribs = self.getAttribs(tags)
			for attr in attribs:
				commEmptied = commEmptied.replace('%%', str(attr), 1)
			customAttribs.append(commEmptied)
		return customAttribs
	

	#Ajoute le support de '$ ... $' pour des chaines optionelles
	def getOptionalAttribs(self,comm, sort=False):
		(commEmptied, oParts) = Song.getTagName(comm, True)
		oRes = []
		for p in oParts:
			(oPartEmptied, otags) = Song.getTagName(p)
			oAttribs = self.getAttribs(otags)
			for attr in oAttribs:
				oPartEmptied = oPartEmptied.replace('%%', str(attr), 1)
			oRes.append(oPartEmptied)
		for p in oRes:
			if '???' not in p:
				commEmptied = commEmptied.replace('$$', str(p), 1)
			else :
				commEmptied = commEmptied.replace('$$', '', 1)
		return self.getAttribsCustom(commEmptied, sort)





#return true iif str exactly matches at least one field of dict
# {} -> str -> bool
def exactMatch(song, str):
    str = str.lower()
    for value in song.tags.values():
        if value.lower() == str:
            return True
    return False
 
 
#return true if any substring of strg of length 3 is a sub string of at least one field of dict
def fuzzyMatch(song, strg):
    strg = strg.lower()
    if len(strg) > 2:
        for value in song.tags.values():
            for index in range(0, len(strg)-2):
                substr = strg[index]+strg[index+1]+strg[index+2]
                if str(value).lower().find(substr) != -1:
                    return True
    else:
        for value in song.tags.values():
                if str(value).lower().find(strg) != -1:
                    return True
    return False


#return true if str is a sub string of at least one field of dict
def preciseMatch(song, strg):
	strg = strg.lower()
	for value in song.tags.values():
		if str(value).lower().find(strg) != -1:
			return True
	return False

# Filtre la liste des chansons selon le prédicat (exact ou fuzzy)
# [{}] -> pred -> str -> bool
def filter(songList, pred, str):
    return [ e for e in songList if pred(e, str) ]




#@staticmethod
def exploreMusicFolder(musicFolder, append):
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
				dico['FILE'] = os.path.join(root, name)
				dico['LENGTH'] = file.length
				dico['SAMPLERATE'] = file.sampleRate
				dico['CHANNELS'] = file.channels
				dico['BITRATE'] = file.bitrate
				database.append(dico)
				print(os.path.join(root, name))
	sanitize(database)
	if append:
		db = load()
		database.extend(db)
		
		
	save(database)
	return database



def save(database):
	#Dossier du fichier
	localFolder=os.path.dirname(os.path.realpath(__file__))
	with open(os.path.join(localFolder,'musicDB.json'), mode='w', encoding='utf-8') as f:
		json.dump(database, f, indent=2)
def load():
	#Dossier du fichier
	localFolder=os.path.dirname(os.path.realpath(__file__))
	try:
		with open(os.path.join(localFolder,'musicDB.json'), 'r', encoding='utf-8') as f:
			return json.load(f)
	except IOError:
   		return []

def sanitize(database):
	for dico in database:
		if 'TRACKNUMBER' in dico:	
			try: 
				int(dico['TRACKNUMBER'])
				isInt = True
			except ValueError:
				isInt = False
			if isInt:
				dico['TRACKNUMBER']=str(int(dico['TRACKNUMBER']))

