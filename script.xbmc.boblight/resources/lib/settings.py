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
__ID__   = sys.modules[ "__main__" ].__ID__

from boblight import *
from tools import log

bob = Boblight()

class settings():
  def __init__( self, *args, **kwargs ):
    log('settings() - __init__')
    self.staticBobActive            = False
    self.category                   = "static"
    self.start()
     
  def start(self):
    log('settings() - start')
    self.force_update               = True    
    self.networkaccess              = __addon__.getSetting("networkaccess") == "true"
    self.overwrite_cat              = __addon__.getSetting("overwrite_cat") == "true"
    self.overwrite_cat_val          = int(__addon__.getSetting("overwrite_cat_val"))
    self.screensaver                = xbmc.getCondVisibility("System.ScreenSaverActive")
    self.bobdisable                 = __addon__.getSetting("bobdisable") == "true"
    self.current_option             = ""
    
    if not self.networkaccess:
      self.hostip   = None
      self.hostport = -1
    else:
      self.hostip                   = __addon__.getSetting("hostip")
      self.hostport                 = int(__addon__.getSetting("hostport"))
    
    # Other settings
    self.other_static_bg            = __addon__.getSetting("other_static_bg") == "true"
    self.other_static_red           = int(float(__addon__.getSetting("other_static_red")))
    self.other_static_green         = int(float(__addon__.getSetting("other_static_green")))
    self.other_static_blue          = int(float(__addon__.getSetting("other_static_blue")))
    self.other_static_onscreensaver = __addon__.getSetting("other_static_onscreensaver") == "true"
    
    # Movie settings
    self.movie_saturation           = float(__addon__.getSetting("movie_saturation"))
    self.movie_value                = float(__addon__.getSetting("movie_value"))
    self.movie_speed                = float(__addon__.getSetting("movie_speed"))
    self.movie_autospeed            = float(__addon__.getSetting("movie_autospeed"))
    self.movie_interpolation        = int(__addon__.getSetting("movie_interpolation") == "true")
    self.movie_threshold            = float(__addon__.getSetting("movie_threshold"))
    self.movie_preset               = int(__addon__.getSetting("movie_preset"))
    
    # Music Video settings
    self.music_saturation           = float(__addon__.getSetting("musicvideo_saturation"))
    self.music_value                = float(__addon__.getSetting("musicvideo_value"))
    self.music_speed                = float(__addon__.getSetting("musicvideo_speed"))
    self.music_autospeed            = float(__addon__.getSetting("movie_autospeed"))
    self.music_interpolation        = int(__addon__.getSetting("musicvideo_interpolation") == "true")
    self.music_threshold            = float(__addon__.getSetting("musicvideo_threshold"))
    self.music_preset               = int(__addon__.getSetting("musicvideo_preset"))

  #handle boblight configuration from the "Movie" category
  #returns the new settings
  def setupForMovie(self):
    log('settings() - setupForMovie')
  
    if self.movie_preset == 1:       #preset smooth
      saturation    = 3.0
      value         = 10.0
      speed         = 20.0
      autospeed     = 0.0 
      interpolation = 0
      threshold     = 0.0
    elif self.movie_preset == 2:     #preset action
      saturation    = 3.0
      value         = 10.0
      speed         = 80.0
      autospeed     = 0.0  
      interpolation = 0
      threshold     = 0.0
    elif self.movie_preset == 0:     #custom
      saturation      =  self.movie_saturation
      value           =  self.movie_value
      speed           =  self.movie_speed
      autospeed       =  self.movie_autospeed
      interpolation   =  self.movie_interpolation
      threshold       =  self.movie_threshold
    return (saturation,value,speed,autospeed,interpolation,threshold)
  
  #handle boblight configuration from the "MusicVideo" category
  #returns the new settings
  def setupForMusicVideo(self):
    log('settings() - setupForMusicVideo')
  
    if self.music_preset == 1:       #preset Ballad
      saturation    = 3.0
      value         = 10.0
      speed         = 20.0  
      autospeed     = 0.0
      interpolation = 1
      threshold     = 0.0
    elif self.music_preset == 2:     #preset Rock
      saturation    = 3.0
      value         = 10.0
      speed         = 80.0
      autospeed     = 0.0  
      interpolation = 0
      threshold     = 0.0
    elif self.music_preset == 0:     #custom
      saturation      =  self.movie_saturation
      value           =  self.movie_value
      speed           =  self.movie_speed
      autospeed       =  self.movie_autospeed
      interpolation   =  self.movie_interpolation
      threshold       =  self.movie_threshold    
    return (saturation,value,speed,autospeed,interpolation,threshold)
  
  #handle boblight configuration from the "other" category
  #returns the new settings
  def setupForOther(self):
    log('settings() - setupForOther')
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
    log('settings() - setupForStatic')
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
    log('settings() - handleStaticBgSettings')
    if (self.category == "other" and 
            self.other_static_bg and  
            (not (self.screensaver and self.other_static_onscreensaver))
            ):#for now enable static light on other if settings want this
      bob.bob_set_priority(128)                                  #allow lights to be turned on
      rgb = (c_int * 3)(self.other_static_red,self.other_static_green,self.other_static_blue)
      ret = bob.bob_set_static_color(byref(rgb))
      log('settings() - bob.bob_set_static_color = %s' % ret)
      self.staticBobActive = True
      log('settings() - handleStaticBgSettings[Active]')
    else:
      self.staticBobActive = False

  #handles the boblight configuration of all categorys
  #and applies changed settings to boblight
  #"movie","musicvideo" and "other
  #returns if a setting has been changed
  def handleGlobalSettings(self):
    log('settings() - handleGlobalSettings')
    #call the right setup function according to categroy
    #switch case in python - dictionary with function pointers
    option = { "movie"      : self.setupForMovie,
               "musicvideo" : self.setupForMusicVideo,
               "other"      : self.setupForOther,
               "static"     : self.setupForStatic, 
    }
    saturation,value,speed,autospeed,interpolation,threshold = option[self.category]()
    self.set_option(saturation,value,speed,autospeed,interpolation,threshold)
  
  #handle change of category we are in
  #"movie","musicvideo" or "other"
  #returns if category has changed  
  def handleCategory(self, category):
    log('settings() - handleCategory(%s)' % category)
    self.category = category
    self.handleGlobalSettings()
    self.handleStaticBgSettings()
      
    
  def set_option(self,saturation,value,speed,autospeed,interpolation,threshold):
    if (self.current_option != self.category) or self.force_update:
      log('settings() - set_option')
      ret = bob.bob_setoption("saturation    %s" % str(saturation))
      log("changed saturation    to %s (ret: %s)" % (str(saturation),ret))
      ret = bob.bob_setoption("value         %s" % str(value))
      log("changed value         to %s (ret: %s)" % (str(value),ret))
      ret = bob.bob_setoption("speed         %s" % str(speed))
      log("changed speed         to %s (ret: %s)" % (str(speed),ret))
      ret = bob.bob_setoption("autospeed     %s" % str(autospeed))
      log("changed autospeed     to %s (ret: %s)" % (str(autospeed),ret))
      ret = bob.bob_setoption("interpolation %s" % str(interpolation))
      log("changed interpolation to %s (ret: %s)" % (str(interpolation),ret))
      ret = bob.bob_setoption("threshold     %s" % str(threshold))
      log("changed threshold     to %s (ret: %s)" % (str(threshold),ret))
      
      self.current_option = self.category
      self.force_update = False

  #configures boblight for the initial bling bling
  def confForBobInit(self):
    log('confForBobInit')
    nrLights = bob.bob_getnrlights()
    log("settings() - Found %s lights" % str(nrLights))
    for i in range(0, nrLights):
      lightname = bob.bob_getlightname(i)
      log(lightname)
    
    self.handleGlobalSettings()

    bob.bob_set_priority(128)           #allow lights to be turned on
    rgb = (c_int * 3)(255,0,0)
    bob.bob_set_static_color(byref(rgb))
    xbmc.sleep(1500)
    rgb = (c_int * 3)(0,255,0)
    bob.bob_set_static_color(byref(rgb))
    xbmc.sleep(1500)
    rgb = (c_int * 3)(0,0,255)
    bob.bob_set_static_color(byref(rgb))
    xbmc.sleep(1500)
    rgb = (c_int * 3)(0,0,0)
    bob.bob_set_static_color(byref(rgb))
    xbmc.sleep(1500)
    bob.bob_set_priority(255)           #turn the lights off   

