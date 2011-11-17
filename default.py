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

#if __settings__.getSetting('enabled') != 'true':
#  exit(0)

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

capture_width = 32
capture_height = 32

def process_boblight():
  capture = xbmc.RenderCapture()
  capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)
  while not xbmc.abortRequested:
    checkForNewSettings(True)
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

#-------------------START handle settings functions--------------------
def checkForNewSettings(withReconnect):
#todo  for now impl. stat on addon.getAddonInfo('profile')/settings.xml and use mtime
#check for new settings every 5 secs
  global g_timer
  if time.time() - g_timer > 5:
    print "boblight: checking for new settings"
    setup("movie",withReconnect)			#fixme category
    g_timer = time.time()
        
def setupForMovie(): 
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
    interpolation   =  int(bool(__settings__.getSetting("movie_interpolation")))
    threshold       =  float(__settings__.getSetting("movie_threshold"))
  return (saturation,value,speed,autospeed,interpolation,threshold)

def setupForMusicVideo():
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
    interpolation   =  int(bool(__settings__.getSetting("musicvideo_interpolation")))
    threshold       =  float(__settings__.getSetting("musicvideo_threshold"))
  return (saturation,value,speed,autospeed,interpolation,threshold)

def setupForOther():
  saturation      =  float(__settings__.getSetting("other_saturation"))
  value           =  float(__settings__.getSetting("other_value"))
  speed           =  float(__settings__.getSetting("other_speed"))
  autospeed       =  float(__settings__.getSetting("movie_autospeed"))
  interpolation   =  int(bool(__settings__.getSetting("other_interpolation")))
  threshold       =  float(__settings__.getSetting("other_threshold"))
  return (saturation,value,speed,autospeed,interpolation,threshold)

def setup(category, withReconnect):
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

#switch case in python - dictionary with function pointers
  option = { "movie"      : setupForMovie,
             "musicvideo" : setupForMusicVideo,
             "other"      : setupForOther,
  }
#call the right setup function according to categroy
  saturation,value,speed,autospeed,interpolation,threshold = option[category]()

  networkaccess = __settings__.getSetting("networkaccess") == "true"
  hostip = __settings__.getSetting("hostip")
  hostport = int(__settings__.getSetting("hostport"))

#server settings
  if g_networkaccess != networkaccess:
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
    if withReconnect:
      reconnectBoblight()

#setup boblight - todo error checking
  if g_saturation != saturation:  
    ret = bob_setoption("saturation    " + str(saturation))
    print "boblight: changed saturation to " + str(saturation) + "(ret " + str(ret) + ")"
    g_saturation = saturation
  
  if g_value != value:  
    ret = bob_setoption("value         " + str(value))
    print "boblight: changed value to " + str(value) + "(ret " + str(ret) + ")"
    g_value = value

  if g_speed != speed:  
    ret = bob_setoption("speed         " + str(speed))
    print "boblight: changed speed to " + str(speed) + "(ret " + str(ret) + ")"
    g_speed = speed

  if g_autospeed != autospeed:  
    ret = bob_setoption("autospeed     " + str(autospeed))
    print "boblight: changed autospeed to " + str(autospeed) + "(ret " + str(ret) + ")"
    g_autospeed = autospeed

  if g_interpolation != interpolation:  
    ret = bob_setoption("interpolation " + str(interpolation))
    print "boblight: changed interpolation to " + str(interpolation) + "(ret " + str(ret) + ")"
    g_interpolation = interpolation

  if g_threshold != threshold:  
    ret = bob_setoption("threshold     " + str(threshold))
    print "boblight: changed threshold to " + str(threshold) + "(ret " + str(ret) + ")"
    g_threshold = threshold
#-------------------END handle settings functions--------------------

def initGlobals():
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
  global g_networkaccess
  global g_hostip
  global g_hostport  

  g_networkaccess  = False
  g_hostip         = "127.0.0.1"
  g_hostport       = None
  g_saturation     = -1.0 
  g_value          = -1.0
  g_speed          = -1.0
  g_autospeed      = -1.0
  g_interpolation  = -1
  g_threshold      = -1.0
  g_timer          = time.time()
  g_failedConnectionNotified = False   
  g_networkaccess  = __settings__.getSetting("networkaccess") == "true"
  g_hostip         = __settings__.getSetting("hostip")
  g_hostport       = int(__settings__.getSetting("hostport"))  

def printLights():
  nrLights = bob_getnrlights()
  print "boblight: Found " + str(nrLights) + " lights:"

  for i in range(0, nrLights):
    lightname = bob_getlightname(i)
    print "boblight: " + lightname

def reconnectBoblight():
  global g_failedConnectionNotified

  if g_hostip == None:
    print "boblight: connecting to local boblightd"
  else:
    print "boblight: connecting to boblightd " + g_hostip + ":" + str(g_hostport)

  while not xbmc.abortRequested:
    #check for new settings - but without reconnect on network
    #settings change ... else this would be recursive
    checkForNewSettings(False)               
    ret = bob_connect(g_hostip, g_hostport)

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

while not xbmc.abortRequested:
  initGlobals()

  bob_loadLibBoblight()

  if not g_networkaccess:
    g_hostip = None
    g_hostport = -1

  if reconnectBoblight():
    printLights()
    print "boblight: setting up with user settings"
#fixme with category - movie hardcoded for now
    setup("movie",True)
    process_boblight()

  bob_destroy()
  time.sleep(1)


