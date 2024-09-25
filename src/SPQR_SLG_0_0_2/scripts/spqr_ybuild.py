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

import yaml
import spqr_gui as SGFX
import spqr_window as SWINDOW
import spqr_widgets as SWIDGET
import spqr_events as SEVENTS
import spqr_defines as SPQR

def createWindow(filename):
	"""Function that opens a file in YAML format and creates the
	   described window with all the given widgets"""
	# open then file
	var = yaml.load(open(filename))
	# Two lists where we going to store all the windows and indexes
	jlist = []
	index = []
	# A list for Button detail build
	buttondetails = []
	# loop for each window found in the file
	for j in range(len(var)):
		# first create the window and it's properties. each property
		# has a specific key in the file's dictonary
		jlist.append(SWINDOW.CWindow(var[j]['x'],var[j]['y'],
			var[j]['w'],var[j]['h'],var[j]['title'],var[j]['draw']))
		# We call this when we don't use drawWindow() function
		if var[j]['draw'] == 0 : jlist[j].fillWindowImage()
		# loop for the widget's list for the current window
		# each window has it's own
		for i in range(len(var[j]['items'])) :
			# Create the widget
			wid = createWidget(var[j]['items'][i])
			# Skip button detail widget's
			if wid.describe == "CButtonDetails":
				buttondetails.append(wid)
			else:
				# make it active
				wid.active = True
				# add widget to the window
				jlist[j].addWidget(wid)
		# finally I add the window to the gui
		index.append(SGFX.gui.addWindow(jlist[j]))
		# build the button area if exist
		if buttondetails != [] :
			SGFX.gui.windows[index[j]].buildButtonArea(buttondetails, False)
	return index

def createWidget(wlist):
	""" Function that creates a widget and returns it based on the
		passed list of properties """
	# First we check the key that will always be in our widget's
	# and defines the widget's purpose
	if wlist['widget'] == "CLabel" :
		# if this is a label make it with a text
		label = SWIDGET.buildLabel(wlist['text'])
		# and add the cords to the rect
		label.rect.x = wlist['x']
		label.rect.y = wlist['y']
		# Check if there is any widgets
		try:
			checkCallbacks(label,wlist['callbacks'])
		except:
			pass
		return label
	elif wlist['widget'] == "CCheckBox" :
		intro = SWIDGET.CCheckBox(wlist['x'], wlist['y'], wlist['initial'])
		return intro
	elif wlist['widget'] == "COptionMenu" :
		options = SWIDGET.COptionMenu(wlist['x'], wlist['y'], wlist['options'])
		options.describe = wlist['describe']
		return options
	elif wlist['widget'] == "CSeperator" :
		sepbar = SWIDGET.CSeperator(wlist['x'] , wlist['y'], wlist['w'])
		return sepbar
	elif wlist['widget'] == "CSlider" :
		sepbar = SWIDGET.CSlider(wlist['x'] , wlist['y'], wlist['w'],wlist['start'] , wlist['stop'], wlist['initial'])
		return sepbar
	elif wlist['widget'] == "CButton" :
		# if it is a button we create it and then we must put the callbacks in
		button = SWIDGET.CButton(wlist['x'] , wlist['y'] , wlist['text'])
		# for every callback we check the given function from the global list
		checkCallbacks(button,wlist['callbacks'])
		return button
	elif wlist['widget'] == "CScrollArea" :
		image=SGFX.gui.image(wlist['image'])
		sepbar = SWIDGET.CScrollArea(wlist['x'] , wlist['y'] , wlist['w'] , wlist['h'] , image)
		sepbar.setUpdateFunction(getattr(SEVENTS, wlist['update']))
		return sepbar
	elif wlist['widget'] == "CButtonDetails" :
		buttondetail = SWINDOW.CButtonDetails(wlist['text'], wlist['key'], getattr(SEVENTS, wlist["callback"]))
		return buttondetail

def checkCallbacks(wid,clist):
	""" Function that checks the callbacks and add it to the widget """
	for c in range(len(clist)) :
		if clist[c].keys()[0] == "lclk" and wid.callbacks.mouse_lclk == SPQR.mouse_lclk_std :
			wid.callbacks.mouse_lclk = getattr(SEVENTS, clist[c]["lclk"])
		elif clist[c].keys()[0] == "over" and wid.callbacks.mouse_lclk == SPQR.mouse_over_std :
			wid.callbacks.mouse_over = getattr(SEVENTS, clist[c]["over"])
		elif clist[c].keys()[0] == "rclk" and wid.callbacks.mouse_lclk == SPQR.mouse_rclk_std :
			wid.callbacks.mouse_rclk = getattr(SEVENTS, clist[c]["rclk"])
		elif clist[c].keys()[0] == "ldown" and wid.callbacks.mouse_lclk == SPQR.mouse_ldown_std :
			wid.callbacks.mouse_ldown = getattr(SEVENTS, clist[c]["ldown"])
		elif clist[c].keys()[0] == "rdown" and wid.callbacks.mouse_lclk == SPQR.mouse_rdown_std :
			wid.callbacks.mouse_rdown = getattr(SEVENTS, clist[c]["rdown"])
		elif clist[c].keys()[0] == "dclick" and wid.callbacks.mouse_lclk == SPQR.mouse_dclick_std :
			wid.callbacks.mouse_dclick = getattr(SEVENTS, clist[c]["dclick"])
	return wid

