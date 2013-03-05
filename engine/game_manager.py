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

import logging, sys
from os.path import expanduser, exists, join
from os import makedirs

from engine.db import DBInterface, db_status
from engine.web_types import Game

from engine.util import log

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
        self.share_path = expanduser('~/.local/share/eclipsebb/')
        if not exists(self.share_path):
            makedirs(self.share_path, mode=0o755, exist_ok=True)

        # init logging
        log_file = join(self.share_path, 'eclipse.log')
        logging.basicConfig(filename=log_file, level=logging.DEBUG)
        logging.info('Starting')

        # the games, accessed by their id
        # TODO::limit the number of games loaded in memory at the same
        # time to avoid too important memory consumption
        self.games = {}

        # the players, accessed by their id
        self.web_players = {}

        self.DB = DBInterface(test_mode)

        (status_ext, self.ext_infos) = self.DB.getExtensionsInfos()
        (status_tz, self.timezones) = self.DB.getTZ()
        # if a database error occurs so early, just quit
        if status_ext != db_status.OK or status_tz != db_status.OK:
            sys.exit()

    def debug(self, msg):
        """ called from mako templates to log stuffs """
        logging.debug(msg)

    @log
    def createGame(self, creator_id, name, level, private, password,
                   num_players, players, extensions):
        """
        Instanciate a new game
        return True if success, False otherwise
        """
        game = Game(creator_id, name, level, private, password,
                    num_players, extensions)

        (status, game_id) = self.DB.createGame(game, players)

        if status != db_status.OK:
            logging.error("Error inserting game {!r} by {} in \
database.".format(name, creator_id))
            return False

        logging.info("Game {!r} successfully created".format(name))

        game.id_ = game_id
        self.games[game_id] = game
        return True
        
    @log
    def saveGame(self, game_id):
        """ save a game to the database """
        (status, dummy) = self.DB.saveGame(self.games[game_id])
        return (status == db_status.OK)

    @log
    def loadGame(self, game_id):
        """ load a game from the database """
        if game_id not in self.games:
            # load game
            (status, game) = self.DB.loadGame(game_id)
            if status != db_status.OK:
                logging.error("Can't load game with id {}".format(game_id))
                return None

            # load players
            (status, players_ids) = self.DB.getGamePlayersIds(game_id)
            if status != db_status.OK:
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
            (status, ext) = self.DB.getGameExt(game_id)
            if status != db_status.OK:
                logging.error("Can't load extensions for game with id \
{}".format(game_id))
                return None
            game.extensions = ext

            # load states
            (status, states_ids) = self.DB.getGameStatesIds(game_id)
            if status != db_status.OK:
                logging.error("Can't load states for game with id \
{}".format(game_id))
                return None
            game.states_ids = states_ids

            self.games[game_id] = game

        return self.games[game_id]

    @log
    def getGame(self, game_id):
        """
        Returns the game, load it from database if not already in
        memory
        """
        if game_id not in self.games:
            if not self.loadGame(game_id):
                return None
        return self.games[game_id]

    @log
    def getMyGames(self, player_id):
        """ return the games the player is currently playing
        even the non started ones """
        status, my_games_ids = self.DB.getMyGamesIds(player_id)
        if status != db_status.OK:
            return (False, None)

        my_games = [self.getGame(id_) for id_ in my_games_ids]
        if None in my_games:
            return (False, None)

        return (True, my_games)

    @log
    def getEndedGames(self, player_id):
        """ return the completed games the player played in """
        pass

    @log
    def getPubPrivGames(self):
        """ return (db_ok, pubs, privs) """
        status, (pub_ids, priv_ids) = self.DB.getPubPrivGamesIds()
        if status == db_status.ERROR:
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

    @log
    def loadPlayer(self, player_id):
        """ load a player from the database """
        (status, player) = self.DB.loadPlayer(player_id)
        if status != db_status.OK:
            return None
        else:
            self.web_players[player_id] = player
            return player_id

    @log
    def getPlayer(self, player_id):
        if player_id not in self.web_players:
            if self.loadPlayer(player_id) is None:
                return None

        return self.web_players[player_id]

    @log
    def getPlayersInfos(self):
        (status, players_infos) = self.DB.getPlayersInfos()
        if status != db_status.OK:
            return None
        else:
            return players_infos

    @log
    def authPlayer(self, email, password):
        """ return (db_ok, auth_ok, player_id) """
        (status, id_) = self.DB.authPlayer(email, password)
        if status == db_status.OK:
            return (True, True, id_)
        elif status == db_status.CONST_ERROR:
            return (True, False, None)
        else:
            return (False, None, None)

    @log
    def createPlayer(self, name, email, password, tz):
        """ return (db_ok, dup_ok, player_id) """
        (status, id_) = self.DB.createPlayer(name, email, password, tz)
        if status == db_status.OK:
            return (True, True, id_)
        elif status == db_status.CONST_ERROR:
            return (True, False, None)
        else:
            return (False, None, None)

    @log
    def updatePlayer(self, player, to_update):
        """ return (db_ok, upd_ok) """
        (status, dummy) = self.DB.updatePlayer(player, to_update)
        if status == db_status.OK:
            return (True, True)
        elif status == db_status.CONST_ERROR:
            return (True, False)
        else:
            return(False, None)
