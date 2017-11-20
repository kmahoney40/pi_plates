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

    try:
        localLine = 1
        
        localLine += 1
        stdscr.addstr(line + localLine, 0, "BEGIN: getDoorCmnd")
        localLine += 1

        h = { 'content-type': 'application/json' }
        fullUrl = url + 'door'
        stdscr.addstr(line + localLine, 0, "fullurl: " + fullUrl)
        localLine += 1
        ret = requests.get(url + 'door')
        #doorCmnd = False;

        stdscr.addstr(line + localLine, 0, str(ret.text))
        localLine += 1

        if str(ret.text).find('true') > -1:
            #doorCmnd = True
            RELAY.relayON(0, 5)
        else:
            #doorCmnd = False;
            RELAY.relayOFF(0, 5)

        localLine += 1


    except Exception, ex:
        # pring the exception and keep going
        stdscr.addstr(line + localLine, 0, "getDoorCmnd() outter exception: " + str(ex))
        localLine += 3
    else:
        # all good do nothing
        stdscr.addstr(line + localLine, 0, "getDoorCmnd() all good!")
        localLine += 3
    finally:
        # time.sleep(5)
        stdscr.addstr(line + localLine, 0, "END: getDoorCmmd() - " + str(datetime.utcnow()))
        localLine += 3
        # time.sleep(5)
    return localLine

# END getDoorCmnd() function



try:
    stdscr = curses.initscr()
    curses.noecho()
    stdscr.nodelay(1)

    stdscr.addstr(0,0, "Press \"p\" to show count, \"q\" to exit...")
    
    continue1 = True
    line = 1
    tempFanCounter = 0

    stdscr.addstr(line, 0, RELAY.getID(0))
    line += 1
    RELAY.relayOFF(0,3)
    RELAY.relayOFF(0, 5)

    configFile = open("config.txt", "r")

    configData = configFile.read()
    stdscr.addstr(line, 0, configData)
    line += 8

    configJson = json.loads(configData)
    
    url = configJson["url"]
    fanChangeTemp = configJson["fanChangeTemp"]
    fanDelta = configJson["fanDelta"]
    voltageTrigger = configJson["voltageTrigger"]
    loopTime = configJson["loopTime"]
    alpha = configJson["alpha"]

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
    chargerOn = False

    fTemp1 = 0.0
    fTemp2 = 0.0
    fTemp3 = 0.0
    fVolts = 0.0
    loopCount = 0
    timeNow = time.time()
    while continue1 == True:

        #RELAY.relayON(0, 5)
        
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

        if loopCount % 3 == 0:
            ll = loopLine
            #stdscr.addstr(50, 0, "loopLine: " + str(loopLine))
            lll = getDoorCmnd(ll)
            loopLine += lll
            #stdscr.addstr(51, 0, "loopLine: " + str(lll))
            #loopLine += lll
            #loopLine += 1
            #loopLine += 1

            tmp1 = 100 * DAQC.getADC(0, 0) - 50
            tmp1 = round(tmp1, 1)
            tmp2 = 100 * DAQC.getADC(0, 1) - 50
            tmp2 = round(tmp2, 1)
            tmp3 = 100 * DAQC.getADC(0, 2) - 50
            tmp3 = round(tmp3, 1)
            volts = DAQC.getADC(0, 3)
            stdscr.addstr(loopLine, 0, "inside loopCount loopLine: " + str(loopLine))
            loopLine += 1
            loopCount = 0
        else:
            loopLine += 12
            stdscr.addstr(loopLine, 0, "in loopCount else: " + str(loopLine) + "          ")
            loopLine += 1
        loopCount += 1
        stdscr.addstr(loopLine, 0, "rawTmp1: " + str(tmp1))
        loopLine += 1
        stdscr.addstr(loopLine, 0, "rawTmp2: " + str(tmp2))
        loopLine += 1
        stdscr.addstr(loopLine, 0, "rawTmp3: " + str(tmp3))
        loopLine += 1

        fTemp1 = (1 - alpha) * tmp1 + alpha * fTemp1
        fTemp1 = round(fTemp1, 1)

        fTemp2 = (1 - alpha) * tmp2 + alpha * fTemp2
        fTemp2 = round(fTemp2, 1)

        fTemp3 = (1 - alpha) * tmp3 + alpha * fTemp3
        fTemp3 = round(fTemp3, 1)

        fVolts = (1 - alpha) * volts + alpha * fVolts
        fVolts = round(fVolts, 1)

        stdscr.addstr(loopLine, 0, "filteredTmp1: " + str(fTemp1))
        loopLine += 1
        stdscr.addstr(loopLine, 0, "filteredTmp2: " + str(fTemp2))
        loopLine += 1
        stdscr.addstr(loopLine, 0, "filteredTmp3: " + str(fTemp3))
        loopLine += 1

        loopLine += 2
        #if continue1 and 
        myTime = time.localtime(time.time()) 
        myMin = myTime.tm_min
        stdscr.addstr(loopLine, 0, "min: " + str(myMin) + " mod: " + str(myMin % 5) + " tempfanCounter: " + str(tempFanCounter) )
        loopLine += 2

        if myMin % 15 == 0 and tempFanCounter == 0:
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

            stdscr.addstr(loopLine, 0, "tmp1: " + strtmp1)
            loopLine += 1
            stdscr.addstr(loopLine, 0, "tmp2: " + strtmp2)
            loopLine += 1
            stdscr.addstr(loopLine, 0, "tmp3: " + strtmp3)
            loopLine += 1

            payload = {"TEMP_1": fTemp1, "TEMP_2": fTemp2, "TEMP_3": fTemp3, "FAN_ON": fanOn, "CHARGER_ON": chargerOn,
                       "VOLTAGE": fVolts, "GMT": str(datetime.utcnow())}
            # str(datetime.now(pytz.utc))}
            stdscr.addstr(loopLine, 0, "payload: " + json.dumps(payload))
            loopLine += 2

            stdscr.addstr(loopLine, 0, "state: " + str(RELAY.relaySTATE(0)))
            loopLine += 1

            headers = { 'content-type': 'application/json' }
            try:
                var = 2
                ret = requests.post(url + 'piplates', json=json.dumps(payload), headers=headers)
                stdscr.addstr(loopLine, 0, "return: " + str(ret.status_code) + " " + ret.text)
            except Exception, ex:
                loopLine += 1
                #stdscr.addstr(loopLine, 0, "requests.post exception: " + ex.message)
                loopLine += 1
                stdscr.addstr(loopLine, 0, "Exception: " + str(ex))
                loopLine += 1
            else:
                loopLine += 1
                stdscr.addstr(loopLine, 0, "All good")
                loopLine += 2
            finally:
                loopLine += 1
                stdscr.addstr(loopLine, 0, "datetime: " + str(datetime.utcnow()))
                loopLine += 2
        else:
            if tempFanCounter > 0:
                tempFanCounter += 1
                if tempFanCounter > 60:
                    tempFanCounter = 0
#                tempFanCounter += 1
            stdscr.addstr(loopLine, 0, "tempFanCounter else: " + str(tempFanCounter) + "                    ")
            loopLine += 1

        loopLine += 1
        time.sleep(1)

        # if continue1 and loopCount > loopTime:
        #     loopCount = 0

            #itmp1 = 100 * DAQC.getADC(0, 0) - 50
            #tmp1 = round(tmp1, 1)
            #tmp2 = 100 * DAQC.getADC(0, 1) - 50
            #tmp2 = round(tmp2, 1)
            #tmp3 = 100 * DAQC.getADC(0, 2) - 50
            #tmp3 = round(tmp3, 1)
            #volts = DAQC.getADC(0, 3)
#             strtmp1 = str(fTemp1)
#             strtmp2 = str(fTemp2)
#             strtmp3 = str(fTemp3)
#
#             stdscr.addstr(loopLine, 0, "sentTmp1: " + strtmp1)
#             loopLine += 1
#             stdscr.addstr(loopLine, 0, "sentTmp2: " + strtmp2)
#             loopLine += 1
#             stdscr.addstr(loopLine, 0, "sentTmp3: " + strtmp3)
#             loopLine += 1
#
#             if fVolts < voltageTrigger:
#                 RELAY.relayON(0,7)
#                 chargerOn = True
#             else:
#                 RELAY.relayOFF(0,7)
#                 chargerOn = False
#
#
#             if fTemp1 > fanChangeTemp + fanDelta:
#                 RELAY.relayON(0,3)
#                 fanOn = True
#             elif fTemp1 < fanChangeTemp - fanDelta:
#                 RELAY.relayOFF(0,3)
#                 fanOn = False
#
# #            stdscr.addstr(loopLine, 0, "tmp1: " + strtmp1)
# #            loopLine += 1
# #            stdscr.addstr(loopLine, 0, "tmp2: " + strtmp2)
# #            loopLine += 1
# #            stdscr.addstr(loopLine, 0, "tmp3: " + strtmp3)
# #            loopLine += 1
#
#             payload = {"TEMP_1":fTemp1, "TEMP_2":fTemp2, "TEMP_3":fTemp3, "FAN_ON": fanOn, "CHARGER_ON": chargerOn, "VOLTAGE": fVolts, "GMT": str(datetime.utcnow())}
# #str(datetime.now(pytz.utc))}
#             stdscr.addstr(loopLine, 0, "payload: " + json.dumps(payload))
#             loopLine += 2
#
#             stdscr.addstr(loopLine, 0, "state: " + str(RELAY.relaySTATE(0)))
#             loopLine += 1
#
#             #headers = { 'content-type': 'application/json' }
#             try:
#                 ret = requests.post(url + 'piplates', json=json.dumps(payload), headers=headers)
#                 stdscr.addstr(loopLine, 0, "return: " + str(ret.status_code) + " " + ret.text)
#             except Exception, ex:
#                 loopLine += 1
#                 stdscr.addstr(loopLine, 0, "request.post : " + payload + " exception.")
#                 loopLine += 1
#                 stdscr.addstr(loopLine, 0, "Exception: " + str(ex))
#                 loopLine += 1
#             else:
#                 loopLine += 1
#                 stdscr.addstr(loopLine, 0, "All good")
#                 loopLine += 2
#             finally:
#                 loopLine += 1
#                 stdscr.addstr(loopLine, 0, "datetime: " + str(datetime.now(pytz.utc)))
#                 loopLine += 2
#         else:
#             loopCount += 1

        #time.sleep(1)
finally:
    curses.endwin()

