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
import logging

def init(fileName):
    xdg_dir = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))
    path = os.path.join(xdg_dir, 'steam-tools')

    if not os.path.isdir(path):
        os.mkdir(path)

    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)

    file = logging.FileHandler(os.path.join(path, fileName))
    file.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    file.setLevel(logging.DEBUG)
    logger.addHandler(file)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(message)s'))
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    httpfile = logging.FileHandler(os.path.join(path, 'requests_'+fileName))
    httpfile.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    httpfile.setLevel(logging.DEBUG)

    requests = logging.getLogger("requests.packages.urllib3")
    requests.setLevel(logging.DEBUG)
    requests.removeHandler("root")
    requests.addHandler(httpfile)

    return logger