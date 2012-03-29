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
import xbmc
import xbmcaddon
import xbmcgui
import os

__addon__      = xbmcaddon.Addon()
__cwd__        = __addon__.getAddonInfo('path')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__icon__       = __addon__.getAddonInfo('icon')
__language__   = __addon__.getLocalizedString

__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )

sys.path.append (__resource__)

import settings

from boblight import *
from tools import *

log( "[%s] - Version: %s Started" % (__scriptname__,__version__))

capture_width = 32
capture_height = 32

settings = settings.settings()

class MyPlayer( xbmc.Player ):
    def __init__( self, *args, **kwargs ):
        xbmc.Player.__init__( self )
        self.function = kwargs[ "function" ]
        self.function( 'stop' )
          
    def onPlayBackStopped( self ):
        self.function( 'stop' )
    
    def onPlayBackEnded( self ):
        self.function( 'stop' )     
    
    def onPlayBackStarted( self ):
        self.function( 'start' )

def process_boblight():
  capture = xbmc.RenderCapture()
  capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)
  player_monitor = MyPlayer(function=myPlayerChanged)
  while not xbmc.abortRequested or settings.bobdisable: 
    
    xbmc.sleep(50)
    settings.handleStaticBgSettings()

    if not bob_ping():
      reconnectBoblight()
      
    capture.waitForCaptureStateChangeEvent(1000)
    if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
      if not bob_set_priority(128):
        return

      width = capture.getWidth();
      height = capture.getHeight();
      pixels = capture.getImage();
      bob_setscanrange(width, height)
      rgb = (c_int * 3)()
      for y in range(height):
        row = width * y * 4
        for x in range(width):
          rgb[0] = pixels[row + x * 4 + 2]
          rgb[1] = pixels[row + x * 4 + 1]
          rgb[2] = pixels[row + x * 4]
          bob_addpixelxy(x, y, byref(rgb))

      if not bob_sendrgb():
        log("boblight: error sending values: %s" % bob_geterror())
        return
    else:
      if not settings.staticBobActive:  #don't kill the lights in accident here
        if not bob_set_priority(255):
          return
          
  bob_set_priority(255) # we are shutting down, kill the LEDs
  xbmc.sleep(50)
  del player_monitor
  
def printLights():
  nrLights = bob_getnrlights()
  log("Found %s lights" % str(nrLights))

  for i in range(0, nrLights):
    lightname = bob_getlightname(i)
    log(lightname)

#do a initial bling bling with the lights
def showRgbBobInit():
  settings.confForBobInit()
  bob_set_priority(128)   #allow lights to be turned on
  rgb = (c_int * 3)(255,0,0)
  bob_set_static_color(byref(rgb))
  xbmc.sleep(1500)
  rgb = (c_int * 3)(0,255,0)
  bob_set_static_color(byref(rgb))
  xbmc.sleep(1500)
  rgb = (c_int * 3)(0,0,255)
  bob_set_static_color(byref(rgb))
  xbmc.sleep(1500)
  rgb = (c_int * 3)(0,0,0)
  bob_set_static_color(byref(rgb))
  xbmc.sleep(1500)
  bob_set_priority(255) #turn the lights off 

def reconnectBoblight():
  
  failedConnectionNotified = False 
  hostip   = settings.hostip
  hostport = settings.hostport
  
  if hostip == None:
    log("connecting to local boblightd")
  else:
    log("connecting to boblightd %s:%s" % (hostip, str(hostport)))

  while not xbmc.abortRequested:
    ret = bob_connect(hostip, hostport)

    if not ret:
      log("connection to boblightd failed: %s" % bob_geterror())
      count = 10
      while (not xbmc.abortRequested) and (count > 0):
        xbmc.sleep(1000)
        count -= 1
      if not failedConnectionNotified:
        failedConnectionNotified = True
        text = __language__(500)
        xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))
    else:
      text = __language__(501)
      xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))
      log("connected to boblightd")
      break
  return True

def myPlayerChanged(state):
  log('PlayerChanged(%s)' % state)
  if state == 'stop':
    ret = "other"
  else:
    if xbmc.getCondVisibility("VideoPlayer.Content(musicvideos)"):
      ret = "musicvideo"
    else:
      ret = "movie"  
    
    if settings.overwrite_cat:				#fix his out when other isn't the static light anymore
      if settings.overwrite_cat_val == 0:
        ret = "movie"
      else:
        ret = "musicvideo"
  settings.handleCategory(ret, True)

platform = get_platform()
libpath  = get_libpath(platform)
loaded   = bob_loadLibBoblight(libpath)

if loaded == 1:            #libboblight not found
#ask user if we should fetch the lib for osx and windows
  if platform == 'osx' or platform == 'win32':
    t1 = __language__(504)
    t2 = __language__(509)
    if xbmcgui.Dialog().yesno(__scriptname__,t1,t2):
      tools_downloadLibBoblight(platform)
      loaded = bob_loadLibBoblight(libpath)
  
  if platform == 'linux':
    t1 = __language__(504)
    t2 = __language__(505)
    t3 = __language__(506)
    xbmcgui.Dialog().ok(__scriptname__,t1,t2,t3)
elif loaded == 2:        #no ctypes available
  t1 = __language__(507)
  t2 = __language__(508)
  xbmcgui.Dialog().ok(__scriptname__,t1,t2) 

if loaded == 0:
  if reconnectBoblight():
    printLights()         #print found lights to debuglog
    showRgbBobInit()      #init light bling bling
    process_boblight()    #boblight loop

#cleanup
bob_destroy()


