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
import xbmc
import xbmcaddon
import time
import os

__settings__   = xbmcaddon.Addon(id='script.xbmc.boblight')
__cwd__        = __settings__.getAddonInfo('path')
__icon__       = os.path.join(__cwd__,"icon.png")
__scriptname__ = "XBMC Boblight"

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)

from boblight import *
from settings import *

#if __settings__.getSetting('enabled') != 'true':
#  exit(0)

global g_failedConnectionNotified

capture_width = 32
capture_height = 32

def process_boblight():
  capture = xbmc.RenderCapture()
  capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)
  while not xbmc.abortRequested:
    if settings_checkForNewSettings():
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
        print "boblight: error sending values: " + bob_geterror()
        return
    else:
      if not bob_set_priority(255):
        return

def initGlobals():
  global g_failedConnectionNotified

  g_failedConnectionNotified = False   
  settings_initGlobals()

def printLights():
  nrLights = bob_getnrlights()
  print "boblight: Found " + str(nrLights) + " lights:"

  for i in range(0, nrLights):
    lightname = bob_getlightname(i)
    print "boblight: " + lightname

def reconnectBoblight():
  global g_failedConnectionNotified
  
  hostip   = settings_getHostIp()
  hostport = settings_getHostPort()
  
  if hostip == None:
    print "boblight: connecting to local boblightd"
  else:
    print "boblight: connecting to boblightd " + hostip + ":" + str(hostport)

  while not xbmc.abortRequested:
    #check for new settingsk
    if settings_checkForNewSettings():    #networksettings changed?
      g_failedConnectionNotified = False  #reset notification flag
    hostip   = settings_getHostIp()
    hostport = settings_getHostPort()    
    ret = bob_connect(hostip, hostport)

    if not ret:
      print "boblight: connection to boblightd failed: " + bob_geterror()
      count = 10
      while (not xbmc.abortRequested) and (count > 0):
        time.sleep(1)
        count -= 1
      if not g_failedConnectionNotified:
        g_failedConnectionNotified = True
        text = "Failed to connect to boblightd!"
        xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))
    else:
      text = "Connected to boblightd!"
      xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))
      print "boblight: connected to boblightd"
      break
  return True


#MAIN - entry point
initGlobals()
bob_loadLibBoblight()
  
#main loop
while not xbmc.abortRequested:

  if reconnectBoblight():
    printLights()
    print "boblight: setting up with user settings"
#fixme with category - movie hardcoded for now
    settings_setup()
    process_boblight()

  time.sleep(1)

#cleanup
bob_destroy()
