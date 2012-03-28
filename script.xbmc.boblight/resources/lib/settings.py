# -*- coding: utf-8 -*- 
'''
    Boblight for XBMC
    Copyright (C) 2012 Team XBMC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import xbmc, xbmcgui

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__addon__      = sys.modules[ "__main__" ].__addon__
__cwd__        = sys.modules[ "__main__" ].__cwd__
__icon__       = sys.modules[ "__main__" ].__icon__
__language__   = sys.modules[ "__main__" ].__language__


from boblight import *
from tools import log
from ctypes import *

class settings():
  def __init__( self, *args, **kwargs ):
    log('__init__')
    self.start()
    
  def start(self):
    log('start')
    self.saturation                 = -1.0 
    self.value                      = -1.0
    self.speed                      = -1.0
    self.autospeed                  = -1.0
    self.interpolation              = -1
    self.threshold                  = -1.0
    self.bobdisable                 = -1
    self.staticBobActive            = False
    self.category                   = "other"
    self.networkaccess              = __addon__.getSetting("networkaccess") == "true"
    self.overwrite_cat              = __addon__.getSetting("overwrite_cat") == "true"
    self.overwrite_cat_val          = int(__addon__.getSetting("overwrite_cat_val"))
    self.other_static_bg            = __addon__.getSetting("other_static_bg") == "true"
    self.other_static_red           = int(float(__addon__.getSetting("other_static_red")))
    self.other_static_green         = int(float(__addon__.getSetting("other_static_green")))
    self.other_static_blue          = int(float(__addon__.getSetting("other_static_blue")))
    self.other_static_onscreensaver = __addon__.getSetting("other_static_onscreensaver") == "true"

    if not self.networkaccess:
      self.hostip   = None
      self.hostport = -1
    else:
      self.hostip          = __addon__.getSetting("hostip")
      self.hostport        = int(__addon__.getSetting("hostport"))    

  #configures boblight for the initial bling bling
  def confForBobInit(self):
    log('confForBobInit')
    saturation,value,speed,autospeed,interpolation,threshold = self.setupForStatic()
    bob_setoption("saturation    " + str(saturation))
    bob_setoption("value         " + str(value))
    bob_setoption("speed         " + str(speed))
    bob_setoption("autospeed     " + str(autospeed))
    bob_setoption("interpolation " + str(interpolation))
    bob_setoption("threshold     " + str(threshold))

  #handle boblight configuration from the "Movie" category
  #returns the new settings
  def setupForMovie(self):
    log('setupForMovie') 
    preset = int(__addon__.getSetting("movie_preset"))
  
    if preset == 1:       #preset smooth
      saturation    = 3.0
      value         = 10.0
      speed         = 20.0
      autospeed     = 0.0 
      interpolation = 0
      threshold     = 0.0
    elif preset == 2:     #preset action
      saturation    = 3.0
      value         = 10.0
      speed         = 80.0
      autospeed     = 0.0  
      interpolation = 0
      threshold     = 0.0
    elif preset == 0:     #custom
      saturation      =  float(__addon__.getSetting("movie_saturation"))
      value           =  float(__addon__.getSetting("movie_value"))
      speed           =  float(__addon__.getSetting("movie_speed"))
      autospeed       =  float(__addon__.getSetting("movie_autospeed"))
      interpolation   =  __addon__.getSetting("movie_interpolation") == "true"
      threshold       =  float(__addon__.getSetting("movie_threshold"))
    return (saturation,value,speed,autospeed,interpolation,threshold)
  
  #handle boblight configuration from the "MusicVideo" category
  #returns the new settings
  def setupForMusicVideo(self):
    log('setupForMusicVideo')
    preset = int(__addon__.getSetting("musicvideo_preset"))
  
    if preset == 1:       #preset Ballad
      saturation    = 3.0
      value         = 10.0
      speed         = 20.0  
      autospeed     = 0.0
      interpolation = 1
      threshold     = 0.0
    elif preset == 2:     #preset Rock
      saturation    = 3.0
      value         = 10.0
      speed         = 80.0
      autospeed     = 0.0  
      interpolation = 0
      threshold     = 0.0
    elif preset == 0:     #custom
      saturation      =  float(__addon__.getSetting("musicvideo_saturation"))
      value           =  float(__addon__.getSetting("musicvideo_value"))
      speed           =  float(__addon__.getSetting("musicvideo_speed"))
      autospeed       =  float(__addon__.getSetting("movie_autospeed"))
      interpolation   =  __addon__.getSetting("musicvideo_interpolation") == "true"
      threshold       =  float(__addon__.getSetting("musicvideo_threshold"))
    return (saturation,value,speed,autospeed,interpolation,threshold)
  
  #handle boblight configuration from the "other" category
  #returns the new settings
  def setupForOther(self):
    log('setupForOther')
  # FIXME don't use them for now - reactivate when boblight works on non rendered scenes (e.x. menu)
  #  saturation      =  float(__addon__.getSetting("other_saturation"))
  #  value           =  float(__addon__.getSetting("other_value"))
  #  speed           =  float(__addon__.getSetting("other_speed"))
  #  autospeed       =  float(__addon__.getSetting("other_autospeed"))
  #  interpolation   =  __addon__.getSetting("other_interpolation") == "true"
  #  threshold       =  float(__addon__.getSetting("other_threshold"))
    return self.setupForStatic()
  
  #handle boblight configuration for static lights
  #returns the new settings
  def setupForStatic(self):
    log('setupForStatic')
    saturation    = 4.0
    value         = 1.0
    speed         = 50.0
    autospeed     = 0.0 
    interpolation = 1
    threshold     = 0.0
    return (saturation,value,speed,autospeed,interpolation,threshold)

  #handle all settings according to the static bg light
  #this is used until category "other" can do real boblight
  #when no video is rendered
  #category - the category we are in currently
  def handleStaticBgSettings(self):
    if (self.category == "other" and 
            self.other_static_bg and 
            not self.bobdisable and 
            (not xbmc.getCondVisibility("System.ScreenSaverActive") and not self.other_static_onscreensaver)
            ):#for now enable static light on other if settings want this
      bob_set_priority(128)                                  #allow lights to be turned on
      rgb = (c_int * 3)(self.other_static_red,self.other_static_green,self.other_static_blue)
      bob_set_static_color(byref(rgb))
      self.staticBobActive = True
    else:
      self.staticBobActive = False

  #handles the boblight configuration of all categorys
  #and applies changed settings to boblight
  #"movie","musicvideo" and "other
  #returns if a setting has been changed
  def handleGlobalSettings(self):
    log('handleGlobalSettings - category [%s]' % self.category)
    #call the right setup function according to categroy
    #switch case in python - dictionary with function pointers
    option = { "movie"      : self.setupForMovie,
               "musicvideo" : self.setupForMusicVideo,
               "other"      : self.setupForOther,
    }
    self.saturation,self.value,self.speed,self.autospeed,self.interpolation,self.threshold = option[self.category]()
  
  #handle change of category we are in
  #"movie","musicvideo" or "other"
  #returns if category has changed  
  def handleCategory(self, category):
    log('handleCategory(%s)' % category)
    self.category = category
    log("boblight: use settings for %s" % category)
    self.handleStaticBgSettings()
    if not self.staticBobActive:
      self.handleGlobalSettings()

  
  #handle bob disable setting
  #sets the global g_bobdisable and prints
  #toast dialog on disable
  def handleDisableSetting(self):
    self.bobdisable = __addon__.getSetting("bobdisable") == "true"

  def run_all(self):
    self.handleStaticBgSettings()


                



