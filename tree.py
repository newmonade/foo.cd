import sys, os

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QWidget, QTreeView, QStandardItemModel, QAbstractItemView, QStandardItem, QItemSelectionModel)

from PyQt4 import QtCore
from PyQt4 import QtGui

#import song
from song import Song
import thread


class Tree(QTreeView):
	def sortFunc(self,chanson):
		return chanson.getOptionalValues(self.comm)

	
	def populateTree(self,disco):
		
		#get all attributes from first song
		if len(disco) < 1:
			attribs = {}
		else:
			attribs = disco[0].getOptionalValues(self.comm)
		length=len(attribs)
		
		
		if length >0:
			#Create corresponding nodes
			nodes = []
			for i in attribs:
				nodes.append(QStandardItem(i))
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



	addSongs = QtCore.pyqtSignal(list,bool)
	

	def __init__(self, parent, comm):
		super(Tree, self).__init__(parent)
		self.comm=comm
		self.initUI()
        
	def initUI(self):
		self.setModel(QStandardItemModel())

		self.setUniformRowHeights(True)
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)	#Cellules pas editables
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setHeaderHidden(True)

		db = thread.load()

		songList = []
		for dict in db:
			songList.append(Song(dict,self.comm))
		
		songList.sort(key=self.sortFunc)
		self.populateTree(songList)

		self.show()
	



	def focusOutEvent(self, e):
		self.selectionModel().clearSelection()

	def focusInEvent(self, e):
		self.selectionModel().select(self.selectionModel().currentIndex(),QItemSelectionModel.Select)


	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Return and int(event.modifiers()) == (QtCore.Qt.ShiftModifier):
			#Table.keyPressEvent(self.window().table, event)
			index = self.selectedIndexes()[0]
			crawler = index.model().itemFromIndex(index)
			children=[]
			self.getChildren(crawler,children)
			self.addSongs.emit(children, False)
		elif event.key() == Qt.Key_Return:
			index = self.selectedIndexes()[0]
			crawler = index.model().itemFromIndex(index)
			children=[]
			self.getChildren(crawler,children)
			self.addSongs.emit(children, True)
		else:
			QTreeView.keyPressEvent(self, event)


		


	
	def getChildren(self,item, children):
		if item.hasChildren():
			for childIndex in range(0,item.rowCount()):
				self.getChildren(item.child(childIndex), children)
		else:
			children.append(item.data())