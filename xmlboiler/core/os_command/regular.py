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
import sys

from dependency_injector import providers
from subprocess import PIPE, DEVNULL

from xmlboiler.core.execution_context_builders import my_logger
from .base import Timeout


class RegularCommandRunner(object):
    def __init__(self, timeout=None, timeout2=None):
        self.timeout = timeout
        self.timeout2 = timeout2

    # TODO: Terminate the subprocesses on terminating our program.
    def run_pipe(self, args, input):
        loop = asyncio.get_event_loop()
        try:
            # asyncio.set_event_loop(loop)
            # future = asyncio.Future()
            res = loop.run_until_complete(self.run_pipe_impl(args, input))
            # res = future.result()
        finally:
            pass  # loop.close()
        return res

    async def run_pipe_impl(self, args, input):
        my_logger().info("Executing:" + ' '.join(args))  # TODO: Dependency injection
        t = await asyncio.create_subprocess_exec(*args, stdin=PIPE, stdout=PIPE)
        try:
            stdout, stderr = await asyncio.wait_for(t.communicate(input), self.timeout)
            return t.returncode, stdout
        except asyncio.TimeoutError:
            t.terminate()
            try:
                await asyncio.wait_for(t.wait(), self.timeout2)
            except asyncio.TimeoutError:
                t.kill()
            raise Timeout()


# TODO: Use proper dependency injection
regular_provider = providers.Factory(RegularCommandRunner,
                                     timeout=None,
                                     timeout2=None)