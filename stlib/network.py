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

import requests


class Session:
    def __init__(self):
        self.session = requests.Session()

    def update_headers(self, data):
        self.session.headers.update(data)

    def update_cookies(self, cookies):
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)

    def get_response(self, url, data=None, timeout=10, verify='cacert.pem', stream=False):
        try:
            if data:
                response = self.session.post(url, data=data, timeout=timeout, verify=verify, stream=stream)
            else:
                response = self.session.get(url, timeout=timeout, verify=verify, stream=stream)

            response.raise_for_status()
            return response
        except requests.exceptions.TooManyRedirects:
            return 1
        except requests.exceptions.HTTPError:
            return 2
