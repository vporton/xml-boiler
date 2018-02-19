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
    # TODO: Terminate the subprocesses on terminating our program.
    @classmethod
    def run_pipe(cls, args, input, timeout=None, timeout2=None):
        loop = asyncio.get_event_loop()
        try:
            future = asyncio.Future()
            res = loop.run_until_complete(cls.run_pipe_impl(cls, args, input, timeout, timeout2))
            # res = future.result()
        finally:
            loop.close()
        return res

    async def run_pipe_impl(cls, args, input, timeout=None, timeout2=None):
        t = await asyncio.create_subprocess_exec(*args, stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
        try:
            stdout, stderr = await asyncio.wait_for(t.communicate(input), timeout)
            return t.returncode, stdout
        except asyncio.TimeoutError:
            t.terminate()
            try:
                asyncio.wait_for(t.wait(), timeout2)
            except asyncio.TimeoutError:
                t.kill()
            raise Timeout()
