"""
Copyright (C) 2012-2013  manu, adri

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
import os
import sys

_ind_level = 0
_IND_STR = ' '
def log(fun):
    """ a simple decorator to display functions calls with params/return """
    def _logger(*args, **kargs):
        """ inner function """
        global _ind_level
        _ind_level += 1

        app_logger = logging.getLogger('ecbb.util')
        app_logger.debug("{}in_){} [{}] [[{}]]".format(_IND_STR*_ind_level, fun,
                                                       args, kargs))
        ret = fun(*args, **kargs)
        app_logger.debug("{}out){} [{}]".format(_IND_STR*_ind_level, fun, ret))
        _ind_level -= 1
        return ret
    return _logger

def enum(**enums):
    """ to define c-like enums.
    usage: STATUS = engine.util.enum(OK=0, ERROR=1, DUP_ERROR=2, NO_ROWS=3)
    """
    return type('Enum', (), enums)

_already_called = False
def init_logging(test_mode=False):
    """ put logging into a log file, use different loggers for the different
    modules in the application, the main logger beeing called 'eclipsebb'
    """
    # called by every tests, but must be executed only once
    global _already_called
    if _already_called:
        return
    else:
        _already_called = True

    # directory storing the log file
    shared_path = os.path.expanduser('~/.local/share/eclipsebb/')
    try:
        os.makedirs(shared_path, mode=0o755, exist_ok=True)
    except OSError:
        msg = 'Error creating directory {}'.format(shared_path)
        logging.exception(msg)
        sys.exit()

    ## create a logger only during tests, pyramid already create one
    if test_mode is True:
        # init eclipsebb main logger
        logger = logging.getLogger('ecbb')
        logger.setLevel(logging.DEBUG)

        # during tests empty the log file first
        mode = 'w'
        log_file = os.path.join(shared_path, 'eclipsebb.log')
        file_hand = logging.FileHandler(log_file, mode=mode)
        file_hand.setLevel(logging.DEBUG)

        form = logging.Formatter(('%(asctime)s:%(levelname)-5.5s:'
                                  '[%(name)s]:%(message)s'))
        file_hand.setFormatter(form)
        logger.addHandler(file_hand)
