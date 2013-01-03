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

import sqlite3
from os.path import expanduser, exists, dirname, abspath, join
import logging

class DBInterface:
    """
    Handles the connections to the database
    """

    def __init__(self):
        """
        if the .db file doesn't exist create all the tables in the db
        """
        self.db_path = expanduser('~/.local/share/eclipsebb/eclipse.db')
        if not exists(self.db_path):
            logging.info('Creating database schema...')

            # schema declaration is stored in db.sql
            cwd = dirname(abspath(__file__))
            sql = open(join(cwd, './db.sql'), 'r').read()

            # initiate database 
            db = sqlite3.connect(self.db_path)
            db.executescript(sql)
            db.commit()
            db.close()

            logging.info('Database schema created.')

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
    def createGame(self, players, extensions):
        """ returns the game id """
        pass

    def saveGame(self, game):
        """
        update the content of the game row.
        also save the current state.
        """
        pass

    def loadGame(self, gameId):
        """ returns a game object """
        pass

    # infos saved in the database for a player:
    # -id: uniq id of the player (sqlite rowid)
    # -name: name of the player (uniq)
    # -email: email address of the player (uniq)
    # -password: md5 sum of the password
    def createPlayer(self, name, email, password):
        """
        register new player in database.
        if a player with same email or name already exists, raise an
        exception.
        """
        conn = sqlite3.connect(self.db_path)

        conn.close()

    def authPlayer(self, email, password):
        """
        check password with the one in database
        returns True if ok, False otherwise
        """
        pass

    # infos saved in the database for a state:
    # -id: uniq increasing id (sqlite rowid)
    # -gameid: id of the game hosting the state
    # -pickle: pickled string of the state
    def saveState(self, gameId, state):
        pass

    def loadState(self, stateId):
        pass

    # infos saved in the database for an extension:
    # -id uniq id of the extension (sqlite rowid)
    # -name name of the extension
    # -desc description of the extension
