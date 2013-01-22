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
import hashlib
import logging
import pickle
from engine.data_types import WebPlayer

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

            # initiate database. do not catch exceptions, we want the
            # program to stop if we can't create the database.
            db = self.connect()
            db.executescript(sql)
            db.commit()
            db.close()

            logging.info('Database schema created.')

    def connect(self):
        """
        the detect_types param allow us to store python types directly
        in the databse.
        """
        return sqlite3.connect(self.db_path,
                               detect_types=sqlite3.PARSE_DECLTYPES)

    def createGame(self, game, players_ids):
        """ returns the game id """
        sql_game = "insert into games (name, level, private, password, \
start_date, num_players, creator_id) values (?, ?, ?, ?, ?, ?, ?);"
        params_game = (game.name, game.level, game.private, game.password,
                       game.start_date, game.num_players, game.creator_id)
        sql_player = "insert into games_players (game_id, player_id) \
values (?, ?);"
        sql_extension = "insert into games_extensions (game_id, \
extension_id) values (?, ?);"
        try:
            db = self.connect()
            cursor = db.cursor()

            # create game
            cursor.execute(sql_game, params_game)
            game_id = cursor.lastrowid

            # add game/player
            for player_id in players_ids:
                if player_id is not None and player_id != -1:
                    cursor.execute(sql_player, (game_id, player_id))
                    game.players_ids.append(player_id)

            # add game/extensions
            for ext_id in game.extensions.values():
                cursor.execute(sql_extension, (game_id, ext_id))

            # commit only when everything is inserted
            db.commit()
        except Exception:
            logging.exception("Can't create game {!r} by \
{}".format(game.name, game.creator_id))
            return None
        else:
            return game_id
        finally:
            cursor.close()
            db.close()

    def saveGame(self, game):
        """
        update the content of the game row.
        return None if error, True if success
        """
        sql = "update games set started=?, ended=?, level=?, \
cur_turn=?, cur_state=?, next_player=?, private=?, password=?, \
start_date=?, last_play=?, num_players=? where id = ?"
        try:
            db = self.connect()
            cursor = db.cursor()

            cursor.execute(sql, (game.started, game.ended, game.level,
                                 game.cur_turn, game.cur_state,
                                 game.next_player, game.private,
                                 game.password, game.start_date,
                                 game.last_play, game.num_players,
                                 game.id_))
            db .commit()
        except Exception:
            logging.exception()
            return None
        else:
            return True
        finally:
            cursor.close()
            db.close()

    def loadGame(self, game_id):
        """
        returns a game object
        do not load players ids, extensions ids, states ids
        """
        sql = "select * from games where id = ?;"
        try:
            db = self.connect()
            # to have access to returned row as a dict
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(sql, (game_id, ))
        except Exception:
            logging.exception("DBException while loading game with \
id {}".format(game_id))
            return None
        else:
            game_params = cursor.fetchone()
            if game_params is None:
                return None
            game = Game.fromDB(**game_params)
            return game
        finally:
            cursor.close()
            db.close()

    def getGamePlayersIds(self, game_id):
        """ return a list of players ids """
        sql = "select player_id from games_players where game_id = ?;"
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (game_id, ))
        except Exception:
            logging.exception("DBException while getting players for game \
with id {}".format(game_id))
            return None
        else:
            players_ids = cursor.fetchall()
            players_ids = [id_[0] for id_ in players_ids]
            return players_ids
        finally:
            cursor.close()
            db.close()

    def getGameExt(self, game_id):
        """ return a dict of id: name """
        sql = "select g.extension_id, e.name from games_extensions g, \
extensions e where g.extension_id = e.id and g.game_id = ?;"
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (game_id, ))
        except Exception:
            logging.exception("DBException while getting extensions for game\
 with id {}".format(game_id))
            return None
        else:
            ext_ids_names = cursor.fetchall()
            ext_ids_names = {id_: name for (id_, name) in ext_ids_names}
            return ext_ids_names
        finally:
            cursor.close()
            db.close()

    def getGameStatesIds(self, game_id):
        """ return a list of states ids """
        sql = "select id from state where game_id = ?;"
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (game_id, ))
        except Exception:
            logging.exception("DBException while getting states for game\
 with id {}".format(game_id))
            return None
        else:
            states_ids = cursor.fetchall()
            states_ids = [id_[0] for id_ in states_ids]
            return states_ids
        finally:
            cursor.close()
            db.close()

    def getPubPrivGamesIds(self):
        """
        return (None, None) if error
        """
        sql_pub = 'SELECT id FROM games where started = 0 and private = 0 \
order by name;'
        sql_priv = 'SELECT id FROM games where started = 0 and private = 1 \
order by name;'
        try:
            db = self.connect()
            cursor_pub = db.cursor()
            cursor_pub.execute(sql_pub)
            cursor_priv = db.cursor()
            cursor_priv.execute(sql_priv)
        except Exception:
            logging.exception("DBException while fetching pub/priv games")
            return (None, None)
        else:
            pub_ids = cursor_pub.fetchall()
            pub_ids = [id_[0] for id_ in pub_ids]
            priv_ids = cursor_priv.fetchall()
            priv_ids = [id_[0] for id_ in priv_ids]
            return (pub_ids, priv_ids)
        finally:
            cursor_pub.close()
            cursor_priv.close()
            db.close()

    # infos saved in the database for a player:
    # -id: uniq id of the player (sqlite rowid)
    # -name: name of the player (uniq)
    # -email: email address of the player (uniq)
    # -password: md5 sum of the password
    def getPassHash(self, id_, password):
        """ sha1 of the salted password """
        salted_pass = id_[:2] + password
        return hashlib.sha1(salted_pass.encode('utf-8')).hexdigest()

    def createPlayer(self, name, email, password, timezone):
        """
        register new player in database.
        return playerId
        return None if a player with same email or name already exists
        """
        sha1_pass = self.getPassHash(email, password)
        sql = "INSERT INTO players VALUES (NULL, ?, ?, ?, ?)"
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (name, email, sha1_pass, timezone))
            db.commit()
        except sqlite3.IntegrityError:
            logging.debug("Player ({}, {}) already registered".format(name, email))
            return None
        except Exception:
            logging.exception("DBException while creating player with \
name {}".format(name))
            return None
        else:
            # the id primary key = rowid in sqlite3
            playerId = cursor.lastrowid
            return playerId
        finally:
            cursor.close()
            db.close()

    def authPlayer(self, email, password):
        """
        check password with the one in database
        returns playerId if ok, None otherwise
        """
        sha1_pass = self.getPassHash(email, password)
        sql = 'select id from players where email = ? and password = ?'
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (email, sha1_pass))
        except Exception:
            logging.exception("DBException while auth player with \
email {}".format(email))
            return None
        else:
            result = cursor.fetchone()
            if result is None:
                return None
            else:
                player_id = result[0]
                return player_id
        finally:
            cursor.close()
            db.close()

    def loadPlayer(self, player_id):
        """"
        get player info in database, then instanciate a player
        """
        sql = 'select id, name, email, timezone from players where id = ?'
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (player_id, ))
        except Exception:
            logging.exception("DBException while loading player with \
id {}".format(player_id))
            return None
        else:
            result = cursor.fetchone()
            if result is None:
                return None
            else:
                return WebPlayer(*result)
        finally:
            cursor.close()
            db.close()


    def getPlayersInfos(self):
        """
        get players infos to be displayed in the game creation page
        return an ordered list (id, name)
        """
        sql = 'SELECT id, name FROM players order by name;'
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql)
        except Exception:
            logging.exception("DBException while fetching players")
            return None
        else:
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()
            db.close()

    def getTZ(self):
        """ return an ordered list (tzId, tzName) """
        sql = 'SELECT diff, name FROM timezones order by diff;'
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql)
        except Exception:
            logging.exception("DBException while fetching timezones")
            return None
        else:
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()
            db.close()

    def saveState(self, game_id, state):
        """
        infos saved in the database for a state:
         -id: uniq increasing id (sqlite rowid)
         -gameid: id of the game hosting the state
         -pickle: pickled string of the state

        return the state_id, None if error
        """
        sql = "INSERT INTO state VALUES (NULL, ?, ?);"
        try:
            pic_state = pickle.dumps(state)
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (game_id, pic_state))
            db.commit()
        except Exception:
            logging.exception("DBException while saving state for \
game {}".format(game_id))
            return None
        else:
            state_id = cursor.lastrowid
            return state_id
        finally:
            cursor.close()
            db.close()

    def loadState(self, state_id):
        """ return None if error """
        sql = "select pickle from state where id = ?;"
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (state_id, ))
        except Exception:
            logging.exception("DBException while loading state \
{}".format(state_id))
            return None
        else:
            pic_state = cursor.fetchone()
            return pickle.loads(pic_state)
        finally:
            cursor.close()
            db.close()

    def getExtensionsInfos(self):
        """ return a list (id, name, desc) """
        sql = 'SELECT id, name, desc FROM extensions;'
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql)
        except Exception:
            logging.exception("DBException while fetching extensions")
            return None
        else:
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()
            db.close()
