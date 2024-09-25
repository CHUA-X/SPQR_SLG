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
import sys,pygame
from pygame.locals import *

import spqr_data as SDATA
import spqr_defines as SPQR
import spqr_window as SWINDOW
import spqr_widgets as SWIDGET
import spqr_gui as SGFX
import spqr_sound as SSFX
import spqr_ybuild as SYAML

# thanks go to John Schanck for the following module
import pyconsole

# found here are all the functions triggered by the various mouse events
# they must all have the structure
# def function_name(handle,xpos,ypos)
# xpos and ypos are the offset into whatever
# was clicked, and handle being a pointer to the widget that was clicked

# Important note: keyboard events assume a function like all the rest, i.e. with
# 3 parameters. However, the actual params that get sent on a keypress are
# (0,-1,-1). So make sure that the function doesn't depend on x and y, and
# *DOESN'T* use the handle in a keyboard callback. You can always do code like
# if xpos == -1: to check if it was a keyboard event

# one more note: some of these functions are complex enough to be split up
# so not *all* functions are this format, just the majority

# we start with just the quit function (cos it's real easy!)
def quitSpqr(handle, xpos, ypos):
	"""Messagebox to confirm quit game.
		 Returns True or doesn't return at all!"""
	result = SGFX.gui.messagebox((SPQR.BUTTON_OK|SPQR.BUTTON_CANCEL),
		"Really quit SPQR?", "Quit Message")
	if result == SPQR.BUTTON_OK:
		# exit the game
		sys.exit(True)
	return True
		
def centreMap(handle, xpos, ypos):
	"""Routine centres the map on the city of Rome"""
	# centre map on rome
	SGFX.gui.map_screen.x = SPQR.ROME_XPOS - (SGFX.gui.map_rect.w/2)
	SGFX.gui.map_screen.y = SPQR.ROME_YPOS - (SGFX.gui.map_rect.h/2)
	# make sure hex is selected as well
	# this also updates the screen for us
	x = SGFX.gui.map_screen.w/2
	y = (SGFX.gui.map_screen.h/2)+SPQR.WINSZ_TOP
	SGFX.gui.mapClick(x, y)
	return True

# left click on mini map gives us this
def miniMapClick(handle, xpos, ypos):
	"""Called when user clicks on mini-map
	   Resets map display area and update the screen"""
	# make the click point to the centre:
	# convert to map co-ords
	xpos = xpos*SGFX.gui.width_ratio
	ypos = ypos*SGFX.gui.height_ratio
	# correct to centre of screen
	xpos -= SGFX.gui.map_rect.h/2
	ypos -= SGFX.gui.map_rect.w/2
	SGFX.gui.map_screen.x = xpos
	SGFX.gui.map_screen.y = ypos
	# correct if out of range
	SGFX.gui.normalizeScrollArea()
	# update the screen	
	SGFX.gui.updateMiniMap()
	SGFX.gui.updateMap()
	return True

def miniMapDrag(handle, xpos, ypos):
	"""Called when left click dragging over mini-map.
	   Catches all calls until the left mouse button
	   is released again"""
	# to make life a lot easier, we utilise miniMapClick()
	# a fair bit here...
	miniMapClick(handle, xpos, ypos)
	while(True):
		event = pygame.event.poll()
		if event.type == MOUSEBUTTONUP and event.button == 1:
			# time to exit
			return True
		elif event.type == MOUSEMOTION:
			xpos += event.rel[0]
			ypos += event.rel[1]
			miniMapClick(handle, xpos, ypos)

def unitClicked(handle, xpos, ypos):
	"""Called when a unit image is clicked"""
	# only highlight if there is a move left
	SGFX.gui.focusOnUnit(handle.data)
	return True

def highlightNextUnit(handle, xpos, ypos):
	unit = SDATA.nextUnitToMove(SGFX.gui.current_highlight)
	if unit != None:
		SGFX.gui.focusOnUnit(unit)
	return True

# here come the defines for the menu system, but let's start with a general
# one to say that that part still needs to be coded
def notYetCoded(handle, xpos, ypos):
	"""Routine used as a placeholder for various pieces of
	   code until they've actually been done"""
	SGFX.gui.messagebox(SPQR.BUTTON_OK, "Sorry, this feature has yet to be coded", "NYC")
	return True

def menuPreferences(handle, xpos, ypos):
	"""Display the user preferences window. You can only really
	   play with the music and volume settings for now"""
	# first off, let's make the window that we need
	index = SGFX.gui.addWindow(SWINDOW.CWindow(-1, -1, 288, 152, "SPQR Preferences", True))
	# we'll need an image first
	img = SWIDGET.buildImageAlpha("img_music")
	img.rect.x = 20
	img.rect.y = 20
	# a couple of labels, and there positions
	lbl_MusicOn = SWIDGET.buildLabel("Music On:")
	lbl_MusicOn.rect.x = 88
	lbl_MusicOn.rect.y = 28
	lbl_Volume = SWIDGET.buildLabel("Volume:")
	lbl_Volume.rect.x = 88
	lbl_Volume.rect.y = 60
	# a checkbox for the music option
	chk_Volume = SWIDGET.CCheckBox(247, 30, SSFX.sound.music_playing)
	chk_Volume.active = True
	# connect it to some code
	chk_Volume.addAfterClick(musicCheckbox)
	# a slider for the volume
	sld_Volume = SWIDGET.CSlider(160, 62, 100, 0, 100, SSFX.sound.getVolume())
	sld_Volume.active = True
	# connect to some code
	sld_Volume.setUpdateFunction(setVolume)
	# a seperator
	sep = SWIDGET.CSeperator(10, 90, 274 - SPQR.WINSZ_SIDE)
	# and an ok button
	btn_ok = SWIDGET.CButton(190, 106, "OK")
	btn_ok.callbacks.mouse_lclk = killModalWindow
	btn_ok.active = True
	# add them all to our window
	SGFX.gui.windows[index].addWidget(img)
	SGFX.gui.windows[index].addWidget(lbl_MusicOn)
	SGFX.gui.windows[index].addWidget(lbl_Volume)
	SGFX.gui.windows[index].addWidget(chk_Volume)
	SGFX.gui.windows[index].addWidget(sld_Volume)
	SGFX.gui.windows[index].addWidget(sep)
	SGFX.gui.windows[index].addWidget(btn_ok)
	# make the window modal
	SGFX.gui.windows[index].modal = True
	# add the new key event: o = ok
	SGFX.gui.keyboard.addKey(K_o, killModalWindow)
	SGFX.gui.keyboard.setModalKeys(1)
	# turn off unit animations
	SGFX.gui.unitFlashAndOff()
	# setup dirty rect stuff
	SGFX.gui.addDirtyRect(SGFX.gui.windows[index].drawWindow(),
		SGFX.gui.windows[index].rect)
	# and thats us done
	return True

# now follow the events for the preferences screen
def musicCheckbox(handle, xpos, ypos):
	"""Starts / stops music"""
	if handle.status == True:
		# start music
		SSFX.sound.startMusic()
	else:
		# stop music
		SSFX.sound.stopMusic()
	return True
	
def setVolume(handle, xpos, ypos):
	"""Sets volume according to slider value"""
	# get current slider value
	volume = handle.getSliderValue()
	# set new volume
	SSFX.sound.setVolume(volume)
	# so simple!
	return True

# define the callbacks
def killCurrentWindow(handle, xpos, ypos):
	"""Removes current window from window list"""
	# kill the current window
	# let me explain the +1 here: the main loop is a loop that counts the 
	# windows - this where SGFX.gui.win_index comes from. However, since we don't
	# know how the loop is going to go, we increment the index pointer as soon
	# as we have a copy of the window to work with. This means our index is 1
	# out. Since the routine counts down and not up, we are 1 less than we
	# should be, hence the +1 :-)
	SGFX.gui.killIndexedWindow(SGFX.gui.win_index + 1)
	return True
	
def killModalWindow(handle, xpos, ypos):
	"""As killCurrentWindow, but this also removes any modal
	   keypresses we might have left behind. It also destroys the
	   dirty rect that you must have left behind"""
	SGFX.gui.keyboard.removeModalKeys()
	SGFX.gui.deleteTopDirty()
	SGFX.gui.killTopWindow()
	# for animations, we turn them back on if the top window is
	# now NOT modal
	if SGFX.gui.windows[-1].modal == False:
		SGFX.gui.unitFlashOn()
	else:
		# just to make sure...
		SGFX.gui.unitFlashAndOff()
	return True

def startGame(handle, xpos, ypos):
	"""Called when user starts game"""
	killModalWindow(0, 0, 0)
	# remove top dirty image as well
	SGFX.gui.deleteTopDirty()
	# update screen
	SGFX.gui.updateGUI()
	string = "To get help at any time, press F1. For a list of "
	string += "keys and their actions, press k."
	SGFX.gui.messagebox(SPQR.BUTTON_OK, string, "Game Start")
	return True

def menuNew(handle, xpos, ypos):
	"""Temp routine, just displays a messagebox for now"""
	SGFX.gui.messagebox(SPQR.BUTTON_OK,
		"Sorry, can't start a new game yet :-(", "New Game")
	return True

def menuLoad(handle, xpos, ypos):
	"""Temp routine, just displays a messagebox for now"""
	SGFX.gui.messagebox(SPQR.BUTTON_OK,
		"Sorry, it is not possible to load games yet.","Load Game")
	return True

def menuSave(handle, xpos, ypos):
	"""Temp routine, just displays a messagebox for now"""
	SGFX.gui.messagebox(SPQR.BUTTON_OK,
		"Sorry, save game has yet to be coded (more code to be done...)",
		"Save Game")
	return True

def showCity(handle, xpos, ypos):
	"""Display city information screen"""
	city = SDATA.data.map.regions["latium_et_campania"].city

	window = SWINDOW.CWindow(-1, -1, 300, 200, "City Info", True)
	window.modal = True
	# we need a label for the name
	lbl_name = SWIDGET.buildLabel(city.name, SPQR.FONT_VERA_LG)
	lbl_name.rect.x = 20
	lbl_name.rect.y = 20
	# a picture of city and surrounding area
	picture = pygame.Surface((80, 80))
	picture.blit(SGFX.gui.image("buffer"), (0, 0))
	city_image = SWIDGET.buildUniqueImage(picture)
	city_image.rect.x = 20
	city_image.rect.y = 60
	# labels for data:
	lbl_population = SWIDGET.buildLabel("Population", SPQR.FONT_VERA)
	lbl_happiness = SWIDGET.buildLabel("Happiness", SPQR.FONT_VERA)
	lbl_food = SWIDGET.buildLabel("Food consumption", SPQR.FONT_VERA)
	
	btn_ok = SWIDGET.CButton(50, 150, "OK")
	btn_ok.callbacks.mouse_lclk = killModalWindow
	btn_ok.active = True
	window.addWidget(lbl_name)
	window.addWidget(city_image)
	window.addWidget(btn_ok)
	SGFX.gui.addWindow(window)
	SGFX.gui.unitFlashAndOff()
	# setup dirty rect stuff
	SGFX.gui.addDirtyRect(window.drawWindow(), window.rect)
	return True

def menuEmpireSenate(handle, xpos, ypos):
	"""Temp routine, just displays a messagebox for now"""
	string = "It is not possible to visit the senate at this moment in time."
	SGFX.gui.messagebox(SPQR.BUTTON_OK, string, "Visit Senate")
	return True

def menuEmpireMilitary(handle, xpos, ypos):
	"""Routine sets up and displays the unit display box
	   Always returns True"""
	   
	# OLD CODE TO DISPLAY EXAMPLE OF AN ITEMLIST
	# TODO: Replace as soon as possible!
	   
	# we need to create the following data to creata an ItemList:
	# lgui,x,y - gui pointer and x/y position (as per normal)
	# a list to say what the column types are (where True is text)
	# a list to give the column titles
	# then a list of lists, each list giving the attributes for
	# each column. Followed by the height of the total widget
	# the column layout should be: Unit gfx, unit name, status, commander
	# create the item list:
	ilist = [False, True, True, False, True]
	# and the column name list:
	clist = ["Image", "Unit Name", "Moves", "Status", "Commander"]
	# that was easy. Now create each list item. Firstly we need
	# every unit that is Roman:
	units = []
	for i in SGFX.gui.data.troops.units:
		if i.owner == SPQR.ROME_SIDE:
			units.append(i.id_number)
	# did we actually get any units?
	if units == []:
		SGFX.gui.messagebox(SPQR.BUTTON_OK, "There are no Roman units!", "Unit List")
		return True

	# now build up the column data that we need:
	uid = []
	ugfx = []
	uname = []
	umoves = []
	ustatus = []
	ucommander = []
	for foo in units:
		uid.append(foo)
		i=SGFX.gui.data.troops.getIndexFromID(foo)
		tunit=SGFX.gui.data.troops.units[i]
		ugfx.append(SGFX.gui.images[tunit.image])
		uname.append(tunit.name)
		umoves.append(str(tunit.moves_left))
		ustatus.append(SGFX.gui.returnGraphImage(i))
		i2=SGFX.gui.data.getPeopleIndex(tunit.commander)
		cname=SGFX.gui.data.people[i2].getShortName()
		ucommander.append(cname)

	# store the sort routines:
	sort = [SGFX.gui.data.sortUnitImage,
		 	SGFX.gui.data.sortUnitName,
		 	SGFX.gui.data.sortUnitMoves,
		 	SGFX.gui.data.sortUnitStatus,
		 	SGFX.gui.data.sortUnitCommander]

	# tie all of that up together and get the ItemList:
	elements = []
	elements.append(ilist)
	elements.append(clist)
	elements.append(ugfx)
	elements.append(uname)
	elements.append(umoves)
	elements.append(ustatus)
	elements.append(ucommander)
	unitlist = SWIDGET.CItemList(SGFX.gui, SPQR.SPACER, SPQR.SPACER, elements, sort, uid, 300)
	sclist = unitlist.listarea

	# now we can actually build up our window. Let's make this as easy
	# as possible. First off, get the size of the area we need:
	wxsize = unitlist.rect.w
	wysize = unitlist.rect.h + sclist.rect.h

	# activate stuff
	unitlist.active = True
	sclist.active = True	
	# build the window, and locate stuff
	# let's have SPACER around the window as filler, except at the bottom,
	# where we have SPACER - checkbox+label - SPACER:
	height = wysize + (SPQR.SPACER*3)
	width = wxsize + ((SPQR.SPACER*2) + SGFX.gui.images[SPQR.SCROLL_TOP].get_width())	
	# now start to build the window
	uwin = (SWINDOW.CWindow(-1, -1, width, height, "Unit List", True))	
	uwin.addWidget(unitlist)
	uwin.addWidget(sclist)
	uwin.modal = True
	
	# add the extra buttons
	b1 = SWINDOW.CButtonDetails("Cancel", K_c, killModalWindow)
	uwin.buildButtonArea([b1], False)
	SGFX.gui.keyboard.setModalKeys(1)
	index = SGFX.gui.addWindow(uwin)

	# turn off unit animations for the moment
	SGFX.gui.unitFlashAndOff()
	# add the dirty rect details
	SGFX.gui.addDirtyRect(SGFX.gui.windows[index].drawWindow(),
		SGFX.gui.windows[index].rect)
	return True

def menuEmpireStatistics(handle, xpos, ypos):
	"""Temp routine, just displays a messagebox for now"""
	string = SPQR.CODELINES+" lines of Python source code\n"
	string += "2.1 Mb of GFX\n"
	string += "47 Litres of Coke\n\n"
	string += "And counting..."
	SGFX.gui.messagebox(SPQR.BUTTON_OK, string, "Statistics")
	return True

def menuHelpAbout(handle, xpos, ypos):
	"""Simple messagebox with game info. Returns True"""
	message = "SPQR " + SPQR.VERSION + "\n\n"
	message += "Written and designed by " + SPQR.AUTHOR + "\n"
	message += "(maximinus@gmail.com)\n"
	message += "Last Update " + SPQR.LAST_UPDATE
	message += "\n\nThanks to Freeciv for the unit gfx, Pygame for the library"
	message += " and Gnome for various GUI graphics."
	SGFX.gui.messagebox(SPQR.BUTTON_OK, message, "About SPQR")
	return True

def menuHelpHelp(handle, xpos, ypos):
	"""Gateway into help system. Currently a messagebox.
	   Always returns True"""
	message = "Hopefully, as the gui progresses, this area should be a fully "
	message += "functional help database.\n\nFor now though, I have to point you "
	message += "to the not so excellent SPQR website:\n\n"
	message += SPQR.WEBSITE
	SGFX.gui.messagebox(SPQR.BUTTON_OK, message, "SPQR Help")
	return True

def keyShowKeys(handle, xpos, ypos):
	"""Displays list of 'standard' keys used in the game"""
	# just a very simple messagebox
	message = "SPQR Keys:\n\n"
	message += "f - Finish unit turn\n"
	message += "k - Show this keylist\n"
	message += "n - highlight next unit\n"
	message += "r - Centre map on Rome\n"
	message += "F1 - Help\n"
	message += "CTRL+Q - Exit the game\n\n"
	SGFX.gui.messagebox(SPQR.BUTTON_OK, message, "SPQR Help")
	return True

# keyboard callbacks to open up the menu
def keyMenuFile(handle, xpos, ypos):
	"""Opens up the menu file"""
	menu = SGFX.gui.windows[SPQR.WIN_MENU].items[0]
	menu.callbacks.mouse_lclk(menu, menu.offsets[0].x, menu.offsets[0].y)
	return True

def keyMenuEmpire(handle, xpos, ypos):
	"""Opens up the empire file"""
	menu = SGFX.gui.windows[SPQR.WIN_MENU].items[0]
	menu.callbacks.mouse_lclk(menu, menu.offsets[1].x, menu.offsets[0].y)
	return True

def keyMenuHelp(handle, xpos, ypos):
	"""Opens up the help file"""
	menu = SGFX.gui.windows[SPQR.WIN_MENU].items[0]
	menu.callbacks.mouse_lclk(menu, menu.offsets[2].x, menu.offsets[0].y)
	return True

def keyMenuDebug(handle, xpos, ypos):
	"""Opens up the dubug menu, if it's there"""
	menu = SGFX.gui.windows[SPQR.WIN_MENU].items[0]
	menu.callbacks.mouse_lclk(menu, menu.offsets[3].x, menu.offsets[0].y)
	return True

def keyMenuEscape(handle, xpos, ypos):
	"""If escape key is pressed, reset the menu"""
	menu = SGFX.gui.windows[SPQR.WIN_MENU].items[0]
	# obviously co-ords -1, -1 are never in the menu
	menu.callbacks.mouse_lclk(menu, -1, -1)
	return True

def keyScrollUp(handle, xpos, ypos):
	"""Handles cursor key up event to scroll map"""
	SGFX.gui.map_screen.y -= SPQR.KSCROLL_SPD
	# check the scroll areas
	SGFX.gui.normalizeScrollArea()
	# and update the screen
	SGFX.gui.updateMiniMap()
	SGFX.gui.updateMap()
	return True

def keyScrollDown(handle, xpos, ypos):
	"""Handles cursor key down event to scroll map"""
	SGFX.gui.map_screen.y += SPQR.KSCROLL_SPD
	# check the scroll areas
	SGFX.gui.normalizeScrollArea()
	# and update the screen
	SGFX.gui.updateMiniMap()
	SGFX.gui.updateMap()
	return True
	
def keyScrollRight(handle, xpos, ypos):
	"""Handles cursor key right event to scroll map"""
	SGFX.gui.map_screen.x += SPQR.KSCROLL_SPD
	# check the scroll areas
	SGFX.gui.normalizeScrollArea()
	# and update the screen
	SGFX.gui.updateMiniMap()
	SGFX.gui.updateMap()
	return True
	
def keyScrollLeft(handle, xpos, ypos):
	"""Handles cursor key left event to scroll map"""
	SGFX.gui.map_screen.x -= SPQR.KSCROLL_SPD
	# check the scroll areas
	SGFX.gui.normalizeScrollArea()
	# and update the screen
	SGFX.gui.updateMiniMap()
	SGFX.gui.updateMap()
	return True

def displayPygameInfo(handle, xpos, ypos):
	"""Simple messagebox to tell user about Pygame"""
	SGFX.gui.messagebox(SPQR.BUTTON_OK,
		"For details on Pygame, vist:\n\nwww.pygame.org\n\nMany thanks to Pete Shinners", "PyGame")
	return True

def welcomeScreen(handle, xpos, ypos):
	"""Routine displays opening screen, with load/save/new/about
	   buttons. Always returns True after doing it's work"""
	# set the sizes
	w = SGFX.gui.iWidth("startup")
	h = SGFX.gui.iHeight("startup")
	# build the window
	welcome = SWINDOW.CWindow(-1, -1, w, h, "SPQR " + SPQR.VERSION, True)
	# add the image that pretty much takes up the whole area:
	main_img = SWIDGET.buildImage("startup")
	welcome.addWidget(main_img)
	# create the 4 main buttons
	btn_new = SWIDGET.CButton(460, 12, "New")
	btn_load = SWIDGET.CButton(460, 52, "Load")
	btn_options = SWIDGET.CButton(460, 92, "Options")
	btn_about = SWIDGET.CButton(460, 132, "About")
	btn_quit = SWIDGET.CButton(460, 192, "Quit")
	# make active
	# add callbacks
	btn_new.callbacks.mouse_lclk = startGame
	btn_load.callbacks.mouse_lclk = menuLoad
	btn_options.callbacks.mouse_lclk = menuPreferences
	btn_about.callbacks.mouse_lclk = menuHelpAbout
	btn_quit.callbacks.mouse_lclk = quitSpqr
	
	# include a link for information about pygame
	# we'll do this by adding an active button that is not displayed
	btn_pygame = SWIDGET.CButton(420, 332, "*BLANK*")
	# resize it and don't display!
	btn_pygame.rect.width = 127
	btn_pygame.rect.height = 45
	btn_pygame.visible = False
	# add a simple callback
	btn_pygame.callbacks.mouse_lclk = displayPygameInfo
	
	# add all that to the window
	for i in [btn_new, 	btn_load, btn_options, btn_about, btn_quit, btn_pygame]:
		i.active = True
		welcome.addWidget(i)
	# make modal
	welcome.modal = True	
	# add the modal key events: n=new, l=load, o=options, a=about, q=quit
	SGFX.gui.keyboard.addKey(K_n, startGame)
	SGFX.gui.keyboard.addKey(K_l, menuLoad)
	SGFX.gui.keyboard.addKey(K_o, menuPreferences)
	SGFX.gui.keyboard.addKey(K_a, menuHelpAbout)
	SGFX.gui.keyboard.addKey(K_q, quitSpqr)
	SGFX.gui.keyboard.setModalKeys(5)
	# turn off unit animations
	SGFX.gui.unitFlashAndOff()
	# add the window as a dirty image
	SGFX.gui.addDirtyRect(welcome.drawWindow(), welcome.rect)
	SGFX.gui.addWindow(welcome)
	return True

# place all debugging events below this line
# these are only activated if DEBUG_MODE is set to True

# here are some console output routines called from an extra menu area
def consoleUnitNames(handle, xpos, ypos):
	"""Outputs to console the names of all the units in play"""
	print "No units"
	return True

def consoleUnitNumbers(handle, xpos ,ypos):
	"""Outputs to console the id numbers of all units"""
	print "No units"
	return True

def consoleUnitOwners(handle, xpos, ypos):
	"""Outputs to console owners of roman units"""
	print "No owners"
	return True

def consoleCityNames(handle, xpos, ypos):
	"""Outputs to console the names of all the cities in play"""
	print "No cities"
	return True

def windowTest2(handle, xpos, ypos):
	"""Routine to test whatever the latest version of the window
	   code is. Does nothing clever really"""
	# get a window
	index = SGFX.gui.addWindow(SWINDOW.CWindow(-1, -1, 320, 200, "Test", True))
	# make a list of 2 buttons
	buttons = []
	buttons.append(SWINDOW.CButtonDetails("OK", K_o, killModalWindow))
	buttons.append(SWINDOW.CButtonDetails("?!?", None, killModalWindow))
	SGFX.gui.windows[index].buildButtonArea(buttons, False)
	# we have to add modal keypresses ourselves
	SGFX.gui.keyboard.setModalKeys(1)
	# make modal
	SGFX.gui.windows[index].modal = True
	# turn off unit animations
	SGFX.gui.unitFlashAndOff()
	# add the window as a dirty image
	win_img = SGFX.gui.windows[index].drawWindow()
	SGFX.gui.addDirtyRect(win_img, SGFX.gui.windows[index].rect)
	return True

def widgetTest(handle, xpos, ypos):
	"""Routine to bring up a window with all widgets
	   on display. Used to test widgets, as the name implies"""
	# we start by building up all of the widgets
	lbl_widget = SWIDGET.buildLabel("Label")
	lbl_widget.rect.x = 10
	lbl_widget.rect.y = 10
	btn_widget = SWIDGET.CButton(10, 30, "Quit")
	btn_widget.callbacks.mouse_lclk = killModalWindow
	btn_widget.active = True	
	chk_widget = SWIDGET.CCheckBox(10, 68, True)
	chk_widget.active = True
	sld_widget = SWIDGET.CSlider(10, 90, 150, 0, 150, 75)
	sld_widget.active = True
	dc_widget = SWIDGET.buildLabel("Double-Click Me!")
	dc_widget.rect.x = 20
	dc_widget.rect.y = 230
	dc_widget.active = True
	dc_widget.callbacks.mouse_dclick = dclickTest
	options = ["Romans", "Iberians", "Greeks", "Selucids"]
	opt_widget = SWIDGET.COptionMenu(120, 30, options)
	opt_widget.active = True
	w = SGFX.gui.iWidth("test_image")
	scl_widget = SWIDGET.CScrollArea(10, 114, w, 96, SGFX.gui.image("test_image"))
	scl_widget.active = True
	# make sure we have a console output for the example slider
	sld_widget.setUpdateFunction(displaySliderContents)
	# let's have a window
	index = SGFX.gui.addWindow(SWINDOW.CWindow(-1, -1, 260, 300, "Widget Test", True))
	# add items to window
	SGFX.gui.windows[index].addWidget(lbl_widget)
	SGFX.gui.windows[index].addWidget(btn_widget)
	SGFX.gui.windows[index].addWidget(chk_widget)
	SGFX.gui.windows[index].addWidget(sld_widget)
	SGFX.gui.windows[index].addWidget(scl_widget)
	SGFX.gui.windows[index].addWidget(dc_widget)
	SGFX.gui.windows[index].addWidget(opt_widget)
	
	# set it modal
	SGFX.gui.windows[index].modal = True
	# there is only one key, but don't forget to add an enter one button windows
	SGFX.gui.keyboard.addKey(K_q, killModalWindow)
	SGFX.gui.keyboard.addKey(K_RETURN, killModalWindow)
	SGFX.gui.keyboard.setModalKeys(2)
	# turn off unit animations for the moment and thats it
	SGFX.gui.unitFlashAndOff()
	# add the dirty rect details
	SGFX.gui.addDirtyRect(SGFX.gui.windows[index].drawWindow(),
		SGFX.gui.windows[index].rect)
	return True

def dclickTest(handle, xpos, ypos):
	"""Test routine to check double-clicks"""
	SGFX.gui.messagebox(SPQR.BUTTON_OK, "Double-clicked!", "Test")
	return True

def displayConsole(handle, xpos, ypos):
	"""Opens console for display and editing
	   This loop catches *all* input until you exit.
	   Always returns True"""
	# Bugs have been fixed but I need to spend some more
	# time with this to make it actually fit for some purpose
	console_surface = pygame.Surface((SPQR.CONSOLE_WIDTH, SPQR.CONSOLE_HEIGHT))
	console = pyconsole.Console(
		console_surface,
		(0, 0, SPQR.CONSOLE_WIDTH, SPQR.CONSOLE_HEIGHT),
		vars = {"gui":SGFX.gui},
		functions = {"exit":SGFX.gui.exitConsole,
					 "dunits":SGFX.gui.cfuncs.showUnits,
					 "drunits":SGFX.gui.cfuncs.showRomanUnits,
					 "dpeople":SGFX.gui.cfuncs.showPeople,
					 "windows":SGFX.gui.cfuncs.showWindows})
	# console needs to stay displayed
	SGFX.gui.console = True
	while(True):
		console.process_input()
		console.draw()
		SGFX.gui.screen.blit(console_surface, (0, SPQR.WINSZ_TOP - 2))
		pygame.display.flip()
		# are we still drawing the console?
		if SGFX.gui.console == False:
			break
		pygame.time.wait(10)
	# clean up the screen
	# since we only ever draw over the map, simply re-draw that
	SGFX.gui.updateMap()
	return True

def displaySliderContents(handle, xpos, ypos):
	"""As well as showing you how to read slider contents,
	   this function outputs the slider value to a console.
	   Sometimes useful for checking/debugging. You can add
	   it to any slider function callback"""
	# only if debugging is turned on, of course...
	if SPQR.DEBUG_MODE == True:
		print "Slider value:", handle.getSliderValue()
	return True
	
def windowTest(handle, xpos, ypos):
	"""Routine to test whatever the latest version of the window
	   code is. Does nothing clever really"""
	# get the window from a yaml file and this returns a list of indexes
	# incase we import more than 1 window we get their indexes
	# here we have 1 window so we get the first index
	index = SYAML.createWindow("../data/layouts/window_test.yml")[0]
	SGFX.gui.windows[index].modal = True
	# we have to add modal keypresses ourselves
	SGFX.gui.keyboard.setModalKeys(1)
	# turn off unit animations
	SGFX.gui.unitFlashAndOff()
	# add the window as a dirty image
	win_img = SGFX.gui.windows[index].drawWindow()
	SGFX.gui.addDirtyRect(win_img, SGFX.gui.windows[index].rect)
	return True

# functions for the setup.py

def okClick(handle, x, y):
	for i in SGFX.gui.windows[0].items:
		if i.describe == "opt-Resolution":
			print "You selected a resolution of", i.option
			sys.exit(True)

def cancelClick(handle, x, y):
	"""quit utility and don't change anything"""
	sys.exit(True)
