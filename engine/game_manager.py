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
from os.path import expanduser, exists, join
from os import makedirs

from engine.db import DBInterface
from engine.data_types import Game

class GamesManager:
    """
    As we can have multiple games running at the same time we need an
    object to handle them.
    The entry point for the webserver.
    Save the games in the database after each turn.
    Load running games from the database (after a program stop).
    Allow to browse ended games.
    """
    def __init__(self):
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

        self.DB = DBInterface()

        self.ext_infos = self.DB.getExtensionsInfos()
        self.timezones = self.DB.getTZ()

    def saveGame(self, game_id):
        """ save a game to the database """
        self.DB.saveGame(self.games[game_id])

    def loadGame(self, game_id):
        """ load a game from the database """
        if game_id not in self.games:
            # load game
            game = self.DB.loadGame(game_id)
            if game is None:
                logging.error("Can't load game with id {}".format(game_id))
                return None

            # load players
            players_ids = self.DB.getGamePlayersIds(game_id)
            if players_ids is None:
                logging.error("Can't get players ids for game with id \
{}".format(game_id))
                return None

            game.players_ids = players_ids
            for player_id in players_ids:
                if self.loadPlayer(player_id) == None:
                    logging.error("Can't load player with id \
{}".format(player_id))
                    return None

            # load extensions
            ext = self.DB.getGameExt(game_id)
            if ext is None:
                logging.error("Can't load extensions for game with id \
{}".format(game_id))
                return None
            game.extensions = ext

            # load states
            states_ids = self.DB.getGameStatesIds(game_id)
            if states_ids is None:
                logging.error("Can't load states for game with id \
{}".format(game_id))
                return None
            game.states_ids = states_ids

            self.games[game_id] = game

        return self.games[game_id]

    def getGame(self, game_id):
        """
        Returns the game, load it from database if not already in
        memory
        """
        if game_id not in self.games:
            if not self.loadGame(game_id):
                return None
        return self.games[game_id]

    def getRunningGames(self, player_id):
        """ return the games the player is currently playing """
        pass
    #        web_games = self.DB.getRunningGames(player_id)
    #        games = []
    #        for web_game in web_games:
    #            game.append(self.loadGame(game_id))

    def getEndedGames(self, player_id):
        """ return the completed games the player played in """
        pass

    def getPubPrivGames(self):
        """ """
        pub_ids, priv_ids = self.DB.getPubPrivGamesIds()

        logging.debug("pub=[{}] priv=[{}]".format(pub_ids, priv_ids))

        pub_games = [self.getGame(id_) for id_ in pub_ids]
        if None in pub_games:
            return (None, None)

        priv_games = [self.getGame(id_) for id_ in priv_ids]
        if None in priv_games:
            return (None, None)

        return (pub_games, priv_games)

    def createGame(self, creator_id, name, level, private, password,
                   num_players, players, extensions):
        """
        Instanciate a new game
        return game_id if success, None otherwise
        """
        game = Game(creator_id, name, level, private, password,
                    num_players, extensions)

        game_id = self.DB.createGame(game, players)

        if game_id is None:
            logging.error("Error inserting game {!r} by {} in \
database.".format(name, creator_id))
            return None

        logging.info("Game {!r} successfully created".format(name))

        game.id_ = game_id
        self.games[game_id] = game
        return game_id
        
    def loadPlayer(self, player_id):
        """ load a player from the database """
        player = self.DB.loadPlayer(player_id)
        if player is None:
            return None
        else:
            self.web_players[player_id] = player
            return player_id

    def getPlayer(self, player_id):
        if player_id not in self.web_players:
            if self.loadPlayer(player_id) is None:
                return None

        return self.web_players[player_id]
