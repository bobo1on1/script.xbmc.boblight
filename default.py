# ---
# Copyright (C) 2011 Andreas Auras <yak54@inkennet.de>
#
# This file is part of DFAtmo the driver for 'Atmolight' controllers for XBMC and xinelib based video players.
#
# DFAtmo is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# DFAtmo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110, USA
#
# This is the DFAtmo XBMC addon.
#
# ---

import os, sys, threading, time, imp
import xbmc, xbmcaddon, xbmcgui

addon = xbmcaddon.Addon()
addonPath = addon.getAddonInfo('path')
addonId = addon.getAddonInfo('id')
addonConfigFile = xbmc.translatePath('special://profile/addon_data/{0}/settings.xml'.format(addonId))

addonResourcePath = xbmc.translatePath(os.path.join(addonPath, 'resources', 'lib'))
sys.path.append(addonResourcePath)

addonDriverDir = xbmc.translatePath(os.path.join(addonResourcePath, 'drivers'))
sys.path.append(addonDriverDir)

addonIconFile = xbmc.translatePath(os.path.join(addonPath, 'icon.png'))

DFATMO_DRIVER_VERSION = 1
OUTPUT_DRIVER_INTERFACE_VERSION = 1

LOG_NONE = 0
LOG_ERROR = 1
LOG_INFO = 2
LOG_DEBUG = 3


logLevel = addon.getSetting('log_level')
if logLevel and len(logLevel) > 0:
    logLevel = int(logLevel)
else:
    logLevel = LOG_INFO
    
    
def log(level, msg):
    if level <= logLevel:
        if level == LOG_ERROR:
            l = xbmc.LOGERROR
        elif level == LOG_INFO:
            l = xbmc.LOGINFO
        elif level == LOG_DEBUG:
            l = xbmc.LOGDEBUG
        xbmc.log("DFAtmo: " + str(msg), l)

    
def displayNotification(level, msg):
    log(level, msg)
    if level == LOG_ERROR:
        xbmc.executebuiltin('Notification("DFAtmo","' + str(msg) + '",20000,' + addonIconFile + ')')
    else:
        xbmc.executebuiltin('Notification("DFAtmo","' + str(msg) + '",3000,' + addonIconFile + ')')


if ( __name__ == "__main__" ):
    if xbmcgui.getCurrentWindowId() == 10000:
        if addon.getSetting('enabled') != 'true':
            log(LOG_INFO, "Automatic launch of addon not enabled")
            sys.exit(0)


try:
    if xbmc.CAPTURE_STATE_DONE:
        pass
except:
    displayNotification(LOG_ERROR, "XBMC does not have RenderCapture interface patch!")
    sys.exit(1)


def getDFAtmoInstDir():
    instdir = None
    if os.name == 'posix':
        for instdir in [ '/usr/lib/dfatmo', '/usr/local/lib/dfatmo' ]:
            if os.access(os.path.join(instdir, 'atmodriver.so'), os.R_OK):
                break
        else:
            instdir = None

    if instdir == None:
        instdir = os.path.join(addonPath, 'resources', 'lib.' + str.lower(os.name))
                    
    instdir = xbmc.translatePath(instdir)
    log(LOG_INFO, "DFAtmo installation directory: '%s'" % instdir)
    return instdir

dfAtmoInstDir = getDFAtmoInstDir()    
if dfAtmoInstDir:
    sys.path.append(dfAtmoInstDir)

try:
    import atmodriver
except ImportError as err:
    displayNotification(LOG_ERROR, "Loading native atmodriver failed: " + str(err))
    sys.exit(1)

if atmodriver.getDriverVersion() != DFATMO_DRIVER_VERSION:
    displayNotification(LOG_ERROR, "Wrong version of native atmodriver!")
    sys.exit(1)


class Logger:
    def __init__(self):
        self.LOG_NONE = LOG_NONE
        self.LOG_ERROR = LOG_ERROR
        self.LOG_INFO = LOG_INFO
        self.LOG_DEBUG = LOG_DEBUG

    def log(self, level, msg):
        global log
        log(level, msg)


dfatmoParmList = (
    ( 't', 'driver' ),
    ( 't', 'custom_driver' ),
    ( 't', 'driver_param' ),
    ( 'i', 'log_level' ),
    ( 'i', 'top' ),
    ( 'i', 'bottom' ),
    ( 'i', 'left' ),
    ( 'i', 'right' ),
    ( 'b', 'center' ),
    ( 'b', 'top_left' ),
    ( 'b', 'top_right' ),
    ( 'b', 'bottom_left' ),
    ( 'b', 'bottom_right' ),
    ( 'i', 'overscan' ),
    ( 'i', 'darkness_limit' ),
    ( 'i', 'edge_weighting' ),
    ( 'i', 'hue_win_size' ),
    ( 'i', 'sat_win_size' ),
    ( 'i', 'hue_threshold' ),
    ( 'b', 'uniform_brightness' ),
    ( 'i', 'brightness' ),
    ( 'i', 'filter' ),
    ( 'i', 'filter_smoothness' ),
    ( 'i', 'filter_length' ),
    ( 'i', 'filter_threshold' ),
    ( 'i', 'filter_delay' ),
    ( 'i', 'wc_red' ),
    ( 'i', 'wc_green' ),
    ( 'i', 'wc_blue' ),
    ( 'i', 'gamma' ),
    ( 'i', 'analyze_rate' ),
    ( 'i', 'analyze_size' ),
    ( 'b', 'enabled' ))


IDLE_WAIT_TIME = 0.5
CONFIG_UPDATE_TIME = 1.0

class OutputThread(threading.Thread):
    def __init__(self, captureDriver, atmoDriver, outputDriver):
        threading.Thread.__init__(self, name="DFAtmoOutput")
        self.captureDriver = captureDriver
        self.atmoDriver = atmoDriver
        self.outputDriver = outputDriver
        self.running = False

    def start(self):
        self.running = True
        threading.Thread.start(self)

    def stop(self):
        self.running = False
        self.join(0.5)

    def run(self):
        log(LOG_INFO, "output thread running")
        cd = self.captureDriver
        ad = self.atmoDriver
        od = self.outputDriver
        outputRate = ad.output_rate
        outputRateTime = outputRate / 1000.0
        nextLoopTime = 0.0
        outputStartTime = 0.0
        lightsOn = False
        outputCount = 0
        try:
            ad.resetFilters()
            while self.running:
                actualTime = time.time()
                if actualTime < nextLoopTime:
                    time.sleep(nextLoopTime - actualTime)
                    continue

                if outputRate != ad.output_rate:
                    outputRate = ad.output_rate
                    outputRateTime = outputRate / 1000.0
                nextLoopTime = actualTime + outputRateTime

                colors = cd.analyzedColors
                if colors:
                    if not lightsOn:
                        lightsOn = True
                        outputStartTime = time.time()
                        outputCount = 0
                    colors = ad.filterAnalyzedColors(colors)
                    colors = ad.filterOutputColors(colors)
                    od.outputColors(colors)
                    outputCount = outputCount + 1
            if lightsOn:
                od.turnLightsOff()
                if outputCount:
                    log(LOG_INFO, "average output interval: %.3f" % ((time.time() - outputStartTime) / outputCount))
        except atmodriver.error as err:
            displayNotification(LOG_ERROR, err)
        log(LOG_INFO, "output thread stopped")


class CaptureThread(threading.Thread):
    def __init__(self, atmoDriver):
        threading.Thread.__init__(self, name="DFAtmoCapture")
        self.running = -1
        self.atmoDriver = atmoDriver
        self.analyzedColors = None
        self.configFileTime = 0
        self.useCustomDriver = False
        self.customDriver = ''
        self.customDriverModule = None
        self.outputDriver = None

    def start(self):
        if self.setConfig(addon):
            if self.configure():
                self.running = 1
                threading.Thread.start(self)

    def stop(self):
        if self.running != -1:
            self.running = 0
            self.join(0.5)
            self.running = -1
            self.close()

    def setConfig(self, config, diff=False):
        global logLevel

        if not os.path.isfile(addonConfigFile):
            self.configFileTime = 0
            displayNotification(LOG_ERROR, "Addon not configured!")
            return False
        self.configFileTime = os.path.getmtime(addonConfigFile)

        for p in dfatmoParmList:
            type, name = p
            v = config.getSetting(name)
            
            if type == 'b':
                if v == 'true':
                    v = 1
                else:
                    v = 0
            elif type == 'i':
                v = int(v)
            else:
                v = v.strip()

            ov = None
            doSetParm = True
            
            if name == 'log_level':
                ov = logLevel
                logLevel = v
                atmodriver.setLogLevel(logLevel, log)
                doSetParm = False
            elif name == 'driver':
                if self.useCustomDriver:
                    ov = 'custom'
                if v == 'custom':
                    self.useCustomDriver = True
                    v = 'null'
                else:                                
                    self.useCustomDriver = False
            elif name == 'custom_driver':
                ov = self.customDriver
                self.customDriver = v
                doSetParm = False
                
            if ov == None:
                ov = self.atmoDriver.getParm(name)

            if doSetParm:
                try:
                    self.atmoDriver.setParm(name, v)
                except atmodriver.error as err:
                    displayNotification(LOG_ERROR, err)
                    return False

            if name == 'driver' and self.useCustomDriver:
                v = 'custom'
                
            if diff:
                if v != ov:
                    log(LOG_INFO, "parameter '{0}': '{1}' -> '{2}'".format(name, ov, v))
            else:
                log(LOG_INFO, "parameter '{0}': '{1}'".format(name, v))

        return True

    def getConfig(self, config, diff=False):
        self.configFileTime = os.path.getmtime(addonConfigFile)

        for p in dfatmoParmList:
            type, name = p

            if name == 'driver' and self.useCustomDriver:
                v = 'custom'
            elif name == 'custom_driver':
                v = self.customDriver
            elif name == 'log_level':
                v = str(logLevel)
            else:
                v = self.atmoDriver.getParm(name)
                if type == 'b':
                    if v:
                        v = 'true'
                    else:
                        v = 'false'
                elif type == 'i':
                    v = str(v)

            if diff:
                ov = config.getSetting(name)
                if ov != None:
                    ov = ov.strip()
                if v == ov:
                    continue
                log(LOG_INFO, "parameter '{0}': '{1}' -> '{2}'".format(name, ov, v))
            else:
                log(LOG_INFO, "parameter '{0}': '{1}'".format(name, v))
            
            config.setSetting(name, v)

    def configure(self):
        self.close()

        if self.useCustomDriver:
            if len(self.customDriver) == 0:
                displayNotification(LOG_ERROR, "No custom driver specified!")
                return False

            try:
                self.customDriverModule = __import__(self.customDriver)
            except Exception as err:
                log(LOG_INFO, "Loading script custom driver fails: %s. Will try native custom driver." % err)
                self.atmoDriver.setParm('driver', self.customDriver)
                self.outputDriver = self.atmoDriver
            else:
                try:
                    self.outputDriver = self.customDriverModule.newOutputDriver(self, Logger())
                except atmodriver.error as err:
                    displayNotification(LOG_ERROR, "Instantiating script custom driver fails: %s" % err)
                    return False
                
                if self.outputDriver.getInterfaceVersion() != OUTPUT_DRIVER_INTERFACE_VERSION:
                    displayNotification(LOG_ERROR, "Script custom driver has wrong interface version")
                    return False
    
                try:
                    self.outputDriver.openOutputDriver()
                    self.outputDriver.turnLightsOff()
                except atmodriver.error as err:
                    displayNotification(LOG_ERROR, err)
                    return False
        else:
            self.outputDriver = self.atmoDriver
            
        try:
            self.atmoDriver.configure()
        except atmodriver.error as err:
            displayNotification(LOG_ERROR, err)
            return False
        
        return True

    def getParm(self, name):
        return self.atmoDriver.getParm(name)
    
    def setParm(self, name, value):
        self.atmoDriver.setParm(name, value)
    
    def driverError(self, msg):
        return atmodriver.error(str(msg))
    
    def close(self):
        om = self.customDriverModule
        od = self.outputDriver
        self.customDriverModule = None
        self.outputDriver = None
            
        if od:
            try:
                od.closeOutputDriver()
            except atmodriver.error as err:
                displayNotification(LOG_ERROR, err)
                return False
        return True

    def run(self):
        player = xbmc.Player()
        capture = xbmc.RenderCapture()
        ad = self.atmoDriver
        ot = None
        
        fmt = capture.getImageFormat()
        if fmt == 'RGBA':
            imgFmt = atmodriver.IMAGE_FORMAT_RGBA
        else:
            imgFmt = atmodriver.IMAGE_FORMAT_BGRA

        analyzeSize = (ad.analyze_size + 1) * 64
        eventWaitTime = ad.analyze_rate
        analyzeRateTime = ad.analyze_rate / 1000.0
        videoPlaying = False
        pending = False
        nextCaptureTime = 0.0
        nextConfigUpdateTime = 0.0
        videoStartTime = 0.0
        captureCount = 0
        instantConfigured = False

        displayNotification(LOG_INFO, "Service running")
        while self.running > 0 or (self.running == -1 and not xbmc.abortRequested):
            st = capture.getCaptureState()
            if st != xbmc.CAPTURE_STATE_DONE and st != xbmc.CAPTURE_STATE_FAILED:
                capture.waitForCaptureStateChangeEvent(eventWaitTime)
                continue

            if pending:
                pending = False
                if st == xbmc.CAPTURE_STATE_DONE:
                    self.analyzedColors = ad.analyzeImage(capture.getWidth(), capture.getHeight(), imgFmt, capture.getImage())
                    captureCount = captureCount + 1

            actualTime = time.time()
            if actualTime < nextCaptureTime:
                time.sleep(nextCaptureTime - actualTime)
                continue

            if actualTime >= nextConfigUpdateTime:
                if self.configFileTime != os.path.getmtime(addonConfigFile):
                    log(LOG_INFO, "update of configuration detected")
                    if self.setConfig(xbmcaddon.Addon(), True):
                        if videoPlaying:
                            if ad != self.outputDriver:
                                self.outputDriver.instantConfigure()
                            ad.instantConfigure()
                            instantConfigured = True
                        else:
                            if not self.configure():
                                return
                            self.getConfig(xbmcaddon.Addon(), True)
                            analyzeSize = (ad.analyze_size + 1) * 64
                            eventWaitTime = ad.analyze_rate
                            analyzeRateTime = ad.analyze_rate / 1000.0
                                
                nextConfigUpdateTime = actualTime + CONFIG_UPDATE_TIME
                continue
            
            if player.isPlayingVideo():
                if not videoPlaying:
                    videoPlaying = True
                    log(LOG_INFO, "start playing video: aspect ratio: %.4f" % capture.getAspectRatio())
                    videoStartTime = time.time()
                    captureCount = 0
                    self.analyzedColors = None
                    ot = OutputThread(self, ad, self.outputDriver)
                    ot.start()

                aspectRatio = capture.getAspectRatio()
                if aspectRatio > 0.0:
                    if aspectRatio >= 1.0:
                        capture.capture(analyzeSize, int(analyzeSize / aspectRatio + 0.5))
                    else:
                        capture.capture(int(analyzeSize * aspectRatio + 0.5), analyzeSize)
                    pending = True

                nextCaptureTime = time.time() + analyzeRateTime
                continue

            if videoPlaying:
                videoPlaying = False
                log(LOG_INFO, "stop playing video")
                
                ot.stop()
                ot = None

                if captureCount:
                    log(LOG_INFO, "average capture interval: %.3f" % ((time.time() - videoStartTime) / captureCount))

                if instantConfigured:
                    instantConfigured = False
                    if not self.configure():
                        return
                    self.getConfig(xbmcaddon.Addon(), True)
                    analyzeSize = (ad.analyze_size + 1) * 64
                    eventWaitTime = ad.analyze_rate
                    analyzeRateTime = ad.analyze_rate / 1000.0
            
            nextCaptureTime = time.time() + IDLE_WAIT_TIME
            continue

        if videoPlaying:
            ot.stop()
            ot = None
            if captureCount:
                log(LOG_INFO, "average capture interval: %.3f" % format((time.time() - videoStartTime) / captureCount))

        displayNotification(LOG_INFO, "Service stopped")

    
def runService():
    log(LOG_INFO, "started")
    ad = atmodriver.AtmoDriver()
    cd = CaptureThread(ad)
    runOk = False
    if dfAtmoInstDir:
        ad.driver_path = xbmc.translatePath(os.path.join(dfAtmoInstDir, 'drivers'))
    if cd.setConfig(addon):
        if cd.configure():
            cd.getConfig(xbmcaddon.Addon(), True)
            cd.run()
            cd.close()
    cd = None
    ad = None
    atmodriver.setLogLevel(LOG_NONE, None)


if ( __name__ == "__main__" ):
    runService()
