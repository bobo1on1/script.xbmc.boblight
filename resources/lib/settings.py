'''
    Boblight for XBMC
    Copyright (C) 2011 Team XBMC

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
import time
import xbmc
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__settings__   = sys.modules[ "__main__" ].__settings__
__cwd__        = sys.modules[ "__main__" ].__cwd__
__icon__       = sys.modules[ "__main__" ].__icon__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
sys.path.append (__cwd__)

from boblight import *

global g_networkaccess
global g_hostip
global g_hostport
global g_saturation 
global g_value 
global g_speed 
global g_autospeed 
global g_interpolation 
global g_threshold
global g_timer
global g_category
global g_bobdisable

def settings_initGlobals():
  global g_networkaccess
  global g_hostip
  global g_hostport  
  global g_saturation 
  global g_value 
  global g_speed 
  global g_autospeed 
  global g_interpolation 
  global g_threshold
  global g_networkaccess
  global g_hostip
  global g_hostport  
  global g_timer
  global g_category
  global g_bobdisable

  g_networkaccess  = False
  g_hostip         = "127.0.0.1"
  g_hostport       = None
  g_saturation     = -1.0 
  g_value          = -1.0
  g_speed          = -1.0
  g_autospeed      = -1.0
  g_interpolation  = -1
  g_threshold      = -1.0
  g_networkaccess  = __settings__.getSetting("networkaccess") == "true"
  g_hostip         = __settings__.getSetting("hostip")
  g_hostport       = int(__settings__.getSetting("hostport"))  
  g_timer          = time.time()
  g_category       = "movie"
  g_bobdisable     = -1
  
  if not g_networkaccess:
    g_hostip   = None
    g_hostport = -1

def settings_getHostIp():
  global g_hostip
  return g_hostip

def settings_getHostPort():
  global g_hostport
  return g_hostport 

def settings_getBobDisable():
  global g_bobdisable
  return g_bobdisable

def settings_loadForBobInit():
  saturation    = 4.0
  value         = 1.0
  speed         = 35.0
  autospeed     = 0.0 
  interpolation = 1
  threshold     = 0.0
  bob_setoption("saturation    " + str(saturation))
  bob_setoption("value         " + str(value))
  bob_setoption("speed         " + str(speed))
  bob_setoption("autospeed     " + str(autospeed))
  bob_setoption("interpolation " + str(interpolation))
  bob_setoption("threshold     " + str(threshold))

def settings_getSettingCategory():                 
  ret = "other"

  playing = xbmc.getCondVisibility("Player.HasVideo")

  if playing:		#we play something
    ret = "movie"
    musicvideo = xbmc.getCondVisibility("VideoPlayer.Content(musicvideos)")
    if musicvideo:
      ret = "musicvideo"
  return ret
  
def settings_checkForNewSettings():
#todo  for now impl. stat on addon.getAddonInfo('profile')/settings.xml and use mtime
#check for new settings every 5 secs
  global g_timer
  reconnect = False

  if time.time() - g_timer > 5:
    if settings_setup():
      reconnect = True
    g_timer = time.time()
  return reconnect
        
def settings_setupForMovie(): 
  preset = int(__settings__.getSetting("movie_preset"))

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
    saturation      =  float(__settings__.getSetting("movie_saturation"))
    value           =  float(__settings__.getSetting("movie_value"))
    speed           =  float(__settings__.getSetting("movie_speed"))
    autospeed       =  float(__settings__.getSetting("movie_autospeed"))
    interpolation   =  __settings__.getSetting("movie_interpolation") == "true"
    threshold       =  float(__settings__.getSetting("movie_threshold"))
  return (saturation,value,speed,autospeed,interpolation,threshold)

def settings_setupForMusicVideo():
  preset = int(__settings__.getSetting("musicvideo_preset"))

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
    saturation      =  float(__settings__.getSetting("musicvideo_saturation"))
    value           =  float(__settings__.getSetting("musicvideo_value"))
    speed           =  float(__settings__.getSetting("musicvideo_speed"))
    autospeed       =  float(__settings__.getSetting("movie_autospeed"))
    interpolation   =  __settings__.getSetting("musicvideo_interpolation") == "true"
    threshold       =  float(__settings__.getSetting("musicvideo_threshold"))
  return (saturation,value,speed,autospeed,interpolation,threshold)

def settings_setupForOther():
  saturation      =  float(__settings__.getSetting("other_saturation"))
  value           =  float(__settings__.getSetting("other_value"))
  speed           =  float(__settings__.getSetting("other_speed"))
  autospeed       =  float(__settings__.getSetting("movie_autospeed"))
  interpolation   =  __settings__.getSetting("other_interpolation") == "true"
  threshold       =  float(__settings__.getSetting("other_threshold"))
  return (saturation,value,speed,autospeed,interpolation,threshold)

def settings_setup():
  global g_networkaccess
  global g_hostip
  global g_hostport
  global g_saturation 
  global g_value 
  global g_speed 
  global g_autospeed 
  global g_interpolation 
  global g_threshold
  global g_timer
  global g_failedConnectionNotified
  global g_category
  global g_bobdisable
  reconnect = False
  settingChanged = False
  categoryChanged = False
  bobdisable  = __settings__.getSetting("bobdisable") == "true"

#switch case in python - dictionary with function pointers
  option = { "movie"      : settings_setupForMovie,
             "musicvideo" : settings_setupForMusicVideo,
             "other"      : settings_setupForOther,
  }
#call the right setup function according to categroy
  category = settings_getSettingCategory()
  saturation,value,speed,autospeed,interpolation,threshold = option[category]()
  
  if g_category != category:
    categoryChanged = True				#don't change notify when category changes
    print "boblight: use settings for " + category
    g_category = category
 
  networkaccess = __settings__.getSetting("networkaccess") == "true"
  hostip = __settings__.getSetting("hostip")
  hostport = int(__settings__.getSetting("hostport"))

#server settings
  #we need to reconnect if networkaccess bool changes
  #or if network access is enabled and ip or port have changed
  if g_networkaccess != networkaccess or ((g_hostip != hostip or g_hostport != hostport) and g_networkaccess) :
    print "boblight: changed networkaccess to " + str(networkaccess)
    g_networkaccess = networkaccess

    if not networkaccess:
      g_hostip = None
      g_hostport = -1
    else:
      if g_hostip != hostip:
        print "boblight: changed hostip to " + str(hostip)
        g_hostip = hostip
    
      if g_hostport != hostport:
        print "boblight: changed hostport to " + str(hostport)
        g_hostport = hostport
  
    g_failedConnectionNotified = False
    reconnect = True

#setup boblight - todo error checking
  if g_saturation != saturation:  
    ret = bob_setoption("saturation    " + str(saturation))
    settingChanged = True
    print "boblight: changed saturation to " + str(saturation) + "(ret " + str(ret) + ")"
    g_saturation = saturation
  
  if g_value != value:  
    ret = bob_setoption("value         " + str(value))
    settingChanged = True
    print "boblight: changed value to " + str(value) + "(ret " + str(ret) + ")"
    g_value = value

  if g_speed != speed:  
    ret = bob_setoption("speed         " + str(speed))
    settingChanged = True
    print "boblight: changed speed to " + str(speed) + "(ret " + str(ret) + ")"
    g_speed = speed

  if g_autospeed != autospeed:  
    ret = bob_setoption("autospeed     " + str(autospeed))
    settingChanged = True
    print "boblight: changed autospeed to " + str(autospeed) + "(ret " + str(ret) + ")"
    g_autospeed = autospeed

  if g_interpolation != interpolation:  
    ret = bob_setoption("interpolation " + str(interpolation))
    settingChanged = True
    print "boblight: changed interpolation to " + str(interpolation) + "(ret " + str(ret) + ")"
    g_interpolation = interpolation

  if g_threshold != threshold:  
    ret = bob_setoption("threshold     " + str(threshold))
    settingChanged = True
    print "boblight: changed threshold to " + str(threshold) + "(ret " + str(ret) + ")"
    g_threshold = threshold
    
  if g_bobdisable != bobdisable:
    if bobdisable:
      text = __settings__.getLocalizedString(503)
      xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))
      print "boblight: boblight disabled"
    else:
      print "boblight: boblight enabled"
    g_bobdisable = bobdisable

  if settingChanged and not categoryChanged:
    text = __settings__.getLocalizedString(502)
    xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))

  return reconnect
