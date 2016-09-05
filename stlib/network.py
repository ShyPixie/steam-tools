#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2016
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

import logging
import threading
import time

import bs4
import gevent
import requests

import stlib
import ui

LOGGER = logging.getLogger(__name__)

STEAM_LOGIN_PAGES = [
    'https://steamcommunity.com/login/home/',
    'https://store.steampowered.com//login/',
]

USER_AGENT = {'User-Agent': 'Unknown/0.0.0'}


class Threaded(threading.Thread):
    def __init__(self, function, *args, **kwargs):
        threading.Thread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.return_ = None

    def run(self):
        self.return_ = self.function(*self.args, **self.kwargs)


# It's Magic!
def async_wait(function):
    def async_call(*args, **kwargs):
        thread = Threaded(function, *args, **kwargs)
        thread.start()

        while thread.is_alive():
            ui.Gtk.main_iteration()
            gevent.sleep(0.01)
        else:
            return thread.return_

    return async_call

@async_wait
def get_response(url, data=None, cookies=None, headers=USER_AGENT, timeout=10, verify='cacert.pem', stream=False):
    if headers:
        headers.update(USER_AGENT)

    kwargs = {'data': data,
              'headers': headers,
              'cookies': cookies,
              'timeout': timeout,
              'verify': verify,
              'stream': stream}

    for i in range(1, 4):
        try:
            if data:
                response = requests.post(url, **kwargs)
            else:
                response = requests.get(url, **kwargs)

            response.raise_for_status()
        except requests.exceptions.SSLError:
            LOGGER.critical('INSECURE CONNECTION DETECTED!')
            LOGGER.critical('Invalid SSL Certificates.')
            return None
        except(requests.exceptions.ConnectionError,
               requests.exceptions.RequestException,
               requests.exceptions.Timeout):
            LOGGER.error('Unable to connect. Trying again... ({}/3)'.format(i))
            time.sleep(3)
        else:
            return response


def try_get_response(service_name, url, data=None):
    config_parser = stlib.config.read()
    auto_recovery = False

    while True:
        try:
            cookies = config_parser._sections[service_name + 'Cookies']

            if not cookies:
                raise KeyError

            response = get_response(url, data, cookies)

            if service_name is 'steam':
                if any(page in str(response.content) for page in STEAM_LOGIN_PAGES):
                    raise requests.exceptions.TooManyRedirects
        except(requests.exceptions.TooManyRedirects, KeyError):
            if not auto_recovery:
                LOGGER.error('Unable to find cookies for {}'.format(service_name))
                LOGGER.error('Trying to auto recovery')
                auto_recovery = True
                cookies = stlib.browser.get_cookies(url)

                config_parser[service_name + 'Cookies'] = cookies
                stlib.config.write()
            else:
                LOGGER.error('Unable to get cookies for {}'.format(service_name))
                return None
        else:
            return response


def get_html(*args, **kwargs):
    response = get_response(*args, **kwargs)

    return bs4.BeautifulSoup(response.content, 'html.parser')


def try_get_html(*args, **kwargs):
    response = try_get_response(*args, **kwargs)

    if response:
        return bs4.BeautifulSoup(response.content, 'html.parser')
    else:
        return None
