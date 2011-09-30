"""

cheat sheet

c_void_p(libboblight.boblight_init())
libboblight.boblight_destroy(boblight)
c_int(libboblight.boblight_connect(boblight, const char* address, int port, int usectimeout))
c_int(libboblight.boblight_setpriority(boblight, int priority))
c_char_p(libboblight.boblight_geterror(boblight))
c_int(libboblight.boblight_getnrlights(boblight))
c_char_p(libboblight.boblight_getlightname(boblight, int lightnr))
c_int(libboblight.boblight_getnroptions(boblight))
c_char_p(libboblight.boblight_getoptiondescriptboblight, int option))
c_int(libboblight.boblight_setoption(boblight, int lightnr, const char* option))
c_int(libboblight.boblight_getoption(boblight, int lightnr, const char* option, const char** output))
libboblight.boblight_setscanrange(boblight, int width, int height)
c_int(libboblight.boblight_addpixel(boblight, int lightnr, int* rgb))
libboblight.boblight_addpixelxy(boblight, int x, int y, int* rgb)
c_int(libboblight.boblight_sendrgb(boblight, int sync, int* outputused))
c_int(libboblight.boblight_ping(boblight, int* outputused))

"""

import xbmc, time, xbmcaddon
from ctypes import *

addon = xbmcaddon.Addon()
if addon.getSetting('enabled') != 'true':
  exit(0)

# load libboblight.so
cdll.LoadLibrary("libboblight.so")
libboblight = CDLL("libboblight.so")
libboblight.boblight_init.restype = c_void_p
libboblight.boblight_geterror.restype = c_char_p
libboblight.boblight_getlightname.restype = c_char_p
libboblight.boblight_getoptiondescript.restype = c_char_p

current_priority = -1
def set_priority(boblight, priority):
  global current_priority
  if priority != current_priority:
    current_priority = priority
    if not libboblight.boblight_setpriority(boblight, current_priority):
      print "boblight: error setting priority: " + c_char_p(libboblight.boblight_geterror(boblight)).value
      return False
    else:
      return True;
  else:
    return True;

capture_width = 32
capture_height = 32
def process_boblight(boblight):
  capture = xbmc.RenderCapture()
  capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)
  while not xbmc.abortRequested:
    capture.waitForCaptureStateChangeEvent(1000)
    if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
      if not set_priority(boblight, 128):
        return

      width = capture.getWidth();
      height = capture.getHeight();
      pixels = capture.getImage();
      libboblight.boblight_setscanrange(boblight, width, height)
      rgb = (c_int * 3)()
      for y in range(height):
        row = width * y * 4
        for x in range(width):
          rgb[0] = pixels[row + x * 4 + 2]
          rgb[1] = pixels[row + x * 4 + 1]
          rgb[2] = pixels[row + x * 4]
          libboblight.boblight_addpixelxy(boblight, x, y, byref(rgb))

      if not c_int(libboblight.boblight_sendrgb(boblight, 1, None)):
        print "boblight: error sending values: " + c_char_p(libboblight.boblight_geterror(boblight)).value
        return
    else:
      if not set_priority(boblight, 255):
        return


while not xbmc.abortRequested:
  boblight = c_void_p(libboblight.boblight_init(None))
  global current_priority
  current_priority = -1

  print "boblight: connecting to boblightd"
  returnv = c_int(libboblight.boblight_connect(boblight, None, -1, 1000000))
  if returnv.value == 0:
    print "boblight: connection to boblightd failed: " + c_char_p(libboblight.boblight_geterror(boblight)).value
    count = 10
    while (not xbmc.abortRequested) and (count > 0):
      time.sleep(1)
      count -= 1
  else:
    print "boblight: connected to boblightd"
    libboblight.boblight_setoption(boblight, -1, "saturation 3.0")
    libboblight.boblight_setoption(boblight, -1, "value      10.0")
    libboblight.boblight_setoption(boblight, -1, "speed      20.0")
    process_boblight(boblight)

  libboblight.boblight_destroy(boblight)
  time.sleep(1)
   
"""
boblight = c_void_p(libboblight.boblight_init(None))

print "connecting to boblightd"
returnv = c_int(libboblight.boblight_connect(boblight, None, -1, 1000000))

if returnv.value == 0:
 print "connection failed: ",
 print c_char_p(libboblight.boblight_geterror(boblight)).value
 exit()

print "connection succeeded"

libboblight.boblight_setpriority(boblight, 128)

rgb = (c_int * 3)(255, 128, 64);

libboblight.boblight_addpixel(boblight, -1, byref(rgb))
libboblight.boblight_sendrgb(boblight, 0, None)

sleep(10)
"""

"""
print "boblight XBMC addon"
width = 64
height = 64
capture = xbmc.RenderCapture()
capture.capture(width, height, xbmc.CAPTURE_FLAG_CONTINUOUS)
window = gtk.Window(gtk.WINDOW_TOPLEVEL)
window.show()
image = gtk.Image()
window.add(image)

while (not xbmc.abortRequested):
  capture.waitForCaptureStateChangeEvent(1000)
  if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE:
    print "Capture successful"
    for x in range(capture.getWidth()):
      for y in range(capture.getHeight()):
        a = 1

    pixbuf = gtk.gdk.pixbuf_new_from_data(
            buffer(capture.getImage()), # data
            gtk.gdk.COLORSPACE_RGB, # color mode
            True, # has alpha
            8, # bits
            capture.getWidth(), # width
            capture.getHeight(), # height
            capture.getWidth() * 4 # rowstride
            ) 
    image.set_from_pixbuf(pixbuf)
    image.show()

  else:
    print "Capture failed"

  gtk.main_iteration(False)
"""
