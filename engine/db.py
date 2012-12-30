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

class DBInterface:
    """
    Handles the connections to the database
    """

    def initDB(self):
        """
        if the .db file doesn't exist create all the tables in the db
        """
        pass

    # infos saved in the database for a game:
    # -id uniq id of the game (sqlite rowid)
    # -ended
    # -current state id
    #
    # game/players relations stored in a table:
    # -id
    # -player id
    #
    # game/extensions relations stored in a table:
    # -id
    # -extension id
    def saveGame(self, game):
        """ """
        pass

    def createGame(self, ):
        pass

    # infos saved in the database for a state:
    # -id: uniq increasing id (sqlite rowid)
    # -gameid: id of the game hosting the state
    # -pickle: pickled string of the state
