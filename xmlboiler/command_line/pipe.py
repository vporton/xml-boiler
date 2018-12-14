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

import re


def split_pipeline(s):
    res = [['']]
    r = r'\\\\|\\\+|\\\s|\s+\+\s+|\s+|[^\s\\]+'
    for m in re.finditer(r, s, re.M|re.S):
        if m[0][0] == '\\':
            res[-1][-1] += m[0][1:]
        elif re.match(r'^\s+\+\s+$', m[0], re.M|re.S):
            res.append([''])
        elif re.match(r'^\s+$', m[0], re.M | re.S):
            res[-1].append('')
        else:
            res[-1][-1] += m[0]
    return res

# print(split_pipeline(r'a\\ \+  b + c\ d +'))
