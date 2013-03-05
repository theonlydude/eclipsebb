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

# TODO::do we need it ?
class StatesManager(object):
    """
    store the states, accessed by their id
    """
    def __init__(self):
        self.states = {}

    def get(self, id_):
        """ return a state """
        if id_ in self.states:
            return self.states[id_]
        else:
            return None

    def add(self, state):
        pass

class GamesManager(object):
    """
    As we can have multiple games running at the same time we need an
    object to handle them.
    The entry point for the webserver.
    Save the games in the database after each turn.
    Load running games from the database (after a program stop).
    Allow to browse ended games.
    """
    def __init__(self, test_mode=False):
        share_path = os.path.expanduser('~/.local/share/eclipsebb/')
        if not os.path.exists(share_path):
            os.makedirs(share_path, mode=0o755, exist_ok=True)

        # init logging
        log_file = os.path.join(share_path, 'eclipse.log')
        logging.basicConfig(filename=log_file, level=logging.DEBUG)
        logging.info('Starting')

        # the games, accessed by their id
        # TODO::limit the number of games loaded in memory at the same
        # time to avoid too important memory consumption
        self._games = {}

        # the players, accessed by their id
        self._web_players = {}

        self.DB = DBInterface(test_mode)

        (status_ext, self.ext_infos) = self.DB.get_extensions_infos()
        (status_tz, self.timezones) = self.DB.get_TZ()
        # if a database error occurs so early, just quit
        if status_ext != DB_STATUS.OK or status_tz != DB_STATUS.OK:
            sys.exit()

    def debug(self, msg):
        """ called from mako templates to log stuffs """
        logging.debug(msg)

    @engine.util.log
    def createGame(self, creator_id, name, level, private, password,
                   num_players, players, extensions):
        """
        Instanciate a new game
        return True if success, False otherwise
        """
        game = Game(creator_id, name, level, private, password,
                    num_players, extensions)

        (status, game_id) = self.DB.create_game(game, players)

        if status != DB_STATUS.OK:
            logging.error("Error inserting game {!r} by {} in \
database.".format(name, creator_id))
            return False

        logging.info("Game {!r} successfully created".format(name))

        game.id_ = game_id
        self._games[game_id] = game
        return True
        
    @engine.util.log
    def saveGame(self, game_id):
        """ save a game to the database """
        (status, dummy) = self.DB.save_game(self._games[game_id])
        return (status == DB_STATUS.OK)

    @engine.util.log
    def loadGame(self, game_id):
        """ load a game from the database """
        if game_id not in self._games:
            # load game
            (status, game) = self.DB.load_game(game_id)
            if status != DB_STATUS.OK:
                logging.error("Can't load game with id {}".format(game_id))
                return None

            # load players
            (status, players_ids) = self.DB.get_game_players_ids(game_id)
            if status != DB_STATUS.OK:
                logging.error("Can't get players ids for game with id \
{}".format(game_id))
                return None

            game.players_ids = players_ids
            for player_id in players_ids:
                if self.getPlayer(player_id) == None:
                    logging.error("Can't load player with id \
{}".format(player_id))
                    return None

            # load extensions
            (status, ext) = self.DB.get_game_ext(game_id)
            if status != DB_STATUS.OK:
                logging.error("Can't load extensions for game with id \
{}".format(game_id))
                return None
            game.extensions = ext

            # load states
            (status, states_ids) = self.DB.get_game_states_ids(game_id)
            if status != DB_STATUS.OK:
                logging.error("Can't load states for game with id \
{}".format(game_id))
                return None
            game.states_ids = states_ids

            self._games[game_id] = game

        return self._games[game_id]

    @engine.util.log
    def getGame(self, game_id):
        """
        Returns the game, load it from database if not already in
        memory
        """
        if game_id not in self._games:
            if not self.loadGame(game_id):
                return None
        return self._games[game_id]

    @engine.util.log
    def getMyGames(self, player_id):
        """ return the games the player is currently playing
        even the non started ones """
        status, my_games_ids = self.DB.get_my_games_ids(player_id)
        if status != DB_STATUS.OK:
            return (False, None)

        my_games = [self.getGame(id_) for id_ in my_games_ids]
        if None in my_games:
            return (False, None)

        return (True, my_games)

    @engine.util.log
    def getEndedGames(self, player_id):
        """ return the completed games the player played in """
        pass

    @engine.util.log
    def getPubPrivGames(self):
        """ return (db_ok, pubs, privs) """
        status, (pub_ids, priv_ids) = self.DB.get_pub_priv_games_ids()
        if status == DB_STATUS.ERROR:
            return (False, None, None)

        if pub_ids is None or priv_ids is None:
            return (False, None, None)

        pub_games = [self.getGame(id_) for id_ in pub_ids]
        if None in pub_games:
            return (False, None, None)

        priv_games = [self.getGame(id_) for id_ in priv_ids]
        if None in priv_games:
            return (False, None, None)

        return (True, pub_games, priv_games)

    @engine.util.log
    def loadPlayer(self, player_id):
        """ load a player from the database """
        (status, player) = self.DB.load_player(player_id)
        if status != DB_STATUS.OK:
            return None
        else:
            self._web_players[player_id] = player
            return player_id

    @engine.util.log
    def getPlayer(self, player_id):
        if player_id not in self._web_players:
            if self.loadPlayer(player_id) is None:
                return None

        return self._web_players[player_id]

    @engine.util.log
    def getPlayersInfos(self):
        (status, players_infos) = self.DB.get_players_infos()
        if status != DB_STATUS.OK:
            return None
        else:
            return players_infos

    @engine.util.log
    def authPlayer(self, email, password):
        """ return (db_ok, auth_ok, player_id) """
        (status, id_) = self.DB.auth_player(email, password)
        if status == DB_STATUS.OK:
            return (True, True, id_)
        elif status == DB_STATUS.CONST_ERROR:
            return (True, False, None)
        else:
            return (False, None, None)

    @engine.util.log
    def createPlayer(self, name, email, password, tz):
        """ return (db_ok, dup_ok, player_id) """
        (status, id_) = self.DB.create_player(name, email, password, tz)
        if status == DB_STATUS.OK:
            return (True, True, id_)
        elif status == DB_STATUS.CONST_ERROR:
            return (True, False, None)
        else:
            return (False, None, None)

    @engine.util.log
    def updatePlayer(self, player, to_update):
        """ return (db_ok, upd_ok) """
        (status, dummy) = self.DB.update_player(player, to_update)
        if status == DB_STATUS.OK:
            return (True, True)
        elif status == DB_STATUS.CONST_ERROR:
            return (True, False)
        else:
            return(False, None)
