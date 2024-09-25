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

import pygame
from pygame.locals import *

import spqr_defines as SPQR
import spqr_events as SEVENT
import spqr_keys as SKEY
import spqr_gui as SGFX

# what follows is the base class used for the callback functions of the widgets. Every
# widget has one, and you can modify the widgets be pointing mouse_* to different functions
class CCallbacks(object):
	"""Simple class holding callbacks for widgets."""
	def __init__(self, description):
		self.mouse_over = SPQR.mouse_over_std
		self.mouse_ldown = SPQR.mouse_ldown_std
		self.mouse_rdown = SPQR.mouse_rdown_std
		self.mouse_dclick = SPQR.mouse_dclick_std
		self.mouse_lclk = SPQR.mouse_lclk_std
		self.mouse_rclk = SPQR.mouse_rclk_std
		self.describe = description

# now a class for the items contained within the window
# this is the base class that you will only use to generate custom widgets
# in almost all cases you'll use the widgets defined by the library
class CWidget(object):
	"""Base class for widgets: All other widgets should build on this one"""
	def __init__(self, rect, htype, image, describe,
				 parent=False, active=False, visible=True):
		self.active = active
		self.visible = visible
		self.rect = rect
		self.wtype = htype
		# add callbacks
		self.callbacks = CCallbacks(describe+"_Callback")
		# set an image up for later
		self.image = image
		# following used to store the parent window of the
		# widget... False if there is no valid parent
		self.parent = False
		# if a widget needs to store state information, it goes here
		self.data = None
		self.describe = describe

# place the standard items here, starting with a label
class CLabel(CWidget):
	"""Label class stes and stores details for a simple label"""
	def __init__(self, x, y, width, height, text, font = SPQR.FONT_VERA):
		CWidget.__init__(self, pygame.Rect(x,y,width,height), SPQR.WT_LABEL,
					     None, "CLabel") 
		self.background_colour = SPQR.BGUI_COL
		self.text_colour = SPQR.COL_BLACK
		self.font = font
		self.justification = SPQR.LEFT_JUSTIFY
		self.text = text	
		# render the image text
		if self.buildLabel() == False:
			# well, something went wrong, lets create an empty gfx
			image=pygame.Surface((self.rect. w,self.rect.h))
			image.fill(self.background_colour)
	
	# code for the following routine taken from the Pygame code repository.
	# written by David Clark, amended by Chris Handy
	def buildLabel(self):
		"""Called to redraw the text on the label
		   Returns false (and displays message on console) if
		   the new text will not fit the image. (possible on low res)"""
		final_lines = []
		requested_lines = self.text.splitlines()
		# Create a series of lines that will fit on the provided rectangle
		for requested_line in requested_lines:
			if SGFX.gui.fonts[self.font].size(requested_line)[0] > self.rect.w:
				words = requested_line.split(' ')
				# if any of our words are too long to fit, return.
				for word in words:
					if SGFX.gui.fonts[self.font].size(word)[0] >= self.rect.w:
						print "Error: Word (", word, ") was too long in label"
						print "       Width was more than ", self.rect.w
						return(False)
				# Start a new line
				accumulated_line = ""
				for word in words:
					test_line = accumulated_line + word + " "
					# Build the line while the words fit.
					if SGFX.gui.fonts[self.font].size(test_line)[0] < self.rect.w:
						accumulated_line = test_line
					else:
						final_lines.append(accumulated_line)
						accumulated_line=word + " "
				final_lines.append(accumulated_line)
			else:
				final_lines.append(requested_line)
		# Let's try to write the text out on the surface.
		self.image=pygame.Surface((self.rect.w, self.rect.h))
		self.image.fill(self.background_colour)
		accumulated_height = 0
		for line in final_lines:
			if accumulated_height + SGFX.gui.fonts[self.font].size(line)[1] >= self.rect.h:
				print "Error: Text string too tall in label"
				print "       ah=", accumulated_height, " h=", self.rect.h
				return False
			if line != "":
				tempsurface = SGFX.gui.fonts[self.font].render(line, 1, self.text_colour)
				if self.justification == SPQR.LEFT_JUSTIFY:
					self.image.blit(tempsurface, (0, accumulated_height))
				elif self.justification == SPQR.CENTRE_HORIZ:
					self.image.blit(tempsurface, ((self.rect.w-tempsurface.get_width())/2, accumulated_height))
				elif self.justification == SPQR.RIGHT_JUSTIFY:
					self.image.blit(tempsurface, (self.rect.w - tempsurface.get_width(), accumulated_height))
				else:
					print "Error: Invalid justification value in label"
					return False
			accumulated_height += SGFX.gui.fonts[self.font].size(line)[1]
		return True

# possibly something even SIMPLER than the label - an image
class CImage(CWidget):
	"""Image class states and stores details for a simple image"""	
	def __init__(self, x, y, width, height, image):
		tmp_image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
		if image != None:
			tmp_image.blit(SGFX.gui.image(image), (0, 0))
		CWidget.__init__(self, pygame.Rect(x, y, width, height),
						 SPQR.WT_IMAGE, tmp_image.convert_alpha(), "CImage")

# and the simplest of all - a seperator bar
# regardless of width, they all have a height of 2
class CSeperator(CWidget):
	"""Seperator class states and stores details for a seperator"""
	def __init__(self, x, y, width):
		image = pygame.Surface((width, 2))
		# now blit the 2 colours to the image
		pygame.draw.line(image, SPQR.SEP_DARK, (0, 0), (width, 0), 1)
		pygame.draw.line(image, SPQR.SEP_LIGHT, (0, 1), (width, 1), 1)
		CWidget.__init__(self, pygame.Rect(x, y, width, 2), SPQR.WT_SEP,
						 image, "CSeperator")

# and now a button
class CButton(CWidget):
	"""Init routine to create a button widget. Call
		 x and y positions, and the text on the button. Returns a
		 button widget item for you to use.
		 Buttons are automagically highlighted when the mouse is over them"""
	def __init__(self, x, y, text):
		width = SGFX.gui.iWidth("button")
		height = SGFX.gui.iHeight("button")
		CWidget.__init__(self, pygame.Rect(x, y, width, height),
						 SPQR.WT_BUTTON, None, "CButton")
		# get the images
		self.image, self.pressed = self.drawButton(text)
		self.highlight = False
		
	# function to draw a standard button
	def drawButton(self, text):
		"""Just call with the text you want displayed, the
			 routine will draw the button for you. Returns
			 the image that has been drawn AND the highlight button"""
		# make a copy of the button bitmap and the highlight one
		foo = pygame.Surface((SGFX.gui.iWidth("button"), SGFX.gui.iHeight("button")))
		bar = pygame.Surface((SGFX.gui.iWidth("button"), SGFX.gui.iHeight("button")))
		area = pygame.Rect((0,0, foo.get_width(), foo.get_height()))
		foo.blit(SGFX.gui.image("button"), area)
		# render the text
		bar.blit(SGFX.gui.image("button_high"), area)
		txt = SGFX.gui.fonts[SPQR.FONT_VERA].render(text, True, SPQR.COL_BUTTON)
		# centre the text and overlay it
		x = (SGFX.gui.iWidth("button") - txt.get_width()) / 2
		y = (SGFX.gui.iHeight("button") - txt.get_height()) / 2
		area = pygame.Rect((x, y, bar.get_width(), bar.get_height()))
		foo.blit(txt, area)
		bar.blit(txt, area)
		return(foo, bar)

class CCheckBox(CWidget):
	"""Checkbox widget"""
	def __init__(self, x, y, initial, on = "check_yes", off = "check_no"):
		"""You need to pass the following parameters to the init() routine:
		   x,y - the offset into the window
		   initial - a boolean describing the start status of the widget"""
		self.on_image = SGFX.gui.image(on)
		self.off_image = SGFX.gui.image(off)
		if initial == True:
			image = self.on_image
		else:
			image = self.off_image
		CWidget.__init__(self, pygame.Rect(x, y, SGFX.gui.iWidth(on), SGFX.gui.iWidth(on)),
						 SPQR.WT_CHECK, image, "CCheckBox")
		# status is the inital boolean value
		self.status = initial
		# automatically add it's own click callback
		self.callbacks.mouse_lclk = self.clicked
		# sometimes you'll need to call another routine as well
		# as updating the graphic. Let's set that here as blank
		self.after_click = SPQR.null_routine
		self.after_click_status = False
	
	def clicked(self, handle, x, y):
		"""Called by the gui routine when clicked. Just
		   updates it's own gfx. In the parent window"""
		if self.status == True:
			self.status = False
			self.image = self.off_image
		else:
			self.status = True
			self.image = self.on_image
		# the image will have to be updated. Since we know that the widget
		# must be active and on display (since we just got a click), we can
		# just update the small bit of screen. Firstly, we get the window
		# co-ords and add the offset:
		xpos = self.parent.rect.x
		ypos = self.parent.rect.y
		xpos += self.rect.x
		ypos += self.rect.y
		# now we just have to blit that checkbox
		SGFX.gui.blitCheckbox(self, xpos, ypos)
		# do we need to do anything else?
		if self.after_click_status == True:
			# yes, do it
			self.after_click(handle, xpos, ypos)
		return True
		
	def addAfterClick(self, routine):
		"""Add routine to be called when left mouse clicked"""
		self.after_click_status = True
		self.after_click = routine
		return True

class CSlider(CWidget):
	"""Slider class states and stores details for a slider
	   Call with following parameters:
	   x/y pos of widget in window
	   width - width of entire widget, start - value on lhs of widget
	   end - value on rhs of widget, initial - initial value"""
	def __init__(self, x, y, width, start, end, initial):
		# width is at least what the gfx width is
		if width < SGFX.gui.iWidth("slider_knob"):
			width = SGFX.gui.iWidth("slider_knob")
		height = SGFX.gui.iHeight("slider_knob")
		CWidget.__init__(self, pygame.Rect(x, y, width, height),
						 SPQR.WT_SLIDER,pygame.Surface((width, height)),
						 "CSlider")
		# we have to check wether the slider knob is being pressed
		# or if it's some other part of the widget 
		self.knob_rect = pygame.Rect(0, 0, SGFX.gui.iWidth("slider_knob"), 
									 SGFX.gui.iHeight("slider_knob"))
		# just check the range is ok
		if start > end:
			start = end
		self.left_value = start
		self.right_value = end
		# also, check initial is ok, else we place it at one end
		if initial < start:
			initial = start
		elif initial > end:
			initial = end
		self.current_value = initial
		# remember that the width of the bar is width of widget -
		# width of slider, since the slider 'overhangs' the bar at
		# both ends of the bar (the left part on the left, and the same
		# on the right, by half the slider width)
		self.slide_bar_width = self.rect.w - SGFX.gui.iWidth("slider_knob")
		self.pixel_increment = (float)(end-start) / (float)(width)
		# mainly with a slider you'll let it do it's own thing
		self.callbacks.mouse_ldown = self.sliderMouseLDown
		# build the image
		self.drawSlider()
		# sometimes you'll want to call a function every time the
		# slider value is set... here are the data points
		self.update_function_valid = False
		self.update_function = SPQR.null_routine

	def drawSlider(self):
		"""Helper routine, draws the slider knob. Called by both
		   the initial routine and the slider callback function"""
		# There are 3 parts here: the slider itself, and then the
		# bars to the left (in blue) and to the right (in normal colors)
		self.image.fill(SPQR.BGUI_COL)
		# now draw the bars in
		spoint = (float)(self.current_value) / (float)(self.right_value - self.left_value)
		spoint = (int)(spoint * self.slide_bar_width)
		# make sure bars are in middle of slider
		yoff = (SGFX.gui.iHeight("slider_knob") / 2) - 2
		# also, allow for fact slide bar is not as long as the widget width
		# because the slider knob 'overhangs'. To make things easier, we just
		# adjust the middle point by half the slider knob width
		spoint += SGFX.gui.iWidth("slider_knob") / 2
		# blue bar is from left hand side up to the spoint
		pygame.draw.line(self.image, SPQR.SLIDER_BDARK, (0,yoff), (spoint, yoff), 1)
		pygame.draw.line(self.image, SPQR.SLIDER_BDARK,(0,yoff),	(0, yoff + 4), 1)
		pygame.draw.line(self.image, SPQR.SLIDER_BDARK,(0,yoff + 4), (spoint, yoff + 4), 1)
		pygame.draw.line(self.image, SPQR.SLIDER_LIGHT,(1,yoff + 1), (spoint, yoff + 1), 1)
		pygame.draw.line(self.image, SPQR.SLIDER_MEDIUM,(1,yoff + 2), (spoint, yoff + 2), 1)
		pygame.draw.line(self.image, SPQR.SLIDER_DARK,(1,yoff + 3), (spoint, yoff + 3), 1)
		# thats the left hand side taken care of, now the right...
		pygame.draw.line(self.image, SPQR.SLIDER_BLIGHT, (spoint, yoff),
			(self.rect.w - 1,yoff), 1)
		pygame.draw.line(self.image, SPQR.SLIDER_BLIGHT, (self.rect.w - 1, yoff), 
			(self.rect.w - 1,yoff + 4), 1)
		pygame.draw.line(self.image, SPQR.SLIDER_BLIGHT, (spoint, yoff + 4),
			(self.rect.w-1,yoff+4), 1)
		pygame.draw.line(self.image, SPQR.SLIDER_BMED1, (spoint, yoff + 1),
			(self.rect.w - 1, self.rect.y + 1), 1)
		pygame.draw.line(self.image, SPQR.SLIDER_BMED2, (spoint, yoff + 2),
			(self.rect.w - 1, self.rect.y + 2), 1)
		pygame.draw.line(self.image,SPQR.SLIDER_BMED2, (spoint,yoff + 3),
			(self.rect.w - 1, self.rect.y + 3), 1)
		# that was a lot of line drawing... now we just have to blit the
		# slider bar itself, in the right place
		xpos = spoint - (SGFX.gui.iWidth("slider_knob") / 2)
		self.image.blit(SGFX.gui.image("slider_knob"), (xpos, 0))
		# set knob_rect so we can catch events as well
		self.knob_rect.x = xpos
		# and that's it! updating is all up to you...
		return True
		
	def getSliderValue(self):
		"""Returns current setting of slider. Returns an int"""
		return((int)(self.current_value))

	def setUpdateFunction(self, code):
		"""Set callback function, called every time the value
		   of the slider is called. Must be a usual callback function"""
		self.update_function_valid = True
		self.update_function = code
		return True
		
	def killUpdateFunction(self, code):
		"""Call if you ever want to cancel the slider update function"""
		self.update_function_valid = False
		self.update_function = SPQR.null_routine
		return True

	def sliderMouseLDown(self, handle, xpos, ypos):
		"""Called when user clicks down with the mouse over a slider knob
			 Captures all input until user releases mouse button"""
		# first of all we check to see wether it was over the
		# slider knob or not...
		if xpos > self.knob_rect.x and xpos < (self.knob_rect.x + self.knob_rect.w):
			# ok, enter a loop where we catch all events until the left
			# mouse button is depressed
			# we only handle mouse moves though, everything else is ignored
			while True:
				event = pygame.event.poll()
				if event.type == MOUSEBUTTONUP and event.button == 1:
					# time to exit
					return True
				elif event.type == MOUSEMOTION:
					# we only need to look at x movement:
					xdiff = event.rel[0]	
					# any movement?
					if xdiff != 0:
						# extra bit of bling, as used by many wm's:
						# only move the slider in a given direction as long as the
						# mouse is past the middle of the slider knob in that
						# direction. I.e. to drag left, the mouse must be to the
						# left of the middle of the slider knob :-)
						move = True
						middle = self.parent.rect.x + self.rect.x + self.knob_rect.x
						middle += self.knob_rect.w / 2
						# work out what side we are moving and calculate:
						if xdiff < 0:
							# moving left?
							if event.pos[0] > middle:
								# don't do it
								move = False
						else:
							# must be moving right...
							if event.pos[0] < middle:
								move = False
						if move == True:
							# yes, so move the bar:
							old = self.current_value
							self.current_value += xdiff * self.pixel_increment
							# test for still in range:
							if self.current_value < self.left_value:
								self.current_value = self.left_value
							elif self.current_value > self.right_value:
								self.current_value = self.right_value
							# need to update?
							if old != self.current_value:
								# update the image
								self.drawSlider()
								x = self.parent.rect.x + self.rect.x
								y = self.parent.rect.y + self.rect.y
								SGFX.gui.blitSlider(x, y, self.rect.w, self.rect.h, self.image)
								# *finally*, we may have asked for an extra callback...
								if self.update_function_valid == True:
									# do the callback
									self.update_function(handle, xpos, ypos)
		# nothing might have happened, but be graceful about it anyway
		return True

class CScrollArea(CWidget):
	"""ScrollArea class holds details for a ScrollArea
	   Contains a graphical area that has a scroll bar on it's RHS
	   Call with x/y positon, width and height and image
	   *NOTE*: in the x size, you must allow for the fact that this widget
	   will add a scrollbar on the rhs of a given size!
	   height of widget *MUST BE* >61 pixels or funny gfx effects will occur
	   border area, if true, adds 1 pixel on the lhs and 2 on the y axis"""
	def __init__(self, x, y, width, height, image,border = True):
		CWidget.__init__(self, None, SPQR.WT_SCROLLAREA, None, "CScrollArea")
		self.border = border
		# get size of the area to display:
		vsize = image.get_height()
		# get offset size:
		width += SGFX.gui.iWidth("schan_mid")
		if self.border == True:
			height += 2
			width += 1
		self.rect = pygame.Rect(x, y, width, height)
		# next var holds where to blit the image from.
		# a value of 0 means 'start at the top'
		self.display_ypos = 0
		# we need to know how big the 'handle' is:
		w = SGFX.gui.iWidth("schan_mid")
		y = SGFX.gui.iHeight("scrollbar_top")
		# for the handle height, just make sure the math is ok:
		if vsize < height:
			vsize = height
		# now calculate the handle size. It will indicate how big
		# the unseen area is by being realtive in size to it
		# i.e. rect.h/height = height/vsize
		# allow for height correction
		height -= y * 2
		h = (int)(float((height * height) / (float)(vsize)))
		self.handle_rect = pygame.Rect(0, y, w, h)
		# add automatic callbacks
		self.callbacks.mouse_ldown = self.scrollareaMouseLDown
		self.callbacks.mouse_lclk = self.scrollareaMouseLClk
		# set an image up for later
		# this is the image that we want to actually show *inside*
		# the scrollarea box
		self.display_image = image
		# area_image is what finally goes to the screen, and
		# handle image is the handle gfx
		self.area_image, self.handle_image = self.buildScrollImage()
		self.image = pygame.Surface((self.rect.w, self.rect.h))
		self.updateScrollArea()
		# final set of per-calcs for later routines:
		self.lower_bound = self.handle_rect.y
		self.upper_bound = self.handle_rect.y + (height - self.handle_rect.h)
		# this is the number of pixels we move along for the handle
		self.handle_pixel_range = self.upper_bound - self.lower_bound
		# and this is the same for the displayed image:
		self.gfx_pixel_range = self.display_image.get_height() - self.rect.h
		# possible border to allow for
		if self.border == True:
			self.gfx_pixel_range -= 2
		self.hanpix_ratio = (float)((float)(self.gfx_pixel_range) / (float)(self.handle_pixel_range))
		# the amount we move the bar by on an arrow up/ arrow down click
		self.arrow_click_move = 1
		# following used to store the parent window of the
		# widget... False if there is no valid parent
		self.parent = False
		self.describe = "CScrollArea"
		
	def buildScrollImage(self):
		"""Helper routine to build the base image that
		   is displayed on screen. update_image() should be
		   called to normally, this just sets everything up"""
		# the first thing to do is get a base surface
		piccy = pygame.Surface((self.rect.w, self.rect.h))
		# really, this is quite simple but a lot of legwork
		# start by filling in the base of the scrollbar:
		piccy.fill(SPQR.SCROLL_MIDDLE)
		pygame.draw.line(piccy, SPQR.SCROLL_BORDER, (0, 0), (0, self.rect.h))
		pygame.draw.line(piccy, SPQR.SCROLL_BORDER, (self.rect.w, 0),
			(self.rect.w, self.rect.h))
		# now blit in the arrows at the top and bottom:
		xpos = self.rect.w - SGFX.gui.iWidth("scrollbar_top")
		piccy.blit(SGFX.gui.image("scrollbar_top"), (xpos, 0))
		piccy.blit(SGFX.gui.image("scrollbar_bottom"),
			(xpos, (self.rect.h - SGFX.gui.iHeight("scrollbar_bottom"))))
		# now draw the handlebar for the widget
		# start by making a new surface
		handle_gfx = pygame.Surface((self.handle_rect.w, self.handle_rect.h))
		# fill the area in first
		pixels = self.handle_rect.h
		ypos = 0
		fill = SGFX.gui.iHeight("schand_bulk")
		while pixels > 0:
			if pixels < SGFX.gui.iHeight("schand_bulk"):
				handle_gfx.blit(SGFX.gui.image("schand_bulk"), (0, ypos))
				pixels = 0
			else:
				handle_gfx.blit(SGFX.gui.image("schand_bulk"), (0, ypos))
				ypos += fill
				pixels -= fill
		# do the top and bottom:
		handle_gfx.blit(SGFX.gui.image("schan_top"), (0, 0))
		handle_gfx.blit(SGFX.gui.image("schan_bot"), (0, self.handle_rect.h - 2))
		# work out middle of area and blit that
		middle = (self.handle_rect.h-SGFX.gui.iHeight("schan_mid")) / 2
		handle_gfx.blit(SGFX.gui.image("schan_mid"), (0, middle))
		# draw the border here if we have to
		if self.border == True:
			pygame.draw.line(piccy, SPQR.SCROLL_BORDER,
				(0, 0),(0, self.rect.h))
			pygame.draw.line(piccy, SPQR.SCROLL_BORDER,
				(0, 0),(self.rect.w - self.handle_rect.w, 0))
			pygame.draw.line(piccy, SPQR.SCROLL_BORDER,
				(0, self.rect.h - 1), (self.rect.w - self.handle_rect.w, self.rect.h - 1))
			# set handle rect position:
			self.handle_rect.x = self.display_image.get_width() + 1
		else:
			self.handle_rect.x = self.display_image.get_width()
		self.handle_rect.y = SGFX.gui.iHeight("scrollbar_top")
		return(piccy, handle_gfx)

	def updateScrollArea(self):
		"""Routine to build final image that is displayed on screen"""
		# blit the base image:
		self.image.blit(self.area_image, (0, 0))
		# pre-calculate some stuff:
		if self.border == True:
			x = 1
			y = 1
			h = self.rect.h - 2
		else:
			x = 0
			y = 0
			h = self.rect.h
		# width is always width of the original gfx
		w = self.display_image.get_width()
		# then the slider knob:
		self.image.blit(self.handle_image,
			(self.handle_rect.x, self.handle_rect.y))
		# now blit it
		self.image.blit(self.display_image,
			(x, y), (0, self.display_ypos, w, h))
		# blitting to screen is left to you -
		# mainly because the parent attributes (i.e. the window details)
		# may not have actually been defined at this point in time
		return True

	def scrollareaMouseLDown(self, handle, xpos, ypos):
		"""Called when user clicks down with the mouse over a scroll knob
			 Captures all input until user releases mouse button"""
		# first of all we check to see wether it was over the
		# slider knob or not...
		if self.handle_rect.collidepoint(xpos, ypos) == True:
			# ok, enter a loop where we catch all events until the left
			# mouse button is depressed
			# we only handle mouse moves though, everything else is ignored
			while True:
				event = pygame.event.poll()
				if event.type == MOUSEBUTTONUP and event.button == 1:
					# time to exit
					return True
				elif event.type == MOUSEMOTION:
					# now we actually move the bar
					self.moveScrollHandle(event.rel[1])
		# nothing happened, but be graceful about it anyway
		return True

	def scrollareaMouseLClk(self,handle,xpos,ypos):
		"""For when the user clicks on the thing itself. For the
		   moment, just checks the arrows at the top and bottom"""
		# firstly, check we are in the right area
		if xpos < self.handle_rect.x:
			# nothing to do
			return True
		# at top or bottom... or nowhere?
		if ypos < self.lower_bound:
			# it was a click on the up arrow, so do it
			self.moveScrollHandle(-self.arrow_click_move)
			return True
		elif(ypos>(self.upper_bound+self.handle_rect.h)):
			self.moveScrollHandle(self.arrow_click_move)
			return True
		# could be a click on the blank area
		# don't forget, it's not possible for xpos/ypos to be out
		# of bounds on the widget in question (saves some work)
		if self.handle_rect.collidepoint(xpos, ypos) == True:
			# ignore it if we clicked the handle itself
			return True
		# # TODO very simple, we try and move the middle of the handle
		# widget to where we clicked, or as close as possible
		return True
			
	def moveScrollHandle(self, ydiff):
		"""Move and update the handle graphic. Parameter
		   passed tells us by how many pixels we should
		   update move the widget by"""
		# all we really have to do is calculate a new
		# self.display_ypos and a new self.handle_rect.y
		# luckily, we pre-calculated some stuff earlier
		# firstly though, are we in bounds?
		self.handle_rect.y += ydiff
		if self.handle_rect.y > self.upper_bound or self.handle_rect.y < self.lower_bound:
				# nothing to do, correct and return
				self.handle_rect.y -= ydiff
				return True
		# otherwise, do some easy stuff:
		self.display_ypos = (int)((self.handle_rect.y - self.lower_bound) * self.hanpix_ratio)
		# make the new image and draw it to the screen
		self.updateScrollArea()
		x = self.parent.rect.x + self.rect.x
		y = self.parent.rect.y + self.rect.y
		SGFX.gui.blitScrollarea(x, y, self.rect.w, self.rect.h, self.image)
		return True

	def updateScrollImage(self, image):
		"""Call when you wish to change the scroll image display,
		   but change nothing else. Updates the screen for you"""
		self.display_image = image
		self.updateScrollArea()
		x = self.parent.rect.x + self.rect.x
		y = self.parent.rect.y + self.rect.y
		SGFX.gui.blitScrollarea(x, y, self.rect.w, self.rect.h, self.image)
		return True

class CItemList(CWidget):
	"""Call the init routine with the following parameters:
	   first a list of lists, defined in the following way:
	   The first list lets the routine know wether each element of
	   the rest of the lists is text (True) or an image (False)
	   The second list gives the text headers for the columns
	   Of the rest of the lists, each seperate one contains all the
	   elements needed to draw 1 column of the ScrollArea list
	   Then comes an array of routines to sort the data
	   Next comes a list of id numbers, used when sorting the data
	   Finally, the last param tells you what height you would like
	   the element to take up (including the header height)"""
	def __init__(self, x, y, elements, sorts, id_values, total_height):
		# let's do the easy stuff first - this will be a long routine
		CWidget.__init__(self, pygame.Rect(x, y, 0, 0),
						 SPQR.WT_ITEMLIST, None, "CItemList")
		self.data = []

		# ok, let's now do everything else
		# the most important thing we need to do is figure out the
		# spacing for the gfx images (both the header and the ScrollArea)
		# The most basic system we use is as follows:
		# If the row item is text, then it's size is SPACER+Textsize+SPACER
		# if it's an image, then the size is SPACER+ImageSize+SPACER
		# hey! thats the same - that makes things a bit easier...
		# the extra complication is in the size of the header
		# each headline piece of text must be at least of the size
		# HALFSPCR+text_size+(2*(SPACER))
		
		# firstly, let's grab the list that tells us what the types are
		item_type = elements.pop(0)
		# and the text headers
		text_headers = elements.pop(0)
		# how many rows here? Needed later...
		total_rows = len(elements[0])
		# now we need to go down every column and calculate the maximum size
		column_size = []
		# index for counting item types
		it = 0
		for column in elements:
			# now we have a list that contains each item for the column
			csize = 0
			# what sort of thing is it?
			ctype = item_type[it]
			it += 1
			if ctype == False:
				# easy, it's an image
				for item in column:
					if item.get_width() > csize:
						csize = item.get_width()
			else:
				# must be text
				for item in column:
					tsize = SGFX.gui.fonts[SPQR.FONT_VERA].size(item)
					if tsize[0] > csize:
						csize = tsize[0]
			# now we know the size, just expand it:
			csize += 2 * SPQR.SPACER
			column_size.append(csize)
			
		# now we have the right widths for all of the items
		# let's do a similar thing for the widths of the text headers
		tsize = []
		for text in text_headers:
			width = SGFX.gui.fonts[SPQR.FONT_VERA_SM].size(text)[0]
			# allow some spacing
			width += SPQR.HALFSPCR + (2 * SPQR.SPACER)
			tsize.append(width)
		# now construct a final width list
		column_width = []
		for a in tsize:
			b = column_size.pop(0)
			if a > b:
				column_width.append(a)
			else:
				column_width.append(b)
		# first xpos is always 0
		column_width.insert(0, 0)
		
		# we also need to check out the heights of the rows
		# since each row is the same size, then we only need to
		# look at any one particular row - in this case the first one
		row_height = 0
		it = 0
		theight = 0
		# we have (2*SPACER) as vertical spacing
		spacing = 2 * SPQR.SPACER
		for column in item_type:
			if column == False:
				# image, easy:
				h = elements[it][0].get_height() + spacing
				if h > theight:
					theight = h
			else:
				# text, a bit more complex
				h = SGFX.gui.fonts[SPQR.FONT_VERA].size("Aq")[1] + spacing
				if h > theight:
					theight = h
			it += 1

		# now we can work out the height and width of the ScrollArea
		height = theight * len(elements[0])
		width = 0
		# we should save the column size as the first thing in the window
		# data storage area as well
		l = []
		for i in column_width:
			width += i
			l.append(width)
		self.data.append(l)
		
		# now we know theight and the width, we can use it to work out what
		# gradiant fill we use - generally the smallest one larger than theight
		index = 0
		size = False
		# oh for a fast gradiant fill :-o
		for i in SPQR.GRADBAR_SIZES:
			if theight < i:
				# found an image of the right size
				size = True
				break
			else:
				# try the next one
				index += 1
		# create the base image
		row_image = pygame.Surface((width,theight),SRCALPHA)
		# did we find one small enough?
		if size == False:
			# we'll have to create a false image
			row_image.fill(SPQR.BGUI_COL)
		else:
			# we at least found the right size
			yoffset = (SPQR.GRADBAR_SIZES[index] - theight) / 2
			# blit across until complete
			xsize_blit = width
			xpos = 0
			while xsize_blit > 0:
				row_image.blit(SGFX.gui.image(SPQR.GRADBAR_NAMES[index]),
					(xpos, 0), (0, yoffset, SPQR.GRADBAR_WIDTH, SPQR.GRADBAR_SIZES[index]))
				xpos += SPQR.GRADBAR_WIDTH
				xsize_blit -= SPQR.GRADBAR_WIDTH
		# finally, draw in the bottom line
		pygame.draw.line(row_image, SPQR.SEP_DARK, (0, theight - 1), (width, theight - 1), 1)
		
		# Finally!! We can now build up the ScrollArea image
		# we'll do this a column at a time, since that's the way the
		# data is given to us in the lists
		# firstly, get the basic image
		sc_image = pygame.Surface((width, height), SRCALPHA)
		sc_image.fill(SPQR.BGUI_COL)
		# fill in the base row images
		count = 0
		ypos = 0
		while count < total_rows:
			sc_image.blit(row_image, (0, ypos))
			ypos += row_image.get_height()
			count += 1

		# set index for column width
		it = 0
		# all items are offset by SPACER. Since the arithmatic is
		# acummulative, we set that offset here
		base_x = SPQR.SPACER
		# now go down each column
		for column in elements:
			# point to next column
			base_x += column_width[it]
			it += 1
			# get the base image:
			ctype = item_type.pop(0)
			if ctype == False:
				# it's already images, easy stuff...
				base_y = 0
				for i in column:
					yoff = (theight - i.get_height()) / 2
					# blit the image
					sc_image.blit(i,(base_x, base_y+yoff))
					base_y += theight
			else:
				# it's text, so make the image first
				base_y = 0
				for i in column:
					timg = SGFX.gui.fonts[SPQR.FONT_VERA].render(i, True, SPQR.COL_BLACK)
					yoff = (theight - timg.get_height()) / 2
					# blit the text
					sc_image.blit(timg, (base_x, base_y + yoff))
					base_y += theight
		
		# because we may have to re-order the list, then we need
		# to store some copy of it. We do this by saving each row
		# as a seperate graphic:
		rows = []
		ypos = 0
		while ypos < sc_image.get_height():
			img = pygame.Surface((width, theight))
			img.blit(sc_image, (0, 0), (0, ypos, width, theight))
			rows.append((id_values.pop(0), img))
			ypos += theight
		# save that info for another time...
		self.row_height = theight
		self.display_width = width
		
		# Now *all* that's left is to fraw the main header, fully define
		# the ScrollArea, and then tidy up a few loose ends
		# Let's draw the main header first
		# start by getting the tallest text item and then adding
		# SPACER to it:
		hheight = 0
		for i in text_headers:
			t = SGFX.gui.fonts[SPQR.FONT_VERA_SM].size(i)
			if t[1] > hheight:
				hheight = t[1]
		hheight += SPQR.SPACER
		# create the base image
		header_img = pygame.Surface((width, hheight), SRCALPHA)
		header_img.fill(SPQR.BGUI_COL)
		# draw in some of the funky lines
		pygame.draw.line(header_img, SPQR.SEP_DARK, (0, 0), (width - 1, 0), 1)
		pygame.draw.line(header_img, SPQR.SEP_DARK, (0, hheight-1), (width - 1, hheight - 1), 1)
		pygame.draw.line(header_img, SPQR.SEP_LIGHT, (0, 1), (width - 1, 1), 1)
		pygame.draw.line(header_img, SPQR.SEP_LIGHT, (0, 1), (0,hheight - 1), 1)
		# now we can go along each text header item
		# all the items are offset by HALFSPCR
		base_x = SPQR.HALFSPCR
		hxsize = 0
		
		for txt in text_headers:
			# point to next column
			new_x = column_width.pop(0)
			base_x += new_x
			timg = SGFX.gui.fonts[SPQR.FONT_VERA_SM].render(txt, True, SPQR.COL_BLACK)
			base_y = (hheight - timg.get_height()) / 2
			header_img.blit(timg, (base_x, base_y))
			# we also need to draw those funky lines
			hxsize += new_x
			if hxsize != 0:
				# i.e. not the first time we meet...
				pygame.draw.line(header_img, SPQR.SEP_LIGHT,
					(hxsize - 1, SPQR.HALFSPCR), (hxsize - 1, hheight - SPQR.HALFSPCR), 1)
				pygame.draw.line(header_img, SPQR.SEP_DARK,
					(hxsize - 2, SPQR.HALFSPCR), (hxsize - 2, hheight - SPQR.HALFSPCR), 1)
		# there will be one more set of lines to draw
		hxsize += column_width.pop(0)
		pygame.draw.line(header_img, SPQR.SEP_LIGHT,
			(hxsize - 1, SPQR.HALFSPCR), (hxsize - 1, hheight - SPQR.HALFSPCR), 1)
		pygame.draw.line(header_img, SPQR.SEP_DARK,
			(hxsize - 2, SPQR.HALFSPCR), (hxsize - 2, hheight - SPQR.HALFSPCR), 1)
		# the actual rectangle size for the ItemList is merely the
		# size of the image we have just drawn
		self.rect.w = width
		self.rect.h = hheight
		self.image = header_img
		# now we generate the ScrollArea
		sc_h = total_height - hheight
		# was there an error there?
		if sc_h < SPQR.SCAREA_MINH:
			print "Error: Size for ItemList too small"
			# do it, but nasty things may happen
			# probably the widget display will look nasty
			sc_h = sc_image.get_height()/2
		# we always have a border on these scroll areas
		y += hheight
		self.listarea = CScrollArea(x, y, width, sc_h, sc_image, True)
		
		# we need to put in the callbacks.
		self.callbacks.mouse_lclk = self.itemsHeaderClick
		# define the status of the colum headers, i.e what direction
		# the arrows start out at
		# False is pointing UP, True is pointing DOWN
		head = []
		for i in self.data[0]:
			head.append(True)
		self.data.append(head)
		# then add the list of id/image collections
		self.data.append(rows)
		# save the sort routines and then we are done
		self.data.append(sorts)

	def itemsHeaderClick(self,handle,xpos,ypos):
		"""Routine called when ItemList top header amount is clicked"""
		# which column of data?	
		# column will actually be off by 1 (since it's *always* >0)
		# so let's make this easy by lowering the start value
		column =- 1
		for i in self.data[0]:
			if xpos < i:
				break
			column += 1

		# just a test for now
		# now we know that we can draw in the arrow
		# we also have to delete the other arrows
		# what arrow graphic do we use?
		if self.data[1][column] == True:
			arrow = SGFX.gui.image("arrown_down")
			# invert for next time
			self.data[1][column] = False
		else:
			# similar code
			arrow = SGFX.gui.image("arrow_up")
			self.data[1][column] = True
		
		# create another image to blit over the other arrows
		erase = pygame.Surface((arrow.get_width(), arrow.get_height()))
		erase.fill(SPQR.BGUI_COL)
		# erase every image
		xoff = (self.parent.rect.x + self.rect.x) - (SPQR.SPACER + SPQR.HALFSPCR)	
		yoff = self.parent.rect.y + self.rect.y
		# centre the arrow
		yoff += (self.rect.h - arrow.get_height()) / 2
		# erase any previous ones (just delete all)
		for i in self.data[0]:
			# don't do the first one
			if i != 0:
				SGFX.gui.screen.blit(erase, (xoff + i, yoff))
		# now draw the arrow
		# since the offset is negative, we need to blit to the next
		# column along
		SGFX.gui.screen.blit(arrow, (xoff + self.data[0][column+1], yoff))
		
		# now we can re-build the scrollarea image:
		img = pygame.Surface((self.display_width,
			self.row_height * len(self.data[2])))

		# now sort the list
		# we can actually only sort the id numbers, so get that list:
		nums = []
		for i in self.data[2]:
			nums.append(i[0])		
		# sort *that* list:
		nums.sort(self.data[3][column])
		# if column data is True, reverse the list	
		if self.data[1][column] == True:
			nums.reverse()
		
		# now build up the new image
		ypos = 0
		for foo in nums:
			# get the referrring id value:
			for bar in self.data[2]:
				if foo == bar[0]:
					img.blit(bar[1], (0, ypos))
					ypos += self.row_height
					break
		# update the screen (don't forget to reset xpos accuratly -
		# thus all that spacer stuff)
		pygame.display.update((xoff + SPQR.SPACER + SPQR.HALFSPCR, yoff, self.rect.w, self.rect.h))
		# and the new scrollist image		
		self.listarea.updateScrollImage(img)
		return True

# an optionmenu is a widget that let's you choose an item from a drop-down
# menu. The current option is shown in the box.
# width of the widget is dependant on the text length of the options
# height is completly dependant on the graphic widget

class COptionMenu(CWidget):
	"""OptionMenu widget lets user choose from a drop-down menu.
	   Call with the x and y position, and then a
	   list of the options, in text format"""
	   # TODO: If you move the optmenu, you must manually set the
	   # drop_rect co-ords as well
	def __init__(self,x,y,options):
		CWidget.__init__(self, None, SPQR.WT_OPTMENU, None, "COptionMenu")
		# just a simple check - there has to be at least 1 option!
		if len(options) < 1:
			if SPQR.DEBUG_MODE == True:
				print "Error: Asked for OptionMenu with no options"
				# enter the error options
				options = ["Error", "No","Options", "Given"]

		# first we must build the image as seen when the widget is unused
		# calculate width
		width = 0
		for i in options:
			tlen = SGFX.gui.fonts[SPQR.FONT_VERA].size(i)[0]
			if tlen > width:
				width = tlen
		# add a spacer either side
		width += 2 * SPQR.SPACER
		# then allow for the graphics on either side
		width += SGFX.gui.iWidth("optionmenu_rhand")
		# save info for later
		xpos = width
		width += SGFX.gui.iWidth("optionmenu_rhand")
		# we can now work out the rect size
		height = SGFX.gui.iHeight("optionmenu_rhand")
		self.rect = pygame.Rect(x, y, width, height)
		# we can now start to build the base image
		self.image = pygame.Surface((width, height), SRCALPHA)
		# build up the base image
		self.image.fill(SPQR.COL_WHITE)
		self.image.blit(SGFX.gui.image("optionmenu_lhand"), (0, 0))
		self.image.blit(SGFX.gui.image("optionmenu_rhand"), (xpos, 0))
		# now we draw the lines at the top and bottom
		xstart = SGFX.gui.iWidth("optionmenu_lhand")
		pygame.draw.line(self.image, SPQR.BGUI_HIGH, (xstart, 0), (xpos, 0), 1)
		pygame.draw.line(self.image,SPQR.COLG_RED, (xstart, 1), (xpos, 1), 1)
		pygame.draw.line(self.image,SPQR.COLG_RHIGH, (xstart, 2), (xpos, 2), 1)
		height -= 1
		pygame.draw.line(self.image, SPQR.BGUI_HIGH, (xstart, height), (xpos, height), 1)
		height -= 1
		pygame.draw.line(self.image, SPQR.COLG_RED, (xstart, height), (xpos, height), 1)
		height -= 1
		pygame.draw.line(self.image, SPQR.COLG_RHIGH, (xstart, height), (xpos, height), 1)
		# finally, we need to blit the text
		txtx = xstart + SPQR.SPACER
		txtg = SGFX.gui.fonts[SPQR.FONT_VERA].render(options[0], True, SPQR.COL_BLACK)
		txty = (self.image.get_height() - txtg.get_height()) / 2
		self.image.blit(txtg, (txtx, txty))
		
		# well, thats it for *that* image, but we still need to get an image
		# set up for when we drop the menu down
		# the image size should be widget_height-HALFSPCR for each row,
		# and then length should be the same as the widget minus the arrow
		row_height = self.image.get_height() - SPQR.HALFSPCR
		ysize = len(options) * row_height
		ysize += SPQR.HALFSPCR + SPQR.QTRSPCR
		xsize = self.image.get_width()
		self.drop_image = pygame.Surface((xsize, ysize))
		self.drop_image.fill(SPQR.OPTM_BDARK)
		# draw nice borders
		pygame.draw.rect(self.drop_image, SPQR.BGUI_COL, (1, 1, xsize - 2, ysize - 2), 0)
		pygame.draw.rect(self.drop_image, SPQR.OPTM_BDARK, (2, 2, xsize - 4, ysize - 4), 0)
		pygame.draw.rect(self.drop_image, SPQR.COL_WHITE, (3, 3, xsize - 6, ysize - 6), 0)
		# now we need to render the text names:
		ypos = SPQR.HALFSPCR+SPQR.QTRSPCR + 1
		xpos = SPQR.SPACER+SGFX.gui.iWidth("optionmenu_lhand")
		# we'll build the rects for menu checks as well
		self.menu_highlights = []
		ymstart = self.rect.y + self.image.get_height() + SPQR.QTRSPCR + 3
		for txt in options:
			rend = SGFX.gui.fonts[SPQR.FONT_VERA].render(txt, True, SPQR.COL_BLACK)
			self.drop_image.blit(rend, (xpos, ypos))
			ypos += row_height
			self.menu_highlights.append([(pygame.Rect(self.rect.x + 3,
				ymstart, xsize - 6, row_height)), txt])
			ymstart += row_height

		self.drop_rect = pygame.Rect(self.rect.x,
			self.rect.y + self.image.get_height() + SPQR.QTRSPCR, xsize, ysize)
		# we'll need to update it on the first loop:
		self.drop_rect_update = False
		# we'll just set up a rect which we use to check the mouse against
		self.mouse_check = pygame.Rect(xpos + xstart, 0, width - xpos, height)
		# and also a menu highlight image
		# the 32 is to force a 32 bit surface for alpha blitting
		self.himage = pygame.Surface((xsize - 6, row_height), 0, 32)
		# then set the alpha value
		self.himage.set_alpha(SPQR.MENU_ALPHA)
		# flood fill it
		self.himage.fill(SPQR.MENU_HLCOL)
		
		# and then the basic callback
		self.callbacks.mouse_lclk = self.optionsSelect
		# before we finish off, we need somewhere to store the current option
		self.option = options[0]

	def setPositionX(self, x):
		"""Used when you change the position of the optmenu"""
		self.rect.x = x
		self.drop_rect.x = x
		for i in self.menu_highlights:
			i[0].x = x + 3

	def setPositionY(self, y):
		"""Used when you change the position of the optmenu"""
		self.drop_rect.y = y + self.image.get_height() + SPQR.QTRSPCR
		for i in self.menu_highlights:
			i[0].y += y - self.rect.y
		self.rect.y = y

	def optionsSelect(self,handle,xpos,ypos):
		"""Called when the OptionMenu is clicked
			 Returns False if option did not change"""
		if self.mouse_check.collidepoint(xpos, ypos) == False:
			# nothing to do, since arrow was not clicked
			return False
		# first time we do this, update the rectangles:
		if self.drop_rect_update == False:
			self.drop_rect.x += self.parent.rect.x
			self.drop_rect.y += self.parent.rect.y
			# annoying but true: it also won't have updated the x/y postions
			# to account for the window borders....!
			if self.parent.border_offset == True:
				self.drop_rect.x += SPQR.WINSZ_SIDE
				self.drop_rect.y += SPQR.WINSZ_TOP
			# now the highlight rects:
			for item in self.menu_highlights:
				item[0].x += self.parent.rect.x
				item[0].y += self.parent.rect.y
				if self.parent.border_offset == True:
					item[0].x += SPQR.WINSZ_SIDE
					item[0].y += SPQR.WINSZ_TOP
			self.drop_rect_update = True
		
		# got the click: firstly, update the screen with a new dirty
		# rect (the previously drawn drop-down graphic)
		SGFX.gui.addDirtyRect(self.drop_image, self.drop_rect)
		opt_highlight = None
		# loop through events until user clicks inside the new rect
		img_old = pygame.Surface((self.himage.get_width(), self.himage.get_height()))
		while True:
			event = pygame.event.poll()
			if event.type == MOUSEMOTION:
				over = False
				# over a highlight rect?
				for items in self.menu_highlights:
					rect = items[0]
					if rect.collidepoint(event.pos[0], event.pos[1]):
						# yes
						over = True
						if opt_highlight != rect:
							# last given highlight was not this one,
							# so it is at least unique
							if opt_highlight != None:
								# *something* was highlighted last time,
								# so put back the original
								SGFX.gui.screen.blit(img_old, opt_highlight)
								pygame.display.update(opt_highlight)
							# save the old screen part
							img_old.blit(pygame.display.get_surface(), (0, 0), rect)
							# draw in the new highlight
							SGFX.gui.screen.blit(self.himage, rect)
							pygame.display.update(rect)
							# save position for next time
							opt_highlight = rect
						break
				if over == False and opt_highlight != None:
					# left highlight area
					SGFX.gui.screen.blit(img_old, opt_highlight)
					pygame.display.update(opt_highlight)
					opt_highlight = None
			elif event.type == MOUSEBUTTONUP and event.button == 1:
				# click, but inside the rect?
				# go through all the options:
				for items in self.menu_highlights:
					if items[0].collidepoint(event.pos[0], event.pos[1]):
						# time to exit - but store the new option
						self.option = items[1]
						
						# hey! *all* we have to do is update the original gfx now!
						# firstly render some text
						newtxt = SGFX.gui.fonts[SPQR.FONT_VERA].render(self.option, True, SPQR.COL_BLACK)
						# now erase old text
						oldtxt = pygame.Rect(0, 3, 0, self.image.get_height() - 6)
						oldtxt.x = SGFX.gui.iWidth("optionmenu_lhand") + SPQR.SPACER
						oldtxt.w = self.rect.w - SGFX.gui.iWidth("optionmenu_lhand")
						oldtxt.w -= SGFX.gui.iWidth("optionmenu_rhand") + SPQR.SPACER
						pygame.draw.rect(self.image, SPQR.COL_WHITE, oldtxt)
						# blit text into image
						xpos = SGFX.gui.iWidth("optionmenu_lhand") + SPQR.SPACER
						ypos = (self.rect.h-newtxt.get_height()) / 2
						self.image.blit(newtxt, (xpos, ypos))
						# erase menu drop
						SGFX.gui.deleteTopDirty()
						# force update of window portion
						xpos = self.parent.rect.x + self.rect.x
						ypos = self.parent.rect.y + self.rect.y
						SGFX.gui.screen.blit(self.image, (xpos, ypos))
						new_update = pygame.Rect(xpos, ypos, self.rect.w, self.rect.h)
						pygame.display.update(new_update)
						# you can now return safely - it's been updated!
						return True
				# no click on an option, we assume nothing was wanted
				SGFX.gui.deleteTopDirty()
				# but no option change
				return False
		# shouldn't ever get here, really
		SGFX.gui.deleteTopDirty()
		return False

# helper routines to build stuff follow
def buildLabel(text, font = SPQR.FONT_VERA):
	"""Helper function to build a label given just the text.
	   Uses standard font, which is FONT_VERA. Returns the new label"""
	# get the size
	w, h = SGFX.gui.fonts[font].size(text)
	# TODO: annoyingly enough, despite asking what size the font is, if
	# I render to an image of that size, it doesn't work. So we have to add 1
	# any answers to this one, or have I missed something?
	return(CLabel(0, 0, w, h+1, text, font))

def buildImage(image):
	"""Helper function to build a image given just the image
	   title. Pass index of image. Returns the new widget"""
	w = SGFX.gui.iWidth(image)
	h = SGFX.gui.iHeight(image)
	# create and return
	return(CImage(0, 0, w, h, image))

def buildImageAlpha(image):
	"""As buildImage, but blits alpha image over gui color"""
	w = SGFX.gui.iWidth(image)
	h = SGFX.gui.iHeight(image)
	# create out initial image and make it the right color
	piccy = pygame.Surface((w, h))
	piccy.fill(SPQR.BGUI_COL)
	# now blit over the real image
	piccy.blit(SGFX.gui.image(image), (0, 0))
	# and thats almost it
	return(buildUniqueImage(piccy))

def buildUniqueImage(picture):
	"""As buildImage, but this time you pass your own image"""
	new=CImage(0, 0, 0, 0, None)
	# now amend that image
	new.rect.w = picture.get_width()
	new.rect.h = picture.get_height()
	new.image = picture
	return new

