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

import sys, pygame, re, os
from pygame.locals import *

import spqr_defines as SPQR
import spqr_window as SWINDOW
import spqr_widgets as SWIDGET
import spqr_keys as SKEY
import spqr_events as SEVENT
import spqr_console as SCONSOLE
import spqr_sound as SSFX
import spqr_data as SDATA

# class that holds the dirty rectangle updates
class CDirtyRect(object):
	def __init__(self, pic, rec):
		self.image = pic
		self.rect = rec

# now of course we need a class to hold all of the windows, i.e. the basic GUI class
# this class also inits the gfx display
# call with the x and y resolution of the screen, and a pointer to the data
class CGFXEngine(object):
	def __init__(self):
		self.info_widget = None
		self.map_widget = None

	def mainInit(self, width, height, fullscreen, load_screen= True):
		"""Long, boring routine that initiates the gui"""
		pygame.init()
		# ok, now init the basic screen
		# done now so image.convert works when we load the images
		if fullscreen == True:
			self.screen = pygame.display.set_mode((width, height),
				HWSURFACE|FULLSCREEN|DOUBLEBUF)
		else:
			self.screen = pygame.display.set_mode((width, height), HWSURFACE|DOUBLEBUF)
		self.images = {}
		if load_screen == True:
			self.displayLoadingScreen(width, height)
		# next up is to load in some images into the gfx array
		self.images["map"] = pygame.image.load("../gfx/map/map.jpg").convert()
		# add a back buffer map render.. this will become the map that we render
		foo = pygame.Surface((self.iWidth("map"), self.iHeight("map")))
		self.images["buffer"] = foo
		# we will need a copy of the board without the units rendered, for movement, flashing
		# etc.. It is not stored with the other images, but I'll declare it here anyway. Start
		# it with a dummy image:
		self.map_render = pygame.Surface((self.iWidth("map"),  self.iHeight("map")))

		self.windows = []
		# the font that the messagebox will use:
		self.msg_font = SPQR.FONT_VERA
		# highlight over button at the moment?
		self.over_button = False
		# interrupt for timers?
		self.timer = True
		# item to check double-click against
		self.dclick_handle = None
		# store a simple console class
		self.cfuncs = SCONSOLE.CConsole()
		# console currently being displayed?
		self.console = False
		pygame.display.set_caption("SPQR "+SPQR.VERSION)
		
		# get all filenames:
		files = []
		for i in SPQR.GRAPHICS_F:
			files.extend(["../gfx/" + i +"/" + name for name in os.listdir("../gfx/" + i + "/")])
		# if it's a png, strip the name and insert it into a new hash
		for i in files:
			if i[-4:] == ".png":
				self.images[i.split("/")[-1][:-4]] = pygame.image.load(i).convert_alpha()

		# set up the fonts
		pygame.font.init()
		self.fonts = []
		self.fonts.append(pygame.font.Font("../gfx/Vera.ttf", SPQR.FONT_STD))
		self.fonts.append(pygame.font.Font("../gfx/Vera.ttf", SPQR.FONT_SMALL))
		self.fonts.append(pygame.font.Font("../gfx/Vera.ttf", SPQR.FONT_LARGE))

		# update buffer images
		self.updateMapData()
		self.renderPixelMap()
		# we have 2 blit areas for the flashing unit:
		self.flash_draw = pygame.Surface((0, 0))
		self.flash_erase = pygame.Surface((0, 0))
		self.flash_old = pygame.Surface((0, 0))
		# and the destination rect:
		self.flash_rect = pygame.Rect(0, 0, 0, 0)
		# index of troop we are flashing
		self.flash_highlight = None
		self.current_highlight = None
		# modal windows use a dirty rect list to update, here it is
		self.dirty = []
		# enable keyboard reponses
		self.keyboard = SKEY.CKeyboard()
		# start the first song here, as well
		SSFX.sound.startNextSong()
		# some basic variables that SPQR uses regularly
		# where to start the map blit from when blasting it to the screen
		foo = (SPQR.SCREEN_HEIGHT - self.iHeight("win_tl")) + 1
		# define the 'from' rectangle
		self.map_screen = pygame.Rect((0, 0, SPQR.SCREEN_WIDTH, foo))
		# and the target rectangle for the blit:
		self.map_rect = pygame.Rect((0, (self.iHeight("win_tl"))-1,
			SPQR.SCREEN_WIDTH, foo))
		# area that the map covers on the screen:
		self.map_area = pygame.Rect((0, self.iHeight("win_tl"),
			SPQR.SCREEN_WIDTH, (SPQR.SCREEN_HEIGHT-self.iHeight("win_tl"))))
		# centre the map for the start blit
		self.map_screen.x = SPQR.ROME_XPOS-(self.map_rect.w/2)
		self.map_screen.y = SPQR.ROME_YPOS-(self.map_rect.h/2)
		# store a rect of the maximum map limits we can scroll to
		# obviously 0/0 for top left corner - this just denotes bottom right corner
		self.map_max_x = self.iWidth("map") - SPQR.SCREEN_WIDTH
		self.map_max_y = self.iHeight("map") - self.map_rect.h
		# damn silly variable for the mini map rect blit
		self.y_offset_mini_map = SPQR.BBOX_HEIGHT + self.iHeight("win_tl")
		# a temp image for some uses
		self.temp_image = pygame.Surface((0, 0))
		# variables so callbacks and external code can communicate
		self.callback_temp = SPQR.BUTTON_FAIL
		# a flag to see if a menu is waiting for input
		self.menu_active = False
		# set up the mini map
		self.blit_rect = pygame.Rect(0, 0, 0, 0)
		# calculate width and height of square to blit
		self.width_ratio = float(self.iWidth("map")) / float(self.iWidth("small_map") - 2)
		self.height_ratio = float(self.iHeight("map")) / float(self.iHeight("small_map") - 2)
		# LESSON: in python, you need to force the floats sometimes
		self.blit_rect.w = int(float(self.map_rect.w) / self.width_ratio)
		self.blit_rect.h = int(float(self.map_rect.h) / self.height_ratio)
		# pre-calculate some stuff
		self.mini_x_offset = SPQR.SCREEN_WIDTH - (self.iWidth("small_map") + 7)
		self.mini_y_offset = SPQR.SCREEN_HEIGHT - (self.iHeight("small_map") + 17)
		self.mini_source = pygame.Rect(0, 0, self.iWidth("small_map"), self.iHeight("small_map"))
		self.mini_dest = pygame.Rect(self.mini_x_offset-1, self.mini_y_offset-1, 0, 0)
		# load other data required by mapboard
		self.updateMiniMap()
		self.flash_on = False
		# list to hold possible moves being shown
		self.map_click_moves = []

	def displayLoadingScreen(self, width, height):
		"""Displays the loading screen"""
		load_screen = pygame.image.load("../gfx/load_screen.png").convert()
		self.screen.fill(SPQR.COL_BLACK)
		xpos = (width - load_screen.get_width()) / 2
		ypos = (height - load_screen.get_height()) / 2
		self.screen.blit(load_screen, (xpos, ypos))
		pygame.display.update()

	def iWidth(self, name):
		return self.images[name].get_width()
	
	def iHeight(self, name):
		return self.images[name].get_height()
	
	def image(self, name):
		return self.images[name]

	def updateMapData(self):
		"""The size of the regions is known by the size of the images
		   This function updates the game data after the images have
		   been loaded. Also we give the masks as well"""
		for i in SDATA.iterRegions():
			image = self.image(i.image)
			i.rect.width = image.get_width()
			i.rect.height = image.get_height()
		i = []
		for key in self.images.iterkeys():
			if key[-5:] == "_mask":
				i.append([key, self.image(key)])
		SDATA.updateRegionMasks(i)

	def renderRegions(self):
		"""Draw all regions to the back buffer"""
		for i in SDATA.iterRegions():
			# render the map
			region = pygame.Surface(self.image(i.image).get_size()).convert()
			region.fill(i.colour)
			mask = self.image(i.image).copy()
			mask.blit(region, (0, 0), None, pygame.BLEND_ADD)
			self.image("buffer").blit(mask, (i.rect.x, i.rect.y))

	def renderSingleRegion(self, region):
		"""Update the regions cities and unit gfx to the back buffer"""
		# first we erase the old unit + city gfx
		i = SDATA.getRegion(region)
		pos = SDATA.getCityPosition(i)
		self.image("buffer").blit(self.image("map"), pos,
								  pygame.Rect(pos[0], pos[1], SPQR.UNIT_WIDTH, SPQR.UNIT_HEIGHT))
		self.image("buffer").blit(self.image("map"), i.text_rect, i.text_rect)
		# then we repair the border
		area = pygame.Surface(self.image(i.image).get_size()).convert()
		area.fill(i.colour)
		mask = self.image(i.image).copy()
		mask.blit(area, (0, 0), None, pygame.BLEND_ADD)
		self.image("buffer").blit(mask, (i.rect.x, i.rect.y))
		# either a city is there or not: if it is, then the text has already
		# been blitted and we just need to blit the city, otherwise do nothing
		if i.city != None:
			self.renderSingleCity(i)

	def renderCities(self):
		"""Draw all cities, and their names, on the board"""
		for i in SDATA.iterRegions():
			if i.city != None:
				self.renderSingleCity(i)

	def renderSingleCity(self, region):
		self.fonts[SPQR.FONT_VERA].set_bold(True)
		name = region.city.name
		x, y = SDATA.getCityPosition(region)
		# draw the city
		self.image("buffer").blit(self.image(region.city.image), (x, y))
		# draw the text	
		text = self.fonts[SPQR.FONT_VERA].render(name, True, SPQR.COL_WHITE)
		shadow = self.fonts[SPQR.FONT_VERA].render(name, True, SPQR.COL_BLACK)
		border = pygame.Surface((text.get_width() + 2, text.get_height() + 2))
		border.fill(SPQR.COL_BLACK)
		border.set_alpha(127)
		x -= int((text.get_width() - SPQR.UNIT_WIDTH) / 2)
		y += SPQR.UNIT_HEIGHT + 1
		self.image("buffer").blit(border,(x -1, y -1))
		self.image("buffer").blit(shadow, (x + 1, y + 1))
		self.image("buffer").blit(text, (x, y))
		# save the text area rect for later
		region.text_rect = pygame.Rect(x - 1, y - 1, text.get_width() + 2, text.get_height() + 2)
		self.fonts[SPQR.FONT_VERA].set_bold(False)

	def renderUnits(self):
		for i in SDATA.iterUnits():
			self.image("buffer").blit(self.image(i.image), SDATA.getUnitPosition(i.name))

	# now a function to add a window
	# it has it's own function because it has to return the index number
	# of the created window
	def addWindow(self, window):
		"""Call to add a window to the gui window list. It always goes
		   on the top of the window pile, and thus if modal traps all
		   user input. Returns the index number of the window in the list,
		   so you can amend the window afterwards"""
		self.windows.append(window)
		# since we always append to the list, the index is always
		# the size of the array minus 1 (since we start the array at 0)
		index = len(self.windows) - 1
		return index
	
	def addDirtyRect(self, new, rectangle):
		"""Routine adds dirty rectangle and details to the current list"""
		# get the old image from the screen
		img = pygame.Surface((rectangle.w, rectangle.h))
		img.blit(pygame.display.get_surface(), (0, 0), rectangle)
		# now blit the new image
		self.screen.blit(new, (rectangle.x, rectangle.y))
		pygame.display.update(rectangle)
		self.dirty.append(CDirtyRect(img, rectangle))
		return True

	def deleteTopDirty(self):
		"""Routine deletes current top dirty window, and draws
		   back the old image"""
		# actually got something to do?
		if len(self.dirty) > 0:
			# yes, update the screen first
			self.screen.blit(self.dirty[-1].image, self.dirty[-1].rect)
			pygame.display.update(self.dirty[-1].rect)
			self.dirty.pop()
		else:
			return False
		return True
	
	# TODO: Sort out wether we need to really update the gui here
	# generally used to kill the active window
	def killIndexedWindow(self, index):
		"""Remove window. Call with index number of window. Redraws
		   gui as well"""
		del self.windows[index]
		return True
	
	def killTopWindow(self):
		"""Remove top window. Redraws gui as well"""
		self.windows.pop()
		#self.updateGUI()
		return True

	def updateGUI(self):
		"""Redraws entire screen. Should avoid calling this really and use
		   dirty rectangles technique. Having said that, it's not actually
		   that slow either"""
		# if we have anything in the dirty list, we merely have to update that area
		# with the new image etc...
		if len(self.dirty) > 0:
			self.screen.blit(self.dirty[-1].image, self.dirty[-1].rect)
			pygame.display.update(self.dirty[-1].rect)
			return True
		# before doing anything else, blit the map
		self.screen.blit(self.image("buffer"), self.map_rect, self.map_screen)
		index = 0
		# we have to do the window testing in reverse to the way we blit, as the first
		# object blitted is on the 'bottom' of the screen, and we have to test from the top
		for foo in self.windows:
			if foo.display == True:
				self.screen.blit(foo.image, (foo.rect.x, foo.rect.y))
			for bar in foo.items:
				if bar.visible == True:
					# is this the mini-map?
					if bar.describe  ==  "mini-map":
						# just update it
						self.updateMiniMap()
						x1 = foo.rect.x+bar.rect.x
						y1 = foo.rect.y+bar.rect.y
						self.screen.blit(bar.image, (x1, y1))
					else:
						x1 = foo.rect.x+bar.rect.x
						y1 = foo.rect.y+bar.rect.y
						self.screen.blit(bar.image, (x1, y1))
			index += 1
		pygame.display.flip()
		return True
	
	def updateOverlayWindow(self):
		"""Draw the window with the widget overlays only"""
		# TODO: a better way of finding the window
		offset = self.windows[-1].rect
		for i in self.windows[-1].items:
			if i.visible == True:
				self.screen.blit(i.image, (i.rect.x+offset.x, i.rect.y+offset.y))

	def updateUnitWidget(self):
		print "update me"

	# this one merely updates the map, rather than blit all those
	# gui things as well
	def updateMap(self):
		"""Updates (i.e. redraws) map to main screen"""
		self.screen.blit(self.image("buffer"), self.map_rect, self.map_screen)
		self.updateOverlayWindow()
		pygame.display.flip()
		# doing this *always* redraws the units as well, so make sure that
		# the next flash unit action will be to erase the unit
		self.unitFlashOn()

	# and this one merely blits the cursor in the mini map
	def updateMiniMap(self):
		"""Redraws mini-map, usually called after any changes to
		   the map on the main screen"""
		# work out what the corrent co-ords are for the mini-map cursor
		xpos = int(self.map_screen.x / self.width_ratio)
		ypos = int(self.map_screen.y / self.height_ratio)
		self.blit_rect.x = xpos + 1
		self.blit_rect.y = ypos + 1
		if self.map_widget != None:
			self.map_widget.image = self.images["small_map"].copy()
			self.screen.blit(self.images["small_map"], self.mini_dest, self.mini_source)
			pygame.draw.rect(self.map_widget.image, (0, 0, 0), self.blit_rect, 1)
		return True
	
	def updateUnits(self):
		"""Unit is to be called when a unit is placed or
		   removed from the map. Always returns True"""
		# blit the map_render original across first
		self.image("buffer").blit(self.map_render, (0, 0))
		self.updateMap()
		return True

	def centreMap(self, xpos, ypos):
		"""Centre map to the given co-ords, or at least as close as you we
		   get. DOES NOT update the screen for you"""
		# firstly, rectify the co-ords so that they will be in the
		# centre of the screen
		xpos -= self.map_screen.w/2
		ypos -= self.map_screen.h/2
		if xpos < 0:
			xpos = 0
		elif xpos > (self.iWidth("map") - self.map_screen.w):
			xpos = self.iWidth("map") - self.map_sceen.w
		# and then check y size
		if ypos < 0:
			ypos = 0
		elif ypos > (self.iHeight("map") - self.map_screen.h):
			ypos = self.iWidth("map") - self.map_screen.h
		# set new co-ords
		self.map_screen.x = xpos
		self.map_screen.y = ypos
		return True

	def normalizeScrollArea(self):
		"""Checks co-ords after scrolling the map to make sure
		   they are not out of range. Resets them if needed"""
		if self.map_screen.x < 0:
			self.map_screen.x = 0
		elif self.map_screen.x > self.map_max_x:
			self.map_screen.x = self.map_max_x
		if self.map_screen.y < 0:
			self.map_screen.y = 0
		elif self.map_screen.y > self.map_max_y:
			self.map_screen.y = self.map_max_y
		return True
	
	def handleKeypress(self, event):
		"""Handle a keypress"""
		# does it match anything?
		foo, bar, handle = self.keyboard.getKeyFunction(event.key, event.mod)
		if foo == True:
			# set win_index to TOP of current window list -2 to enable
			# killing of current window from keyboard function
			self.win_index = len(self.windows)-2
			# now call the function
			if handle == None:
				bar(0, -1, -1)
			else:
				bar(handle, -1, -1)
			return True
		else:
			return False
	
	# routine captures what event we got, then passes that message along
	# to the testing routine (i.e. this code only checks if a MOUSE event
	# happened, the later function checks if we got a GUI event)
	def checkInputs(self):
		"""checkInputs() is called on a loop whilst the game is waiting
		   for user input (i.e. most of the time). It doens't actually do
		   anything with the input except pass the event along to somewhere
		   else, so think of it more like a sorting office"""
		event = pygame.event.wait()
		# lets start with the simple case: handling keypress values
		if event.type == KEYDOWN:
			return self.handleKeypress(event)
		# now handle animation requests from the timer
		if event.type == pygame.USEREVENT and self.timer == True:
			self.flashUnit()
			return False
		action = SPQR.MOUSE_NONE
		# catch other stuff here, before we process the mouse
		# perhaps it was just that the song ended?
		if event.type == SPQR.EVENT_SONGEND:
			# just start the next song
			SSFX.sound.startNextSong()
			return True
		# was it the end of a double-click check?
		if event.type == SPQR.EVENT_DC_END:
			# kill timer and handle data
			pygame.time.set_timer(SPQR.EVENT_DC_END, 0)
			self.dclick_handle = None
			return True
		# worst of all, could be an instant quit!
		if event.type == pygame.QUIT:
			SEVENT.quitSpqr(None, -1, -1)
			return True
		# cancel current menu if we got mouse button down
		if event.type == MOUSEBUTTONDOWN and self.menu_active == True:
			self.menu_active = False
			return False
		if event.type != NOEVENT:
			# if it's a rmb down, then possibly exit
			if event.type == MOUSEBUTTONDOWN and event.button == 3:
				if SPQR.RMOUSE_END == True:
					sys.exit(False)
			# was it left mouse button up?
			elif event.type == MOUSEBUTTONUP and event.button == 1:
				x, y = pygame.mouse.get_pos()
				action = SPQR.MOUSE_LCLK
				self.testMouse(x, y, action)
			# some things (like sliders) respond to a mousedown event
			elif event.type == MOUSEBUTTONDOWN and event.button == 1:
				x, y = pygame.mouse.get_pos()
				action = SPQR.MOUSE_LDOWN
				self.testMouse(x, y, action)
			# was it a middle click?
			elif event.type == MOUSEBUTTONDOWN and event.button == 2:
				# pan the map, unless we have a modal window:
				if self.windows[len(self.windows) - 1].modal == False:
					# must be over main map for panning to work
					x, y = pygame.mouse.get_pos()
					if self.map_area.collidepoint(x, y) == True:
						self.panMap()
			else:
				# have we moved?
				if event.type == MOUSEMOTION:
					x, y = pygame.mouse.get_pos()
					action = SPQR.MOUSE_OVER
					if self.testMouse(x, y, action) == False:
						self.checkButtonHighlights(x, y)
			if action == SPQR.MOUSE_NONE:
				return False
			else:	
				return True

	def checkButtonHighlights(self, x, y):	
		"""Check all of the buttons inside the top-layer window to see
		   if any need to be highlighted. Returns True if anything
		   on the screen needed to be updated"""
		for bar in self.windows[-1].items:
			if bar.active == True and bar.wtype == SPQR.WT_BUTTON:
				xoff = x-self.windows[-1].rect.x
				yoff = y-self.windows[-1].rect.y
				if bar.rect.collidepoint(xoff, yoff) == True:
					# don't forget to test here if it's actually visible or not... ;-)
					if bar.visible == False:
						return False
					# already highlighted?
					if bar.highlight == True:
						return False
					else:
						# update a dirty rect
						bar.highlight = True
						dest = pygame.Rect(bar.rect.x+self.windows[-1].rect.x,
							bar.rect.y+self.windows[-1].rect.y, bar.rect.w, bar.rect.h)
						self.screen.blit(bar.pressed, dest)
						pygame.display.update(dest)
						return True
				if bar.highlight == True and bar.wtype == SPQR.WT_BUTTON:
					# an old highlight needs rubbing out
					bar.highlight = False
					dest = pygame.Rect(bar.rect.x+self.windows[-1].rect.x,
						bar.rect.y+self.windows[-1].rect.y, bar.rect.w, bar.rect.h)
					self.screen.blit(bar.image, dest)
					pygame.display.update(dest)
					return True
		return False

	# use this function to test the mouse against all objects
	def testMouse(self, x, y, action):
		"""testMouse returns False if nothing got called
		   Otherwise it handles checking the action against all
		   of the widgets, menus and windows that are active"""
		quit = False
		# normally I'd use for foo in self.windows, but we need to traverse
		# this list in the opposite direction to the way we render them
		self.win_index = len(self.windows)-1
		while(self.win_index>-1):
			# define a new variable that we can use later to kill the current window off
			foo = self.windows[self.win_index]			
			self.win_index = self.win_index-1
			if quit == True:
				return False
			# if this is a modal window, then stop after processing:
			quit = foo.modal
			# is the mouse pointer inside the window, or is there any window at all?
			if foo.rect.collidepoint(x, y) == True or foo.display == False:
				# check all of the points inside the window
				for bar in foo.items:
					if bar.active == True:
						x_off = x-foo.rect.x
						y_off = y-foo.rect.y
						if bar.rect.collidepoint(x_off, y_off) == True:
							# get offset into widget
							x_widget = x_off-bar.rect.x
							y_widget = y_off-bar.rect.y
							# now test to see if we need to make a call
							if action == SPQR.MOUSE_OVER and bar.callbacks.mouse_over != SPQR.mouse_over_std:
								# widget asked for callback on mouse over
								bar.callbacks.mouse_over(bar, x_widget, y_widget)
								return True
							elif action == SPQR.MOUSE_LCLK and bar.callbacks.mouse_lclk != SPQR.mouse_lclk_std:
								# widget asked for callback on mouse left click								
								bar.callbacks.mouse_lclk(bar, x_widget, y_widget)
								return True
							elif action == SPQR.MOUSE_LCLK and \
									 bar.callbacks.mouse_dclick != SPQR.mouse_dclick_std and \
									 self.dclick_handle != bar:
								# widget wants a double-click: this was the first one, so we need
								# to keep an eye out for the next click
								self.dclick_handle = bar
								# set our timer
								pygame.time.set_timer(SPQR.EVENT_DC_END, SPQR.DCLICK_SPEED)
								return False
							elif action == SPQR.MOUSE_LCLK and \
									bar.callbacks.mouse_dclick != SPQR.mouse_dclick_std and \
									self.dclick_handle == bar:	 
								# it's a real bona-fida double-click
								# firstly clear all double-click data, then run the code
								pygame.time.set_timer(SPQR.EVENT_DC_END, 0)
								self.dclick_handle = None
								bar.callbacks.mouse_dclick(bar, x_widget, y_widget)
								return True
							elif action == SPQR.MOUSE_DCLICK:
								# obviously we got a double-click where it wasn't needed
								pygame.time.set_timer(SPQR.EVENT_DC_END, 0)
								self.dclick_handle = None
								return False
							elif action == SPQR.MOUSE_LDOWN and bar.callbacks.mouse_ldown != SPQR.mouse_ldown_std:
								# widget asked for callback on mouse left down
								bar.callbacks.mouse_ldown(bar, x_widget, y_widget)
								return True
							elif action == SPQR.MOUSE_RCLK and bar.callbacks.mouse_rclk != mouse_rclk_std:
								# whilst still debugging, I've left this one out
								print "Do a mouse right click on ", bar.describe
								return True
							# and then exit
							return False
		# finally, if NO message was met, then check to see if the event was
		# a click on the main map
		if action == SPQR.MOUSE_LCLK:
			if self.map_area.collidepoint(x, y) == True:
				# handle it elsewhere
				self.mapClick(x, y)
				return True
		return False

	def screenToMapCoords(self, x, y):
		"""Convert screen click co-ords to map co-ords"""
		x += self.map_screen.x
		y -= self.iHeight("titlebar")
		y += self.map_screen.y
		return x, y

	def mapClick(self, x, y):
		"""Updates information in bottom box, dependant on users click
		   over the map. Call with x and y, being the click on the map
		   in screen co-ords"""
		x, y = self.screenToMapCoords(x, y)
		# waiting for move input? then deal with it
		if self.map_click_moves != []:
			self.moveUnit(SDATA.regionClicked(x, y))
			return True
		# first we check units, then cities, then regions
		unit = SDATA.unitClicked(x, y)
		if unit != False:
			if unit.moves_left > 0:
				self.highlightMoves(unit.name)
		else:
			self.unitFlashAndOff()
		name = SDATA.regionClicked(x, y)
		if name != False:
			self.renderRegionInfoBox(name)
			self.renderImageUnits(name)
			self.updateGUI()
		else:
			# clear box if no info
			if self.info_widget.visible == True:
				self.info_widget.visible = False
				self.updateGUI()
		return True

	def moveUnit(self, region):
		"""Move the unit (or not)"""
		def cancelMoves(): 
			self.map_click_moves = []
			self.renderPixelMap()
			self.updateMap()
		# there are 2 choices: player clicked no region,
		# or region not on list: reset map and move on
		# played clicked region on list: move unit
		if region in self.map_click_moves:
			# get current unit
			unit = self.flash_highlight
			# delete image from current map
			old_region = SDATA.getUnitRegion(unit)
			SDATA.moveUnit(unit, region)
			cancelMoves()
			self.unitFlashAndOff()
			self.flushFlash()
			self.renderSingleRegion(old_region)
			# finally, we should click the map on the new region city
			# now highlight the new unit if it has moves left, or focus on the city
			if SDATA.getUnitMoves(unit) != 0:
				self.focusOnUnit(unit)
			else:
				cx, cy = SDATA.getCityPosition(SDATA.getRegion(region))
				cx += 5
				cy += 5
				self.mapClick(cx, cy)
				self.updateGUI()
			return True
		# cancel everything
		cancelMoves()
		self.unitFlashAndOff()
		return False

	def highlightMoves(self, unit):
		"""Redraw buffer with highlighted areas and animate the given unit"""
		# is it navy or army?
		if SDATA.unitNaval(unit):
			moves = SDATA.getNavalMoves(SDATA.getUnitRegion(unit))
		else:
			# get possible 1 move locations
			moves = SDATA.getNeighbors(SDATA.getUnitRegion(unit))
		# now highlight all of those regions
		for i in moves:
			name = SDATA.getRegion(i)
			region = pygame.Surface(self.image(name.image + "_mask").get_size())
			region.fill(SPQR.COL_WHITE)
			mask = self.image(name.image + "_mask").copy()
			mask.blit(region, (0, 0), None, pygame.BLEND_ADD)
			self.image("buffer").blit(mask, (name.rect.x, name.rect.y))
			# blit the city, if it exists
			self.renderSingleCity(name)
		# animate the unit
		self.flash_highlight = unit
		self.unitFlashOn()
		self.map_click_moves = moves
		self.updateMap()

	def focusOnUnit(self, unit):
		"""Given a units name, centre the map on this unit and activate it"""
		x, y = SDATA.getUnitPosition(unit)
		x += int(SPQR.UNIT_WIDTH / 2)
		y += int(SPQR.UNIT_HEIGHT / 2)
		# we need to clean the map up
		self.map_click_moves = []
		self.renderPixelMap()
		self.centreMap(x, y)
		# only highlight if we have some moves
		if SDATA.getUnitMoves(unit) > 0:
			self.flash_old = None
			self.highlightMoves(unit)

	# this is the main game loop. There are 2 varients of it, one which keeps
	# looping forever, and a solo version which runs only once
	def mainLoop(self):
		"""CGFXEngine.mainLoop() - call with nothing"""
		while True:
			pygame.event.pump()
			# ok main loop: after setting everything up, just keep calling self.checkInputs()
			self.checkInputs()

	def mainLoopSolo(self):
		"""As mainLoop, but only for 1 event"""
		pygame.event.pump()
		self.checkInputs()

	# this is the function that allows you to pan the the map with the 
	# middle mouse button
	def panMap(self):
		"""CGFXEngine.panMap() - call with nothing
			 Returns nothing, allows user to pan map with middle click"""
		# before doing anything else, turn off unit flashing
		self.unitFlashAndOff()
		xpos, ypos = pygame.mouse.get_rel()
		while True:
			event = pygame.event.poll()
			if event.type == MOUSEMOTION:
				# cancel current action if we got mouse button up
				a, b, c = pygame.mouse.get_pressed()
				if b != 1:
					# mouse has been de-pressed
					# turn unit animation back on
					self.unitFlashOn()
					return
				# grab relative grabs
				xpos, ypos = pygame.mouse.get_rel()
				# update the map thus
				self.map_screen.x -= xpos
				self.map_screen.y -= ypos
				# check the scroll areas...
				self.normalizeScrollArea()
				# and then finally draw it!
				self.updateMiniMap()
				self.updateMap()

	# routine draws the map we actually render
	def renderPixelMap(self):
		"""Routine generates map we actually display to the screen,
		   having rendered cities, units, roads etc.
		   The current ordering of the blits, from first to last, is:
		   Back map, Regions""" 
		# blit the original map across first
		self.image("buffer").blit(self.image("map"), (0, 0))
		# start by blitting the regions and units
		self.renderRegions()
		self.renderCities()
		# save this image as it is for now without the images for using
		# as the backdrop for all unit animations
		self.map_render.blit(self.image("buffer"), (0, 0))
		self.renderUnits()
		return True

	def blitCheckbox(self, widget, xpos, ypos):
		"""Renders a checkbox at the given location
		   Very simple, just used to isolate gfx drawing out
		   of the checkbox widget code"""
		# we need to blit the buffer copy first
		self.screen.blit(self.image("buffer"),
						 (xpos + self.map_screen.x,
						  ypos + self.map_screen.y + self.iHeight("win_tl"),
						  widget.rect.w, widget.rect.h))
		self.screen.blit(widget.image, (xpos, ypos, 0, 0))		
		pygame.display.update((xpos, ypos, widget.rect.w, widget.rect.h))
		return True
		
	def blitSlider(self, xpos, ypos, width, height, image):
		"""Renders the slider bar at given position"""
		# just blit image and update
		self.screen.blit(image, (xpos, ypos, 0, 0))
		pygame.display.update((xpos, ypos, width, height))
		return True
		
	def blitScrollarea(self, xpos, ypos, width, height, image):
		"""Renders the scrollarea at given position"""
		# very similar to blitSlider
		self.screen.blit(image, (xpos, ypos, 0, 0))
		pygame.display.update((xpos, ypos, width, height))
		return True

	# here follows the timer routines. They mainly deal with unit
	# flashing, animation etc...
	def flashUnit(self):
		"""Flashes current highlighted unit. Returns True if the screen
		   was updated, false otherwise"""
		# this is quite a long, boring, routine so I'll explain all here:
		# we create here 3 images. One is the sprite ON, and the other OFF, for
		# animation purposes. To do this, we grab the square area that we are
		# going to animate from map_render, which doesn't contain any units:
		# This is the erase render
		# then we copy that image and add our focus unit: this is the other frame.
		# third image is used to store the original status of the back map in this
		# area so that we can restore the original state later
		# TODO: split this huge routine up
		# do we need to flash at all?
		if self.flash_highlight == None:
			return False
		# Here's the logic to this: we need 2 images: the first has the area WITH 
		# the unit gfx and, the second has just the area
		# We just blit between the 2. Firstly we need
		# to see if the unit highlight has changed at all
		if self.flash_highlight != self.current_highlight:
			self.current_highlight = self.flash_highlight
			# we now have an new flashing unit. Firstly, remove the old blit area
			if self.flash_old != None:
				self.image("buffer").blit(self.flash_old, self.flash_rect)	
			# now we generate the part we use to erase the area.
			self.flash_erase = pygame.Surface((SPQR.UNIT_WIDTH, SPQR.UNIT_HEIGHT), SRCALPHA)
			# ok, we can blit the rendered map over
			# get the x,y co-ords we need
			x, y = SDATA.getUnitPosition(self.current_highlight)
			# so we can calculate the blit rectangle
			self.flash_rect = pygame.Rect(x, y, SPQR.UNIT_WIDTH, SPQR.UNIT_HEIGHT)
			# use this to copy are from map_render:
			self.flash_erase.blit(self.map_render, (0, 0), self.flash_rect)
			# also make a copy of the area to blit back to the back map:
			self.flash_old = pygame.Surface((SPQR.UNIT_WIDTH, SPQR.UNIT_HEIGHT))
			self.flash_old.blit(self.image("buffer"), (0, 0), self.flash_rect)
			# now we can construct the draw image. Get a copy of the last image
			self.flash_draw = pygame.Surface((SPQR.UNIT_WIDTH, SPQR.UNIT_HEIGHT), SRCALPHA)
			self.flash_draw.blit(self.flash_erase, (0, 0))
			# then draw the unit over it
			index = SDATA.getUnitImage(self.current_highlight)
			self.flash_draw.blit(self.image(index), (0, 0))
			# add to both images the moves left
			moves = "moves" + str(SDATA.getUnitMoves(self.current_highlight))
			self.flash_erase.blit(self.image(moves), (0, 0))
			self.flash_draw.blit(self.image(moves), (0, 0))
			
			# make sure that we draw the erase part of the image first
			self.flash_on = True
			# screen map probably needs updating, do it here
			self.updateMap()
		
		# thats it, we have a copy of the draw, erase and clean-up images
		# since both areas are square and use the same size image, we can
		# start by working out the blit area. Let's see if the images overlap:
		dest = pygame.Rect(self.flash_rect.x, self.flash_rect.y, 
			self.flash_rect.w, self.flash_rect.h)
		# correct for on-screen co-ords
		dest.x -= self.map_screen.x
		dest.y -= self.map_screen.y - SPQR.WINSZ_TOP + 1
		dest = dest.clip(self.map_rect)
		if dest.h != 0:
			# yes, we still have work to do
			area = pygame.Rect(0, 0, dest.w, dest.h)
			# correct for top and left of screen
			if dest.x == 0:
				area.x = SPQR.UNIT_WIDTH - dest.w
			if dest.y == SPQR.WINSZ_TOP - 1:
				area.y = SPQR.UNIT_HEIGHT - dest.h
			# now blit the right rectangle:
			if self.flash_on == True:
				self.screen.blit(self.flash_erase, dest, area)
				# be prepared for next time...
				self.flash_on = False
			else:
				self.screen.blit(self.flash_draw, dest, area)
				self.flash_on = True
			# update the screen and we're done
			pygame.display.update(dest)
			return True
		# the rectangles didn't overlap, but get ready for next round:
		if self.flash_on == True:
			self.flash_on = False
		else:
			self.flash_on = True
		return False

	def clearFlash(self):
		"""Routine clears any gfx stuff on the map due to flashing"""
		# really simple code at the moment
		self.image("buffer").blit(self.flash_old, self.flash_rect)
		self.updateMap()

	def unitFlashAndOff(self):
		"""Call to turn off unit flashing. Also draws unit back to screen
		   if it is currently not on"""
		# if the timer is not currently active, don't do a thing
		if self.timer == False:
			return
		# is unit currently on screen?
		if self.flash_on == False:
			# no, so update it
			self.image("buffer").blit(self.flash_draw, self.flash_rect)
			self.updateMap()
			self.flash_on = True
			self.flash_old = None
		# turn flashing off
		self.timer = False

	def flushFlash(self):
		"""Forces a redraw next time we flash, but DON'T draw old map image onto buffer"""
		self.flash_old = None
		self.current_highlight = None
		self.flash_highlight = None

	def unitFlashOn(self):
		"""Call to turn unit flashing back on. Returns False if this
		   didn't happen for some reason"""
		# already on?
		if self.timer == True:
			return True
		# make sure first call is show the erase frame
		self.flash_on = True
		self.timer = True
		return True

	def renderImageUnits(self, region):
		"""Update the unit info boxes with their data"""
		# are there any units at all?
		# trash current data
		for i in self.unit_widgets:
			i.visible = False
			i.active = False
		units = SDATA.getRegionUnits(region)
		if units == []:
			return False
		# start by putting the widgets in the right place
		xpos = (len(units) * (SPQR.UNIT_WIDTH + SPQR.SPACER)) - SPQR.SPACER
		xpos = int((SPQR.SCREEN_WIDTH - xpos) / 2)
		ypos = SPQR.BBOX_HEIGHT - (SPQR.UNIT_HEIGHT + (SPQR.SPACER * 2))
		for i in range(len(units)):
			image = pygame.Surface((SPQR.UNIT_WIDTH, SPQR.UNIT_HEIGHT),
								   pygame.SRCALPHA, 32).convert_alpha()
			image.blit(self.image("unit_background"), (0, 0))
			image.blit(self.image(units[i].image), (0, 0))
			self.unit_widgets[i].image = image
			self.unit_widgets[i].visible = True
			self.unit_widgets[i].active = True
			self.unit_widgets[i].rect.x = xpos
			self.unit_widgets[i].data = units[i].name
			xpos += SPQR.UNIT_WIDTH + SPQR.SPACER
			self.unit_widgets[i].rect.y = ypos
		return True

	def renderRegionInfoBox(self, region):
		"""Render the image for the widget that shows the region info"""
		info = pygame.Surface(self.image("small_map").get_size()).convert_alpha()
		info.fill(SPQR.BGUI_COL)
		pygame.draw.rect(info, SPQR.COL_BLACK,
						 pygame.Rect(0, 0, info.get_width(), info.get_height()), 1)
		info.blit(self.image("mapicon_back"), 
				  (info.get_width() - (self.iWidth("mapicon_back") + 4), 4))
		icon_name = region + "_icon"
		# draw the right region icon
		if self.iWidth(icon_name) == SPQR.REGION_ICON_SIZE:
			xpos = info.get_width() - (SPQR.REGION_ICON_SIZE + 6)
			ypos = int((SPQR.REGION_ICON_SIZE - self.iHeight(icon_name)) / 2) + 4
		else:
			xpos = info.get_width() - (SPQR.REGION_ICON_SIZE + 6) + \
				   int((SPQR.REGION_ICON_SIZE - self.iWidth(icon_name)) / 2)
			ypos = 4
		info.blit(self.image(icon_name), (xpos, ypos))
		# render the region name, as well
		region = region.replace("_", " ").title()
		text = self.fonts[SPQR.FONT_VERA_SM].render(region, True, SPQR.COL_BLACK)
		info.blit(text, (int((info.get_width() - text.get_width()) / 2),
						(info.get_height() - (text.get_height() + 2))))
		self.info_widget.image = info
		self.info_widget.visible = True

# TODO: Below code should be moved into spqr_widgets.py, and messageboc made into a class

	def fitText(self, text, x, y, fnt):
		"""Call with the text, the x and y size of the area
		   to test against, and the font. Returns false if
		   it couldn't be done, otherwise returns true and
		   the image is in the gui spare image"""
		final_lines = []
		requested_lines = text.splitlines()
		# Create a series of lines that will fit on the provided rectangle
		for requested_line in requested_lines:
			if self.fonts[fnt].size(requested_line)[0] > x:
				words = requested_line.split(' ')
				# if any of our words are too long to fit, return.
				for word in words:
					if self.fonts[fnt].size(word)[0] >= x:
						# TODO: should actually handle long words, since a web address
						# has been found to be too long for this code!
						# Possible answer: don't use long web addresses, or break them
						# up first.
						print "Error: Word was too long in label"
						return False
				# Start a new line
				accumulated_line = ""
				for word in words:
					test_line = accumulated_line+word+" "
					# Build the line while the words fit.
					if self.fonts[fnt].size(test_line)[0] < x:
						accumulated_line = test_line
					else:
						final_lines.append(accumulated_line)
						accumulated_line = word+" "
				final_lines.append(accumulated_line)
			else:
				final_lines.append(requested_line)
		# everything seemed to work ok.. so far!
		accumulated_height = 0
		for line in final_lines:
			if accumulated_height + self.fonts[fnt].size(line)[1] >= y:
				return False
			accumulated_height += self.fonts[fnt].size(line)[1]
		return True

	# there are always some standard routines in any gui...here is a messagebox
	def messagebox(self, flags, text, win_title):
		"""Call the messagebox with flags (essentially the buttons
		   you want displayed), the text itself, and the message at
		   the top of the window. Handles \n in strings fine
		   I apologise for the length of this function"""
		# just quickly, did we have any buttons?
		if flags == 0:
			return SPQR.BUTTON_FAIL
		# start by calculating the MINIMUM size for this messagebox and txt label
		txt_width = ((self.iWidth("button")+8)*3)+4
		width = txt_width+(SPQR.SPACER*2)
		# get average size of height..
		height = (self.fonts[self.msg_font].size("X")[1])+1
		# really short message? (as long as there are no cr's inside)
		if self.fonts[self.msg_font].size(text)[0] < txt_width and re.search("\n", text) == False:
			# then don't even bother with a 2nd line...easy
			# render text to spare image
			self.temp_image = self.fonts[self.msg_font].render(text, 1, (0, 0, 0))
		else:
			# we KNOW we can't fit it into one line, try with 2,3,4 etc until it fits
			done = False
			ysize = height
			while done == False:
				ysize = ysize+height
				done = self.fitText(text, txt_width, ysize, self.msg_font)
			height = ysize
		# now we have the right size, lets render it!
		# start with a window, but work out the height first...
		wheight = height+SPQR.SPACER
		# add height for sep bar (2) and buttons (2*button height)
		wheight += (self.iHeight("button")*2)+2

		# ok, the window gets rendered for us here
		index = self.addWindow(SWINDOW.CWindow(-1, -1, width, wheight, win_title, True))
		y = SPQR.SPACER
		self.windows[index].addWidget(SWIDGET.CLabel(6, y, txt_width, height, text))
		# now add the seperator bar
		x = 6
		y += height
		self.windows[index].addWidget(SWIDGET.CSeperator(x, y, width-24))
		y += 1+(self.iHeight("button")/2)
		# move x to the right, buttons are blitted from right to left
		x = width-16-(self.iWidth("button"))
		# now we are ready to start printing buttons
		total_buttons = 0
		# logic is simple: found a button? yes, display it and 
		# modify next print pos. quit if 4th button found
		if (flags & SPQR.BUTTON_OK) != 0:
			slot = self.windows[index].addWidget(SWIDGET.CButton(x, y, "OK"))
			# same for every instance of this little loop: add the callbacks
			self.windows[index].items[slot].callbacks.mouse_lclk = msgboxOK
			self.windows[index].items[slot].active = True
			x = x-(self.iWidth("button")+12)
			# add a key for this
			self.keyboard.addKey(K_o, msgboxOK)
			total_buttons += 1
		if (flags & SPQR.BUTTON_CANCEL) != 0:
			slot = self.windows[index].addWidget(SWIDGET.CButton(x, y, "Cancel"))
			self.windows[index].items[slot].callbacks.mouse_lclk = msgboxCancel
			self.windows[index].items[slot].active = True
			x = x-(self.iWidth("button")+12)
			self.keyboard.addKey(K_c, msgboxCancel)
			total_buttons += 1
		if (flags & SPQR.BUTTON_YES) != 0:
			slot = self.windows[index].addWidget(SWIDGET.CButton(x, y, "Yes"))
			self.windows[index].items[slot].callbacks.mouse_lclk = msgboxYes
			self.windows[index].items[slot].active = True
			x = x-(self.iWidth("button")+12)
			self.keyboard.addKey(K_y, msgboxYes)
			total_buttons += 1
		if (flags & SPQR.BUTTON_NO) != 0 and total_buttons < 3:
			slot = self.windows[index].addWidget(SWIDGET.CButton(x, y, "No"))
			self.windows[index].items[slot].callbacks.mouse_lclk = msgboxNo
			self.windows[index].items[slot].active = True
			x = x-(self.iWidth("button") + 12)
			self.keyboard.addKey(K_n, msgboxNo)
			total_buttons += 1
		if (flags & SPQR.BUTTON_QUIT) != 0 and total_buttons < 3:
			slot = self.windows[index].addWidget(SWIDGET.CButton(x, y, "Quit"))
			self.windows[index].items[slot].callbacks.mouse_lclk = msgboxQuit
			self.windows[index].items[slot].active = True
			x = x-(self.iWidth("button") + 12)
			self.keyboard.addKey(K_q, msgboxQuit)
			total_buttons += 1
		if (flags & SPQR.BUTTON_IGNORE) != 0 and total_buttons < 3:
			slot = self.windows[index].addWidget(SWIDGET.CButton(x, y, "Ignore"))
			self.windows[index].items[slot].callbacks.mouse_lclk = msgboxIgnore
			self.windows[index].items[slot].active = True
			self.keyboard.addKey(K_i, msgboxIgnore)
			total_buttons += 1
		# thats the graphics dealt with, make sure the whole window is modal
		self.windows[index].modal = True
		# if there was only one button, then make the enter key also activate it
		if total_buttons == 1:
			# get the routine to call
			rout = self.keyboard.active_keys[-1].function
			self.keyboard.addKey(K_RETURN, rout)
			# allow for extra key on key stack
			total_buttons += 1
		# set keyboard functions
		self.keyboard.setModalKeys(total_buttons)
		# turn off unit animation during the messagebox
		self.unitFlashAndOff()
		# ok, lets get the image we need and the rectangle:
		self.addDirtyRect(self.windows[index].drawWindow(),
			self.windows[index].rect)
		# keep looping until we get a positive result
		self.callback_temp = SPQR.BUTTON_FAIL
		while self.callback_temp == SPQR.BUTTON_FAIL:
			self.mainLoopSolo()
		# so we caught the answer, now we just have to tidy up
		# an active messagebox is ALWAYS top of the list, so just delete it
		# and then redraw the screen
		self.deleteTopDirty()
		# reset the keyboard
		self.keyboard.removeModalKeys()
		# remove the window
		self.windows.pop()
		# put the animation back if the top window is NOT modal
		if self.windows[-1].modal == False:
			self.unitFlashOn()
		# return the value we got
		return self.callback_temp

	def exitConsole(self):
		"""Here's an easy one: kill the current console
		   by setting the console flag to false"""
		self.console = False
		return True

# callbacks for the messegebox routines (if needed)
def msgboxOK(handle, xpos, ypos): 
	"""Callback for messagebox ok button"""
	gui.callback_temp = SPQR.BUTTON_OK
	return SPQR.BUTTON_OK

def msgboxCancel(handle, xpos, ypos):
	"""Callback for messagebox cancel button"""
	gui.callback_temp = SPQR.BUTTON_CANCEL
	return SPQR.BUTTON_CANCEL

def msgboxYes(handle, xpos, ypos):
	"""Callback for messagebox yes button"""
	gui.callback_temp = SPQR.BUTTON_YES
	return SPQR.BUTTON_YES

def msgboxNo(handle, xpos, ypos):
	"""Callback for messagebox no button"""
	gui.callback_temp = SPQR.BUTTON_NO
	return SPQR.BUTTON_NO

def msgboxQuit(handle, xpos, ypos):
	"""Callback for messagebox quit button"""
	gui.callback_temp = SPQR.BUTTON_QUIT
	return SPQR.BUTTON_QUIT

def msgboxIgnore(handle, xpos, ypos):
	"""Callback for messagebox ignore button"""
	gui.callback_temp = SPQR.BUTTON_IGNORE
	return SPQR.BUTTON_IGNORE

# this module acts as the GUI singleton
gui = CGFXEngine()

