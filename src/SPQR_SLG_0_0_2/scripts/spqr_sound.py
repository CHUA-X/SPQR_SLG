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
import spqr_defines as SPQR

# sound and music routines for SPQR

class CSound(object):
	"""Class stores and sets music parameters"""
	def __init__(self):
		# define the sounds:
		self.music = ["prelude_in_c_major.ogg",
					  "twopart_invention_in_eflat.ogg",
					  "twopart_invention_in_e.ogg"]
		self.volume = SPQR.INIT_VOLUME
		# initially the music is OFF
		self.music_playing = False
		# init all the sound stuff
		# give myself a large buffer, as well (last value), otherwise playback stutters
		pygame.mixer.init(44100, -16, True, 4096)

	def startNextSong(self):
		"""Shuffles songs around, then starts playing the next one"""
		# turn of song events...
		pygame.mixer.music.set_endevent()
		songtitle = self.music.pop()
		self.music.insert(0, songtitle)
		pygame.mixer.music.load("../music/" + songtitle)
		# when new music is loaded, the volume param is reset. Fix it
		pygame.mixer.music.set_volume((float)((float)(self.volume) / 100.0))
		pygame.mixer.music.play()
		# set an endevent to catch it
		pygame.mixer.music.set_endevent(SPQR.EVENT_SONGEND)
		self.music_playing=True
		return True

	def setVolume(self,new_volume):
		"""Sets and inits new volume level"""
		# must be within range 0-100
		if new_volume < 0:
			self.volume = 0
		elif new_volume > 100:
			self.volume = 100
		else:
			self.volume = new_volume
		pygame.mixer.music.set_volume((float)((float)(self.volume) / 100.0))
		return True
	
	def getVolume(self):
		"""Returns value of current volume"""
		return self.volume
	
	def stopMusic(self):
		"""Simply stops the current music"""
		# turn off events as well
		pygame.mixer.music.set_endevent()
		pygame.mixer.music.pause()
		self.music_playing = False
		return True
		
	def startMusic(self):
		"""Turns music back on"""
		pygame.mixer.music.set_endevent(SPQR.EVENT_SONGEND)
		pygame.mixer.music.unpause()
		self.music_playing = True
		return True

sound = CSound()

