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

# we need some pygame variables:
import pygame.locals as PYGAME

# this file contains the global defines for spqr
# as you can see, there are quite a few. However, most should be left
# as they are, unless you really know what you are doing. Probably the
# most useful when debugging is SPQR_FULLSCREEN

VERSION				= "v0.3.7"
AUTHOR				= "Chris Handy"
EMAIL				= "maximinus@gmail.com"
WEBSITE				= "http://sourceforge.net/projects/spqr/"
STARTED				= "1st Jan 2005"
LAST_UPDATE			= "15th Jan 2011"
CODELINES			= "5757"
FULLSCREEN			= False

# before we go any further, this one is a must ;-)
# currently adds debug menu bar , along with access to
# a python console
DEBUG_MODE		=	True

# now place the equivalent of some(!) defines
SCREEN_WIDTH 		= 800
SCREEN_HEIGHT 		= 600

# set this next one to true if you want a rh mouse click to exit
RMOUSE_END			= True

# menu icons are always squares
ICON_SIZE			= 24
# size of console screen
CONSOLE_WIDTH		= SCREEN_WIDTH
CONSOLE_HEIGHT		= (SCREEN_HEIGHT / 3) * 2
# checkbox size goes here (always a square)
CHKBOX_SIZE			= 13
# size of unit gfx
UNIT_WIDTH			= 45
UNIT_HEIGHT			= 41
# box size for region icons
REGION_ICON_SIZE	= 95

KSCROLL_SPD			= 80
# location of Rome on main (graphical) map
ROME_XPOS			= 1250
ROME_YPOS			= 1150
# maximum number of units in any region
MAX_STACKING		= 4

# sizes of various gradiant bars used in ItemList widget
GRADBAR_SIZES		= [64, 96, 128]
GRADBAR_NAMES		= ["gradbar64", "gradbar96", "gradbar128"]
GRADBAR_WIDTH		= 128

# fonts used by the game
FONT_VERA			= 0
FONT_VERA_SM		= 1
FONT_VERA_LG		= 2
# and their sizes
FONT_SMALL			= 12
FONT_STD			= 14
FONT_LARGE			= 16

# index numbers of windows that are always present
WIN_MENU			= 0

# the images to load
# just list the folders inside gfx: the game will pull all of the png files
GRAPHICS_F			= ["gui", "icons", "units", "cities" ,"map/regions", "units/overlays"]

# milliseconds between unit flash
# (all animation times are in milliseconds)
ANIM_TIME			= 400
# number of milliseconds in-between move animation frames
MOVE_FRAME			= 24
# number of milliseconds between clicks in a double-click (400 is the Gnome standard)
DCLICK_SPEED		= 400

# mouse events as seen by the gui
MOUSE_NONE			= 0
MOUSE_OVER			= 1
MOUSE_LCLK			= 2
MOUSE_RCLK			= 3
MOUSE_DCLICK		= 4
MOUSE_LDOWN			= 5
MOUSE_RDOWN			= 6

# standard buttons that the messagebox function uses
BUTTON_FAIL			= 0
BUTTON_OK			= 1
BUTTON_CANCEL		= 2
BUTTON_YES			= 4
BUTTON_NO			= 8
BUTTON_QUIT			= 16
BUTTON_IGNORE		= 32

# standard widget types
WT_ROOT				= 0
WT_BUTTON			= 1
WT_LABEL			= 2
WT_IMAGE			= 3
WT_SEP				= 4
WT_CHECK			= 5
WT_MENU				= 6
WT_SLIDER			= 7
WT_SCROLLAREA		= 8
WT_ITEMLIST			= 9
WT_OPTMENU			= 10

# text layout types
LEFT_JUSTIFY		= 0
RIGHT_JUSTIFY		= 1
CENTRE_HORIZ		= 2

# height of bottom box from bottom of screen
BBOX_HEIGHT			= 200

# offsets for when we draw a pop-up menu to screen
MENU_X_OFFSET		= 2
MENU_Y_OFFSET		= 23
# amount of pixels left empty on lhs of any menu
MNU_LSPACE			= 4
# amount of pixels padded out above and below a menu entry
# (distance between menu texts is twice this number)
MNU_HSPACE			= 4
# pixels on rhs left blank on menu
MNU_RSPACE			= 8
# minimum gap between menu text and key text in menu dropdown
MNU_KEY_GAP			= 12
# any other random spacing we need
SPACER				= 8
HALFSPCR			= 4
QTRSPCR				= 2
# offsets when overlaying a move value over a unit
MV_OVER_X			= 6
MV_OVER_Y			= 10
# minimum height of scroll area handle
SCAREA_MINH			= 32

# sizes of the window borders
WINSZ_SIDE			= 6
WINSZ_TOP			= 24
WINSZ_BOT			= 6

# alpha is from 0 to 255, where 0 is transparent
MENU_ALPHA			= 64
# colour of the highlight
MENU_HLCOL			= (170, 83, 83)

# game factor designs
# start year is always 1 year before you want the game to start, as
# the start of the first turn will increment it by 1
START_YEAR			= -201

# define all the colours we use as well
BGUI_COL			= (238, 238, 230)
BGUI_HIGH			= (227, 219, 213)
MENU_COL			= (246, 246, 246)
MENU_BDR_COL		= (220, 220, 220)
MENU_CNR_COL		= (194, 194, 194)
MENU_TXT_COL		= (0, 0, 0)
COL_BLACK			= (0, 0, 0)
COL_WHITE			= (255, 255, 255)
COLG_RED			= (171, 84, 84)
COLG_RHIGH			= (254, 120, 120)
COL_BUTTON			= (0, 0, 0)
COL_WINTITLE		= (0, 0, 0)
SLIDER_LIGHT		= (116, 133, 216)
SLIDER_MEDIUM		= (98, 113, 183)
SLIDER_DARK			= (81, 93, 151)
SLIDER_BDARK		= (70, 91, 110)
SLIDER_BLIGHT		= (170, 156, 143)
SLIDER_BMED1		= (192, 181, 169)
SLIDER_BMED2		= (209, 200, 191)
SCROLL_BORDER		= (170, 156, 143)
SCROLL_MIDDLE		= (209, 200, 191)
SEP_DARK			= (154, 154, 154)
SEP_LIGHT			= (248, 252, 248)
OPTM_BDARK			= (190, 190, 180)

# some user events OTHER than that used by unit flash animation
# (which is *always* = pygame.USEREVENT)
EVENT_SONGEND		= PYGAME.USEREVENT + 1
# stop looking for a double-click when we get this event
EVENT_DC_END		= PYGAME.USEREVENT + 2

# some initial values for the sound system
INIT_VOLUME			= 40
MUSIC_BUFFER		= 8192
MUSIC_ON			= True
SFX_ON				= True

# these are the standard callbacks, they should never be called
# they are here to prevent an exception should an unregistered
# event ever be called
def mouse_over_std(handle, x, y):
	print "SPQR Error: mouse_over_std called"
	return False

def mouse_ldown_std(handle, x, y):
	print "SPQR Error: mouse_ldown_std called"
	return False

def mouse_rdown_std(handle,x,y):
	print "SPQR Error: mouse_rdown_std called"
	return False

def mouse_dclick_std(handle, x, y):
	print "SPQR Error: mouse_dclick_std called"
	return False

def mouse_lclk_std(handle, x, y):
	print "SPQR Error: mouse_lclk_std called"
	return False

def mouse_rclk_std(handle, x, y):
	print "SPQR Error: mouse_rclk_std called"
	return False
	
def null_routine(handle, x, y):
	print "SPQR Error: Null routine called"
	return False

