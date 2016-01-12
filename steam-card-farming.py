#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015
#
# The Steam Tools is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The Steam Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

import os
import subprocess
from time import sleep
from signal import signal, SIGINT
from bs4 import BeautifulSoup as bs

from stlib import stlogger
from stlib import stconfig
from stlib.stnetwork import tryConnect, spamConnect

logger = stlogger.init(os.path.splitext(os.path.basename(__file__))[0]+'.log')
config = stconfig.init(os.path.splitext(os.path.basename(__file__))[0]+'.config')

try:
    cookies = {'sessionid': config.get('COOKIES', 'SessionID'), 'steamLogin': config.get('COOKIES', 'SteamLogin')}
    profile = "http://steamcommunity.com/id/" + config.get('UserInfo', 'ProfileName')
    sort = config.getboolean('CONFIG', 'MostValuableFirst')
    icheck = config.getboolean('DEBUG', "IntegrityCheck")
    dryrun = config.getboolean('DEBUG', "DryRun")
except(configparser.NoOptionError, configparser.NoSectionError):
    logger.critical("Incorrect data. Please, check your config file.")
    exit(1)

def signal_handler(signal, frame):
    print("\n")
    logger.info("Exiting...")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    logger.info("Digging your badge list...")
    fullPage = tryConnect(profile+"/badges/", cookies=cookies).content
    pageCount = bs(fullPage, 'html.parser').findAll('a', class_='pagelink')
    if pageCount:
        logger.debug("I found {} pages of badges".format(pages[-1].text))
        badges = []
        for currentPage in range(1, int(pages[-1].text)):
            page = tryConnect(profile+"/badges/?p="+str(currentPage), cookies=cookies).content
            badges += bs(page, 'html.parser').findAll('div', class_='badge_title_row')
    else:
        logger.debug("I found only 1 pages of badges")
        badges = bs(fullPage, 'html.parser').findAll('div', class_='badge_title_row')

    if not badges:
        logger.critical("Something is wrong! (Invalid profile name?)")
        exit(1)

    logger.info("Checking if we are logged.")
    if not bs(fullPage, 'html.parser').findAll('div', class_='profile_xp_block_right'):
        logger.critical("You are not logged into steam! (Invalid cookies?)")
        exit(1)

    logger.info("Getting badges info...")
    badgeSet = {}
    badgeSet['gameID'   ] = []
    badgeSet['gameName' ] = []
    badgeSet['cardCount'] = []
    badgeSet['cardURL'  ] = []
    badgeSet['cardValue'] = []
    for badge in badges:
        progress = badge.find('span', class_='progress_info_bold')
        title = badge.find('div', class_='badge_title')
        title.span.unwrap()

        if not progress or "No" in progress.text:
            logger.debug("{} have no cards to drop. Ignoring.".format(title.text.split('\t\t\t\t\t\t\t\t\t', 2)[1]))
            continue

        badgeSet['cardCount'].append(int(progress.text.split(' ', 3)[0]))
        badgeSet['gameID'].append(badge.find('a')['href'].split('/', 3)[3])
        badgeSet['gameName'].append(title.text.split('\t\t\t\t\t\t\t\t\t', 2)[1])
        badgeSet['cardURL'].append("http://api.enhancedsteam.com/market_data/average_card_price/?appid="+badgeSet['gameID'][-1]+"&cur=usd")

    logger.info("Getting cards values...")
    badgeSet['cardValue'] = spamConnect('text', badgeSet['cardURL'])

    if icheck:
        logger.debug("Checking consistency of dictionaries...")
        rtest = [ len(badgeSet[i]) for i,v in badgeSet.items() ]
        if len(set(rtest)) == 1:
            logger.debug("Looks good.")
        else:
            logger.debug("Very strange: {}".format(rtest))
            exit(1)

    if sort:
        logger.info("Getting highest card value...")
        if icheck: logger.debug("OLD: {}".format(badgeSet))
        order = sorted(range(0, len(badgeSet['cardValue'])), key=lambda key: badgeSet['cardValue'][key], reverse=True)
        for item, value in badgeSet.items():
            badgeSet[item] = [value[i] for i in order]
        if icheck:
            logger.debug("NEW: {}".format(badgeSet))

    logger.info("Ready to start.")
    for index in range(0, len(badgeSet['gameID'])):
        print("")
        logger.info("Starting game {} ({})".format(badgeSet['gameName'][index], badgeSet['gameID'][index]))
        if not dryrun:
            fakeApp = subprocess.Popen(['python', 'fake-steam-app.py', badgeSet['gameID'][index]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            print("{:2d} cards drop remaining. Waiting... {:7s}".format(badgeSet['cardCount'][index], ' '), end='\r')
            logger.debug("Waiting cards drop loop")
            if icheck: logger.debug("Current: {}".format([badgeSet[i][index] for i,v in badgeSet.items()]))
            for i in range(0, 30):
                if not dryrun and fakeApp.poll():
                    print("")
                    logger.critical(fakeApp.stderr.read().decode('utf-8'))
                    exit(1)
                sleep(1)

            print("Checking if game have more cards drops...", end='\r')
            logger.debug("Updating cards count")
            if icheck: logger.debug("OLD: {}".format(badgeSet['cardCount'][index]))
            badge = tryConnect(profile+"/gamecards/"+badgeSet['gameID'][index], cookies=cookies).content
            badgeSet['cardCount'][index] = bs(badge, 'html.parser').find('span', class_="progress_info_bold")
            if icheck: logger.debug("NEW: {}".format(badgeSet['cardCount'][index]))
            if dryrun: badgeSet['cardCount'][index] = ""
            if not badgeSet['cardCount'][index] or "No" in badgeSet['cardCount'][index].text:
                print("")
                logger.info("The game has no more cards to drop.")
                break
            else:
                badgeSet['cardCount'][index] = int(badgeSet['cardCount'][index].text.split(' ', 3)[0])

        logger.info("Closing {}".format(badgeSet['gameName'][index]))
        if not dryrun:
            fakeApp.terminate()
            fakeApp.wait()

    logger.info("There's nothing else we can do. Leaving.")
