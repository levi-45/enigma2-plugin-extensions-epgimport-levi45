#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.MenuList import MenuList
from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, gFont, getDesktop
from Tools.Directories import SCOPE_PLUGINS, resolveFilename
from Tools.LoadPixmap import LoadPixmap


FHD = False
WQHD = False
if getDesktop(0).size().width() == 1920:
	FHD = True
if getDesktop(0).size().width() == 2560:
	WQHD = True


PathPlugin = resolveFilename(SCOPE_PLUGINS, "Extensions/EPGImport/")
expandableIcon = LoadPixmap(PathPlugin + "icon/expandable.png")
expandedIcon = LoadPixmap(PathPlugin + "icon/expanded.png")
lock_on = LoadPixmap(PathPlugin + "icon/lock_on.png")
lock_off = LoadPixmap(PathPlugin + "icon/lock_off.png")


def loadSettings():
	global cat_desc_loc, entry_desc_loc, cat_icon_loc, entry_icon_loc

	if WQHD:
		x, y, w, h = (50, 4, 1200, 120)
	elif FHD:
		x, y, w, h = (40, 9, 1200, 60)
	else:
		x, y, w, h = (20, 3, 800, 30)
	ind = x	 # Indent the entries by the same amount as the icon.
	cat_desc_loc = (x, y, w, h)
	entry_desc_loc = (x + ind, y, w - ind, h)

	if WQHD:
		x, y, w, h = (0, 18, 30, 33)  # y calcolato come (70 - 33) / 2
	elif FHD:
		x, y, w, h = (0, 12, 30, 33)  # y calcolato come (50 - 33) / 2
	else:
		x, y, w, h = (0, 0, 30, 33)	 # y calcolato come (30 - 33) / 2
	cat_icon_loc = (x, y, w, h)
	entry_icon_loc = (x + ind, y, w, h)


boxPythonMultiContent = eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST


def category(description, isExpanded=False):
	global cat_desc_loc, cat_icon_loc
	icon = expandedIcon if isExpanded else expandableIcon
	return [
		(description, isExpanded, []),
		(eListboxPythonMultiContent.TYPE_TEXT,) + cat_desc_loc + (0, RT_HALIGN_LEFT, description),
		(boxPythonMultiContent,) + cat_icon_loc + (icon,)
	]


def entry(description, value, selected):
	global entry_desc_loc, entry_icon_loc
	res = [
		(description, value, selected),
		(eListboxPythonMultiContent.TYPE_TEXT,) + entry_desc_loc + (0, RT_HALIGN_LEFT, description)
	]
	if selected:
		selectionpng = lock_on
		res.append((boxPythonMultiContent,) + entry_icon_loc + (selectionpng,))
	else:
		selectionpng = lock_off
		res.append((boxPythonMultiContent,) + entry_icon_loc + (selectionpng,))
	return res


def expand(cat, value=True):
	# cat is a list of data and icons
	if cat[0][1] != value:
		if WQHD:
			ix, iy, iw, ih = (10, 10, 25, 70)
		elif FHD:
			ix, iy, iw, ih = (10, 5, 25, 40)
		else:
			ix, iy, iw, ih = (10, 2, 25, 25)
		icon = expandedIcon if value else expandableIcon
		t = cat[0]
		cat[0] = (t[0], value, t[2])
		cat[2] = (boxPythonMultiContent,) + cat_icon_loc + (icon,)


def isExpanded(cat):
	return cat[0][1]


def isCategory(item):
	# Return whether list enty is a Category
	return hasattr(item[0][2], "append")


class ExpandableSelectionList(MenuList):
	def __init__(self, tree=None, enableWrapAround=False):
		"tree is expected to be a list of categories"
		MenuList.__init__(self, [], enableWrapAround, content=eListboxPythonMultiContent)

		if WQHD:
			font = ("Regular", 48, 70)	# Altezza riga: 70
		elif FHD:
			font = ("Regular", 37, 60)	# Altezza riga: 60
		else:
			font = ("Regular", 24, 30)	# Altezza riga: 30

		self.l.setFont(0, gFont(font[0], font[1]))
		self.l.setItemHeight(font[2])
		self.tree = tree or []
		self.updateFlatList()

	def updateFlatList(self):
		# Update the view of the items by flattening the tree
		ln = []
		for cat in self.tree:
			ln.append(cat)
			if isExpanded(cat):
				for item in cat[0][2]:
					ln.append(entry(*item))
		self.setList(ln)

	def toggleSelection(self):
		idx = self.getSelectedIndex()
		item = self.list[idx]
		# Only toggle selections, not expandables...
		if isCategory(item):
			expand(item, not item[0][1])
			self.updateFlatList()
		else:
			# Multiple items may have the same key. Toggle them all,
			# in both the visual list and the hidden items
			i = item[0]
			key = i[1]
			sel = not i[2]
			for idx, e in enumerate(self.list):
				if e[0][1] == key:
					self.list[idx] = entry(e[0][0], key, sel)
			for cat in self.tree:
				for idx, e in enumerate(cat[0][2]):
					if e[1] == key and e[2] != sel:
						cat[0][2][idx] = (e[0], e[1], sel)
			self.setList(self.list)

	def enumSelected(self):
		for cat in self.tree:
			for entry in cat[0][2]:
				if entry[2]:
					yield entry


loadSettings()
