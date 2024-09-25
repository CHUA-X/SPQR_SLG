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

class unitStats(object):
	def __init__(self, strength, quality, morale):
		self.strength = strength
		self.quality = quality
		self.morale = morale

class CUnit(object):
	"""Normally the calling functions read q and m from a file,
		 hence the odd maths when it calculates morale and quality"""
	def __init__(self, name, image, move = 4, stats = None, naval = False):
		self.name = name
		self.moves = move
		self.moves_left = move
		self.image = image
		self.stats = stats
		self.region = None
		self.turn_done = False
		self.naval = naval
		
	def __str__(self):
		"""Return a string of the unit details"""
		text = "  Name: " + self.name
		text += "\nRegion: " + self.region + "\n"
		return text

