#!/usr/bin/python

# SPQR source code, Copyright 2005-2011 The SPQR Team

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

# now include my own libs
from scripts import spqr_defines as SPQR
from scripts import spqr_data as SDATA
from scripts import spqr_gui as SGFX
from scripts import spqr_window as SWINDOW
from scripts import spqr_widgets as SWIDGET
from scripts import spqr_menu as SMENU
from scripts import spqr_events as SEVENT


class CSPQR(object):
    def __init__(self):
        self.fullscreen = SPQR.FULLSCREEN
        self.intro = True
        self.init_only = False
        # init the data
        SDATA.addUnits()
        self.sortOptions()
        SGFX.gui.mainInit(SPQR.SCREEN_WIDTH, SPQR.SCREEN_HEIGHT, self.fullscreen)
        # actually go any furthur?
        if self.init_only:
            # no, so exit here
            print("SPQR: init() worked fine.")
            sys.exit(True)

    # TODO: use optparse, don't re-invent the wheel
    def executeFlag(self, flag):
        """Call with flag, which should be a single letter.
		   Routine does whatever has to be done. Returns
		   True if something happened, false otherwise"""
        # big simple if statement:
        if flag == 'f':
            # set to fullscreen
            self.fullscreen = True
            return True
        elif flag == 'n':
            # don't show intro, just jump into a game
            self.intro = False
            return True
        elif flag == 't':
            # exit after initing data
            self.init_only = True
            return True
        elif flag == 'v':
            # show version details and exit
            print("SPQR " + SPQR.VERSION + ", written and designed by Chris Smith")
            print("  Copr. 2005-2010, released under the GNU Public License v2")
            print("  Last code update: " + SPQR.LAST_UPDATE)
            sys.exit(True)
        elif flag == 'g':
            print("[SPQR]: In memory of Jerry Garcia")
            return True
        elif flag == "?":
            print("SPQR Command line options:")
            print("  -f : Fullscreen")
            print("  -n : Skip intro")
            print("  -t : Test init only")
            print("  -v : Show version details")
            print("  -? : Show this display")
            # all done, a valid exit point
            sys.exit(True)
        # no match, but not a terrible error
        print("[SPQR] Error: No option for flag " + flag)
        return False

    def sortOptions(self):
        """Routine reads command-line options, splits them up
		   and makes sure they are executed. Returns False if there
		   was some problem"""
        options = sys.argv
        # any args at all?
        if len(options) == 1:
            return True
        # remove the first one
        options.pop(0)
        for i in options:
            # split into characters:
            chars = list(i)
            # first character must be a '-'
            if chars[0] != '-':
                print("[SPQR]: Error: Flag sequence does not start with '-'")
                sys.exit(False)
            # remove it
            chars.pop(0)
            # anything left?
            if len(chars) == 0:
                print("[SPQR]: Error: No flags following '-' char")
                return False
            # do each flag
            for flag in chars:
                self.executeFlag(flag)
        # everything must have worked
        return True

    # routine to init everything...
    def setupStart(self):
        """This is a very important function call that sets up the spqr gui.
		   It adds almost all of the useful and usual keychecks, windows
		   menus and so on. SPQR will *NOT* work unless this gets called.
		   And yes, it is very long but it's not at all complicated"""
        # The interface. there are 3 parts to this: the menu bar at the top -
        # DO NOT add widgets here, only the menu and the version number info
        # are held here; The main map and then the widgets on the main map.
        # we make a seperate blank window to hold all of these widgets
        # build up a menu
        menu = []
        menu.append(SMENU.CMenuParent("File"))
        menu.append(SMENU.CMenuParent("Empire"))
        menu.append(SMENU.CMenuParent("Help"))
        if (SPQR.DEBUG_MODE == True):
            menu.append(SMENU.CMenuParent("Debug"))
        # then add the sub menus below these
        menu[0].addChild(SMENU.CMenuChild("New Game", "new", "Ctrl+N", SEVENT.menuNew))
        menu[0].addChild(SMENU.CMenuChild("sep", None, "", SEVENT.notYetCoded))
        menu[0].addChild(SMENU.CMenuChild("Load Game", "open", "Ctrl+L", SEVENT.menuLoad))
        menu[0].addChild(SMENU.CMenuChild("Save Game", "save", "Ctrl+S", SEVENT.menuSave))
        # this is a seperate, drawn bar to split the text
        menu[0].addChild(SMENU.CMenuChild("sep", None, "", SEVENT.notYetCoded))
        menu[0].addChild(SMENU.CMenuChild("Preferences", "preferences", "Ctrl+P", SEVENT.menuPreferences))
        menu[0].addChild(SMENU.CMenuChild("sep", None, "", SEVENT.notYetCoded))
        menu[0].addChild(SMENU.CMenuChild("Exit SPQR", "exit", "Ctrl+Q", SEVENT.quitSpqr))
        menu[1].addChild(SMENU.CMenuChild("Visit Senate", "senate", "F2", SEVENT.menuEmpireSenate))
        menu[1].addChild(SMENU.CMenuChild("Statistics", "statistics", "", SEVENT.menuEmpireStatistics))
        menu[2].addChild(SMENU.CMenuChild("About", "about", "Ctrl+A", SEVENT.menuHelpAbout))
        menu[2].addChild(SMENU.CMenuChild("sep", None, "", SEVENT.notYetCoded))
        menu[2].addChild(SMENU.CMenuChild("Help", "help", "F1", SEVENT.menuHelpHelp))

        # debug menu is always last - it's easy to remove then
        if SPQR.DEBUG_MODE == True:
            menu[3].addChild(SMENU.CMenuChild("Show unit names", "debug", "", SEVENT.consoleUnitNames))
            menu[3].addChild(SMENU.CMenuChild("Show unit IDs", "debug", "", SEVENT.consoleUnitNumbers))
            menu[3].addChild(SMENU.CMenuChild("Show unit owners", "debug", "", SEVENT.consoleUnitOwners))
            menu[3].addChild(SMENU.CMenuChild("Show example city", "debug", "", SEVENT.showCity))
            menu[3].addChild(SMENU.CMenuChild("sep", "debug", "", SEVENT.notYetCoded))
            menu[3].addChild(SMENU.CMenuChild("Window test", "debug", "", SEVENT.windowTest))
            menu[3].addChild(SMENU.CMenuChild("Widget test", "debug", "", SEVENT.widgetTest))
            menu[3].addChild(SMENU.CMenuChild("sep", "debug", "", SEVENT.notYetCoded))
            menu[3].addChild(SMENU.CMenuChild("Open Console", "debug", "", SEVENT.displayConsole))

        # Add the menubar at the top. It has no drawn window
        # THIS MUST BE THE FIRST WINDOW
        index = SGFX.gui.addWindow(SWINDOW.CWindow(0, 0, 0, 0, "", False, describe="Menus"))
        SGFX.gui.windows[index].border_offset = False
        # add the prepared menu onto this
        SGFX.gui.windows[index].addWidget(SMENU.CMenu(menu))

        # add a window with no frame that holds the widgets to overlay on the map
        bwindow = SWINDOW.CWindow(0, SPQR.SCREEN_HEIGHT - SPQR.BBOX_HEIGHT,
                                  SPQR.SCREEN_WIDTH, SPQR.BBOX_HEIGHT, "",
                                  False, "map_widgets")
        # and the mini-map on the rhs
        w = SGFX.gui.iWidth("small_map")
        h = SGFX.gui.iHeight("small_map")
        x = SPQR.SCREEN_WIDTH - (SGFX.gui.iWidth("small_map") + SPQR.SPACER + bwindow.rect.x)
        y = SPQR.SCREEN_HEIGHT - (SGFX.gui.iHeight("small_map") + (2 * SPQR.SPACER) + 1 + bwindow.rect.y)
        mini_map = SWIDGET.CImage(x, y, w, h, "small_map")
        # allow left mouse button dragging as well (also simulates a mini-map click)
        mini_map.callbacks.mouse_ldown = SEVENT.miniMapDrag
        mini_map.active = True
        mini_map.describe = "mini-map"
        bwindow.addWidget(mini_map)

        image = pygame.Surface(SGFX.gui.image("small_map").get_size()).convert_alpha()
        image.fill(SPQR.BGUI_COL)
        info = SWIDGET.buildUniqueImage(image)
        info.rect.x = SPQR.SPACER
        info.rect.y = y
        info.describe = ("info-box")
        info.visible = False
        bwindow.addWidget(info)
        # we need to store it as well
        SGFX.gui.info_widget = info
        SGFX.gui.map_widget = mini_map

        # complete with centre on rome button
        w = SGFX.gui.iWidth("rome_button")
        h = SGFX.gui.iHeight("rome_button")
        x += SGFX.gui.iWidth("small_map") - w
        y = SPQR.BBOX_HEIGHT - h
        centre_button = SWIDGET.CImage(x, y, w, h, "rome_button")
        centre_button.callbacks.mouse_lclk = SEVENT.centreMap
        centre_button.active = True
        centre_button.describe = "centre button"
        bwindow.addWidget(centre_button)

        # areas for MAX_STACKING units to be displayed
        units = []
        for i in range(SPQR.MAX_STACKING):
            w = SWIDGET.buildImage("rome_legion")
            # set params
            w.describe = "mapunit+" + str(i + 1)
            w.rect.x = 10 + (i * 55)
            w.rect.y = 10
            w.visible = False
            w.active = False
            w.callbacks.mouse_lclk = SEVENT.unitClicked
            units.append(w)
            bwindow.addWidget(w)
        SGFX.gui.unit_widgets = units
        SGFX.gui.addWindow(bwindow)

        # draw the whole screen
        SGFX.gui.updateGUI()
        SGFX.gui.updateMap()
        self.addKeys()
        # make sure Rome is centered and highlighted
        SEVENT.centreMap(0, -1, -1)
        # finally, the last thing we do is start the animation timer
        pygame.time.set_timer(pygame.USEREVENT, SPQR.ANIM_TIME)
        # display the welcome screen if needed
        if self.intro == True:
            # start with intro window displayed
            SEVENT.welcomeScreen(0, 0, 0)

    def addKeys(self):
        """Adds keys needed at the start of the game"""
        # n for next unit, r for rome, i.e. centre the map
        # CTRL-Q for exit, F1 for help; alt-f, alt-e and alt-h for menus
        # n - next unit turn, r - centre map on rome
        # f - finish this units turn, k - display standard keys list;
        SGFX.gui.keyboard.addKey(K_r, SEVENT.centreMap)
        SGFX.gui.keyboard.addKey(K_f, SEVENT.keyMenuFile, KMOD_LALT)
        SGFX.gui.keyboard.addKey(K_e, SEVENT.keyMenuEmpire, KMOD_LALT)
        SGFX.gui.keyboard.addKey(K_h, SEVENT.keyMenuHelp, KMOD_LALT)
        # debug menu added?
        if SPQR.DEBUG_MODE == True:
            SGFX.gui.keyboard.addKey(K_d, SEVENT.keyMenuDebug, KMOD_LALT)
        SGFX.gui.keyboard.addKey(K_ESCAPE, SEVENT.keyMenuEscape)
        # allow map scrolling with curser keys
        SGFX.gui.keyboard.addKey(K_UP, SEVENT.keyScrollUp)
        SGFX.gui.keyboard.addKey(K_DOWN, SEVENT.keyScrollDown)
        SGFX.gui.keyboard.addKey(K_RIGHT, SEVENT.keyScrollRight)
        SGFX.gui.keyboard.addKey(K_LEFT, SEVENT.keyScrollLeft)
        # add menu shortcut keys
        SGFX.gui.keyboard.addKey(K_n, SEVENT.menuNew, KMOD_LCTRL)
        SGFX.gui.keyboard.addKey(K_l, SEVENT.menuLoad, KMOD_LCTRL)
        SGFX.gui.keyboard.addKey(K_s, SEVENT.menuSave, KMOD_LCTRL)
        SGFX.gui.keyboard.addKey(K_p, SEVENT.menuPreferences, KMOD_LCTRL)
        SGFX.gui.keyboard.addKey(K_q, SEVENT.quitSpqr, KMOD_LCTRL)
        SGFX.gui.keyboard.addKey(K_F5, SEVENT.menuEmpireStatistics)
        SGFX.gui.keyboard.addKey(K_a, SEVENT.menuHelpAbout, KMOD_LCTRL)
        SGFX.gui.keyboard.addKey(K_F1, SEVENT.menuHelpHelp)
        SGFX.gui.keyboard.addKey(K_k, SEVENT.keyShowKeys)
        SGFX.gui.keyboard.addKey(K_n, SEVENT.highlightNextUnit)


def main():
    """Setup everything and then run it"""
    game = CSPQR()
    game.setupStart()
    # call the gui main loop
    SGFX.gui.mainLoop()


if __name__ == '__main__':
    main()
