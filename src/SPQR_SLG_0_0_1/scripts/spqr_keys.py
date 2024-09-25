#!/usr/bin/python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys, pygame
from pygame.locals import *

import spqr_events as SEVENT

# class to hold a key value
class CKeypress(object):
	"""Class defines a simple keypress, as stores in the keyboard
	   handling code"""
	def __init__(self, press, mod, routine, parent = None):
		self.key = press
		self.mod = mod
		self.function = routine
		self.handle = parent

class CKeyboard(object):
	"""CKeyboard holds a list of keyboard events to respond to
	   and the functions that they should call (defined in the normal SEVENT)
	   Note: You can set one key to have more than one function
	   in fact this is normal behaviour in a modal window
	   if the window is modal, then the last one in the list will get called,
	   if not then the first will get called."""
	def __init__(self):
		self.active_keys = []		
		self.modal = []
		self.move_keys = 0
	
	def addKey(self, key, code, mod = 0):
		"""Call addKey with the keypress and the function
		   to call, and it gets added to the list."""
		# firstly, check we haven't already got this key:
		for i in self.active_keys:
			if i.key == key and i.mod == mod and i.function == code:
					# don't allow this
					return False
		# we havn't seen it yet, so add it
		self.active_keys.append(CKeypress(key, mod, code))
		return True
		
	def removeKey(self, key, mod = 0):
		"""Use removeKey to remove from the events list the
		   keypress sent as a parameter. If False is received
		   back, that key didn't exist anyway"""
		index = 0
		for i in self.active_keys:
			if i.key == key and i.mod == mod:
				del self.active_keys[index]
				return True
			index += 1
		return False

	def keyExists(self, key, mod = 0):
		"""Check if a keypress already exists"""
		for i in self.keys:
			if i.key == key and i.mod == mod:
				return True
		return False

	def setModalKeys(self, value):
		"""Set a unique number of keys on the top of the stack that
		   are to be the only keys to respond to. Used for modal dialogs
		   I should explain how modal strings work:
		   self.modal is an array. When this routine searches through
		   the keylist, it only looks at the self.modal[-1] ones (i.e. the
	 	   the number at the top of the list) starting backwards
	 	   if you really want to ignore keys, set the top value to -1"""
		self.modal.append(value)
		
	def removeModalKeys(self):
		"""Stops modal searching, removes the keys for you as well"""
		# anything to remove?
		if len(self.modal) == 0:
			return
		# yes, at least some work:
		count = self.modal[-1]
		# remove these modal keys
		while count > 0:
			self.active_keys.pop()
			count -= 1
		# then remove this modal value from the stack
		self.modal.pop()

	def getKeyFunction(self, key, mod):
		"""Returns function and true/false if key is on the list"""
		# modal keys in operation?
		if len(self.modal) == 0:
			# start with the easy, no modal stuff
			for i in self.active_keys:
				if i.key == key and i.mod & mod == i.mod:
					return True, i.function, i.handle
			# no match
			return False, False, None
		elif self.modal[-1] != -1:
			# we need to do modal keys
			index = len(self.active_keys) - 1
			count = self.modal[-1]
			while count > 0:
				if self.active_keys[index].key == key and \
					self.active_keys[index].mod & mod == self.active_keys[index].mod:
					# found the match
					return True, self.active_keys[index].function, self.active_keys[index].handle
				count -= 1
				index -= 1
		return False, False, None

