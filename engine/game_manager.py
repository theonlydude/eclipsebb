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
import sys
import os
import os.path
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
        share_path = os.path.expanduser('~/.local/share/eclipsebb/')
        if not os.path.exists(share_path):
            os.makedirs(share_path, mode=0o755, exist_ok=True)

        # init logging
        log_file_name = os.path.join(share_path, 'eclipse.log')
        logging.basicConfig(filename=log_file_name, level=logging.DEBUG)
        logging.info('Starting')

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
        logging.debug(msg)

    @engine.util.log
    def create_game(self, creator_id, name, level, private, password,
                    num_players, players, extensions):
        """
        Instanciate a new game
        return True if success, False otherwise
        """
        game = Game(creator_id, name, level, private, password,
                    num_players, extensions)

        (status, game) = self._db.create_game(game, players)

        if status != DB_STATUS.OK:
            logging.error(("Error inserting game {!r} by {} in "
                           "database.").format(name, creator_id))
            return False

        logging.info("Game {!r} successfully created".format(name))

        self._games[game.id_] = game
        return True
        
    @engine.util.log
    def save_game(self, game_id):
        """ save a game to the database """
        (status, dummy) = self._db.save_game(self._games[game_id])
        return (status == DB_STATUS.OK)

    @engine.util.log
    def _load_game(self, game_id):
        """ load a game from the database """
        if game_id not in self._games:
            # load game
            (status, game) = self._db.load_game(game_id)
            # TODO::handle NO_ROWS and ERROR
            if status != DB_STATUS.OK:
                logging.error("Can't load game with id {}".format(game_id))
                return None

            # load players
            (status, players_ids) = self._db.get_game_players_ids(game_id)
            if status != DB_STATUS.OK:
                logging.error(("Can't get players ids for game with id "
                               "{}").format(game_id))
                return None

            game.players_ids = players_ids
            for player_id in players_ids:
                if self.get_player(player_id) == None:
                    logging.error(("Can't load player with id "
                                  "{}").format(player_id))
                    return None

            # load extensions
            (status, ext) = self._db.get_game_ext(game_id)
            if status != DB_STATUS.OK:
                logging.error(("Can't load extensions for game with id "
                               "{}").format(game_id))
                return None
            game.extensions = ext

            # load states
            (status, states_ids) = self._db.get_game_states_ids(game_id)
            if status != DB_STATUS.OK:
                logging.error(("Can't load states for game with id "
                               "{}").format(game_id))
                return None
            game.states_ids = states_ids

            self._games[game_id] = game

        return self._games[game_id]

    @engine.util.log
    def get_game(self, game_id):
        """
        Returns the game, load it from database if not already in
        memory
        """
        if game_id not in self._games:
            if not self._load_game(game_id):
                return None
        return self._games[game_id]

    @engine.util.log
    def get_my_games(self, player_id):
        """ return the games the player is currently playing
        even the non started ones """
        status, my_games_ids = self._db.get_my_games_ids(player_id)
        if status != DB_STATUS.OK:
            return (False, None)

        my_games = [self.get_game(id_) for id_ in my_games_ids]
        if None in my_games:
            return (False, None)

        return (True, my_games)

    @engine.util.log
    def get_ended_games(self, player_id):
        """ return the completed games the player played in """
        pass

    @engine.util.log
    def get_pub_priv_games(self):
        """ return (db_ok, pubs, privs) """
        status, ids = self._db.get_pub_priv_games_ids()
        if status == DB_STATUS.ERROR:
            return (False, None, None)

        pub_ids, priv_ids = ids
        if pub_ids is None or priv_ids is None:
            return (False, None, None)

        pub_games = [self.get_game(id_) for id_ in pub_ids]
        if None in pub_games:
            return (False, None, None)

        priv_games = [self.get_game(id_) for id_ in priv_ids]
        if None in priv_games:
            return (False, None, None)

        return (True, pub_games, priv_games)

    @engine.util.log
    def _load_player(self, player_id):
        """ load a player from the database.
        args: player_id (int)
        return:
         ERROR: None
         OK: player_id (int)
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
         ERROR: None
         OK: Player object
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
         ERROR: None
         OK: [(id_1, name_1), ..., (id_n, name_n)] ordered by name
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
        elif status == DB_STATUS.DUP_ERROR:
            return (True, False)
        else:
            return(False, False)
