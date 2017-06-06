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
from decimal import Decimal


def getDoorCmnd(line):
    headers = { 'content-type': 'application/json' }
    fullUrl = url + 'door'
    stdscr.addstr(line, 0, fullUrl)
    line += 1
    ret = requests.get(fullUrl, headers=headers)
    stdscr.addstr(line, 0, str(ret.status_code) + ": " + str(ret.text) )
    line += 1
    return

try:
    stdscr = curses.initscr()
    curses.noecho()
    stdscr.nodelay(1)

    stdscr.addstr(0,0, "Press \"p\" to show count, \"q\" to exit...")
    
    continue1 = True
    line = 1

    stdscr.addstr(line, 0, RELAY.getID(0))
    line += 1
    RELAY.relayOFF(0,3)

    configFile = open("config.txt", "r")

    configData = configFile.read()
    stdscr.addstr(line, 0, configData)
    line += 5

    configJson = json.loads(configData)
    
    url = configJson["url"]
    fanChangeTemp = configJson["fanChangeTemp"]
    fanDelta = configJson["fanDelta"]
    loopTime = configJson["loopTime"]

    stdscr.addstr(line, 0, "url: " + url)
    line += 1
    stdscr.addstr(line, 0, "fanChangeTemp: " + str(fanChangeTemp))
    line += 1
    stdscr.addstr(line, 0, "fanDelta: " + str(fanDelta))
    line += 1
    stdscr.addstr(line, 0, "loopTime: " + str(loopTime))
    line += 1
    line += 1

    headers = { 'content-type': 'application/json' }
    
    fanOn = False

    loopCount = 0
    while continue1 == True:

        loopLine = line

        readChar = stdscr.getch()
        if readChar == ord('q'):
            stdscr.addstr(loopLine, 0, "Quit")
            loopLine += 1
            continue1 = False

        if loopCount % 2 == 0:
            getDoorCmnd(line)
            loopLine += 1
            loopLine += 1

        if continue1 and loopCount > 9:
            loopCount = 0

            tmp1 = 100 * DAQC.getADC(0, 0) - 50
            tmp1 = round(tmp1, 1)
            tmp2 = 100 * DAQC.getADC(0, 1) - 50
            tmp2 = round(tmp2, 1)
            tmp3 = 100 * DAQC.getADC(0, 2) - 50
            tmp3 = round(tmp3, 1)
            volts = DAQC.getADC(0, 3)
            strtmp1 = str(tmp1)
            strtmp2 = str(tmp2)
            strtmp3 = str(tmp3)

            if tmp1 > fanChangeTemp + fanDelta:
                RELAY.relayON(0,3)
                fanOn = True
            elif tmp1 < fanChangeTemp - fanDelta:
                RELAY.relayOFF(0,3)
                fanOn = False

            stdscr.addstr(loopLine, 0, "tmp1: " + str(tmp1))
            loopLine += 1
            stdscr.addstr(loopLine, 0, "tmp2: " + str(tmp2))
            loopLine += 1
            stdscr.addstr(loopLine, 0, "tmp3: " + str(tmp3))
            loopLine += 1

            payload = {"TEMP_1":tmp1, "TEMP_2":tmp2, "TEMP_3":tmp3, "FAN_ON": fanOn, "VOLTAGE": volts, "GMT": str(datetime.now(pytz.utc))}
            stdscr.addstr(loopLine, 0, "payload: " + json.dumps(payload))
            loopLine += 1

            stdscr.addstr(loopLine, 0, "state: " + str(RELAY.relaySTATE(0)))
            loopLine += 1

            #headers = { 'content-type': 'application/json' }
            ret = requests.post(url + 'piplates', json=json.dumps(payload), headers=headers)
            stdscr.addstr(loopLine, 0, "return: " + str(ret.status_code) + " " + ret.text)
            loopLine += 1
            stdscr.addstr(loopLine, 0, "datetime: " + str(datetime.now(pytz.utc)))
            loopLine += 1
        else:
            loopCount += 1

        time.sleep(1)
finally:
    curses.endwin()

