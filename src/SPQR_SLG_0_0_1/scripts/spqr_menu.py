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

import sys, pygame, os.path
from pygame.locals import *

import spqr_defines as SPQR
import spqr_widgets as SWIDGET
import spqr_gui as SGFX

# this is the definition of an item in a menu drop-down
class CMenuChild(object):
	"""Class defines an item in a drop-down menu"""
	def __init__(self, text, icon, key, code):
		self.active = True
		self.visible = True
		self.text = text
		self.icon = icon
		self.key_text = key
		# rectangle is defined when the parent menu is drawn
		self.rect = pygame.Rect(0, 0, 0, 0)
		self.callbacks = SWIDGET.CCallbacks("HMenuChild_Callback")
		# less faffing as we add the menu code pointer right here in the constructor
		self.callbacks.mouse_lclk = code
		self.parent = False
		self.describe = "CMenuChild"

# following 2 routines are placeholders - they are the standard routines called if
# you do NOT specify a routine to be called

# standard entry point when a menu parent is clicked
def menuParentClick(handle, xpos, ypos):
	"""Standard entry point if you fail to define what happens when you click
	   a parent menu. Normally you can ignore this since adding child menus
	   will make sure this code doesn't get run"""
	messagebox(SPQR.BUTTON_OK, "You clicked a parent menu", SPQR.FONT_VERA)
	return True

# and the same for a child click
def menuChildClick(handle, xpos, ypos):
	"""Standard entry point for code when you click a child menu. This code can
	   normally be ignored since generally you will pass over a new function to
	   be called instead of this one"""
	messagebox(SPQR.BUTTON_OK, "You clicked a child menu", SPQR.FONT_VERA)
	return True

class CMenuParent(object):
	"""Class defines a parent menu (something like the 'File' part of
	   a normal drop-down menu)"""
	def __init__(self, text):
		self.active = True
		self.visible = True
		self.text = text
		self.children = []
		# a place to store the graphics...
		self.image = pygame.Surface((1, 1))
		self.highlight = pygame.Surface((1, 1))
		# the area of this rect is set when the Hmenu is set up
		self.rect = pygame.Rect(0, 0, 0, 0)
		self.callbacks = SWIDGET.CCallbacks("CMenuParent_Callback")
		self.callbacks.mouse_lclk = menuParentClick
		self.parent = False
		self.describe = "CMenuParent"
		
	def addChild(self, child):
		"""Add a child menu to a parent. This is always added to the end
			 of any current child menus. Returns index number of the new child"""
		self.children.append(child)
		return len(self.children) - 1

# Here's a fairly complex one - the menu system, only ever one instance of in our code (?)
# it always occupies the top of the screen
class CMenu(object):
	"""Class holds all of the parent menus - thus there is only ever one
	   instance of this class in our code"""
	def __init__(self, children):
		self.active = True
		self.visible = True
		self.wtype = SPQR.WT_MENU
		self.parents = []
		# children is an array of arrays, with a one-on-one
		self.menu = children
		# load the base image we will use to generate the titlebar gfx
		titlebar = pygame.image.load(os.path.normpath("../gfx/gui/titlebar.png")).convert()
		# store the rect for later
		self.rect = pygame.Rect(0,0,SPQR.SCREEN_WIDTH,titlebar.get_height())
		# draw the top bar starting here
		# now work out what size the rhs pixmap text is
		rhs_txt = "SPQR "+SPQR.VERSION
		rhs_txt_width = SGFX.gui.fonts[SPQR.FONT_VERA].size(rhs_txt)[0] + SPQR.SPACER
		# blit the lhs
		x_blits = int((SPQR.SCREEN_WIDTH-rhs_txt_width - 51) / 8)
		self.image = pygame.Surface((SPQR.SCREEN_WIDTH,titlebar.get_height()))
		dest = pygame.Rect(0, 0, SPQR.SPACER, titlebar.get_height())
		for foo in range(x_blits - 6):
			self.image.blit(titlebar, dest)
			dest.x += 8
		# blit the rhs
		titlebar = pygame.image.load(os.path.normpath("../gfx/gui/titlebar_fill.png")).convert()
		dest.x = SPQR.SCREEN_WIDTH - (rhs_txt_width + 56)
		while dest.x < SPQR.SCREEN_WIDTH:
			self.image.blit(titlebar,dest)
			dest.x += titlebar.get_width()
		# ok, now we can add the text to the rhs:
		foo = SGFX.gui.fonts[SPQR.FONT_VERA].render(rhs_txt, True, SPQR.COL_BLACK)
		dest.x = SPQR.SCREEN_WIDTH - (rhs_txt_width + SPQR.SPACER)
		dest.y = 4
		self.image.blit(foo, dest)
		# and then the menu on the lhs:
		# here is where we set up the rects for mouse selection
		self.offsets = []
		dest.x = SPQR.SPACER
		for foo in self.menu:
			text = foo.text
			SGFX.gui.fonts[SPQR.FONT_VERA].set_bold(True)
			itmp = SGFX.gui.fonts[SPQR.FONT_VERA].render(text,True,SPQR.COL_WHITE)
			SGFX.gui.fonts[SPQR.FONT_VERA].set_bold(False)
			self.image.blit(itmp,dest)
			# add rect area of this menu entry
			self.offsets.append(pygame.Rect((dest.x, 1, itmp.get_width() + 12,titlebar.get_height() - 1)))
			# calculate offset for next menu entry
			dest.x += itmp.get_width() + (SPQR.SPACER * 2)
			# draw the actual menu here as well
			self.drawMenu(foo)
		# finish the defines
		self.callbacks = SWIDGET.CCallbacks("CMenu_Callback")
		# now set so that the menu traps all the clicks on it
		self.callbacks.mouse_lclk = self.getMenuOption
		self.parent = False
		self.describe = "CMenu"
		
	def drawMenu(self,menu):
		"""Given a menu, return an image of that menu. This is called only
		   when the menu is changed in some way, not every time the menu
		   is dropped down"""
		# draw a menu, given the menu
		pics = []
		height = 0
		i = 0
		width = 0
		sep_bar = False
		# firstly draw all the parts we need to fully render the menu image
		for foo in menu.children:
			# loop through all children of this menu
			text = foo.text
			# is it a seperator?
			if text == "sep":
				# remember that fact
				pics.append(pygame.Surface((1, 1)))
				sep_bar = True
				height += (2 * SPQR.MNU_HSPACE) + 1
			else:
				# create the text seperatly at first
				text_image = SGFX.gui.fonts[SPQR.FONT_VERA].render(text, True, SPQR.MENU_TXT_COL)
				# expand the image horizontally and vertically by making a new image
				# and then blitting over the top of it...
				final_text = pygame.Surface(
					(text_image.get_width() + (SPQR.MNU_LSPACE * 2) + SPQR.ICON_SIZE + SPQR.SPACER,
					text_image.get_height() + (SPQR.MNU_HSPACE * 2)), SRCALPHA)
				final_text.fill(SPQR.MENU_COL)
				# blit the icon
				if foo.icon != None:
					final_text.blit(SGFX.gui.image(foo.icon),
						(SPQR.MNU_LSPACE, (SPQR.ICON_SIZE-final_text.get_height()) / 2))
				final_text.blit(text_image, ((2 * SPQR.MNU_LSPACE) + SPQR.ICON_SIZE, SPQR.MNU_HSPACE))
				pics.append(final_text)
				height += final_text.get_height()
			# longest section so far?
			# get size of keytext to render
			wk, hk = SGFX.gui.fonts[SPQR.FONT_VERA].size(foo.key_text)
			# add minimum gap
			wk += SPQR.MNU_KEY_GAP+final_text.get_width()
			if wk > width:
				width = wk
			i += 1
		# store text height for highlight use later
		hgh_h = final_text.get_height()
		# so then , do we need a sep bar? If so, draw it
		if sep_bar == True:
			bar = pygame.Surface((width, (SPQR.MNU_HSPACE * 2) + 1))
			bar.fill((246, 246, 246))
			pygame.draw.line(bar,(149, 149, 149), (2, SPQR.MNU_HSPACE),
							(width - 2, SPQR.MNU_HSPACE), 1)
		# now place all of those renders together
		# allow for a 1 pixel border around the menu
		width += SPQR.HALFSPCR
		height += SPQR.HALFSPCR
		menu.image = pygame.Surface((width, height))
		# set background and draw border
		menu.image.fill((246, 246, 246))
		pygame.draw.line(menu.image, SPQR.MENU_BDR_COL, (0, 0), (0, 0), 1)
		pygame.draw.line(menu.image, SPQR.MENU_BDR_COL, (width - 1, 0), (width - 1, 0), 1)
		pygame.draw.line(menu.image, SPQR.MENU_BDR_COL, (0, height - 1), (0, height - 1), 1)
		pygame.draw.line(menu.image, SPQR.MENU_BDR_COL, (width - 1, height - 1), (width - 1, height - 1), 1)
		pygame.draw.line(menu.image, SPQR.MENU_CNR_COL, (1, 0), (width - 2, 0), 1)
		pygame.draw.line(menu.image, SPQR.MENU_CNR_COL, (0, 1), (0, height - 2), 1)
		pygame.draw.line(menu.image, SPQR.MENU_CNR_COL, (width - 1, 1), (width - 1, height), 1)
		pygame.draw.line(menu.image, SPQR.MENU_CNR_COL, (1, height - 1), (width, height - 1), 1)
		# now drop in the text
		dest=pygame.Rect((1, 1, 0, 0))
		# FINALLY we can draw what will be the highlight for this menu
		# the 32 is to force a 32 bit surface for alpha blitting
		menu.highlight = pygame.Surface((width - SPQR.QTRSPCR, hgh_h), 0, 32)
		# then set the alpha value
		menu.highlight.set_alpha(SPQR.MENU_ALPHA)
		# lets try to draw on this surface
		menu.highlight.fill(SPQR.MENU_HLCOL)
		index = 0
		# allow for small gap between menu and menubar
		dest.x = 1
		dest.y = 1 + SPQR.QTRSPCR
		# now render the actual menu bar proper
		index = 0
		for text in pics:
			dest.h = text.get_height()
			if dest.h == 1:
				# draw the sep bar
				dest.h = bar.get_height()
				menu.image.blit(bar, dest)
				# store details for later
				menu.children[index].rect = pygame.Rect((1, 1, 1, 1))
				index += 1
				dest.y += dest.h
			else:
				# create the key text
				ktxt = SGFX.gui.fonts[SPQR.FONT_VERA].render(
					menu.children[index].key_text, True, SPQR.MENU_TXT_COL)
				# blit the text
				dest.h = text.get_height()
				menu.image.blit(text,dest)
				# and then the key text
				wr = pygame.Rect(width - (ktxt.get_width() + SPQR.HALFSPCR),
								 ((dest.h-ktxt.get_height()) / 2) + dest.y,
								 ktxt.get_width(), ktxt.get_height())
				menu.image.blit(ktxt, wr)
				# store the rect for mouse selection later
				menu.children[index].rect = pygame.Rect((1, dest.y, width - SPQR.QTRSPCR, hgh_h))
				index += 1
				dest.y += dest.h
		# and thats it
		return True
		
	def addMenu(self, parent):
		"""Add a menu to the HMenu. Returns index number of new menu"""
		self.parents.append(parent)
		return len(self.parents) - 1

	def getMenuOption(self, handle, xpos, ypos):
		"""Routine called when the mouse has clicked over the parent menu area
			 Should always return True"""
		# first check if we are in the target areas
		# *titlebar has to be at top of screen for this to work*
		code_called = False
		i = 0
		index =- 1
		while i < len(handle.offsets):
			if handle.offsets[i].collidepoint(xpos, ypos) == True:
				index = i
			i += 1
		if index == -1:
			return True
		new_menu = False
		while new_menu == False:
			# set the destination rect...
			w = handle.menu[index].image.get_width()
			h = handle.menu[index].image.get_height()
			dest = pygame.Rect((handle.offsets[index].x - SPQR.MENU_X_OFFSET, SPQR.MENU_Y_OFFSET, w, h))
			# make a copy of whats on the screen right here...
			screen_copy = pygame.Surface((dest.w, dest.h))
			screen_copy.blit(pygame.display.get_surface(), (0, 0), dest)
			# copy the menu image across
			SGFX.gui.screen.blit(handle.menu[index].image, dest)
			# and update the screen
			pygame.display.update(dest)
		
			# should halt and test mouse responses here
			# any click outside of menu - leave routine
			# any click inside the menu - do the code
			# any mouse_over in a valid menu option - highlight the menu option
			# any keypress: leave the routine
		
			# loop forever
			exit_menu = False
			highlight_on = False
			last_highlight = pygame.Rect(1, 1, 1, 1)
			key_function = False
			while exit_menu == False:
				event=pygame.event.poll()
				# was it a keypress:	
				if event.type == KEYDOWN:
					# did it match?
					key_function,bar, handle = SGFX.gui.keyboard.getKeyFunction(event.key, event.mod)
					if key_function == True:
						exit_menu = True
						new_menu = True
				# did user release the mouse?
				elif event.type == MOUSEBUTTONUP and event.button == 1:
					x, y = pygame.mouse.get_pos()
					# outside our menu?
					if dest.collidepoint(x, y) == False:
						# no more work to do
						exit_menu = True
						new_menu = True
					else:
						# check to see if we clicked something...
						for foo in handle.menu[index].children:
							hrect = pygame.Rect(foo.rect.x, foo.rect.y, foo.rect.w, foo.rect.h)
							# offset into menu
							hrect.x += dest.x
							hrect.y += dest.y
							# are we in this one?
							if hrect.collidepoint(x,y) == True:
								# call the routine, clear up and then exit
								# firstly erase the shown menu
								SGFX.gui.screen.blit(screen_copy,dest)
								pygame.display.update(dest)
								# now do the call
								foo.callbacks.mouse_lclk(foo, x, y)
								code_called = True
								exit_menu = True
								new_menu = True
				elif event.type == MOUSEMOTION:
					x, y = pygame.mouse.get_pos()
					# is the mouse NOT in the last_highlight? Cos if so, we
					# need to update that portion of that screen
					if last_highlight.collidepoint(x, y) == False:
						last_highlight.x -= dest.x
						last_highlight.y -= dest.y
						# copy portion on menu to screen
						SGFX.gui.screen.blit(handle.menu[index].image,dest)
						# and update the screen
						pygame.display.update(dest)
						# test against all highlights
					# inside the menu?
					if dest.collidepoint(x, y) == True:
						for foo in handle.menu[index].children:
							hrect = pygame.Rect(foo.rect.x, foo.rect.y, foo.rect.w, foo.rect.h)
							# offset into menu
							hrect.x += dest.x
							hrect.y += dest.y
							# already highlighted this?
							if last_highlight != hrect and hrect.w != 1:
								# are we in this one?
								if hrect.collidepoint(x, y) == True:
									# draw the highlight
									SGFX.gui.screen.blit(handle.menu[index].highlight,hrect)
									pygame.display.update(dest)
									highlight_on = True
									last_highlight = hrect
					else:
						# well, we wern't in the menu area, perhaps we are over the parent?
						i = 0
						tindx = -1
						while i < len(handle.offsets):
							if handle.offsets[i].collidepoint(x,y) == True:
								tindx = i
							i += 1
						if tindx != -1:
							# we are over a menu. Same one?
							if tindx!=index:
								index = tindx
								# force redraw etc...
								SGFX.gui.screen.blit(screen_copy, dest)
								pygame.display.update(dest)
								exit_menu = True
		# if no code called, tidy the screen back up again
		if code_called == False:
		# tidy the screen back up again
			SGFX.gui.screen.blit(screen_copy, dest)
		# update the screen
			pygame.display.update(dest)
		# if there was a keypress valid, or a mouseover event, run the code
		if key_function == True:
			bar(0, -1, -1)
		return True

