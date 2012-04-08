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
__ID__         = __addon__.getAddonInfo('id')
__language__   = __addon__.getLocalizedString

__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )

sys.path.append (__resource__)

from settings import *
from tools import *

log( "[%s] - Version: %s Started" % (__scriptname__,__version__))

capture_width = 32
capture_height = 32

settings = settings()

class MyPlayer( xbmc.Player ):
    def __init__( self, *args, **kwargs ):
        xbmc.Player.__init__( self )
        log('MyPlayer - init')
        self.function = kwargs[ "function" ]
        self.function( 'stop' )
          
    def onPlayBackStopped( self ):
        self.function( 'stop' )
    
    def onPlayBackEnded( self ):
        self.function( 'stop' )     
    
    def onPlayBackStarted( self ):
        self.function( 'start' )

class MyMonitor( xbmc.Monitor ):
    def __init__( self, *args, **kwargs ):
        xbmc.Monitor.__init__( self )
        log('MyMonitor - init')
          
    def onSettingsChanged( self ):
        settings.start()
        settings.handleGlobalSettings()
        settings.handleStaticBgSettings()
        
    def onScreensaverDeactivated( self ):
        settings.screensaver = False
        settings.handleStaticBgSettings()
        
    def onScreensaverActivated( self ):    
        settings.screensaver = True
        settings.handleStaticBgSettings()


def process_boblight():
  capture = xbmc.RenderCapture()
  capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)
  xbmc_monitor   = MyMonitor()
  player_monitor = MyPlayer(function=myPlayerChanged)
  
  bobdisable = False
  while not xbmc.abortRequested:
    xbmc.sleep(100)
    if not settings.bobdisable:
      bobdisable = True
      if not bob.bob_ping():
        connectBoblight()
        
      capture.waitForCaptureStateChangeEvent(1000)
      if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
        if not bob.bob_set_priority(128):
          return
  
        width = capture.getWidth();
        height = capture.getHeight();
        pixels = capture.getImage();
        bob.bob_setscanrange(width, height)
        rgb = (c_int * 3)()
        for y in range(height):
          row = width * y * 4
          for x in range(width):
            rgb[0] = pixels[row + x * 4 + 2]
            rgb[1] = pixels[row + x * 4 + 1]
            rgb[2] = pixels[row + x * 4]
            bob.bob_addpixelxy(x, y, byref(rgb))
  
        if not bob.bob_sendrgb():
          log("error sending values: %s" % bob.bob_geterror())
          return
      else:
        if not settings.staticBobActive:  #don't kill the lights in accident here
          if not bob.bob_set_priority(255):
            return
            
    elif bobdisable:
      log('boblight disabled in Addon Settings')
      bobdisable = False
      bob.bob_set_priority(255)
                       
  bob.bob_set_priority(255) # we are shutting down, kill the LEDs
  xbmc.sleep(50)
  del player_monitor
  xbmc.sleep(50)
  del xbmc_monitor

def connectBoblight():  
  failedConnectionNotified = False 
  hostip   = settings.hostip
  hostport = settings.hostport
  
  if hostip == None:
    log("connecting to local boblightd")
  else:
    log("connecting to boblightd %s:%s" % (hostip, str(hostport)))

  while not xbmc.abortRequested:
    ret = bob.bob_connect(hostip, hostport)

    if not ret:
      log("connection to boblightd failed: %s" % bob.bob_geterror())
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
  xbmc.sleep(500)
  if state == 'stop':
    ret = "other"
  else:
    if xbmc.getCondVisibility("VideoPlayer.Content(musicvideos)"):
      ret = "musicvideo"
    else:
      ret = "movie"  
  
    if settings.overwrite_cat:				          # fix his out when other isn't
      if settings.overwrite_cat_val == 0:       # the static light anymore
        ret = "movie"
      else:
        ret = "musicvideo"
  settings.handleCategory(ret)


if ( __name__ == "__main__" ):
  platform = get_platform()
  libpath  = get_libpath(platform)
  loaded   = bob.bob_loadLibBoblight(libpath)
  
  if loaded == 1:                                #libboblight not found                                               
    if platform == 'osx' or platform == 'win32': # ask user if we should fetch the
      t1 = __language__(504)                     # lib for osx and windows
      t2 = __language__(509)
      if xbmcgui.Dialog().yesno(__scriptname__,t1,t2):
        tools_downloadLibBoblight(platform)
        loaded = bob.bob_loadLibBoblight(libpath)
    
    elif platform == 'linux':
      t1 = __language__(504)
      t2 = __language__(505)
      t3 = __language__(506)
      xbmcgui.Dialog().ok(__scriptname__,t1,t2,t3)
      
  elif loaded == 2:         #no ctypes available
    t1 = __language__(507)
    t2 = __language__(508)
    xbmcgui.Dialog().ok(__scriptname__,t1,t2) 
  
  elif loaded == 0:
    if connectBoblight():
      settings.confForBobInit()      #init light bling bling
      process_boblight()             #boblight loop
       
  #cleanup
  bob.bob_destroy()


