"""

cheat sheet

c_void_p(g_libboblight.boblight_init())
g_libboblight.boblight_destroy(boblight)
c_int(g_libboblight.boblight_connect(boblight, const char* address, int port, int usectimeout))
c_int(g_libboblight.boblight_setpriority(boblight, int priority))
c_char_p(g_libboblight.boblight_geterror(boblight))
c_int(g_libboblight.boblight_getnrlights(boblight))
c_char_p(g_libboblight.boblight_getlightname(boblight, int lightnr))
c_int(g_libboblight.boblight_getnroptions(boblight))
c_char_p(g_libboblight.boblight_getoptiondescriptboblight, int option))
c_int(g_libboblight.boblight_setoption(boblight, int lightnr, const char* option))
c_int(g_libboblight.boblight_getoption(boblight, int lightnr, const char* option, const char** output))
g_libboblight.boblight_setscanrange(boblight, int width, int height)
c_int(g_libboblight.boblight_addpixel(boblight, int lightnr, int* rgb))
g_libboblight.boblight_addpixelxy(boblight, int x, int y, int* rgb)
c_int(g_libboblight.boblight_sendrgb(boblight, int sync, int* outputused))
c_int(g_libboblight.boblight_ping(boblight, int* outputused))

"""

import sys

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__settings__ = sys.modules[ "__main__" ].__settings__
__cwd__ = sys.modules[ "__main__" ].__cwd__
__icon__ = sys.modules[ "__main__" ].__icon__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__

try:
  from ctypes import *
  HAVE_CTYPES = True
except:
  HAVE_CTYPES = False

global g_boblightLoaded
global g_bobHandle
global g_current_priority
global g_libboblight
global g_connected

def bob_loadLibBoblight():
  global g_boblightLoaded
  global g_current_priority
  global g_libboblight  
  global g_bobHandle
  global g_connected

  g_connected = False
  g_current_priority = -1

  if HAVE_CTYPES:
    # load g_libboblight.so
    try:
      cdll.LoadLibrary("libboblight.so")
      g_libboblight = CDLL("libboblight.so")
      g_libboblight.boblight_init.restype = c_void_p
      g_libboblight.boblight_geterror.restype = c_char_p
      g_libboblight.boblight_getlightname.restype = c_char_p
      g_libboblight.boblight_getoptiondescript.restype = c_char_p
      g_boblightLoaded = True
      g_bobHandle = c_void_p(g_libboblight.boblight_init(None))
    except:
      g_boblightLoaded = False
      print "boblight: Error loading g_libboblight.so - only demo mode."
  else:
    print "boblight: No ctypes available - only demo mode."

def bob_set_priority(priority):
  global g_current_priority
  
  ret = True
  if g_boblightLoaded and g_connected:
    if priority != g_current_priority:
      g_current_priority = priority
      if not g_libboblight.boblight_setpriority(g_bobHandle, g_current_priority):
        print "boblight: error setting priority: " + c_char_p(g_libboblight.boblight_geterror(g_bobHandle)).value
        ret = False
  return ret
  
def bob_setscanrange(width, height):
  if g_boblightLoaded and g_connected:
    g_libboblight.boblight_setscanrange(g_bobHandle, width, height)
  
def bob_addpixelxy(x,y,rgb):
  if g_boblightLoaded and g_connected:
    g_libboblight.boblight_addpixelxy(g_bobHandle, x, y, rgb)

def bob_sendrgb():
  ret = False
  if g_boblightLoaded and g_connected:
    ret = c_int(g_libboblight.boblight_sendrgb(g_bobHandle, 1, None))  != 0
  else:
    ret = True
  return ret
  
def bob_setoption(option):
  ret = False
  if g_boblightLoaded and g_connected:
    ret = c_int(g_libboblight.boblight_setoption(g_bobHandle, -1, option))  != 0
  else:
    ret = True
  return ret
  
def bob_getnrlights():
  ret = c_int(0)
  if g_boblightLoaded and g_connected:
    ret = c_int(g_libboblight.boblight_getnrlights(g_bobHandle))
  return ret.value
  
def bob_getlightname(nr):
  ret = ""
  if g_boblightLoaded and g_connected:
    ret = g_libboblight.boblight_getlightname(g_bobHandle,nr)
  return ret

def bob_connect(hostip, hostport):
  global g_connected
  
  if hostip != None:
    print "connect to " + hostip + "/" + str(hostport) + " loaded " + str(g_boblightLoaded)
  else:
    print "connect to None/" + str(hostport) + " loaded " + str(g_boblightLoaded)
  if g_boblightLoaded:
    ret = c_int(g_libboblight.boblight_connect(g_bobHandle, hostip, hostport, 1000000))
    g_connected = ret.value != 0
    print str(ret) + " " + str(ret.value)
  else:
    g_connected = True
  return g_connected

def bob_destroy():
  if g_boblightLoaded:
    g_libboblight.boblight_destroy(boblight)

def bob_geterror():
  ret = ""
  if g_boblightLoaded:
    ret = c_char_p(g_libboblight.boblight_geterror(g_bobHandle)).value
  return ret
