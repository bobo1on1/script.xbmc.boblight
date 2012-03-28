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
import time
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

from boblight import *
from settings import *
from tools import *

log( "[%s] - Version: %s Started" % (__scriptname__,__version__))

global g_failedConnectionNotified

capture_width = 32
capture_height = 32

def process_boblight():
  capture = xbmc.RenderCapture()
  capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)
  while not xbmc.abortRequested:
    if settings_checkForNewSettings() or not bob_ping():
      reconnectBoblight()
      settings_setup()                    #after reconnect reload settings
    if settings_getBobDisable():
      bob_set_priority(255)
      time.sleep(1)
      continue
      
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
        log("boblight: error sending values: " + bob_geterror())
        return
    else:
      if not settings_isStaticBobActive():  #don't kill the lights in accident here
        if not bob_set_priority(255):
          return

def initGlobals():
  global g_failedConnectionNotified

  g_failedConnectionNotified = False   
  settings_initGlobals()

def printLights():
  nrLights = bob_getnrlights()
  log("boblight: Found " + str(nrLights) + " lights:")

  for i in range(0, nrLights):
    lightname = bob_getlightname(i)
    log("boblight: " + lightname)

#do a initial bling bling with the lights
def showRgbBobInit():
  settings_confForBobInit()
  bob_set_priority(128)   #allow lights to be turned on
  rgb = (c_int * 3)(255,0,0)
  bob_set_static_color(byref(rgb))
  time.sleep(0.3)
  rgb = (c_int * 3)(0,255,0)
  bob_set_static_color(byref(rgb))
  time.sleep(0.3)
  rgb = (c_int * 3)(0,0,255)
  bob_set_static_color(byref(rgb))
  time.sleep(0.3)
  rgb = (c_int * 3)(0,0,0)
  bob_set_static_color(byref(rgb))
  time.sleep(3)
  bob_set_priority(255) #turn the lights off 

def reconnectBoblight():
  global g_failedConnectionNotified
  
  hostip   = settings_getHostIp()
  hostport = settings_getHostPort()
  
  if hostip == None:
    log("boblight: connecting to local boblightd")
  else:
    log("boblight: connecting to boblightd " + hostip + ":" + str(hostport))

  while not xbmc.abortRequested:
    #check for new settingsk
    if settings_checkForNewSettings():    #networksettings changed?
      g_failedConnectionNotified = False  #reset notification flag
    hostip   = settings_getHostIp()
    hostport = settings_getHostPort()    
    ret = bob_connect(hostip, hostport)

    if not ret:
      log("boblight: connection to boblightd failed: " + bob_geterror())
      count = 10
      while (not xbmc.abortRequested) and (count > 0):
        time.sleep(1)
        count -= 1
      if not g_failedConnectionNotified:
        g_failedConnectionNotified = True
        text = __language__(500)
        xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))
    else:
      text = __language__(501)
      xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))
      log("boblight: connected to boblightd")
      settings_initGlobals()        #invalidate settings after reconnect
      break
  return True

#MAIN - entry point
initGlobals()
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
  #main loop
  while not xbmc.abortRequested:

    if reconnectBoblight():
      printLights()         #print found lights to debuglog
      log("boblight: setting up with user settings")
      showRgbBobInit()      #init light bling bling
      settings_setup()
      process_boblight()    #boblight loop

    time.sleep(1)

#cleanup
bob_destroy()
