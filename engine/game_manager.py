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
        # the games, accessed by their id
        # TODO::limit the number of games loaded in memory at the same
        # time to avoid too important memory consumption
        self.games = {}

        self.DB = DBInterface()

    def saveGame(self, gameId):
        """ save a game to the database """
        pass

    def loadGame(self, gameId):
        """ load a game from the database """
        pass

    def getGame(self, gameId):
        """
        Returns the game, load it from database if not already in
        memory
        """
        pass


    def getRunningGames(self, playerId):
        """ return the ids of the games the player is currently playing """
        pass

    def getEndedGames(self, playerId):
        """ return the ids of the completed games the player played in """
        pass


    def createNewGame(self, players, extensions):
        """
        Instanciate a new game using the list of players ids and the
        activated extensions.
        Store it in the database.
        """
        pass

    def createNewPlayer(self, name, email, password):
        """ create the player in the database """
        pass

    def 
