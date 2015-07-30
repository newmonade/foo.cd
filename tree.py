import sys, os

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QWidget, QTreeView, QStandardItemModel, QAbstractItemView, QStandardItem, QItemSelectionModel)

from PyQt4 import QtCore
from PyQt4 import QtGui

#import song
from song import Song
import thread

# For natural sorting
import re

#temporaly
import time

class Tree(QTreeView):

	def sortFunc(self,chanson):
		(emptiedLevel, tagNames) = Song.getTagName(self.comm)
		values = ' '.join(chanson.getValues(tagNames))
		def tryint(s):
			try:
				return int(s)
			except:
				return s
		# Split the string between numeric and literal chunks and 
		# return a list of string and int
		return [ tryint(c) for c in re.split('([0-9]+)', values) ]

		
	
	def populateTree(self,disco):
		
		# Get all attributes from first song
		if len(disco) < 1:
			attribs = {}
		else:
			attribs = disco[0].getOptionalValues(self.comm)
		length=len(attribs)
			
		if length >0:
			# Create corresponding nodes
			nodes = []
			for i in attribs:
				nodes.append(QStandardItem(i))
			# Add them to each other
			for i in range(1, length):
				nodes[i-1].appendRow(nodes[i])
			# Add data to the last one
			nodes[length-1].setData(disco[0])
			# Append to tree
			self.model().appendRow(nodes[0])
		else:
			#Create corresponding nodes
			nodes = [QStandardItem('Nothing')]
			nodes[0].setData('nothing')
			self.model().appendRow(nodes[0])
	
		#Pour la tail de la liste
		for s in disco[1:]:
			attr = s.getOptionalValues(self.comm)
			length=len(attr)
			#First attribut separated because attached to node
			if attr[0] != attribs[0]:
				node=QStandardItem(attr[0])
				#self.model().appendRow(node)
				nodes[0]=node
				self.model().appendRow(nodes[0])
				attribs[0]=attr[0]		
			
			for i in range(1, length-1):
				if (attr[i] != attribs[i]):# or differ:
					node=QStandardItem(attr[i])
					nodes[i-1].appendRow(node)
					if i<len(nodes):
						nodes[i]=node
					else:
						nodes.append(node)
					attribs[i]=attr[i]
			#Dernier attribut
			node = QStandardItem(attr[length-1])
			nodes[length-2].appendRow(node)
			node.setData(s)
			
	#should be checked on big librairy before using this version
	'''
	def populateTree(self,disco):
		#get all attributes from first song
		if len(disco) < 1:
			attribs = {}
		else:
			attribs = disco[0].getOptionalValues(self.comm)
		length=len(attribs)
		
		if length >0:
			#Create corresponding nodes
			nodes = [QStandardItem(x) for x in attribs]
			#Add them to each other
			for i in range(1, length):
				nodes[i-1].appendRow(nodes[i])
			#Add data to the last one
			nodes[length-1].setData(disco[0])
			#Append to tree
			self.model().appendRow(nodes[0])
		else:
			#Create corresponding nodes
			nodes = [QStandardItem('Nothing')]
			nodes[0].setData('nothing')
			self.model().appendRow(nodes[0])

		
		#Pour la tail de la liste
		#for s in disco[1:]:
		#	attr = s.getOptionalValues(self.comm)
		#	length=len(attr)
		for attr in (s.getOptionalValues(self.comm) for s in disco[1:]):
			length=len(attr)
			#First attribut separated because attached to node
			if attr[0] != attribs[0]:
				node=QStandardItem(attr[0])
				#self.model().appendRow(node)
				nodes[0]=node
				self.model().appendRow(nodes[0])
				attribs[0]=attr[0]		
			
			for i in range(1, length-1):
				if (attr[i] != attribs[i]):# or differ:
					node=QStandardItem(attr[i])
					nodes[i-1].appendRow(node)
					if i<len(nodes):
						nodes[i]=node
					else:
						nodes.append(node)
					attribs[i]=attr[i]
			#Dernier attribut
			node = QStandardItem(attr[length-1])
			nodes[length-2].appendRow(node)
			node.setData(attr)
	'''
	
	addSongs = QtCore.pyqtSignal(list,bool)
	
	def __init__(self, parent, comm):
		super(Tree, self).__init__(parent)
		self.comm=comm
		self.initUI()
        
	def initUI(self):
		self.setModel(QStandardItemModel())
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.setUniformRowHeights(True)
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setHeaderHidden(True)

		db = thread.load()
		songList = [Song(self.comm, **dict) for dict in db]
		
		songList.sort(key=self.sortFunc)
		
		#start1 = time.perf_counter()
		self.populateTree(songList)
		#start2 = time.perf_counter()
		#print('time', start2-start1)
		
		self.show()
	



	def focusOutEvent(self, e):
		self.selectionModel().clearSelection()

	def focusInEvent(self, e):
		self.selectionModel().select(self.selectionModel().currentIndex(),QItemSelectionModel.Select)

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Return and int(event.modifiers()) == (QtCore.Qt.ShiftModifier):
			#Table.keyPressEvent(self.window().table, event)
			#index = self.selectedIndexes()[0]
			#crawler = self.model().itemFromIndex(index)
			#children=[]
			children = self.getChildren()
			self.addSongs.emit(children, False)
		elif event.key() == Qt.Key_Return:
			#index = self.selectedIndexes()[0]
			#crawler = self.model().itemFromIndex(index)
			#children=[]
			children = self.getChildren()
			self.addSongs.emit(children, True)
		else:
			QTreeView.keyPressEvent(self, event)

	
	# to delete
	def getChildrenOld(self,item, children):
		if item.hasChildren():
			for childIndex in range(0,item.rowCount()):
				self.getChildren(item.child(childIndex), children)
		else:
			children.append(item.data())

	# to delete
	def getChildrenShit(self,item):
		def getChildrenRec(self, item, children):
			if item.hasChildren():
				for childIndex in range(0,item.rowCount()):
					getChildrenRec(self, item.child(childIndex), children)
			else:
				children.append(item.data())
		res = []
		getChildrenRec(self, item, res)
		return res
			
	def getChildren(self):
		def getChildrenRec(self, item, children):
			if item.hasChildren():
				for childIndex in range(0,item.rowCount()):
					getChildrenRec(self, item.child(childIndex), children)
			else:
				children.append(item.data())
		res = []
		index = self.selectedIndexes()[0]
		crawler = self.model().itemFromIndex(index)
		getChildrenRec(self, crawler, res)
		return res		
			
			