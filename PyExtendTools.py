# -*- coding: utf-8 -*-

import ast
import json
import os
import pathlib
import py7zr
import re
import shutil
import send2trash
import sys
import tarfile
import time
import psutil
import zipfile
from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, Qt, Signal, QSize, QFile, QEvent)
from PySide6.QtGui import (QFont, QStandardItem, QStandardItemModel, QDesktopServices, QCursor, QPixmap)
from PySide6.QtWidgets import (QApplication, QCheckBox, QLabel, QListView, QLineEdit, QMainWindow, QPlainTextEdit, QPushButton, QTabWidget, QTreeView, QWidget, QFileSystemModel, QMenu, QAbstractItemView, QDialog, QDialogButtonBox, QVBoxLayout, QFileIconProvider)

BackupNowPath = ['']
PathListory = ['']
SelectedItemPath = ['']
CopiedItems = ['']
CopiedItemCount = [0]
SortedNumbar = ['']
SelectedItem = ['0']
QLinePath = ['']
PathHistorys = []
PathHistorys2 = ['']
CheckPaths = ['0']
StopPath = ['0']
StopPath2 = ['0']
NowRootDirectoryPath = ['']
BackupRootPath = [os.path.expanduser('~')]
OneChecked = ['1']
OneChecked2 = ['0']
OneChecked3 = ['0']
BackPageIndex = [1]

class FileSystemListView(QListView):
	def __init__(self, parent, model=QFileSystemModel()):
		super().__init__(parent)
		self.Model = model
		self.setModel(self.Model)
		self.Model.setRootPath(os.path.expanduser("~"))
		try:
			self.setRootIndex(self.Model.index(os.path.expanduser("~")))
		except:
			self.setRootIndex(self.Model.index(os.path.expanduser("~")))
		self.setGeometry(QRect(276, 80, 534, 521))
		font1 = QFont()
		font1.setPointSize(50)
		self.setAutoScroll(False)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.setViewMode(QListView.ListMode)
		self.setIconSize(QSize(45, 45))
		self.setEditTriggers(QAbstractItemView.SelectedClicked)
		self.setContextMenuPolicy(Qt.CustomContextMenu)

	def index(self, path, column=0):
		return self.Model.index(path, column)

	def sort(self, column, order):
		self.Model.sort(column, order)

	def filePath(self, index):
		return self.Model.filePath(index)

	def rootPath(self):
		return self.Model.rootPath()

	def setRootPath(self, path):
		self.Model.setRootPath(path)

	def mousePressEvent(self, event):
		if not NowRootDirectoryPath[0] == '':
			self.RootPath = NowRootDirectoryPath[0]
		else:
			self.RootPath = os.path.expanduser('~')
		self.OutSideMenu = QMenu()
		if event.type() == QEvent.MouseButtonPress:
			if event.button() == Qt.RightButton:
				try:
					for LoopIndex, FileFolderIndex in enumerate(self.selectedIndexes()):
						if os.path.isfile(self.filePath(FileFolderIndex)) and not os.path.islink(self.filePath(FileFolderIndex)) and LoopIndex == 0:
							self.OutSideMenu.addAction('ファイルを開く', self.OutSideOpenFile)
							self.OutSideMenu.addAction('名前の変更', self.OutSideRenames)
						if not os.path.isfile(self.filePath(FileFolderIndex)) and not os.path.islink(self.filePath(FileFolderIndex)) and LoopIndex == 0:
							self.OutSideMenu.addAction('名前の変更', self.OutSideRenames)
							self.OutSideMenu.addAction('フォルダを開く', self.OutSideOpenFile)
						if os.path.isfile(self.filePath(FileFolderIndex)) and not os.path.islink(self.filePath(FileFolderIndex)) and LoopIndex == 0:
							if event.modifiers() == Qt.ShiftModifier:
								self.OutSideMenu.addAction('完全削除', self.OutSideForceDeleting)
							else:
								self.OutSideMenu.addAction('削除', self.OutSideDeleting)
							self.OutSideMenu.addAction('コピー', self.OutSideCopyFile)
							self.OutSideMenu.addAction('移動', self.OutSideCopyFile)
						if os.path.isfile(self.filePath(FileFolderIndex)) and LoopIndex == 0 and self.filePath(FileFolderIndex).endswith('.zip') or self.filePath(FileFolderIndex).endswith('.tar.gz') or self.filePath(FileFolderIndex).endswith('.7z'):
							self.OutSideMenu.addAction('解凍', self.OutSideUnArchive)
						if not os.path.isfile(self.filePath(FileFolderIndex)) and not os.path.islink(self.filePath(FileFolderIndex)) and LoopIndex == 0:
							if event.modifiers() == Qt.ShiftModifier:
								self.OutSideMenu.addAction('完全削除', self.OutSideForceDeleting)
							else:
								self.OutSideMenu.addAction('削除', self.OutSideDeleting)
							self.OutSideMenu.addAction('フォルダのコピー', self.OutSideCopyFile)
							self.OutSideMenu.addAction('フォルダの移動', self.OutSideCopyFile)
					try:
						if os.path.isfile(self.filePath(self.selectedIndexes()[0])) or os.path.isdir(self.filePath(self.selectedIndexes()[0])):
							self.SendMenu = self.OutSideMenu.addMenu('送る')
							self.SendMenu.addAction('圧縮', self.OutSideArchiveCreate)
					except:
						pass
					self.OutSideMenu.addAction('現在の場所を開く', self.OutSideNowOpenFolder)
					self.OutSideMenu.addAction('現在のフォルダパスをコピー', self.OutSideCopiedPath)
					self.OutSideMenu.addAction('フォルダの新規作成', self.OutSideCreateFolder)
					self.OutSideMenu.addAction('新しいファイルを作成', self.OutSideCreateNewFile)
					if not CopiedItems[0] == '':
						self.OutSideMenu.addAction('ここにファイルをコピー', self.OutSideCopiedFiles)
						self.OutSideMenu.addAction('ここにファイルを移動', self.OutSideMovedFile)
					self.OutSideMenu.exec(self.mapToGlobal(event.position().toPoint()))
				except:
					pass
				super(FileSystemListView, self).mousePressEvent(event)
			else:
				super(FileSystemListView, self).mousePressEvent(event)
		else:
			SelectedItem[0] = '0'
			super(FileSystemListView, self).mousePressEvent(event)

	def OutSideCopiedPath(self):
		QApplication.clipboard().setText(self.rootPath())

	def OutSideForceDeleting(self):
		Result = ForceDeletingOKDialog.OutPutResult()
		try:
			if Result == '0':
				for ForceRemove in self.selectedIndexes():
					if os.path.isfile(self.filePath(ForceRemove)):
						os.remove(self.filePath(ForceRemove))
					else:
						shutil.rmtree(self.filePath(ForceRemove))
		except:
			pass

	def OutSideDeleting(self):
		Result = DeletingOKDialog.OutPutResult()
		try:
			if Result == '0':
				for RemoveItem in self.selectedIndexes():
					send2trash.send2trash(self.filePath(RemoveItem))
		except:
			pass

	def OutSideRenames(self):
		SelectedItemPath[0] = self.filePath(self.selectedIndexes()[0]).split(os.sep)[-1]
		Result = InputDiaLog.OutputResult()
		if Result[1] == '0':
			if not Result[0] == '':
				if not Result[0] == ' ':
					text = Result[0]
					oldname = self.filePath(self.selectedIndexes()[0])
					newName = '{}{}'.format(oldname.split(oldname.split(os.sep)[-1])[0], text)
					try:
						os.rename(oldname, newName)
					except:
						pass

	def OutSideOpenFile(self):
		for SelectedIndex in self.selectedIndexes():
			QDesktopServices.openUrl('file:///{}'.format(self.filePath(SelectedIndex)))

	def OutSideNowOpenFolder(self):
		if not NowRootDirectoryPath[0] == '':
			self.RootPath = NowRootDirectoryPath[0]
		else:
			self.RootPath = os.path.expanduser('~')
		QDesktopServices.openUrl('file:///{}'.format(self.RootPath))

	def OutSideCreateFolder(self):
		if not NowRootDirectoryPath[0] == '':
			self.RootPath = NowRootDirectoryPath[0]
		else:
			self.RootPath = os.path.expanduser('~')
		Result = NewCreateFolderDialog.OutputResult()
		if Result[1] == '0':
			if not Result[0] == '':
				if not Result[0] == ' ':
					try:
						os.mkdir('{}{}{}'.format(self.RootPath, os.sep, Result[0]))
					except:
						for c in range(9999):
							try:
								os.mkdir('{}{}{} ({})'.format(self.RootPath, os.sep, Result[0], c))
								break
							except:
								pass

	def OutSideCreateNewFile(self):
		if not NowRootDirectoryPath[0] == '':
			self.RootPath = NowRootDirectoryPath[0]
		else:
			self.RootPath = os.path.expanduser('~')
		Results = NewFileCreateDialog.OutputResults()
		if Results[1] == '0':
			if not Results[0] == '':
				if not Results[0] == ' ':
					with open('{}{}{}'.format(self.RootPath, os.sep, Results[0]), 'w', encoding='utf-8') as NewFile:
						NewFile.write('')

	def OutSideMovedFile(self):
		if not NowRootDirectoryPath[0] == '':
			self.RootPath = NowRootDirectoryPath[0]
		else:
			self.RootPath = os.path.expanduser('~')
		if CopiedItemCount[0] == len(CopiedItems[0]):
			for MoveItem in CopiedItems[0]:
				try:
					shutil.move(MoveItem, self.RootPath)
				except:
					pass

	def OutSideCopyFile(self):
		CopiedItems[0] = [self.filePath(countItem) for countItem in self.selectedIndexes()]
		CopiedItemCount[0] = len(self.selectedIndexes())

	def OutSideCopiedFiles(self):
		if not NowRootDirectoryPath[0] == '':
			self.RootPath = NowRootDirectoryPath[0]
		else:
			self.RootPath = os.path.expanduser('~')
		if CopiedItemCount[0] == len(CopiedItems[0]):
			for CopiedItem in CopiedItems[0]:
				newPath = '{}{}{}'.format(self.RootPath, os.sep, CopiedItem.split(os.sep)[-1])
				if not QFile.exists(newPath):
					QFile.copy(CopiedItem, newPath)
				else:
					for cc in range(9999):
						if not QFile.exists('{} ({}).{}'.format(newPath.split('.')[0], cc+1, newPath.split('.')[-1])):
							QFile.copy(CopiedItem, '{} ({}).{}'.format(newPath.split('.')[0], cc+1, newPath.split('.')[-1]))
							break
						else:
							pass

	def OutSideArchiveCreate(self):
		BackupNowPath[0] = os.getcwd()
		Result = ArchiveDialog.OutPutResult()
		FileName = Result[0]
		mode = Result[1]
		CheckOK = Result[2]
		if not CheckOK == '':
			if mode == 'ZipArchive':
				os.chdir(self.rootPath())
				with zipfile.ZipFile(FileName, 'w') as ZF:
					for ArchiveDFile in self.selectedIndexes():
						if os.path.isfile(self.filePath(ArchiveDFile)):
							ZF.write(self.filePath(ArchiveDFile).split(os.sep)[-1])
						elif os.path.isdir(self.filePath(ArchiveDFile)):
							for TargetFolder, __, TargetFile in os.walk(self.filePath(ArchiveDFile)):
								for TFile in TargetFile:
									if not TFile.startswith('.'):
										FilePaths = os.path.join(TargetFolder, TFile).replace(os.getcwd(), os.curdir)
										ZF.write(FilePaths)
				os.chdir(BackupNowPath[0])
			if mode == 'TarArchive':
				os.chdir(self.rootPath())
				with tarfile.open(FileName, 'w:gz') as Tgz:
					for TarAddFiles in self.selectedIndexes():
						Tgz.add(self.filePath(TarAddFiles).replace(os.getcwd(), os.curdir))
				os.chdir(BackupNowPath[0])
			if mode == '7ZipArchive':
				os.chdir(self.rootPath())
				with py7zr.SevenZipFile(FileName, 'w') as SevenZipper:
					for SevenFilesIndex in self.selectedIndexes():
						SevenZipper.writeall(self.filePath(SevenFilesIndex).replace(os.getcwd(), os.curdir))
				os.chdir(BackupNowPath[0])

	def OutSideUnArchive(self):
		BackupNowPath[0] = os.getcwd()
		os.chdir(self.rootPath())
		for DetectFile in self.selectedIndexes():
			if self.filePath(DetectFile).endswith('.zip'):
				os.makedirs(self.filePath(DetectFile).replace(os.getcwd(), os.curdir).split('.zip')[0], exist_ok=True)
				with zipfile.ZipFile(self.filePath(DetectFile), 'r') as ExtractZip:
					ExtractZip.extractall(path='{}{}{}'.format(os.getcwd(), os.sep, self.filePath(DetectFile).split(os.getcwd())[-1].split('.zip')[0]))
			if self.filePath(DetectFile).endswith('.tar.gz'):
				os.makedirs(self.filePath(DetectFile).replace(os.getcwd(), os.curdir).split('.tar.gz')[0], exist_ok=True)
				with tarfile.open(self.filePath(DetectFile), 'r') as ExtractTgz:
					ExtractTgz.extractall(path='{}{}{}'.format(os.getcwd(), os.sep, self.filePath(DetectFile).split(os.getcwd())[-1].split('.tar.gz')[0]))
			if self.filePath(DetectFile).endswith('.7z'):
				os.makedirs(self.filePath(DetectFile).replace(os.getcwd(), os.curdir).split('.7z')[0], exist_ok=True)
				with py7zr.SevenZipFile(self.filePath(DetectFile), 'r') as ExtractSevenZip:
					ExtractSevenZip.extractall(path='{}{}{}'.format(os.getcwd(), os.sep, self.filePath(DetectFile).split(os.getcwd())[-1].split('.7z')[0]))
		os.chdir(BackupNowPath[0])

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()
			for ff in event.mimeData().urls():
				newpath = '{}{}{}'.format(self.rootPath(), os.sep, str(ff.toLocalFile()).split(os.sep)[-1])
				try:
					if os.path.isfile(str(ff.toLocalFile())):
							shutil.move(str(ff.toLocalFile()), newpath)
					else:
						shutil.move(str(ff.toLocalFile()), newpath)
				except:
					pass
		else:
			event.ignore()

	def dragMoveEvent(self, event):
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.accept()
		else:
			event.ignore()

	def dropEvent(self, event):
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.setAccepted(True)
			event.accept()
			for c in event.mimeData().urls():
				newpath = '{}{}{}'.format(self.rootPath(), os.sep, str(c.toLocalFile()).split(os.sep)[-1])
				try:
					if os.path.isfile(str(c.toLocalFile())):
							shutil.move(str(c.toLocalFile()), newpath)
					else:
						shutil.move(str(c.toLocalFile()), newpath)
				except:
					pass
		else:
			event.ignore()

class ArchiveDialog(QDialog):
	def __init__(self):
		super(ArchiveDialog, self).__init__()
		self.setWindowTitle('圧縮ファイルの作成')
		self.setFixedSize(300, 200)
		self.ArchiveLabel1 = QLabel('圧縮ファイル名: ', self)
		self.ArchiveInput = QLineEdit()
		self.ArchiveInput.setText('Archive.zip')
		self.ArchiveInput.setClearButtonEnabled(True)
		self.ArchiveType1 = QCheckBox()
		self.ArchiveType1.setChecked(True)
		self.ArchiveType1.setText('.zip')
		self.ArchiveType2 = QCheckBox()
		self.ArchiveType2.setChecked(False)
		self.ArchiveType2.setText('.tar.gz')
		self.ArchiveType3 = QCheckBox()
		self.ArchiveType3.setChecked(False)
		self.ArchiveType3.setText('.7z')
		self.selectorButton = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
		self.selectorButton.accepted.connect(self.accept)
		self.selectorButton.rejected.connect(self.reject)
		self.Popup = QVBoxLayout()
		self.Popup.addWidget(self.ArchiveLabel1)
		self.Popup.addWidget(self.ArchiveInput)
		self.Popup.addWidget(self.ArchiveType1)
		self.Popup.addWidget(self.ArchiveType2)
		self.Popup.addWidget(self.ArchiveType3)
		self.Popup.addWidget(self.selectorButton)
		self.setLayout(self.Popup)
		self.ArchiveType1.stateChanged.connect(self.CheckModes)
		self.ArchiveType2.stateChanged.connect(self.CheckModes)
		self.ArchiveType3.stateChanged.connect(self.CheckModes)

	def CheckModes(self):
		try:
			if self.ArchiveType1.checkState() == Qt.Unchecked and OneChecked[0] == '1':
				self.ArchiveType1.setCheckState(Qt.Checked)
			if self.ArchiveType2.checkState() == Qt.Unchecked and OneChecked2[0] == '1':
				self.ArchiveType2.setCheckState(Qt.Checked)
			if self.ArchiveType3.checkState() == Qt.Unchecked and OneChecked3[0] == '1':
				self.ArchiveType3.setCheckState(Qt.Checked)
			if self.ArchiveType1.checkState() == Qt.Checked and OneChecked2[0] == '1':
				self.ArchiveType2.setCheckState(Qt.Unchecked)
				OneChecked2[0] = '0'
				OneChecked[0] = '1'
			if self.ArchiveType1.checkState() == Qt.Checked and OneChecked3[0] == '1':
				self.ArchiveType3.setCheckState(Qt.Unchecked)
				OneChecked3[0] = '0'
				OneChecked[0] = '1'
			if self.ArchiveType2.checkState() == Qt.Checked and OneChecked[0] == '1':
				self.ArchiveType1.setCheckState(Qt.Unchecked)
				OneChecked[0] = '0'
				OneChecked2[0] = '1'
			if self.ArchiveType3.checkState() == Qt.Checked and OneChecked[0] == '1':
				self.ArchiveType1.setCheckState(Qt.Unchecked)
				OneChecked[0] = '0'
				OneChecked3[0] = '1'
			if self.ArchiveType1.checkState() == Qt.Checked and OneChecked2[0] == '1':
				self.ArchiveType2.setCheckState(Qt.Unchecked)
				OneChecked2[0] = '0'
				OneChecked[0] = '1'
			if self.ArchiveType3.checkState() == Qt.Checked and OneChecked2[0] == '1':
				self.ArchiveType2.setCheckState(Qt.Unchecked)
				OneChecked2[0] = '0'
				OneChecked3[0] = '1'
			if self.ArchiveType1.checkState() == Qt.Checked and OneChecked3[0] == '1':
				self.ArchiveType3.setCheckState(Qt.Unchecked)
				OneChecked3[0] = '0'
				OneChecked[0] = '1'
			if self.ArchiveType2.checkState() == Qt.Checked and OneChecked3[0] == '1':
				self.ArchiveType3.setCheckState(Qt.Unchecked)
				OneChecked3[0] = '0'
				OneChecked[0] = '1'
			if self.ArchiveType3.checkState() == Qt.Checked:
				if not self.ArchiveInput.text() == '':
					self.ArchiveInput.setText(self.ArchiveInput.text().replace(self.ArchiveInput.text().split('.')[-1], '7z').replace('.tar', ''))
				else:
					self.ArchiveInput.setText('Archive.7z')
				OneChecked3[0] = '1'
			if self.ArchiveType2.checkState() == Qt.Checked:
				if not self.ArchiveInput.text() == '':
					if self.ArchiveInput.text().split('.')[-1] == 'zip' or self.ArchiveInput.text().split('.')[-1] == '7z':
						self.ArchiveInput.setText(self.ArchiveInput.text().replace(self.ArchiveInput.text().split('.')[-1], 'tar.gz').replace('.tar.tar', ''))
				else:
					self.ArchiveInput.setText('Archive.tar.gz')
				OneChecked2[0] = '1'
			if self.ArchiveType1.checkState() == Qt.Checked:
				if not self.ArchiveInput.text() == '':
					self.ArchiveInput.setText(self.ArchiveInput.text().replace(self.ArchiveInput.text().split('.')[-1], 'zip').replace('.tar', ''))
				else:
					self.ArchiveInput.setText('Archive.zip')
				OneChecked[0] = '1'
		except:
			pass

	def InputResult(self):
		return self.ArchiveInput.text()

	def ModeCheck(self):
		if self.ArchiveType1.checkState() == Qt.Checked:
			return 'ZipArchive'
		elif self.ArchiveType2.checkState() == Qt.Checked:
			return 'TarArchive'
		elif self.ArchiveType3.checkState() == Qt.Checked:
			return '7ZipArchive'

	@staticmethod
	def OutPutResult():
		Ac = ArchiveDialog()
		Ac.exec()
		inputFileName = Ac.InputResult()
		mode = Ac.ModeCheck()
		if Ac.result() == QDialog.Accepted:
			return inputFileName, mode, '0'
		elif Ac.result() == QDialog.Rejected:
			return '', '', ''

class SearchWindow(QWidget):
	def __init__(self, parent=None, model=None):
		super(SearchWindow, self).__init__(parent)
		self.w = QDialog(parent)
		self.w.resize(QSize(1000, 700))
		self.w.setFixedSize(QSize(1000, 700))
		self.w.setWindowTitle('検索結果')
		self.ListView = QListView()
		self.ListView.setGeometry(QRect(-1, -1, 800, 638))
		self.ListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.ListView.setContextMenuPolicy(Qt.CustomContextMenu)
		self.ListView.customContextMenuRequested.connect(self.CopyOnlyMenu)
		self.Model = model
		self.ListView.setModel(self.Model)
		self.ListView.doubleClicked.connect(self.mouseDoubleClicked)
		self.LayOut = QVBoxLayout()
		self.LayOut.addWidget(self.ListView)
		self.w.setLayout(self.LayOut)

	def CopyOnlyMenu(self, Point):
		self.CopyMenu = QMenu()
		self.CopyMenu.addAction('場所のコピー', self.CopyPath)
		self.CopyMenu.exec(self.ListView.mapToGlobal(Point))

	def CopyPath(self):
		QApplication.clipboard().setText(self.ListView.selectedIndexes()[0].data())

	def mouseDoubleClicked(self):
		QDesktopServices.openUrl('file:///{}'.format(self.ListView.selectedIndexes()[0].data()))

	def show(self):
		self.w.exec()

class MainWindowwView(QMainWindow):
	fileDropped = Signal(list)
	def __init__(self, parent=None):
		super(MainWindowwView, self).__init__(parent)
		self.setAcceptDrops(True)

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()
			for ff in event.mimeData().urls():
				newpath = '{}{}{}'.format(PathListory[0], os.sep, str(ff.toLocalFile()).split(os.sep)[-1])
				try:
					if os.path.isfile(str(ff.toLocalFile())):
							shutil.move(str(ff.toLocalFile()), newpath)
					else:
						shutil.move(str(ff.toLocalFile()), newpath)
				except:
					pass
		else:
			event.ignore()

	def dragMoveEvent(self, event):
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.accept()
		else:
			event.ignore()

	def dropEvent(self, event):
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.setAccepted(True)
			event.accept()
			for c in event.mimeData().urls():
				newpath = '{}{}{}'.format(PathListory[0], os.sep, str(c.toLocalFile()).split(os.sep)[-1])
				try:
					if os.path.isfile(str(c.toLocalFile())):
							shutil.move(str(c.toLocalFile()), newpath)
					else:
						shutil.move(str(c.toLocalFile()), newpath)
				except:
					pass
		else:
			event.ignore()

class DeletingOKDialog(QDialog):
	def __init__(self):
		super(DeletingOKDialog, self).__init__()
		self.setWindowTitle('削除の確認')
		self.setFixedSize(160, 100)
		self.Label1 = QLabel('本当に削除しますか？', self)
		self.selectorButton = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
		self.selectorButton.accepted.connect(self.accept)
		self.selectorButton.rejected.connect(self.reject)
		self.Popup = QVBoxLayout()
		self.Popup.addWidget(self.Label1)
		self.Popup.addWidget(self.selectorButton)
		self.setLayout(self.Popup)

	@staticmethod
	def OutPutResult():
		d = DeletingOKDialog()
		d.exec()
		if d.result() == QDialog.Accepted:
			return '0'
		elif d.result() == QDialog.Rejected:
			return '1'

class ForceDeletingOKDialog(QDialog):
	def __init__(self):
		super(ForceDeletingOKDialog, self).__init__()
		self.setWindowTitle('削除の確認')
		self.setFixedSize(210, 100)
		self.Label1 = QLabel('本当に完全削除しますか？', self)
		self.selectorButton = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
		self.selectorButton.accepted.connect(self.accept)
		self.selectorButton.rejected.connect(self.reject)
		self.Popup = QVBoxLayout()
		self.Popup.addWidget(self.Label1)
		self.Popup.addWidget(self.selectorButton)
		self.setLayout(self.Popup)

	@staticmethod
	def OutPutResult():
		d = ForceDeletingOKDialog()
		d.exec()
		if d.result() == QDialog.Accepted:
			return '0'
		elif d.result() == QDialog.Rejected:
			return '1'

class NewFileCreateDialog(QDialog):
	def __init__(self):
		super(NewFileCreateDialog, self).__init__()
		self.setWindowTitle('新しいファイルの作成')
		self.setFixedSize(240, 100)
		self.Label1 = QLabel('新しいファイルの名前を入れてください', self)
		self.CreateInput1 = QLineEdit()
		self.CreateInput1.setClearButtonEnabled(True)
		self.CreateInput1.setPlaceholderText('ここに新しいファイルの名前を入れてください')
		self.selectorButton1 = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
		self.selectorButton1.accepted.connect(self.accept)
		self.selectorButton1.rejected.connect(self.reject)
		self.Popup = QVBoxLayout()
		self.Popup.addWidget(self.Label1)
		self.Popup.addWidget(self.CreateInput1)
		self.Popup.addWidget(self.selectorButton1)
		self.setLayout(self.Popup)

	def InputResult(self):
		return self.CreateInput1.text()

	@staticmethod
	def OutputResults():
		r = NewFileCreateDialog()
		r.exec()
		input_result = r.InputResult()
		if r.result() == QDialog.Accepted and r.result() != QDialog.Rejected:
			return input_result, '0'
		else:
			return '', '1'

class NewCreateFolderDialog(QDialog):
	def __init__(self):
		super(NewCreateFolderDialog, self).__init__()
		self.setWindowTitle('新しいフォルダの作成')
		self.setFixedSize(240, 100)
		self.Label = QLabel('新しい名前を入れてください', self)
		self.CreateInput = QLineEdit()
		self.CreateInput.setText('新規フォルダ')
		self.CreateInput.setClearButtonEnabled(True)
		self.CreateInput.setPlaceholderText('ここに新しい名前を入れてください')
		self.selectorButton = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
		self.selectorButton.accepted.connect(self.accept)
		self.selectorButton.rejected.connect(self.reject)
		self.Popup = QVBoxLayout()
		self.Popup.addWidget(self.Label)
		self.Popup.addWidget(self.CreateInput)
		self.Popup.addWidget(self.selectorButton)
		self.setLayout(self.Popup)

	def InputResult(self):
		return self.CreateInput.text()

	@staticmethod
	def OutputResult():
		r = NewCreateFolderDialog()
		r.exec()
		input_result = r.InputResult()
		if r.result() == QDialog.Accepted and r.result() != QDialog.Rejected:
			return input_result, '0'
		else:
			return '', '1'

class InputDiaLog(QDialog):
	def __init__(self):
		super(InputDiaLog, self).__init__()
		self.setWindowTitle('名前の変更')
		self.setFixedSize(240, 100)
		self.Label = QLabel('新しい名前を入れてください', self)
		self.renameInput = QLineEdit()
		self.renameInput.setText(SelectedItemPath[0])
		self.renameInput.setClearButtonEnabled(True)
		self.renameInput.setPlaceholderText('ここに新しい名前を入れてください')
		self.selectorButton = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
		self.selectorButton.accepted.connect(self.accept)
		self.selectorButton.rejected.connect(self.reject)
		self.Popup = QVBoxLayout()
		self.Popup.addWidget(self.Label)
		self.Popup.addWidget(self.renameInput)
		self.Popup.addWidget(self.selectorButton)
		self.setLayout(self.Popup)

	def InputResult(self):
		return self.renameInput.text()

	@staticmethod
	def OutputResult():
		r = InputDiaLog()
		r.exec()
		input_result = r.InputResult()
		if r.result() == QDialog.Accepted and r.result() != QDialog.Rejected:
			return input_result, '0'
		else:
			return '', '1'

class Ui_FullTools2(object):
	def setupUi(self, FullTools2):
		if not FullTools2.objectName():
			FullTools2.setObjectName("FullTools2")
		fonter = QFont()
		fonter.setFamilies(["Arial"])
		FullTools2.setFont(fonter)
		FullTools2.resize(1145, 638)
		FullTools2.setStyleSheet("QWidget#FullTools2{\n"
								"background-color: #292828;\n"
								"color: White;\n"
								"}\n")

		self.FullTools2 = FullTools2
		self.Tab3 = QTabWidget(FullTools2)
		self.Tab3.setObjectName("Tab3")
		self.Tab3.setGeometry(QRect(0, 10, 1141, 631))
		font = QFont()
		font.setFamilies(["Arial"])
		self.Tab3.setFont(font)
		self.Tab3.setStyleSheet("QWidget#Tab3{\n"
								"background-color: #2d2d2d;\n"
								"color: #2d2d2d;\n"
								"}\n"
								"QWidget#tab{\n"
								"background-color: #2d2d2d;\n"
								"color: #2d2d2d;\n"
								"}\n"
								"QWidget#tab_2{\n"
								"background-color: #2d2d2d;\n"
								"color: #2d2d2d;\n"
								"}\n"
								"QWidget#tab_3{\n"
								"background-color: #2d2d2d;\n"
								"color: #2d2d2d;\n"
								"}\n"
								"QWidget#tab_4{\n"
								"background-color: #2d2d2d;\n"
								"color: #2d2d2d;\n"
								"}\n"
								"QTabBar::tab{\n"
								"background-color: #2d2d2d;\n"
								"color: White;\n"
								"border: 2px solid #1a1a1a;\n"
								"border-color: #1a1a1a;\n"
								"}\n"
								"QTabBar::tab_2{\n"
								"background-color: #2d2d2d;\n"
								"color: White;\n"
								"border: 2px solid #1a1a1a;\n"
								"border-color: #1a1a1a;\n"
								"}\n"
								"QTabBar::tab_3{\n"
								"background-color: #2d2d2d;\n"
								"color: White;\n"
								"border: 2px solid #1a1a1a;\n"
								"border-color: #1a1a1a;\n"
								"}\n"
								"QTabBar::tab_4{\n"
								"background-color: #2d2d2d;\n"
								"color: White;\n"
								"border: 2px solid #1a1a1a;\n"
								"border-color: #1a1a1a;\n"
								"}\n"
								"QTabBar::tab:!selected{\n"
								"background-color: #2d2d2d;\n"
								"color: #2d2d2d;\n"
								"border: 2px solid #1a1a1a;\n"
								"border-c"
								"olor: #1a1a1a;\n"
								"}\n"
								"QTabBar::tab_2:!selected{\n"
								"background-color: #2d2d2d;\n"
								"color: #2d2d2d;\n"
								"border: 2px solid #1a1a1a;\n"
								"border-color: #1a1a1a;\n"
								"}\n"
								"QTabBar::tab_3:!selected{\n"
								"background-color: #2d2d2d;\n"
								"color: #2d2d2d;\n"
								"border: 2px solid #1a1a1a;\n"
								"border-color: #1a1a1a;\n"
								"}\n"
								"QTabBar::tab_4:!selected{\n"
								"background-color: #2d2d2d;\n"
								"color: #2d2d2d;\n"
								"border: 2px solid #1a1a1a;\n"
								"border-color: #1a1a1a;\n"
								"}\n"
								"")
		self.tab = QWidget()
		self.tab.setObjectName("tab")
		self.FileFinput = QLineEdit(self.tab)
		self.FileFinput.setObjectName("FileFinput")
		self.FileFinput.setGeometry(QRect(92, 20, 269, 31))
		self.FileFinput.setPlaceholderText('ここにファイル名を入力してください')
		self.FileFinput.setStyleSheet("QLineEdit#FileFinput{\n"
"    color: White;\n"
"    background-color: #131519;\n"
"}")
		self.FileOption = QCheckBox(self.tab)
		self.FileOption.setObjectName("FileOption")
		self.FileOption.setGeometry(QRect(582, 20, 199, 31))
		self.FileOption.setStyleSheet("QCheckBox#FileOption{\n"
"	color: White;\n"
"}\n"
"")
		self.FileTypeOption = QCheckBox(self.tab)
		self.FileTypeOption.setObjectName("FileTypeOption")
		self.FileTypeOption.setGeometry(QRect(362, 20, 219, 31))
		self.FileTypeOption.setStyleSheet("QCheckBox#FileTypeOption{\n"
"	color: White;\n"
"}\n"
"")
		self.FileName = QLabel(self.tab)
		self.FileName.setObjectName("FileName")
		self.FileName.setGeometry(QRect(12, 26, 79, 21))
		self.FileName.setStyleSheet("QLabel#FileName{\n"
"	color: White;\n"
"}\n"
"")
		self.FileFinput_2 = QLineEdit(self.tab)
		self.FileFinput_2.setObjectName("FileFinput_2")
		self.FileFinput_2.setGeometry(QRect(92, 70, 269, 31))
		self.FileFinput_2.setPlaceholderText('ここに場所を入力します(例: /)')
		self.FileFinput_2.setStyleSheet("QLineEdit#FileFinput_2{\n"
"    color: White;\n"
"    background-color: #131519;\n"
"}")
		self.FileSystemModel = QFileSystemModel()
		self.FileSystemModel.setRootPath(os.path.expanduser("~"))
		self.FileSystemModel.setNameFilters(['*.app'])
		self.FileSystemModel.setNameFilterDisables(False)
		self.FileSearchInput = QLineEdit(self.tab)
		self.FileSearchInput.textChanged.connect(self.on_TextSearch)
		self.FileSearchInput.setObjectName("FileSearchInput")
		self.FileSearchInput.setGeometry(QRect(0, 130, 331, 35))
		self.FileSearchInput.setPlaceholderText('ここにフォルダ名を入力して検索できます')
		self.FileSearchInput.setStyleSheet("QLineEdit#FileSearchInput {\n"
"background-color: #2d2d2d;\n"
"color: #ededed;\n"
"}")
		self.FolderTree = QTreeView(self.tab)
		self.FolderTree.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.FolderTree.header().setVisible(False)
		self.FolderTree.setObjectName("FolderTree")
		self.FolderTree.setGeometry(QRect(0, 160, 359, 441))
		self.FolderTree.setModel(self.FileSystemModel)
		try:
			self.FolderTree.setRootIndex(self.FileSystemModel.index(os.path.splitdrive(os.environ['windir'])[0] + os.sep))
		except:
			self.FolderTree.setRootIndex(self.FileSystemModel.index('/'))
		self.FolderTree.setStyleSheet("QTreeView#FolderTree {\n"
"    color: White;\n"
"    background-color: #131519;\n"
"}\n"
"")
		self.FolderTree.setColumnWidth(0 ,300)
		self.FolderTree.setColumnHidden(1, True)
		self.FolderTree.setColumnHidden(2, True)
		self.FolderTree.setColumnHidden(3, True)
		self.FolderTree.clicked.connect(self.SelectedItem)
		self.FolderName = QLabel(self.tab)
		self.FolderName.setObjectName("FolderName")
		self.FolderName.setGeometry(QRect(12, 74, 79, 21))
		self.FolderName.setStyleSheet("QLabel#FolderName{\n"
"	color: White;\n"
"}\n"
"")
		self.label_2 = QLabel(self.tab)
		self.label_2.setObjectName("label_2")
		self.label_2.setGeometry(QRect(1, 110, 341, 21))
		self.label_2.setStyleSheet("QLabel#label_2{\n"
"	color: White;\n"
"}\n"
"")
		self.DebugArea = QPlainTextEdit(self.tab)
		self.DebugArea.setObjectName("DebugArea")
		self.DebugArea.setGeometry(QRect(322, 440, 809, 161))
		self.DebugArea.setReadOnly(True)
		self.DebugArea.setStyleSheet("QPlainTextEdit#DebugArea{\n"
"    color: White;\n"
"    background-color: #131519;\n"
"}")
		self.ResultTree = QTreeView(self.tab)
		self.ResultTree.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.ResultTree.setObjectName("ResultTree")
		self.ResultTree.setGeometry(QRect(322, 130, 809, 312))
		self.ResultTree.setAutoScroll(False)
		self.ResultTree.setColumnWidth(0 ,400)
		self.ResultTree.setHeaderHidden(1)
		self.ResultTree.setStyleSheet("QTreeView#ResultTree {\n"
"    color: #e4e4e4;\n"
"    background-color: #131519;\n"
"    outline: 0;\n"
"    font-size: 14px;\n"
"    font-weight: 500;\n"
"    text-transform: capitarise;\n"
"    show-decoration-selected: 1;\n"
"    qproperty-indentation: 24;\n"
"}\n"
"")
		self.SearchButton = QPushButton(self.tab)
		self.SearchButton.setObjectName("SearchButton")
		self.SearchButton.setGeometry(QRect(372, 67, 239, 41))
		self.SearchButton.setStyleSheet("QPushButton#SearchButton{\n"
"	background-color: #2d2d2d;\n"
"	color: White;\n"
"}\n"
"")
		self.SearchButton.pressed.connect(self.SearchingFile)
		self.ResultDelButton = QPushButton(self.tab)
		self.ResultDelButton.setObjectName("ResultDelButton")
		self.ResultDelButton.setGeometry(QRect(922, 67, 209, 41))
		self.ResultDelButton.pressed.connect(self.ClearDebug)
		self.ResultDelButton.setStyleSheet("QPushButton#ResultDelButton{\n"
"	background-color: #2d2d2d;\n"
"	color: #FF0000;\n"
"}")
		self.Tab3.addTab(self.tab, "")
		self.tab_2 = QWidget()
		self.tab_2.setObjectName("tab_2")
		self.resultMOdel = QStandardItemModel()
		self.ResultView2Model = QStandardItemModel()
		self.ResultView2 = QTreeView(self.tab_2)
		self.ResultView2.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.ResultView2.setObjectName("ResultView2")
		self.ResultView2.setHeaderHidden(1)
		self.ResultView2.setGeometry(QRect(433, 131, 703, 321))
		self.ResultView2.setStyleSheet("QTreeView#ResultView2{\n"
"    color: White;\n"
"    background-color: #131519;\n"
"}")
		self.FolderPath = QLineEdit(self.tab_2)
		self.FolderPath.setObjectName("FolderPath")
		self.FolderPath.setGeometry(QRect(112, 60, 279, 31))
		self.FolderPath.setStyleSheet("QLineEdit#FolderPath{\n"
"    color: White;\n"
"    background-color: #131519;\n"
"}")
		self.FolderPath.setPlaceholderText('ここに検索したい場所を入力してください')
		self.FolderPathLabel = QLabel(self.tab_2)
		self.FolderPathLabel.setObjectName("FolderPathLabel")
		self.FolderPathLabel.setGeometry(QRect(9, 67, 109, 20))
		self.FolderPathLabel.setStyleSheet("QLabel#FolderPathLabel{\n"
"	color: White;\n"
"}")
		font = QFont()
		font.setPointSize(13)
		self.FolderPathLabel.setFont(font)
		self.BigFileSearchButton = QPushButton(self.tab_2)
		self.BigFileSearchButton.setObjectName("BigFileSearchButton")
		self.BigFileSearchButton.setGeometry(QRect(392, 54, 239, 41))
		self.BigFileSearchButton.pressed.connect(self.BigFileSearching)
		self.BigFileSearchButton.setStyleSheet("QPushButton#BigFileSearchButton{\n"
"	color: White;\n"
"	background-color: #2d2d2d;\n"
"}\n"
"")
		self.FileSystemModel2 = QFileSystemModel()
		self.FileSystemModel2.setRootPath(os.path.expanduser("~"))
		self.FileSystemModel2.setNameFilters(['*.app'])
		self.FileSystemModel2.setNameFilterDisables(False)
		self.InputView2 = QTreeView(self.tab_2)
		self.InputView2.setObjectName("InputView2")
		self.InputView2.setGeometry(QRect(1, 170, 440, 431))
		self.InputView2.setModel(self.FileSystemModel2)
		self.InputView2.clicked.connect(self.SelectedItem2)
		try:
			self.InputView2.setRootIndex(self.FileSystemModel2.index(os.path.splitdrive(os.environ['windir'])[0] + os.sep))
		except:
			self.InputView2.setRootIndex(self.FileSystemModel2.index('/'))
		self.InputView2.setStyleSheet("QTreeView#InputView2{\n"
"    color: White;\n"
"    background-color: #131519;\n"
"}")
		self.InputView2.header().setVisible(False)
		self.InputView2.setColumnWidth(0, 300)
		self.InputView2.setColumnHidden(1, True)
		self.InputView2.setColumnHidden(2, True)
		self.InputView2.setColumnHidden(3, True)
		self.InputView2.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.DebugLog2 = QPlainTextEdit(self.tab_2)
		self.DebugLog2.setObjectName("DebugLog2")
		self.DebugLog2.setGeometry(QRect(433, 451, 703, 151))
		self.DebugLog2.setReadOnly(True)
		self.DebugLog2.setStyleSheet("QPlainTextEdit#DebugLog2{\n"
"    color: White;\n"
"    background-color: #131519;\n"
"}")
		self.ResultDelButton2 = QPushButton(self.tab_2)
		self.ResultDelButton2.setObjectName("ResultDelButton2")
		self.ResultDelButton2.setGeometry(QRect(922, 70, 209, 41))
		self.ResultDelButton2.setStyleSheet("QPushButton#ResultDelButton2{\n"
"	color: #FF0000;\n"
"	background-color: #2d2d2d;\n"
"}")
		self.ResultDelButton2.pressed.connect(self.ClearDebug2)
		self.Tab3.addTab(self.tab_2, "")
		self.tab_3 = QWidget()
		self.tab_3.setObjectName("tab_3")
		self.SearchInputer = QLineEdit(self.tab_2)
		self.SearchInputer.setObjectName("SearchInputer")
		self.SearchInputer.textChanged.connect(self.on_TextSearch2)
		self.SearchInputer.setGeometry(QRect(1, 130, 442, 42))
		self.SearchInputer.setStyleSheet("QLineEdit#SearchInputer {\n"
										 "background-color: #2d2d2d;\n"
										 "color: #ededed;\n"
										 "}")
		self.SearchInputer.setPlaceholderText('ここに検索したいフォルダを入力してください')
		self.FolderSearchLabel2 = QLabel(self.tab_2)
		self.FolderSearchLabel2.setObjectName("FolderSearchLabel2")
		self.FolderSearchLabel2.setGeometry(QRect(12, 110, 439, 21))
		self.FolderSearchLabel2.setStyleSheet("QLabel#FolderSearchLabel2{\n"
"color: White;\n"
"}")
		self.ResultViewModel3 = QStandardItemModel()
		self.ResultView3 = QTreeView(self.tab_3)
		self.ResultView3.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.ResultView3.setObjectName("ResultView3")
		self.ResultView3.setGeometry(QRect(0, 120, 1141, 481))
		self.ResultView3.setHeaderHidden(1)
		self.ResultView3.setContextMenuPolicy(Qt.CustomContextMenu)
		self.ResultView3.customContextMenuRequested.connect(self.ContextMenu)
		self.ResultView3.setStyleSheet("QTreeView#ResultView3{\n"
									   "    color: White;\n"
									   "    background-color: #131519;\n"
									   "}")
		self.RefreshButton = QPushButton(self.tab_3)
		self.RefreshButton.setObjectName("RefreshButton")
		self.RefreshButton.setGeometry(QRect(502, 20, 158, 51))
		self.RefreshButton.setStyleSheet("QPushButton#RefreshButton{\n"
"	color: White;\n"
"	background-color: #2d2d2d;\n"
"}\n"
"")
		self.RefreshButton.pressed.connect(self.ProcessList)
		self.ProcessSearch = QLineEdit(self.tab_3)
		self.ProcessSearch.setObjectName("ProcessSearch")
		self.ProcessSearch.setGeometry(QRect(0, 100, 1146, 41))
		self.ProcessSearch.setStyleSheet("QLineEdit#ProcessSearch {\n"
										 "background-color: #2d2d2d;\n"
										 "color: #ededed;\n"
										 "}")
		self.ProcessSearch.setPlaceholderText('ここにプロセス名を入れてください(例: firefox)')
		self.ProcessSearch.textChanged.connect(self.on_TextSearch3)
		self.Tab3.addTab(self.tab_2, "")
		self.Tab3.addTab(self.tab_3, "")
		self.Tab3.addTab(self.tab_3, "")
		self.tab_4 = QWidget()
		self.tab_4.setObjectName("tab_4")
		self.RootFolderFileSystemModel = QFileSystemModel()
		self.RootFolderFileSystemModel.setReadOnly(False)
		self.RootFolderFileSystemModel.setRootPath(os.path.expanduser("~"))
		self.RootFolderTree = QTreeView(self.tab_4)
		self.RootFolderTree.setDragEnabled(True)
		self.RootFolderTree.setDragDropOverwriteMode(True)
		self.RootFolderTree.setDragDropMode(QAbstractItemView.DragDrop)
		self.RootFolderTree.setDefaultDropAction(Qt.MoveAction)
		self.RootFolderTree.setObjectName("RootFolderTree")
		self.RootFolderTree.setGeometry(QRect(0, 80, 279, 541))
		self.RootFolderTree.setModel(self.RootFolderFileSystemModel)
		self.RootFolderTree.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.RootFolderTree.setStyleSheet("QTreeView#RootFolderTree{\n"
										  "    color: White;\n"
										  "    background-color: #131519;\n"
										  "}")
		try:
			self.RootFolderTree.setRootIndex(self.RootFolderFileSystemModel.index(os.path.splitdrive(os.environ['windir'])[0] + os.sep))
		except:
			self.RootFolderTree.setRootIndex(self.RootFolderFileSystemModel.index('/'))
		self.RootFolderTree.setHeaderHidden(True)
		self.RootFolderTree.setColumnWidth(0, 200)
		self.RootFolderTree.setColumnHidden(1, True)
		self.RootFolderTree.setColumnHidden(2, True)
		self.RootFolderTree.setColumnHidden(3, True)
		self.RootFolderTree.setIconSize(QSize(30, 30))
		self.RootFolderTree.doubleClicked.connect(self.SelectedFolder)
		self.RootFolderTree.clicked.connect(self.SingleClickRootFolder)
		self.RootFolderTree.setContextMenuPolicy(Qt.CustomContextMenu)
		self.RootFolderTree.customContextMenuRequested.connect(self.FilerContextMenu)
		self.SubFolderTree = FileSystemListView(self.tab_4)
		self.SubFolderTree.setObjectName("SubFolderTree")
		self.SubFolderTree.setDragEnabled(True)
		self.SubFolderTree.setDragDropOverwriteMode(True)
		self.SubFolderTree.setDragDropMode(QAbstractItemView.DragDrop)
		self.SubFolderTree.setDefaultDropAction(Qt.MoveAction)
		self.SubFolderTree.doubleClicked.connect(self.AccessFolder)
		self.SubFolderTree.clicked.connect(self.SinglePreviewSubFolder)
		self.SubFolderTree.setStyleSheet("QListView#SubFolderTree{\n"
										 "    color: White;\n"
										 "    background-color: #131519;\n"
										 "}")
		self.PathBar = QLineEdit(self.tab_4)
		self.PathBar.setObjectName("PathBar")
		self.PathBar.setGeometry(QRect(143, 38, 625, 41))
		self.PathBar.editingFinished.connect(self.EndEditSearchBar)
		self.PathBar.setStyleSheet("QLineEdit#PathBar {\n"
										   "background-color: #2d2d2d;\n"
										   "color: #ededed;\n"
										   "}")
		self.FileTreeSearch2 = QLineEdit(self.tab_4)
		self.FileTreeSearch2.setObjectName("FileTreeSearch2")
		self.FileTreeSearch2.editingFinished.connect(self.on_TextSearch5)
		self.FileTreeSearch2.setClearButtonEnabled(True)
		self.FileTreeSearch2.setGeometry(QRect(802, 38, 595, 41))
		self.FileTreeSearch2.setStyleSheet("QLineEdit#FileTreeSearch2 {\n"
										   "background-color: #2d2d2d;\n"
										   "color: #ededed;\n"
										   "}")
		self.FileTreeSearch2.setPlaceholderText('検索')
		self.UpDirectory = QPushButton(self.tab_4)
		self.UpDirectory.setObjectName("UpDirectory")
		self.UpDirectory.setGeometry(QRect(760, 38, 42, 42))
		self.UpDirectory.setStyleSheet("QPushButton#UpDirectory {\n"
"background-color: #2d2d2d;\n"
"color: #ededed;\n"
"}")
		font2 = QFont()
		font2.setPointSize(24)
		self.UpDirectory.setFont(font2)
		self.UpDirectory.pressed.connect(self.MoveUpDiercory)
		self.PreviewBackground = QPlainTextEdit(self.tab_4)
		self.PreviewBackground.setObjectName("PreviewBackground")
		self.PreviewBackground.setGeometry(QRect(802, 80, 358, 541))
		self.PreviewBackground.setFont(font)
		self.PreviewBackground.viewport().setProperty("cursor", QCursor(Qt.ArrowCursor))
		self.PreviewBackground.setStyleSheet("QPlainTextEdit#PreviewBackground{\n"
											 "    color: White;\n"
											 "    background-color: #131519;\n"
											 "}")
		self.PreviewBackground.setReadOnly(True)
		self.Preview = QLabel(self.tab_4)
		self.Preview.setObjectName("Preview")
		self.Preview.setGeometry(QRect(804, 170, 328, 320))
		self.Preview.setTextFormat(Qt.PlainText)
		self.Preview.setAlignment(Qt.AlignCenter)
		self.Preview.setStyleSheet("QPlainTextEdit#PreviewBackground{\n"
"    color: White;\n"
"    background-color: #131519;\n"
"}")
		self.SortChangeButton = QPushButton(self.tab_4)
		self.SortChangeButton.setObjectName("SortChangeButton")
		self.SortChangeButton.setGeometry(QRect(1032, 18, 109, 21))
		self.SortChangeButton.setStyleSheet("QPushButton#SortChangeButton {\n"
											"background-color: #2d2d2d;\n"
											"color: #ededed;\n"
											"}")
		self.HomeButton = QPushButton(self.tab_4)
		self.HomeButton.setObjectName("HomeButton")
		self.HomeButton.setGeometry(QRect(99, 38, 43, 43))
		self.HomeButton.setStyleSheet("QPushButton#HomeButton {\n"
									  "background-color: #2d2d2d;\n"
									  "color: #ededed;\n"
									  "}")
		self.HomeButton.setAutoDefault(False)
		self.HomeButton.pressed.connect(self.BackHome)
		self.BackButton = QPushButton(self.tab_4)
		self.BackButton.setObjectName("BackButton")
		self.BackButton.setGeometry(QRect(10, 38, 43, 43))
		font4 = QFont()
		font4.setPointSize(35)
		self.BackButton.setFont(font4)
		self.BackButton.setStyleSheet("QPushButton#BackButton {\n"
									  "background-color: #2d2d2d;\n"
									  "color: #ededed;\n"
									  "}")
		self.BackButton.pressed.connect(self.BackReturnDirectory)
		self.OnButton = QPushButton(self.tab_4)
		self.OnButton.setObjectName("OnButton")
		self.OnButton.setGeometry(QRect(58, 38, 43, 43))
		self.OnButton.setFont(font4)
		self.OnButton.setStyleSheet("QPushButton#OnButton {\n"
									"background-color: #2d2d2d;\n"
									"color: #ededed;\n"
									"}")
		self.OnButton.pressed.connect(self.OnMoveDirectory)
		self.SortChangeButton.setText('昇順(A-Z)')
		SortedNumbar[0] = '0'
		self.SortChangeButton.pressed.connect(self.ItemSorting)
		self.Tab3.addTab(self.tab_4, "")
		self.FileFolderSelector()
		self.ProcessList()
		self.retranslateUi(FullTools2)
		self.Tab3.setCurrentIndex(3)
		NowRootDirectoryPath[0] = self.SubFolderTree.rootPath()
		self.PathBar.setText(self.SubFolderTree.rootPath()+os.sep)
		PathHistorys.append(self.SubFolderTree.rootPath()+os.sep)

		QMetaObject.connectSlotsByName(FullTools2)

	def OnMoveDirectory(self):
		for path in reversed(PathHistorys):
			if not self.SubFolderTree.rootPath() == path and StopPath2[0] == '0':
				self.SubFolderTree.setRootPath(path)
				self.SubFolderTree.setRootIndex(self.SubFolderTree.index(path))
				self.PathBar.setText(path)
				StopPath2[0] = '1'
				break

		BackupRootPath.append(self.SubFolderTree.rootPath())

	def BackReturnDirectory(self):
		try:
			BackPath = self.SubFolderTree.rootPath().split([p for p in self.SubFolderTree.rootPath().split(os.sep)][-1])[0]
		except:
			BackPath = ''
		if BackPath == '':
			try:
				BackPath = os.path.splitdrive(os.environ['windir'.lower()])[0]
			except:
				try:
					BackPath = os.path.splitdrive(os.environ['windir'.upper()])[0]
				except:
					BackPath = os.sep
		if PathHistorys[0] == BackPath:
			StopPath[0] = '1'
			self.SubFolderTree.setRootPath(BackPath)
			self.SubFolderTree.setRootIndex(self.SubFolderTree.index(BackPath))
			self.PathBar.setText(BackPath)
			PathHistorys.append(self.SubFolderTree.rootPath())
			StopPath2[0] = '0'
		elif not PathHistorys[0] == BackPath and StopPath[0] == '0':
			if PathHistorys[0] == self.SubFolderTree.rootPath()+os.sep and StopPath[0] == '0':
				pass
			else:
				self.SubFolderTree.setRootPath(BackPath)
				self.SubFolderTree.setRootIndex(self.SubFolderTree.index(BackPath))
				self.PathBar.setText(BackPath)
				PathHistorys.append(self.SubFolderTree.rootPath())
				StopPath2[0] = '0'
		elif StopPath[0] == '1' and PathHistorys[0] == self.SubFolderTree.rootPath()+os.sep:
			BackPath = os.path.expanduser('~')+os.sep
			self.SubFolderTree.setRootPath(BackPath)
			self.SubFolderTree.setRootIndex(self.SubFolderTree.index(BackPath))
			self.PathBar.setText(BackPath)
			PathHistorys.append(self.SubFolderTree.rootPath())
			StopPath2[0] = '0'
		elif StopPath[0] == '0' and not str(pathlib.Path(os.path.expanduser('~')).parent) == self.SubFolderTree:
			BackPath = PathHistorys[-2]
			self.SubFolderTree.setRootPath(BackPath)
			self.SubFolderTree.setRootIndex(self.SubFolderTree.index(BackPath))
			self.PathBar.setText(BackPath)
			PathHistorys.append(self.SubFolderTree.rootPath())
			StopPath2[0] = '0'
		elif StopPath[0] == '2':
			BackPath = PathHistorys[-2]
			self.SubFolderTree.setRootPath(BackPath)
			self.SubFolderTree.setRootIndex(self.SubFolderTree.index(BackPath))
			self.PathBar.setText(BackPath)
			PathHistorys.append(self.SubFolderTree.rootPath())
			StopPath[0] = '0'
			StopPath2[0] = '0'
		BackupRootPath.append(self.SubFolderTree.rootPath())

	def BackHome(self):
		self.SubFolderTree.setRootPath(os.path.expanduser('~'))
		self.SubFolderTree.setRootIndex(self.SubFolderTree.index(os.path.expanduser('~')))
		self.PathBar.setText(self.SubFolderTree.rootPath()+os.sep)
		NowRootDirectoryPath[0] = self.SubFolderTree.rootPath()
		PathHistorys.append(self.SubFolderTree.rootPath()+os.sep)
		StopPath[0] = '0'
		StopPath2[0] = '0'
		BackupRootPath.append(self.SubFolderTree.rootPath())

	def MoveUpDiercory(self):
		try:
			DriveLatter = os.path.splitdrive(os.environ['windir'.lower()])[0]
		except:
			try:
				DriveLatter = os.path.splitdrive(os.environ['windir'.upper()])[0]
			except:
				DriveLatter = os.sep

		self.SubFolderTree.setRootPath(os.path.dirname(self.SubFolderTree.rootPath()))
		self.SubFolderTree.setRootIndex(self.SubFolderTree.index(self.SubFolderTree.rootPath()))
		if not self.SubFolderTree.rootPath() == DriveLatter:
			self.PathBar.setText(self.SubFolderTree.rootPath()+os.sep)
		else:
			self.PathBar.setText(self.SubFolderTree.rootPath())
		PathHistorys.append(self.SubFolderTree.rootPath()+os.sep)
		StopPath[0] = '0'
		StopPath2[0] = '0'
		BackupRootPath.append(self.SubFolderTree.rootPath())

	def AccessFolder(self):
		if not os.path.isfile(self.SubFolderTree.filePath(self.SubFolderTree.selectedIndexes()[0])):
			self.SubFolderTree.setRootPath(self.SubFolderTree.filePath(self.SubFolderTree.selectedIndexes()[0]))
			self.SubFolderTree.setRootIndex(self.SubFolderTree.index(self.SubFolderTree.filePath(self.SubFolderTree.selectedIndexes()[0])))
			self.PathBar.setText(self.SubFolderTree.rootPath()+os.sep)
			StopPath[0] = '0'
			StopPath2[0] = '0'
			PathHistorys.append(self.SubFolderTree.rootPath()+os.sep)
			NowRootDirectoryPath[0] = self.SubFolderTree.rootPath()
			BackupRootPath.append(self.SubFolderTree.rootPath())
		else:
			QDesktopServices.openUrl('file:///{}'.format(self.SubFolderTree.filePath(self.SubFolderTree.selectedIndexes()[0])))

	def EndEditSearchBar(self):
		if self.PathBar.text() == '../':
			self.SubFolderTree.setRootPath(os.path.dirname(self.SubFolderTree.rootPath()+os.sep))
			self.SubFolderTree.setRootIndex(self.SubFolderTree.index(self.SubFolderTree.rootPath()+os.sep))
			self.PathBar.setText(self.SubFolderTree.rootPath()+os.sep)
			PathHistorys.append(self.SubFolderTree.rootPath()+os.sep)
			StopPath[0] = '0'
			StopPath2[0] = '0'
			BackupRootPath.append(self.SubFolderTree.rootPath())
		elif self.PathBar.text() == '.':
			self.SubFolderTree.setRootPath(self.SubFolderTree.rootPath()+os.sep)
			self.SubFolderTree.setRootIndex(self.SubFolderTree.index(self.SubFolderTree.rootPath()+os.sep))
			self.PathBar.setText(self.SubFolderTree.rootPath()+os.sep)
			StopPath[0] = '0'
			StopPath2[0] = '0'
			PathHistorys.append(self.SubFolderTree.rootPath()+os.sep)
			BackupRootPath.append(self.SubFolderTree.rootPath())
		else:
			self.SubFolderTree.setRootPath(self.PathBar.text())
			self.SubFolderTree.setRootIndex(self.SubFolderTree.index(self.SubFolderTree.rootPath()+os.sep))
			self.PathBar.setText(self.SubFolderTree.rootPath()+os.sep)
			StopPath[0] = '0'
			StopPath2[0] = '0'
			PathHistorys.append(self.SubFolderTree.rootPath()+os.sep)
			BackupRootPath.append(self.SubFolderTree.rootPath())

	def SingleClickRootFolder(self):
		try:
			RootIndex = self.RootFolderTree.selectedIndexes()[0]
		except:
			RootIndex = self.RootFolderTree.selectedIndexes()
		if self.RootFolderTree.isExpanded(RootIndex):
			self.RootFolderTree.collapse(RootIndex)
		else:
			self.RootFolderTree.expand(RootIndex)

	def SinglePreviewSubFolder(self):
		SelectedItem[0] = self.SubFolderTree.selectedIndexes()
		PixelMap = QPixmap(self.SubFolderTree.filePath(self.SubFolderTree.selectedIndexes()[0]))
		if PixelMap.isNull():
			self.Preview.setText('プレビューできませんでした')
		else:
			self.Preview.setPixmap(PixelMap.scaled(self.Preview.width(), self.Preview.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

	def FilerContextMenu(self, Point):
		self.Menu1 = QMenu()
		try:
			if os.path.isfile(self.RootFolderFileSystemModel.filePath(self.RootFolderTree.selectedIndexes()[0])):
				self.Menu1.addAction('開く', self.OpenFile)
				self.Menu1.addAction('コピー', self.CopyFile)
				self.Menu1.addAction('削除', self.Deleting)
			else:
				self.Menu1.addAction('コピー', self.CopyFile)
				self.Menu1.addAction('フォルダの新規作成', self.CreateFolder)
				self.Menu1.addAction('フォルダを開く', self.OpenFile)
				self.Menu1.addAction('ここにコピー', self.CopyiedFiles)
			self.Menu1.exec(self.RootFolderTree.mapToGlobal(Point))
		except:
			pass

	def OpenFile(self):
		QDesktopServices.openUrl('file:///{}'.format(self.RootFolderFileSystemModel.filePath(self.RootFolderTree.selectedIndexes()[0])))

	def CopyFile(self):
		CopiedItems[0] = [self.RootFolderFileSystemModel.filePath(countItem) for countItem in self.RootFolderTree.selectedIndexes()]
		CopiedItemCount[0] = len(self.RootFolderTree.selectedIndexes())

	def CreateFolder(self):
		Result = NewCreateFolderDialog.OutputResult()
		if Result[1] == '0':
			if not Result[0] == '':
				if not Result[0] == ' ':
					try:
						os.mkdir('{}{}{}'.format(self.RootFolderFileSystemModel.filePath(self.RootFolderTree.selectedIndexes()[0]), os.sep, Result[0]))
					except:
						for c in range(9999):
							try:
								os.mkdir('{}{}{} ({})'.format(self.RootFolderFileSystemModel.filePath(self.RootFolderTree.selectedIndexes()[0]), os.sep, Result[0], c))
								break
							except:
								pass

	def CopyiedFiles(self):
		try:
			if not self.RootFolderFileSystemModel.filePath(self.RootFolderTree.selectedIndexes()[0]) == '':
				self.RootPath = self.RootFolderFileSystemModel.filePath(self.RootFolderTree.selectedIndexes()[0])
			else:
				self.RootPath = os.path.expanduser('~')
		except:
			self.RootPath = os.path.expanduser('~')
		if CopiedItemCount[0] == len(CopiedItems[0]):
			for CopiedItem in CopiedItems[0]:
				newPath = '{}{}{}'.format(self.RootPath, os.sep, CopiedItem.split(os.sep)[-1])
				if not QFile.exists(newPath):
					QFile.copy(CopiedItem, newPath)
				else:
					for cc in range(9999):
						if not QFile.exists('{} ({}).{}'.format(newPath.split('.')[0], cc+1, newPath.split('.')[-1])):
							QFile.copy(CopiedItem, '{} ({}).{}'.format(newPath.split('.')[0], cc+1, newPath.split('.')[-1]))
							break
						else:
							pass

	def Deleting(self):
		if os.path.isfile(self.RootFolderFileSystemModel.filePath(self.RootFolderTree.selectedIndexes()[0])):
			send2trash.send2trash(self.RootFolderFileSystemModel.filePath(self.RootFolderTree.selectedIndexes()[0]))
		else:
			send2trash.send2trash(self.RootFolderFileSystemModel.filePath(self.RootFolderTree.selectedIndexes()[0]))

	def ItemSorting(self):
		if SortedNumbar[0] == '1':
			self.SortChangeButton.setText('昇順(A-Z)')
			self.SubFolderTree.sort(0, Qt.SortOrder.AscendingOrder)
			SortedNumbar[0] = '0'
		elif SortedNumbar[0] == '0':
			self.SortChangeButton.setText('降順(Z-A)')
			self.SubFolderTree.sort(0, Qt.SortOrder.DescendingOrder)
			SortedNumbar[0] = '1'

	def SortingItemMenu(self):
		if SortedNumbar[0] == '1':
			self.SortChangeButton.setText('昇順(A-Z)')
			self.SubFolderTree.sort(0, Qt.SortOrder.AscendingOrder)
			SortedNumbar[0] = '0'
		elif SortedNumbar[0] == '0':
			self.SortChangeButton.setText('降順(Z-A)')
			self.SubFolderTree.sort(0, Qt.SortOrder.DescendingOrder)
			SortedNumbar[0] = '1'

	def on_TextSearch(self, text):
		try:
			if not self.FolderTree.isExpanded(self.FolderTree.selectedIndexes()[0]):
				self.FolderTree.expandRecursively(self.FolderTree.selectedIndexes()[0], 3)
		except:
			pass
		self.FolderTree.keyboardSearch('')
		self.FolderTree.keyboardSearch(text)

	def on_TextSearch2(self, text):
		try:
			if not self.InputView2.isExpanded(self.InputView2.selectedIndexes()[0]):
				self.InputView2.expandRecursively(self.InputView2.selectedIndexes()[0], 3)
		except:
			pass
		self.InputView2.keyboardSearch('')
		self.InputView2.keyboardSearch(text)

	def on_TextSearch3(self, text):
		try:
			if not self.ResultView3.isExpanded(self.ResultView3.selectedIndexes()[0]):
				self.ResultView3.expandRecursively(self.ResultView3.selectedIndexes()[0], 3)
		except:
			pass
		self.ResultView3.keyboardSearch('')
		self.ResultView3.keyboardSearch(text)

	def on_TextSearch4(self, text):
		try:
			if not self.RootFolderTree.isExpanded(self.RootFolderTree.selectedIndexes()[0]):
				self.RootFolderTree.expandRecursively(self.RootFolderTree.selectedIndexes()[0], 3)
		except:
			pass
		self.RootFolderTree.keyboardSearch('')
		self.RootFolderTree.keyboardSearch(text)

	def from_item_to_json(self, parent, data):
		for c in range(len(data)):
			path = json.loads(data[c]).get('PATH')
			if os.path.isfile(path):
				icon = QFileIconProvider().icon(QFileIconProvider.File)
			else:
				icon = QFileIconProvider().icon(QFileIconProvider.Folder)
			c2 = QStandardItem(icon, path)
			parent.appendRow(c2)

	def on_TextSearch5(self):
		if not self.FileTreeSearch2.text() == '':
			DicFiles = []
			for File in pathlib.Path(self.SubFolderTree.rootPath()+os.sep).glob('**/{}'.format(self.FileTreeSearch2.text())):
				DicFiles.append(json.dumps({'PATH': '{}'.format(str(File))}, indent=2, ensure_ascii=False))
			self.ItemModel = QStandardItemModel()
			self.from_item_to_json(self.ItemModel.invisibleRootItem(), sorted(DicFiles))
			SearchWindow(model=self.ItemModel).show()

	def SelectedItem(self, index):
		try:
			rootIndex = self.FolderTree.selectedIndexes()[0]
			self.FolderTree.expand(rootIndex)
		except:
			pass
		if os.path.isfile(self.FileSystemModel.filePath(self.FileSystemModel.index(index.row(), 0, index.parent()))):
			pass
		else:
			self.FileFinput_2.setText(self.FileSystemModel.filePath(self.FileSystemModel.index(index.row(), 0, index.parent())))

	def SelectedItem2(self, index):
		try:
			rootIndex2 = self.InputView2.selectedIndexes()[0]
			self.InputView2.expand(rootIndex2)
		except:
			pass
		if os.path.isfile(self.FileSystemModel2.filePath(self.FileSystemModel2.index(index.row(), 0, index.parent()))):
			pass
		else:
			self.FolderPath.setText(self.FileSystemModel2.filePath(self.FileSystemModel2.index(index.row(), 0, index.parent())))

	def SelectedFolder(self):
		try:
			RootIndex = self.RootFolderTree.selectedIndexes()[0]
		except:
			RootIndex = self.RootFolderTree.selectedIndexes()
		if not os.path.isfile(self.RootFolderFileSystemModel.filePath(RootIndex)):
			if self.RootFolderTree.isExpanded(RootIndex):
				self.RootFolderTree.collapse(RootIndex)
			else:
				self.RootFolderTree.expand(RootIndex)
			PathListory[0] = self.RootFolderFileSystemModel.filePath(RootIndex)
			self.SubFolderTree.setRootPath(self.RootFolderFileSystemModel.filePath(RootIndex))
			self.SubFolderTree.setRootIndex(self.SubFolderTree.index(self.RootFolderFileSystemModel.filePath(RootIndex)))
			self.PathBar.setText(self.SubFolderTree.rootPath()+os.sep)
			NowRootDirectoryPath[0] = self.SubFolderTree.rootPath()
			StopPath[0] = '2'
			StopPath2[0] = '0'
			PathHistorys.append(self.SubFolderTree.rootPath()+os.sep)
			BackupRootPath.append(self.SubFolderTree.rootPath())
		else:
			QDesktopServices.openUrl('file:///{}'.format(self.RootFolderFileSystemModel.filePath(RootIndex)))

	def FileFolderSelector(self):
		if self.FileFinput.text() == '**':
			self.FileFinput.setText('*.*')
		self.FileOption.stateChanged.connect(self.FileFolderSelectorCallBak)
		self.FileTypeOption.stateChanged.connect(self.FileFolderSelectorCallBak)
		if self.FileFinput.text() == '**':
			self.FileFinput.setText('*.*')

	def FileFolderSelectorCallBak(self):
		if self.FileTypeOption.checkState() == Qt.Checked:
			if not '*' in self.FileFinput.text():
				try:
					FileName = self.FileFinput.text().split('.')[0]
				except:
					FileName = ''
				try:
					FileType = self.FileFinput.text().split('.')[1]
				except:
					FileType = ''
				if FileName == '':
					FileName = ''
				if FileType == '':
					FileType = '.*'
				if FileName == '' and FileType == '':
					FileName = ''
					FileType = '.*'
				if not '**' in self.FileFinput.text():
					self.FileFinput.setText('{}{}'.format(FileName, FileType).replace('..', '.'))
				else:
					self.FileFinput.setText('*.*')
			elif self.FileOption.checkState() == Qt.Checked and self.FileTypeOption.checkState() == Qt.Checked:
				self.FileFinput.setText('*.*')
			elif self.FileFinput.text() == '*.*':
				self.FileFinput.setText('*.')
			elif self.FileFinput.text() == '*.':
				self.FileFinput.setText('.*')
			elif '*' in self.FileFinput.text() and self.FileOption.checkState() == Qt.Checked:
				if '.' in self.FileFinput.text() and not '*' in self.FileFinput.text():
					try:
						Fname = self.FileFinput.text().split('.')[0]
					except:
						Fname = ''
					try:
						Ftype = self.FileFinput.text().split('.')[1]
					except:
						Ftype = ''
					self.FileFinput.setText('{}{}'.format(Fname, Ftype))
				elif self.FileFinput.text() == '*.':
					self.FileFinput.setText('.*')
				else:
					self.FileFinput.setText('*.*')
		elif self.FileOption.checkState() == Qt.Unchecked and self.FileTypeOption.checkState() == Qt.Unchecked:
			self.FileFinput.setText(self.FileFinput.text().replace('.*', '').replace('*.', '').replace('*', ''))
		if self.FileOption.checkState() == Qt.Checked:
			self.dPrint('[INFO] ファイル名を設定しました。ファイル名: {}'.format(self.FileFinput.text().split('.')[0]))
		if self.FileOption.checkState() == Qt.Checked:
			if not '*' in self.FileFinput.text():
				try:
					FileName = self.FileFinput.text().split('.')[0]
				except:
					FileName = ''
				try:
					FileType = self.FileFinput.text().split('.')[1]
				except:
					FileType = ''
				if FileName == '':
					FileName = '*.'
				if FileType == '':
					FileType = ''
				if FileName == '' and FileType == '':
					FileName = '*.'
					FileType = ''
				if not '**' in self.FileFinput.text():
					self.FileFinput.setText('{}{}'.format(FileName, FileType).replace('..', '.'))
				else:
					self.FileFinput.setText('*.*')
			elif self.FileOption.checkState() == Qt.Checked and self.FileTypeOption.checkState() == Qt.Checked:
				self.FileFinput.setText('*.*')
			elif self.FileFinput.text() == '*.*':
				self.FileFinput.setText('.*')
			elif self.FileFinput.text() == '.*':
				self.FileFinput.setText('*.')
			elif '*' in self.FileFinput.text() and self.FileTypeOption.checkState() == Qt.Checked:
				if '.' in self.FileFinput.text() and not '*' in self.FileFinput.text():
					try:
						Fname = self.FileFinput.text().split('.')[0]
					except:
						Fname = ''
					try:
						Ftype = self.FileFinput.text().split('.')[1]
					except:
						Ftype = ''
					self.FileFinput.setText('{}{}'.format(Fname, Ftype))
				else:
					self.FileFinput.setText('*.*')
		elif self.FileOption.checkState() == Qt.Unchecked and self.FileTypeOption.checkState() == Qt.Unchecked:
			self.FileFinput.setText(self.FileFinput.text().replace('.*', '').replace('*.', '').replace('*', ''))
		if self.FileTypeOption.checkState() == Qt.Checked:
			self.dPrint('[INFO] ファイルタイプを設定しました。ファイルタイプ: {}'.format(self.FileFinput.text().split('.')[1]))

	def dPrint(self, Log):
		self.DebugArea.appendPlainText(Log)

	def dPrint2(self, Logs):
		self.DebugLog2.appendPlainText(Logs)

	def Fill_Model_from_Json(self, Partent, data, path=''):
		if isinstance(data, dict):
			for itm, childs in data.items():
				if itm == '／':
					Icon = QFileIconProvider().icon(QFileIconProvider.Drive)
				elif os.path.isdir(path) or not os.path.isfile(path):
					Icon = QFileIconProvider().icon(QFileIconProvider.Folder)
				else:
					Icon = QFileIconProvider().icon(QFileIconProvider.File)
				child = QStandardItem(Icon, str(itm))
				Partent.appendRow(child)
				self.Fill_Model_from_Json(child, childs)

		elif isinstance(data, list):
			for P in data:
				self.Fill_Model_from_Json(Partent, P)
		else:
			Partent.appendRow(QStandardItem(str(data)))

	def FindAllFiles(self, path):
		for root, dirC, file in os.walk(path):
			yield root
			for File in file:
				yield os.path.join(root, File)

	def BigFileSearching(self):
		DicsFiles = []
		FoundFiles = []
		size_min_mb = 50 << 20
		for File in self.FindAllFiles(self.FolderPath.text()):
			try:
				if os.path.isfile(File):
					if os.path.getsize(File) >= size_min_mb:
						if os.path.getsize(File) >> 20:
							FoundFiles.append(File)
						self.dPrint2('[INFO] ファイルが見つかりました! 使用容量: {:.1f}MB 場所: {}'.format(os.path.getsize(File) >> 20, File))
			except:
				pass
		try:
			DriveLetter = os.path.splitdrive(os.environ['windir'])[0] + os.sep
		except:
			DriveLetter = '／'
		for Dics in FoundFiles:
			DicsLists = Dics.split(os.sep)
			PathDics = ''.join(pathlist.replace(pathlist, '{"'+pathlist+'": ') for pathlist in DicsLists)
			SearcedPathDic = re.sub('($)', '}'*(len(DicsLists)), PathDics).replace('{"": ', '{"%s": ' % DriveLetter).replace(': }', ': {}}')
			EndValue = re.findall('(".+": )', json.dumps(ast.literal_eval(SearcedPathDic), indent=2, ensure_ascii=False))[-1].split(':')[0]
			PathJson = json.dumps(ast.literal_eval(SearcedPathDic), ensure_ascii=False).replace('{' + EndValue + ': {}', EndValue).replace('}','') + '}' * (len(DicsLists) - 1)
			DicsFiles.append([PathJson, Dics])
		for DicsF, Path in DicsFiles:
			self.Fill_Model_from_Json(self.ResultView2Model.invisibleRootItem(), ast.literal_eval(DicsF), Path)
		self.ResultView2.setModel(self.ResultView2Model)
		self.ResultView2.expandAll()

	def ContextMenu(self, Point):
		self.Menu = QMenu()
		self.Menu.addAction('内容を更新', self.ProcessList)
		self.Menu.addAction('プロセスの終了', self.killProcess)
		self.Menu.addAction('プロセスツリーの終了', self.killTreeProcess)
		self.Menu.exec(self.ResultView3.mapToGlobal(Point))

	def killTreeProcess(self):
		try:
			itm = self.ResultViewModel3.itemFromIndex(self.ResultView3.selectedIndexes()[0]).text()
		except IndexError:
			itm = self.ResultViewModel3.itemFromIndex(self.ResultView3.selectedIndexes()).text()
		ProcssName = itm.split(' (')[0]
		try:
			for Proc in psutil.process_iter(['pid', 'name']):
				if Proc.name()[:len(ProcssName)] == ProcssName:
					ChildrenList = [Child.pid for Child in psutil.Process(Proc.pid).children(recursive=True)]
					for terminate_pid in ChildrenList:
						psutil.Process(terminate_pid).terminate()
					psutil.Process(Proc.pid).terminate()
		except:
			try:
				for Proc in psutil.process_iter(['pid', 'name']):
					if Proc.name()[:len(ProcssName)] == ProcssName:
						Childrens = psutil.Process(Proc.pid).children(recursive=True)
						_, rekillPID = psutil.wait_procs(Childrens, timeout=0)
						for pk in rekillPID:
							pk.kill()
			except:
				pass
		self.ProcessList()

	def killProcess(self):
		try:
			itm = self.ResultViewModel3.itemFromIndex(self.ResultView3.selectedIndexes()[0]).text()
		except IndexError:
			itm = self.ResultViewModel3.itemFromIndex(self.ResultView3.selectedIndexes()).text()
		ProcssName = itm.split(' (')[0]
		try:
			for Proc in psutil.process_iter(['pid', 'name']):
				if Proc.name()[:len(ProcssName)] == ProcssName:
					psutil.Process(Proc.pid).terminate()
		except:
			pass

		self.ProcessList()

	def ProcessList(self):
		try:
			self.ResultViewModel3.removeRows(0, self.ResultViewModel3.rowCount())
			try:
				pILL = {'{} ({})'.format(p.name(), p.pid): {childs.name(): {}} for p in psutil.process_iter(['pid', 'name']) for childs in p.children(recursive=True)}
			except:
				time.sleep(1)
				pILL = {'{} ({})'.format(p.name(), p.pid): {childs.name(): {}} for p in psutil.process_iter(['pid', 'name']) for childs in p.children(recursive=True)}
			self.Fill_Model_from_Json(self.ResultViewModel3.invisibleRootItem(), pILL)
			self.ResultView3.setModel(self.ResultViewModel3)
		except:
			pass

	def SearchingFile(self):
		FileAppends = []
		DicFiles = []

		for File in pathlib.Path(self.FileFinput_2.text()).glob('**/{}'.format(self.FileFinput.text())):
			self.dPrint('[INFO] ファイルが見つかりました! 場所: {}'.format(File))
			FileAppends.append(str(File))

		try:
			DriveLetter = os.path.splitdrive(os.environ['windir'])[0] + os.sep
		except:
			DriveLetter = '／'
		for dics in FileAppends:
			DicsList = dics.split(os.sep)
			PDic = ''.join(pathlist.replace(pathlist, '{"'+pathlist+'": ') for pathlist in DicsList)
			PathDic = re.sub('($)', '}'*(len(DicsList)), PDic).replace('{"": ', '{"%s": ' % DriveLetter).replace(': }', ': {}}')
			EndValue = re.findall('(".+": )', json.dumps(ast.literal_eval(PathDic), indent=2, ensure_ascii=False))[-1].split(':')[0]
			PathJson = json.dumps(ast.literal_eval(PathDic), ensure_ascii=False).replace('{' + EndValue + ': {}', EndValue).replace('}', '') + '}' * (len(DicsList) -1)
			DicFiles.append([PathJson, dics])
		for DicsFF, Path in DicFiles:
				self.Fill_Model_from_Json(self.resultMOdel.invisibleRootItem(), ast.literal_eval(DicsFF), path=Path)
		self.ResultTree.setModel(self.resultMOdel)
		self.ResultTree.expandAll()


	def ClearDebug(self):
		self.DebugArea.clear()
		self.resultMOdel.removeRows(0, self.resultMOdel.rowCount())

	def ClearDebug2(self):
		self.DebugLog2.clear()
		self.ResultView2Model.removeRows(0, self.ResultView2Model.rowCount())

	def retranslateUi(self, Searcher):
		Searcher.setWindowTitle(QCoreApplication.translate("Searcher", "ExtendExplorerTools", None))
		self.FileOption.setText(QCoreApplication.translate("Searcher", "ファイル名を無指定", None))
		self.FileTypeOption.setText(QCoreApplication.translate("Searcher", "ファイル拡張子を無指定", None))
		self.FileName.setText(QCoreApplication.translate("Searcher", "ファイル名:", None))
		self.FolderName.setText(QCoreApplication.translate("Searcher", "フォルダ名:", None))
		self.label_2.setText(QCoreApplication.translate("Searcher", "以下からもフォルダを選択できます", None))
		self.SearchButton.setText(QCoreApplication.translate("Searcher", "ファイル検索を開始", None))
		self.ResultDelButton.setText(QCoreApplication.translate("Searcher", "結果を消す", None))
		self.Tab3.setTabText(self.Tab3.indexOf(self.tab), QCoreApplication.translate("Searcher", "ファイルの詳細検索", None))
		self.FolderPathLabel.setText(QCoreApplication.translate("Searcher", "検索したい場所:", None))
		self.BigFileSearchButton.setText(QCoreApplication.translate("Searcher", "ファイル検索を開始", None))
		self.ResultDelButton2.setText(QCoreApplication.translate("Searcher", "結果を消す", None))
		self.Tab3.setTabText(self.Tab3.indexOf(self.tab_2), QCoreApplication.translate("Searcher", "大きいファイルの詳細検索", None))
		self.RefreshButton.setText(QCoreApplication.translate("Searcher", "内容を更新する", None))
		self.Tab3.setTabText(self.Tab3.indexOf(self.tab_3), QCoreApplication.translate("Searcher", "プロセスの表示", None))
		self.FolderSearchLabel2.setText(QCoreApplication.translate("FullTools2", "以下からもフォルダを選択できます", None))
		self.Tab3.setTabText(self.Tab3.indexOf(self.tab_4), QCoreApplication.translate("FullTools2", "エクスプローラー", None))
		self.UpDirectory.setText(QCoreApplication.translate("FullTools2", "↑", None))
		self.UpDirectory.setToolTip(QCoreApplication.translate("FullTools2", "<html><head/><body><p>上の階層に戻る</p></body></html>", None))
		self.HomeButton.setText(QCoreApplication.translate("FullTools2", "🏠", None))
		self.BackButton.setText(QCoreApplication.translate("FullTools2", "←", None))
		self.OnButton.setText(QCoreApplication.translate("FullTools2", "→", None))

def main():
	app = QApplication(sys.argv)
	main_window = MainWindowwView()
	ui_window = Ui_FullTools2()
	ui_window.setupUi(main_window)
	main_window.setFixedSize(main_window.size())
	main_window.show()
	sys.exit(app.exec())

if __name__ == '__main__':
	main()
