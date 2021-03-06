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

import os
import sys
import ctypes
import time

if __name__ == "__main__":
    if len(sys.argv) > 2:
        os.environ["SteamAppId"] = sys.argv[1]

        try:
            steam_api = ctypes.CDLL(sys.argv[2])
        except OSError:
            sys.exit(1)

        if not steam_api.SteamAPI_Init():
            sys.exit(1)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            os.environ.pop("SteamAppId")
            steam_api.SteamAPI_Shutdown()
            sys.exit(0)

    sys.exit(1)
