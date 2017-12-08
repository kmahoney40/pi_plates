import curses
import time
import piplates.DAQCplate as DAQC
import piplates.RELAYplate as RELAY
import requests
from datetime import datetime
import json

def readConfig(line):
    try:
        stdscr = curses.initscr()
        curses.noecho()
        stdscr.nodelay(1)

        localLine = 1

        configFile = open("config.txt", "r")

        configData = configFile.read()
        stdscr.addstr(line + localLine, 0, configData)
        localLine += 10

        configJson = json.loads(configData)

        url = configJson["url"]
        fanChangeTemp = configJson["fanChangeTemp"]
        fanDelta = configJson["fanDelta"]
        voltageTrigger = configJson["voltageTrigger"]
        alpha = configJson["alpha"]
        modMin = configJson["modMin"]
        modSec = configJson["modSec"]

        stdscr.addstr(line + localLine, 0, "url: " + url)
        localLine += 1
        stdscr.addstr(line + localLine, 0, "fanChangeTemp: " + str(fanChangeTemp))
        localLine += 1
        stdscr.addstr(line + localLine, 0, "fanDelta: " + str(fanDelta) + " alpha: " + str(alpha))
        localLine += 1
        stdscr.addstr(line + localLine, 0, "modMin: " + str(modMin) + " modSec: " + str(modSec))
        localLine += 1
        localLine += 1
    except Exception, ex:
        stdscr.addstr(line + localLine, 0, "getDoorCmnd() outter exception: " + ex.message)
    else:
        stdscr.addstr(line + localLine, 0, "readConfig() all good!")
    finally:
        stdscr.addstr(line + localLine, 0, "END: readConfig() - " + str(datetime.utcnow()))
        localLine += 3

    return localLine
