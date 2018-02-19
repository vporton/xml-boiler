#  Copyright (c) 2018 Victor Porton,
#  XML Boiler - http://freesoft.portonvictor.org
#
#  This file is part of XML Boiler.
#
#  XML Boiler is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.

import asyncio
from subprocess import PIPE, DEVNULL

from .base import Timeout


class RegularCommandRunner(object):
    @classmethod
    def run_pipe(cls, args, input, timeout=None, timeout2=None):
        loop = asyncio.get_event_loop()
        future = asyncio.Future(cls.run_pipe_impl(args, input, timeout, timeout2))
        loop.run_until_complete(future)
        res = future.result()
        loop.close()
        return res

    async def run_pipe_impl(cls, args, input, timeout=None, timeout2=None):
        t = asyncio.create_subprocess_exec(*args, stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
        # FIXME: t.communicate -> t.communicate() and t.wait -> t.wait()?
        try:
            stdout, = asyncio.wait_for(t.communicate, timeout)
            # TODO: check exit status (check=True)
            return stdout
        except asyncio.TimeoutError:
            t.terminate()
            try:
                asyncio.wait_for(t.wait, timeout2)
            except asyncio.TimeoutError:
                t.kill()
            raise Timeout()
