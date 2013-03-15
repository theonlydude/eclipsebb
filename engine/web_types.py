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

from collections import OrderedDict
from datetime import datetime
from engine.data_types import GameState

class WebPlayer(object):
    """ Map the infos stored in database """
    def __init__(self, *args):
        (self.id_,
         self.name,
         self.email,
         self.tz_id,
         self.password) = args

class Timezones(object):
    """ cache tz, allow easy access to tz.

    attributes:
      self.list_tz: timezones arg
      self.dict_tz: {id_1 (int): name_1 (str),
                     ...,
                     id_n: name_n} with keys ordered by id
    """
    def __init__(self, timezones):
        """
        args:
          timezones: [(id_1 (int), name_1 (str)),
                      ...,
                      (id_n, name_n)] ordered by id
        """
        self.list_tz = timezones
        self.dict_tz = OrderedDict(timezones)

class Game(object):
    """ The base game offers functions to query the game state, to apply
    player actions and to export a game state in json.
    It offers hook for extensions.

    can be instanciate two way:
     -when creating a new game from scratch
     -when loading from the DB
    """
    def __init__(self, creator_id, name, level, private, password,
                 num_players, extensions):
        """ creating new game """
        ####################
        # fields saved in DB
        self.id_ = None
        self.name = name
        self.started = False
        self.ended = False
        self.level = level
        self.cur_state_id = -1

        self.private = private
        self.password = password
        self.start_date = datetime.utcnow()
        self.last_play = None
        self.num_players = num_players
        self.creator_id = creator_id

        # the players who joined the game
        self.players_ids = []
        # the activated extensions
        # extensions is a dict of name->id
        self.extensions = extensions
        # the different states throughout the game
        self.state_ids = []

        ########################
        # fields not saved in DB

        # used to revert to the state at the beginning of a player
        # turn if one of its actions is not valid
        self.last_valid_state_id = None

        self.cur_state = GameState(num_players)

    @classmethod
    def from_db(cls, **kargs):
        """ constructor when game is loaded from DB """
        game = cls(kargs['creator_id'], kargs['name'], kargs['level'],
                   kargs['private'], kargs['password'],
                   kargs['num_players'], {})
        game.id_ = kargs['id']
        game.started = kargs['started']
        game.ended = kargs['ended']
        game.cur_state_id = kargs['cur_state_id']
        game.start_date = kargs['start_date']
        game.last_play = kargs['last_play']

        return game

    def load_cur_state(self):
        """ when loading a game from the DB the current state is not loaded,
        it must be manually loaded later by the games manager.
        args: None
        return:
         True: loading successful
         False: error loading/missing state
        """
        if self.cur_state_id == -1:
            return True

        # load current state from DB
        # TODO::if db error or missing state ??
        return True

#    def get_state(self, state_id):
#        """ access to previous states """
#        pass
#
#    def json_state_export(self, state_id):
#        """ returns the json string of the state """
#        pass
#
#    def revert_to_state(self, state_id):
#        """
#        in case one the player action is invalid or if a player want
#        to revert its last turn
#        """
#        pass
#
#    def get_history(self, state_id):
#        """
#        returns a string with all the actions done since the beginning
#        of the game up to the current state, in a textual form
#        """
#        pass
#
#    def init_game(self, players):
#        """
#        initalize the first game state
#        """
#        pass
