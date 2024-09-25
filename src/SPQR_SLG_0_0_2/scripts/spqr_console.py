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

# this file contains a class that contains all of the functions
# used by the spqr console. Each function has to return a text
# string that is then output by the console

import spqr_defines as SPQR
import spqr_gui as SGFX

class CConsole(object):
	def __init__(self):
		pass

	# now start the various functions
	def showUnits(self):
		"""Returns a string containing the unit name
		   and id number, formatted for console output"""
		# output the unit names
		return "No units found"

	def showRomanUnits(self):
		"""Returns a string containing the unit name
		   and id number, formatted for console output"""
		return "No Roman units found"
		
	def showWindows(self):
		"""Display a list of the current windows"""
		string=""
		index=0
		for window in SGFX.gui.windows:
			if window.caption == "":
				title = "NONE"
			else:
				title = window.caption
			string += "Window #" + str(index) + ":" + title + "\n"
			string += "          " + window.describe + "\n"
			index += 1
		return string


