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
import sys
from engine.db import DBInterface, DB_STATUS
import engine.util
from engine.web_types import Game

class GamesManager(object):
    """
    As we can have multiple games running at the same time we need an
    object to handle them.
    The entry point for the webserver view.
    Save the games in the database after each turn.
    Load running games from the database (after a program stop).
    Allow to browse ended games.

    attributes:
      self._games (dict): the games, accessed by their id
      self._web_players (dict): the players, accessed by their id
      self._db (DBInterface object): the DB interface object
    """
    def __init__(self, test_mode=False):
        self._logger = logging.getLogger('eclipsebb.gm')

        # TODO::limit the number of games loaded in memory at the same
        # time to avoid too important memory consumption
        self._games = {}
        self._web_players = {}
        self._db = DBInterface(test_mode)

        # load constants from DB
        (status_ext, self.ext_infos) = self._db.get_extensions_infos()
        (status_tz, self.timezones) = self._db.get_timezones()
        # if a database error occurs so early, just quit
        if status_ext != DB_STATUS.OK or status_tz != DB_STATUS.OK:
            sys.exit()

    def debug(self, msg):
        """ called from mako templates to log stuffs """
        self._logger.debug(msg)

    @engine.util.log
    def create_game(self, creator_id, name, level, private, password,
                    num_players, players_ids, extensions):
        """ Instanciate a new game. Save it to the database to get its uniq id.
        Store it in self._games. Do not return the created game nor its id, the
        game will be visible to the player in the 'my games' view.

        args:
         creator_id (int): id of the player creating the game
         name (str): name of the game given by the creator
         level (int): difficulty (1-4)
         private (bool): True if password protected to join
         password (str): the password to join if private
         num_players (int): number of players in the game
         players_ids [int, ..., int]: list of players id already added to the
                                      game, includes the creator_id
         extensions {id (int) -> name (str)}: activated extensions
        return: db_ok (bool)
        """
        game = Game(creator_id, name, level, private, password,
                    num_players, extensions)

        (status, game) = self._db.create_game(game, players_ids)

        if status != DB_STATUS.OK:
            self._logger.error(("Error inserting game {!r} by {} in "
                                "database.").format(name, creator_id))
            return False

        self._logger.info("Game {!r} successfully created".format(name))

        self._games[game.id_] = game
        return True
        
    @engine.util.log
    def save_game(self, game):
        """ update an existing game into the database.
        args: game (Game object): the game to save
        return: db_ok (bool), upd_ok (bool)
        """
        (status, _) = self._db.save_game(game)
        return (status != DB_STATUS.ERROR, status != DB_STATUS.NO_ROWS)

    @engine.util.log
    def load_game(self, game_id, force=False):
        """ load a game from the database if not already in memory.
        fully load a game, i.e. also load:
         -players
         -extensions ids
         -states ids
         -current state

        args:
         game_id (int): id of the game to load
         force (bool): to force the loading of the game from db even if the game
                       is already in memory
        return:
         OK: (db_ok (bool): True, fully loaded Game object)
         NO_GAME: (db_ok: True, None)
         ERROR: (db_ok: False, None)
        """
        if not force and game_id in self._games:
            return (True, self._games[game_id])

        # load game
        (status, game) = self._db.load_game(game_id)
        if status == DB_STATUS.ERROR:
            self._logger.error("Error loading game {}".format(game_id))
            return (False, None)
        elif status == DB_STATUS.NO_ROWS:
            self._logger.warning("Game {} not found".format(game_id))
            return (True, None)

        # load players
        (status, players_ids) = self._db.get_game_players_ids(game_id)
        if status != DB_STATUS.OK:
            self._logger.error(("Error loading players ids for game "
                                "{}").format(game_id))
            return (False, None)

        game.players_ids = players_ids
        for player_id in players_ids:
            if self.get_player(player_id) == None:
                self._logger.error(("Error loading player {} for game "
                                    "{}").format(player_id, game_id))
                return (False, None)

        # load extensions
        (status, ext) = self._db.get_game_ext(game_id)
        if status != DB_STATUS.OK:
            self._logger.error(("Error loading extensions for game "
                                "{}").format(game_id))
            return (False, None)
        game.extensions = ext

        # load states
        (status, states_ids) = self._db.get_game_states_ids(game_id)
        if status != DB_STATUS.OK:
            self._logger.error(("Error loading states ids for game "
                                "{}").format(game_id))
            return (False, None)
        game.states_ids = states_ids

        # TODO::load current state

        self._games[game_id] = game

        return (True, self._games[game_id])

    @engine.util.log
    def get_game(self, game_id):
        """
        Returns the game, do NOT load it from database if not already in memory.
        The caller must have call load_game manually before.

        args: game_id (int)
        return:
         OK: Game object whose id is game_id
         ERROR: Raise a KeyError exception
        """
        return self._games[game_id]

    @engine.util.log
    def get_my_games(self, player_id):
        """ return the games the player is currently playing
        even the non started ones.
        args: player_id (int)
        return: (db_ok (bool), [game_1, ..., game_n])
        """
        status, my_games_ids = self._db.get_my_games_ids(player_id)
        if status != DB_STATUS.OK:
            return (False, None)

        my_games = []
        for id_ in my_games_ids:
            db_ok, game = self.load_game(id_)
            if db_ok and game is not None:
                my_games.append(game)

        return (True, my_games)

    @engine.util.log
    def get_pub_priv_games(self):
        """ return the not yet started, not ended games, public and private.
        args: None
        return:
         OK: (db_ok (bool): True,
              pubs ([game_1, ..., game_n]),
              privs ([game_1, ..., game_n]))
         ERROR: (db_ok (bool): False, None, None)
        """
        status, ids = self._db.get_pub_priv_games_ids()
        if status == DB_STATUS.ERROR:
            return (False, None, None)

        pub_ids, priv_ids = ids

        pub_games = []
        for id_ in pub_ids:
            db_ok, game = self.load_game(id_)
            if db_ok and game is not None:
                pub_games.append(game)

        priv_games = []
        for id_ in priv_ids:
            db_ok, game = self.load_game(id_)
            if db_ok and game is not None:
                priv_games.append(game)

        return (True, pub_games, priv_games)

    @engine.util.log
    def _load_player(self, player_id):
        """ load a player from the database.
        args: player_id (int)
        return:
         OK: player_id (int)
         ERROR: None
        """
        (status, player) = self._db.load_player(player_id)
        # TODO::handle NO_ROWS and ERROR
        if status != DB_STATUS.OK:
            return None
        else:
            self._web_players[player_id] = player
            return player_id

    @engine.util.log
    def get_player(self, player_id):
        """ load player if not present then return it.
        args: player_id (int)
        return:
         OK: Player object
         ERROR: None
        """
        if player_id not in self._web_players:
            if self._load_player(player_id) is None:
                return None

        return self._web_players[player_id]

    @engine.util.log
    def get_players_infos(self):
        """ get minimal infos (id and name) on all registered players.
        args: None
        return:
         OK: [(id_1, name_1), ..., (id_n, name_n)] ordered by name
         ERROR: None
        """
        (status, players_infos) = self._db.get_players_infos()
        if status != DB_STATUS.OK:
            return None
        else:
            return players_infos

    @engine.util.log
    def auth_player(self, email, password):
        """ check player password with the one encrypted in database.
        args:
         email (str): user email
         password (str): plain password
        return: (db_ok (bool), auth_ok (bool), player_id (int))
        """
        (status, id_) = self._db.auth_player(email, password)
        if status == DB_STATUS.OK:
            return (True, True, id_)
        elif status == DB_STATUS.NO_ROWS:
            return (True, False, None)
        else:
            return (False, None, None)

    @engine.util.log
    def create_player(self, name, email, password, tz_id):
        """ create a new player in the db.
        args:
         name (str): player name
         email (str): player email
         password (str): player plain password
         tz_id (int): id of the player timezone
        return: (db_ok (bool), dup_ok (bool), player_id (int))
        """
        (status, id_) = self._db.create_player(name, email, password, tz_id)
        if status == DB_STATUS.OK:
            return (True, True, id_)
        elif status == DB_STATUS.DUP_ERROR:
            return (True, False, None)
        else:
            return (False, None, None)

    @engine.util.log
    def update_player(self, player, to_update):
        """ update player email/password/tz_id in the db.
        args:
         player: unmodified Player object to update.
         to_update (dict): possible keys:
          email (str): new player email
          password (str): new player password
          timezone (int): new timezone id
        return: (db_ok (bool), upd_ok (bool))
        """
        (status, dummy) = self._db.update_player(player, to_update)
        if status == DB_STATUS.OK:
            # update player in memory
            if self._load_player(player.id_) is None:
                return (False, True)
            else:
                return (True, True)
        elif status == DB_STATUS.DUP_ERROR or status == DB_STATUS.NO_ROWS:
            return (True, False)
        else:
            return(False, False)
