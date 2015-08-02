# -*- coding: utf-8 -*-

class Song(dict):
	
	def __getitem__(self, key):
		if key == 'albumartist':
			return self.get('albumartist', None) or self.get('artist', None) or '???'
		elif key == 'trackartist':
			albumArtist = self.get('albumartist', None)
			artist = self.get('artist', None)
			
			if albumArtist != artist and albumArtist != None and artist != None:
				return artist
			else:
				return '???'
		else:
			return self.get(key, '???')
	
	
	#add tag names included in 'str' into 'tags'
	#et retourne 'str' vidé de ses tags
	#e.g. optionalTags False : ' %tracknumber%. %title% $- %trackartist%$ 
	#           -> (' %%. %% $- %%$', ['tracknumber', 'title', 'trackartist'])
	#e.g. optionalTags True : ' %tracknumber%. %title% $- %trackartist%$ 
	#                    -> (' %tracknumber%. %title% $$', ['- %trackartist%'])
	@staticmethod
	def getTagName(strOrder, optionalTags=False):
		if optionalTags == True:
			separator="$"
		else:
			separator="%"
		indices = [i for i, x in enumerate(strOrder) if x == separator]
		length = len(indices)//2
		tags = [strOrder[indices[2*i]+1:indices[2*i+1]] for i in range(0, length)]
		for t in tags:
			strOrder = strOrder.replace(t, '', 1)
		return (strOrder, tags)
			
	def __init__(self, treeOrder, **kwargs):
		super().__init__(self)
		
		(str, fields) = Song.getTagName(treeOrder)
		fields.extend(['file', 'length', 'samplerate', 'channels', 'bitrate'])
		
		for f in fields:
			if f.upper() in kwargs:
				self.__setitem__(f, kwargs[f.upper()])
			elif f == 'albumartist':
				if 'ARTIST' in kwargs:
					self.__setitem__( 'artist', kwargs['ARTIST'])
			elif f == 'trackartist':
				if 'ARTIST' in kwargs:
					self.__setitem__( 'artist', kwargs['ARTIST'])

	# Return the list of values for tag names tagNameList
	def getValues(self, tagNameList):
		return [self[name] for name in tagNameList]

	# Return tag values customized with string around
	# '[%date%] | -%artist%' will give ['[1998]', '-DaftPunk']
	def getFormatedValues(self, treeOrder):
		treeLevels = [x.strip() for x in treeOrder.split('|')]
		formatedValues = []
		for level in treeLevels:
			(emptiedLevel, tagNames) = Song.getTagName(level)
			
			values = self.getValues(tagNames)
			for val in values:
				emptiedLevel = emptiedLevel.replace('%%', str(val), 1)
			formatedValues.append(emptiedLevel)
		return formatedValues
					
	# Add support for optional formating using '$ ... $'
	def getOptionalValues(self, treeOrder):
		#TODO Rewrite
		(emptiedTreeOrder, optionalParts) = Song.getTagName(treeOrder, True)
		optionalValues1 = []
		for part in optionalParts:
		    (emptiedPart, optionalTagNames) = Song.getTagName(part)
		    optionalValues = self.getValues(optionalTagNames)
		    for val in optionalValues:
		        emptiedPart = emptiedPart.replace('%%', str(val), 1)
		    optionalValues1.append(emptiedPart)
		
		for val in optionalValues1:
		    if '???' not in val:
		        emptiedTreeOrder = emptiedTreeOrder.replace('$$', str(val), 1)
		    else :
		        emptiedTreeOrder = emptiedTreeOrder.replace('$$', '', 1)
		return self.getFormatedValues(emptiedTreeOrder)		
		
	# Return true iif searchedStr exactly matches at least one field of the song
	# Do not match case
	def exactMatch(self, searchedStr):
		searchedStr = searchedStr.lower()
		for value in self.values():
		    if value.lower() == searchedStr:
		        return True
		return False	
	
	# Return true if searchedStr is a substring of at least one field of song
	# Do not match case
	def preciseMatch(self, searchedStr):
		searchedStr = searchedStr.lower()
		for value in self.values():
			if str(value).lower().find(searchedStr) != -1:
				return True
		return False	
	
	# Return true if any substring of searchedStr of length 3 is
	# a sub string of at least one field of song, do not match case
	def fuzzyMatch(self, searchedStr):
		searchedStr = searchedStr.lower()
		if len(searchedStr) > 2:
		    for value in self.values():
		        for index in range(0, len(searchedStr)-2):
		            substr = searchedStr[index]+searchedStr[index+1]+searchedStr[index+2]
		            if str(value).lower().find(substr) != -1:
		                return True
		else:
		    for value in self.values():
		            if str(value).lower().find(searchedStr) != -1:
		                return True
		return False
		
		
		