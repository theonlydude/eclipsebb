"""
Copyright (C) 2012  Emmanuel Gorse, Adrien Durand

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging

ind_level=0
ind_str=' '

def log(fun):
    """ a simple decorator do display functions calls with params/return """
    def logger(*args, **kargs):
        global ind_level
        global ind_str
        ind_level += 1
        logging.debug("{}in){} [{}] [[{}]]".format(ind_str*ind_level, fun,
                                                   args, kargs))
        ret = fun(*args, **kargs)
        logging.debug("{}out){} [{}]".format(ind_str*ind_level, fun, ret))
        ind_level -= 1
        return ret
    return logger

# to define c-like enums
def enum(**enums):
    return type('Enum', (), enums)
