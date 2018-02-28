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

from .regular import RegularCommandRunner


class FirejailCommandRunner(object):
    def __init__(self, timeout=None, timeout2=None):
        self.base = RegularCommandRunner(timeout=timeout, timeout2=timeout2)

    def run_pipe(self, args, input):
        # TODO: --rlimit-* Use an object (not class method), also store timeout and timeout2 in the object
        # FIXME: X11 is not blocked! --net=eth0 or --netfilter=... --netfilter6=...
        fj = ['firejail', '--shell=none', '-c', '--quiet', '--private', '--caps.drop=all', '--disable-mnt',
              '--netfilter', '--nodvd', '--nonewprivs', '--nosound', '--notv', '--novideo', '--x11=none',
              '--blacklist=/home']
        return self.base.run_pipe(fj + args, input)