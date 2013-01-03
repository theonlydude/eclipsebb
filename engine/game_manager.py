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
import hashlib

from engine.db import DBInterface

class GamesManager:
    """
    As we can have multiple games running at the same time we need an
    object to handle them.
    The entry point for the webserver.
    Save the games in the database after each turn.
    Load running games from the database (after a program stop).
    Allow to browse ended games.

    Do not catch database exceptions, to be handled with a big
    try/catch by the webserver.
    """
    def __init__(self):
        self.share_path = expanduser('~/.local/share/eclipsebb/')
        if not exists(self.share_path):
            makedirs(self.share_path, mode=0o755, exist_ok=True)

        # init logging
        log_file = join(self.share_path, 'eclipse.log')
        logging.basicConfig(filename=log_file, level=logging.INFO)

        # the games, accessed by their id
        # TODO::limit the number of games loaded in memory at the same
        # time to avoid too important memory consumption
        self.games = {}

        self.DB = DBInterface()

    def saveGame(self, gameId):
        """ save a game to the database """
        self.DB.saveGame(self.games[gameId])

    def loadGame(self, gameId):
        """ load a game from the database """
        self.games[gameId] = self.DB.loadGame(gameId)

    def getGame(self, gameId):
        """
        Returns the game, load it from database if not already in
        memory
        """
        if gameId in self.games:
            return self.games[gameId]
        else:
            self.loadGame(gameId)
            return self.games[gameId]

    def getRunningGames(self, playerId):
        """ return the ids of the games the player is currently playing """
        pass

    def getEndedGames(self, playerId):
        """ return the ids of the completed games the player played in """
        pass


    def createNewGame(self, players, extensions):
        """
        Instanciate a new game:
         1. create in db to get id
         2. add players/extensions relations in db
         3. create game object
         4. instantiate first state
         5. save game in db
         6. store new game
        """
        # 1,2
        gameId = self.DBInterface.createGame(players, extensions)

        # 3
        game = BaseGame(gameId, extensions)
        # 4
        game.initGame(players)

        # 5
        self.DBInterface.saveGame(game)

        # 6
        self.games[gameId] = game

        return gameId

    def createPlayer(self, name, email, password):
        """
        create the player in the database.
        raise an exception if already a user with same name or email
        """
        sha1_pass = self.getPassHash(email, password)
        playerId = self.DBInterface.createPlayer(name, email, sha1_pass)

        return playerId

    def getPassHash(self, id_, password):
        """ sha1 of the salted password """
        salted_pass = id_[:2] + password
        return hashlib.sha1(salted_pass.encode('utf-8')).hexdigest()
        

    def authPlayer(self, email, password):
        """ return True/False """
        sha1_pass = self.getPassHash(email, password)
        return self.DBInterface.authPlayer(email, sha1_pass)
        
