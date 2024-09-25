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

# setup code for game
# for now, you can only set the game resolution

import sys, pygame
from pygame.locals import *

from scripts import spqr_defines as SPQR
from scripts import spqr_gui as SGFX
from scripts import spqr_window as SWINDOW
from scripts import spqr_widgets as SWIDGET
from scripts import spqr_ybuild as SYAML

SCREEN_WIDTH = 285
SCREEN_HEIGHT = 192

def setupWindow():
	SYAML.createWindow("../data/layouts/setup_window.yml")

def setupWindow2():
	# get a fullsize window, and add the options to it
	window = SWINDOW.CWindow(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
							 "", False, "main-window")
	window.fillWindowImage()
	# an optionmenu, a label, a seperator and 2 buttons
	label1 = SWIDGET.buildLabel("Resolution")
	label1.rect.x = 29
	label1.rect.y = 26
	
	label2 = SWIDGET.buildLabel("Play Music")
	label2.rect.x = 32
	label2.rect.y = 64
	music = SWIDGET.CCheckBox(140, 64, True)
	
	label3 = SWIDGET.buildLabel("Show intro")
	label3.rect.x = 30
	label3.rect.y = 100
	intro = SWIDGET.CCheckBox(140, 100, True)
	
	options = SWIDGET.COptionMenu(124, 20, ["800x600", "1024x768", "Fullscreen"])
	options.describe = "opt-Resolution"
	
	sepbar = SWIDGET.CSeperator(6 ,label1.rect.y + 106, SCREEN_WIDTH - 9)
	
	ok_button = SWIDGET.CButton(165, 148, "OK")
	ok_button.callbacks.mouse_lclk = okClick
	
	cancel_button = SWIDGET.CButton(50, 148, "Cancel")
	cancel_button.callbacks.mouse_lclk = cancelClick
	
	for i in [options, label1, label2, music, label3, intro,
			   sepbar, ok_button, cancel_button]:
		i.active = True
		window.addWidget(i)
	# only 1 window, set it modal
	window.modal = True
	SGFX.gui.addWindow(window)

if __name__ == "__main__":
	SGFX.gui.mainInit(SCREEN_WIDTH, SCREEN_HEIGHT, False, False)
	setupWindow()
	SGFX.gui.updateGUI()
	SGFX.gui.mainLoop()

