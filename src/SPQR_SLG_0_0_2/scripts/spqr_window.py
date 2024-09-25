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

# get modules
import sys, pygame
from pygame.locals import *

import spqr_defines as SPQR
import spqr_widgets as SWIDGET
import spqr_gui as SGFX

# at the moment, you have to allow for the borders when you create a new window
# sorry about, it's definitly on the TODO list

# a simple class that defines button text, active key and event to run
# when adding buttons to bottom of a window
class CButtonDetails(object):
	def __init__(self, text, key, event):
		"""Set key to None if you don't want a keypress to be
		   added to the keyboard callbacks"""
		self.text = text
		self.key = key
		self.event = event
		self.describe="CButtonDetails"

# define an CWindow
class CWindow(object):
	"""Base window class
	   Call with x,y - position
	   width,height, title - text on top of window,
	   draw - wether to place on screen or not"""
	def __init__(self, x, y, width, height, title, draw = True, describe = "CWindow"):
		self.active = True
		self.display = draw
		self.modal = False
		# set this to false if you want added items to NOT be
		# offset by the border widths
		self.border_offset = draw
		self.describe = describe
		# use info as a storage for any of your own stuff
		# (you can use it to pass variables between function callbacks, for example)
		self.info = 0
		# if any widgets need to store data, then we put it here:
		self.data = []
		self.rect = pygame.Rect((x, y, width, height))
		self.rect.w += 2 * SPQR.WINSZ_SIDE
		self.rect.h += SPQR.WINSZ_TOP + SPQR.WINSZ_BOT
		# if the passed values for x and y are -1 then
		# place the window at the centre of the screen
		self.centre = False
		if x == -1 or y == -1:
			self.centreWindow()
			self.centre = True
		self.caption = title
		# finally, we need a list of the items...
		self.items = []
		# get an image of the required size
		self.image = pygame.Surface((self.rect.w, self.rect.h))
		# now lets actually draw the window, if needed
		if draw == True:
			# flood fill it with grey and get a standard rectangle
			self.image.fill(SPQR.BGUI_COL)
			rect = pygame.Rect((0, 0, 0, 0))
			# ok, we start with the sides, with some clever blitting
			# basically blit 4*4 images until you can only do 4*1 ones
			rect.x = 0
			rect.y = SGFX.gui.iHeight("win_tl")
			lrg_draw = int((self.rect.h - rect.y) / 4)
			sml_draw = (self.rect.h - rect.y) - (lrg_draw * 4)
			offset = self.rect.w - SGFX.gui.iWidth("win_rgt")
			for i in range(lrg_draw):
				# blit the large images
				self.image.blit(SGFX.gui.image("win_lft_lg"), rect)
				rect.x += offset
				self.image.blit(SGFX.gui.image("win_rgt_lg"), rect)
				rect.x -= offset	
				rect.y += 4
			# ok, now the final small ones
			if sml_draw != 0:
				for i in range(sml_draw):
					self.image.blit(SGFX.gui.image("win_lft"), rect)
					rect.x += offset
					self.image.blit(SGFX.gui.image("win_rgt"), rect)
					rect.x -= offset
					rect.y += 1
			# same sort of routine for the top and bottom
			rect.y = 0
			rect.x = SGFX.gui.iWidth("win_tl")
			lrg_draw = int((self.rect.w - rect.x) / 4)
			sml_draw = (self.rect.w - rect.x)-(lrg_draw * 4)
			offset = self.rect.h - SGFX.gui.iHeight("win_bot")
			for i in range(lrg_draw):
				# again, the large blits (as can be seen from their name)
				self.image.blit(SGFX.gui.image("win_top_lg"), rect)
				rect.y += offset
				self.image.blit(SGFX.gui.image("win_bot_lg"), rect)
				rect.y -= offset
				rect.x += 4
			# then the small top/bottom fillers
			if sml_draw != 0:
				for i in range(sml_draw):
					self.image.blit(SGFX.gui.image("win_top"), rect)
					rect.y += offset
					self.image.blit(SGFX.gui.image("win_bot"), rect)
					rect.y -= offset
					rect.x += 1
			# now draw in all of the corners
			rect = pygame.Rect((0, 0, 0, 0))
			self.image.blit(SGFX.gui.image("win_tl"), rect)
			rect.y = self.rect.h - SGFX.gui.iHeight("win_bl")
			self.image.blit(SGFX.gui.image("win_bl"), rect)
			rect.x = self.rect.w - SGFX.gui.iWidth("win_br")
			self.image.blit(SGFX.gui.image("win_br"), rect)
			rect.y = 0
			self.image.blit(SGFX.gui.image("win_tr"), rect)
			# right, all that's left to do is draw the text over the title bar
			# firstly render the text in it's own little gfx area
			SGFX.gui.fonts[SPQR.FONT_VERA].set_bold(True)
			title = SGFX.gui.fonts[SPQR.FONT_VERA].render(title, True, SPQR.COL_WINTITLE)
			SGFX.gui.fonts[SPQR.FONT_VERA].set_bold(False)
			# set it to centre of title bar
			rect.x = ((self.rect.w + (SGFX.gui.iWidth("win_tl") * 2)) - title.get_width()) / 2
			rect.y = ((SGFX.gui.iHeight("win_tl") - title.get_height()) / 2) + 1
			# render to image
			self.image.blit(title, rect)
	
	def fillWindowImage(self):
		"""Sometimes you need a simple window with a background"""
		self.image=pygame.Surface((self.rect.width, self.rect.height)).convert()
		self.image.fill(SPQR.BGUI_COL)
		self.display = True
	
	def centreWindow(self):
		"""Call to reset the rect co-ordinates to the centre of the screen"""
		self.rect.x = (SPQR.SCREEN_WIDTH - self.rect.w) / 2
		self.rect.y = (SPQR.SCREEN_HEIGHT - self.rect.h) / 2
		return True
	
	def addWidget(self, new_item):
		"""Function to add a widget to the window. Call with widget to add""" 	
		self.items.append(new_item)
		# we add to the last item, index is thus len()-1
		index = len(self.items) - 1
		# we now have a valid parent to add
		self.items[index].parent = self
		# calling routine will not know about the border, or at least
		# not care about it, so we manually offset into the window
		# you can change this by resetting self.border_offset
		if self.border_offset == True:
			self.items[index].rect.x += SPQR.WINSZ_SIDE
			self.items[index].rect.y += SPQR.WINSZ_TOP
		return index

	def drawWindow(self):
		"""Routine draws the entire window and returns the image"""
		win_img = pygame.Surface((self.rect.w, self.rect.h))
		# blit the current window border across
		win_img.blit(self.image, (0, 0))
		# now draw all the items
		for item in self.items:
			if item.visible == True:
				win_img.blit(item.image, (item.rect.x, item.rect.y))		
		# thats it! pretty simple really.
		return win_img

	def buildButtonArea(self, button_list, lhs = False):
		"""Function to add buttons to bottom of a window. The window's size
		   is amended to take account of this. The routine adds the buttons,
		   and also the seperator widget used.
		   Pass a list of button_details. If the list is empty, nothing is done
		   The buttons are taken but .pop(0), so index 0 is first to be done
		   The final parameter asks to place the last button on the extreme
		   left hand side if equal to True. 
		   Returns a list of index numbers to the buttons if if all ok, False
		   otherwise (and False leaves window as it was to start with)"""
		# any buttons at all? If not, don't do anything
		if len(button_list) == 0:
			return True
		bindex = []
		# Firstly, we need to work out how many buttons can fit on 1 line
		# get the real width of the window minus it's sides
		width = self.rect.w - (2 * SPQR.WINSZ_SIDE)
		# and the button size:
		bwidth = SGFX.gui.iWidth("button")

		# the basic button layout is as follows:
		# we add a sep bar immediatly below. This is always 2 pixels in height
		# The button holding area below this is always 2*BUTTON_HEIGHT,
		# with the buttons being placed in the centre.
		# The buttons are added from right to left, and from top to bottom
		# they are spaced, with from left to right, (SPACER*2),button etc...
		# firstly, have we enough room for 1 button even?
		if width < (SPQR.SPACER * 4) + bwidth:
			# cant do it, so return false
			if SPQR.DEBUG_MODE == True:
				print "Error: Couldn't add buttons (window too small)"
			return False
		# how many buttons can we add then?
		padding = SPQR.SPACER * 2
		totb = (width - padding) / (bwidth + SPQR.SPACER)
		# hopefully we can get away with only one level of buttons:
		if totb >= len(button_list):
			# yes, all buttons go on the one line
			# start by extending the size of the window and rebuilding the image
			extend_height = (SGFX.gui.iHeight("button") * 2) + 2
			self.rect.h += extend_height
			new_image = pygame.Surface((self.rect.w, self.rect.h))
			new_image.fill(SPQR.BGUI_COL)
			# blit most of the old image:
			new_image.blit(self.image, (0, 0),
				(0, 0, self.rect.w, self.rect.h - (SPQR.WINSZ_BOT + extend_height)))
			# blit bottom to the bottom (!)
			new_image.blit(self.image, (0, self.rect.h - SPQR.WINSZ_BOT),
				(0, self.rect.h - (SPQR.WINSZ_BOT + extend_height), self.rect.w, SPQR.WINSZ_BOT))
			# we now need to draw in the sides that are missing.
			# area to draw is actually pretty small. We can assume that there
			# is enough space already on the present window to draw from
			# it sure makes the code a heck of a lot smaller :-)			
			new_image.blit(self.image, (0, (self.rect.h - (extend_height + SPQR.WINSZ_BOT))),
				(0, SPQR.WINSZ_TOP, SPQR.WINSZ_SIDE, extend_height + 1))
			new_image.blit(self.image,
				(self.rect.w - SPQR.WINSZ_SIDE, (self.rect.h - (extend_height + SPQR.WINSZ_BOT))),
				(self.rect.w - SPQR.WINSZ_SIDE, SPQR.WINSZ_TOP, SPQR.WINSZ_SIDE, extend_height + 1))
			# new image is now complete, copy it across
			self.image = new_image
			
			# now we can start to add the various parts. Easiest of all is the bar
			# you may question the maths here (how do we know the length is going to be
			# big enough?), but all we are after is a width >(2*SPACER), ok (if SPACER is
			# fairly small) because we already tested for button width earlier
			self.addWidget(SWIDGET.CSeperator(SPQR.SPACER,
				self.rect.h - (extend_height + SPQR.WINSZ_TOP),
				(self.rect.w - (2 * (SPQR.WINSZ_SIDE + SPQR.SPACER)))))
				
			# now we add the buttons
			xpos = width - ((2 * SPQR.SPACER) + SGFX.gui.iWidth("button"))
			ypos = (self.rect.h - (extend_height + SPQR.WINSZ_TOP))
			ypos += (extend_height-SGFX.gui.iHeight("button")/2)
			while len(button_list) > 0:	
				# get the next button
				button = button_list.pop(0)
				# could be the last button...
				if len(button_list) == 1 and lhs == True:
					# amend xpos - real easy
					xpos = SPQR.SPACER
				# build the button
				bwidget = SWIDGET.CButton(xpos, ypos, button.text)
				bwidget.active = True
				# and then add it
				bindex.append(self.addWidget(bwidget))
				# might as well add the callback now...
				bwidget.callbacks.mouse_lclk = button.event
				# and the keystuff, if needed:
				if button.key != None:
					SGFX.gui.keyboard.addKey(button.key, button.event)
				# reset x position
				xpos -= (2 * SPQR.SPACER) + SGFX.gui.iWidth("button")
		else:
			# 2 lines of buttons not implemented
			if SPQR.DEBUG_MODE == True:
				print "Error: >1 line of buttons not implemented in buildButtonArea()"
			return False
		# one last thing. Recentre the window?
		if self.centre == True:
			self.centreWindow()
		# everything went ok. it seems. I leave it to the calling code to
		# deal with making the window modal, etc...
		return(bindex)

