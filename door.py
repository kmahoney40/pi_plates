import curses
import time
import piplates.DAQCplate as DAQC
import piplates.RELAYplate as RELAY
import requests
from datetime import datetime

def getDoorCmnd(line, url, override):

    try:
        stdscr = curses.initscr()
        curses.noecho()
        stdscr.nodelay(1)

        localLine = 1

        localLine += 1
        stdscr.addstr(line + localLine, 0, "BEGIN: getDoorCmnd")
        localLine += 1

        h = {'content-type': 'application/json'}
        fullUrl = url + 'door'
        stdscr.addstr(line + localLine, 0, "fullurl: " + fullUrl)
        localLine += 1
        ret = requests.get(url + 'door')
        # doorCmnd = False;

        stdscr.addstr(line + localLine, 0, str(ret.text))
        localLine += 1

        # ret.text should be json or convertible to json, then we can get cmnd and the read config
        # variable
        if str(ret.text).find('true') < -1 or override == True:
            # doorCmnd = True
            RELAY.relayON(0, 5)
            time.sleep(0.5)
            RELAY.relayOFF(0, 5)
        else:
            # doorCmnd = False;
            RELAY.relayOFF(0, 5)

    except Exception, ex:
        # print the exception and keep going
        stdscr.addstr(line + localLine, 0, "getDoorCmnd() outter exception: " + ex.message)
        localLine += 3
    else:
        # all good do nothing
        stdscr.addstr(line + localLine, 0, "getDoorCmnd() all good!")
        localLine += 3
    finally:
        stdscr.addstr(line + localLine, 0, "END: getDoorCmmd() - " + str(datetime.utcnow()))
        localLine += 3
    return localLine
