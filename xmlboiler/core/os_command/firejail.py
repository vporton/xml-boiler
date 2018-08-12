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
from dependency_injector import providers

from xmlboiler.core.data import Global
from .regular import RegularCommandRunner


class FirejailCommandRunner(object):
    """
    This does not isolate from X11 on Linux because of abstract sockets!
    """

    def __init__(self, netfilter, timeout=None, timeout2=None):
        self.base = RegularCommandRunner(timeout=timeout, timeout2=timeout2)  # TODO: Use provider
        self.netfilter = netfilter

    def run_pipe(self, args, input):
        """
        This does not isolate from X11 on Linux because of abstract sockets!

        TODO: --rlimit-* --timeout
        """
        fj = ['firejail', '--shell=none', '-c', '--quiet', '--caps.drop=all', '--disable-mnt',
              '--protocol=unix,inet',  # TODO: Also enable IPv6 (after creating the firewall)
              '--netfilter=' + self.netfilter,
              '--hostname=none', '--machine-id', '--name=xmlboiler',
              '--nogroups', '--private', '--private-tmp', '--seccomp',
              '--nodvd', '--nonewprivs', '--nosound', '--notv', '--novideo', #'--x11=none',
              '--blacklist=/home', '--blacklist=/root']
        return self.base.run_pipe(fj + args, input)

firejail_provider = providers.Factory(FirejailCommandRunner,
                                      netfilter=Global.get_filename('core/data/mynolocal.net'),
                                      timeout=None,
                                      timeout2=None)