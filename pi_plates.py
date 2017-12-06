import piplates.DAQCplate as DAQC
import piplates.RELAYplate as RELAY
import time
import pygame
from pygame.locals import *
from datetime import datetime
import pytz
import curses
import httplib
import requests
import json
import door
from decimal import Decimal

try:
    stdscr = curses.initscr()
    curses.noecho()
    stdscr.nodelay(1)

    stdscr.addstr(0,0, "Press \"p\" to show count, \"q\" to exit...")
    
    continue1 = True
    line = 1
    tempFanCounter = 0

    stdscr.addstr(line, 0, str(RELAY.getID(0)))
    line += 1
    RELAY.relayOFF(0, 3)
    RELAY.relayOFF(0, 5)

    configFile = open("config.txt", "r")

    configData = configFile.read()
    stdscr.addstr(line, 0, configData)
    line += 10

    configJson = json.loads(configData)
    
    url = configJson["url"]
    fanChangeTemp = configJson["fanChangeTemp"]
    fanDelta = configJson["fanDelta"]
    voltageTrigger = configJson["voltageTrigger"]
    alpha = configJson["alpha"]
    modMin = configJson["modMin"]
    modSec = configJson["modSec"]

    stdscr.addstr(line, 0, "url: " + url)
    line += 1
    stdscr.addstr(line, 0, "fanChangeTemp: " + str(fanChangeTemp))
    line += 1
    stdscr.addstr(line, 0, "fanDelta: " + str(fanDelta) + " alpha: " + str(alpha))
    line += 1
    stdscr.addstr(line, 0, "modMin: " + str(modMin) + " modSec: " + str(modSec))
    line += 1
    line += 1

    headers = { 'content-type': 'application/json' }
    doorOverride = False
    fanOn = False
    chargerOn = False

    fTemp1 = 0.0
    fTemp2 = 0.0
    fTemp3 = 0.0
    fVolts = 0.0
    tmp1 = tmp2 = tmp3 = 0
    volts = 0
    timeNow = time.time()

    while continue1 == True:

        loopLine = line

        timeNow = time.time()
        stdscr.addstr(loopLine, 0, "1: " + str(timeNow))
        loopLine += 1
        stdscr.addstr(loopLine, 0, "2: " + str(datetime.utcnow()))
        loopLine += 1

        readChar = stdscr.getch()
        if readChar == ord('q'):
            stdscr.addstr(loopLine, 0, "Quit")
            loopLine += 1
            continue1 = False
        if readChar == ord('d'):
            doorOverride = True
    

        myTime = time.localtime(time.time())
        myMin = myTime.tm_min
        mySec = myTime.tm_sec

        if mySec % modSec == 0:
            loopLine += door.getDoorCmnd(loopLine, url, doorOverride)
            doorOverride = False
        else:
            loopLine += 11
            stdscr.addstr(loopLine, 0, "in else no call to getDoorCmd() - mySec: " + str(mySec) + "          ")
        loopLine += 1

        tmp1 = 100 * DAQC.getADC(0, 0) - 50
        tmp1 = round(tmp1, 2)
        tmp2 = 100 * DAQC.getADC(0, 1) - 50
        tmp2 = round(tmp2, 2)
        tmp3 = 100 * DAQC.getADC(0, 2) - 50
        tmp3 = round(tmp3, 2)

        volts = DAQC.getADC(0, 3)

        fTemp1 = (1 - alpha) * tmp1 + alpha * fTemp1
        fTemp1 = round(fTemp1, 1)

        fTemp2 = (1 - alpha) * tmp2 + alpha * fTemp2
        fTemp2 = round(fTemp2, 1)

        fTemp3 = (1 - alpha) * tmp3 + alpha * fTemp3
        fTemp3 = round(fTemp3, 1)

        fVolts = (1 - alpha) * volts + alpha * fVolts
        fVolts = round(fVolts, 1)

        stdscr.addstr(loopLine, 0, "rawTmp1: " + str(tmp1) + " filteredTmp1: " + str(fTemp1))
        loopLine += 1
        stdscr.addstr(loopLine, 0, "rawTmp2: " + str(tmp2) + " filteredTmp2: " + str(fTemp2))
        loopLine += 1
        stdscr.addstr(loopLine, 0, "rawTmp3: " + str(tmp3) + " filteredTmp3: " + str(fTemp3))
        loopLine += 1

        loopLine += 2
        currentMod = myMin % modMin
        stdscr.addstr(loopLine, 0, "min: " + str(myMin) + " sec: " + str(mySec) + " mod: " + str(currentMod) + " tempFanCounter: " + str(tempFanCounter) )
        loopLine += 2

        if currentMod == 0 and tempFanCounter == 0:
            try:
                tempFanCounter = 1
                stdscr.addstr(loopLine, 0, "tempFanCounter inside" + str(tempFanCounter) + "          ")
                loopLine += 1

                strtmp1 = str(fTemp1)
                strtmp2 = str(fTemp2)
                strtmp3 = str(fTemp3)

                stdscr.addstr(loopLine, 0, "sentTmp1: " + strtmp1)
                loopLine += 1
                stdscr.addstr(loopLine, 0, "sentTmp2: " + strtmp2)
                loopLine += 1
                stdscr.addstr(loopLine, 0, "sentTmp3: " + strtmp3)
                loopLine += 1

                if fVolts < voltageTrigger:
                    RELAY.relayON(0, 7)
                    chargerOn = True
                else:
                    RELAY.relayOFF(0, 7)
                    chargerOn = False

                if fTemp1 > fanChangeTemp + fanDelta:
                    RELAY.relayON(0, 3)
                    fanOn = True
                elif fTemp1 < fanChangeTemp - fanDelta:
                    RELAY.relayOFF(0, 3)
                    fanOn = False

                payload = {"TEMP_1": fTemp1, "TEMP_2": fTemp2, "TEMP_3": fTemp3, "FAN_ON": fanOn, "CHARGER_ON": chargerOn,
                           "VOLTAGE": fVolts, "GMT": str(datetime.utcnow())}
                stdscr.addstr(loopLine, 0, "payload: " + json.dumps(payload))
                loopLine += 2

                stdscr.addstr(loopLine, 0, "state: " + str(RELAY.relaySTATE(0)))
                loopLine += 1
            except Exception, ex:
                stdscr.addstr(loopLine, 0, "Exception: " + ex.message)
            finally:
                var = 3
            try:
                headers = {'content-type': 'application/json'}
                ret = requests.post(url + 'piplates', json=json.dumps(payload), headers=headers)
                stdscr.addstr(loopLine, 0, "return: " + str(ret.status_code) + " " + ret.text)
            except Exception, ex:
                loopLine += 2
                stdscr.addstr(loopLine, 0, "Exception: " + ex.message)
                loopLine += 1
            else:
                loopLine += 2
                stdscr.addstr(loopLine, 0, "Send temps all good")
                loopLine += 1
            finally:
                loopLine += 2
                stdscr.addstr(loopLine, 0, "datetime: " + str(datetime.utcnow()))
                loopLine += 1
        else:
            if tempFanCounter > 0:
                tempFanCounter += 1
                if tempFanCounter > 60:
                    tempFanCounter = 0
            stdscr.addstr(loopLine, 0, "tempFanCounter else: " + str(tempFanCounter) + "                    ")
            loopLine += 1

        loopLine += 1
        time.sleep(1)

finally:
    curses.endwin()
