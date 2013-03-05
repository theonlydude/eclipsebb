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
import tempfile
from engine.web_types import Player, Timezones, Game
from engine.util import log, enum

# status returned by all db methods
db_status = enum(OK=0, ERROR=1, CONST_ERROR=2)

# allow some queries to fail for unittest
_fail=False
_fail_filter=None

def change_db_fail(activate, filter_=None):
    global _fail
    global _fail_filter
    _fail = activate
    _fail_filter = filter_

def fail(fun):
    """
    a decorator allowing db calls to return read/write failure
    can filter on function name
    """
    def failer(*args, **kargs):
        global _fail
        global _fail_filter

#        if _fail_filter is not None:
#            print("filter=[{}]".format(_fail_filter))
#            print("fun=[{}]".format(fun.__name__))

        if _fail is True and (_fail_filter is None
                              or fun.__name__ == _fail_filter):
            return (db_status.ERROR, None)
        else:
            return fun(*args, **kargs)

    return failer

class DBInterface:
    """
    Handles the connections to the database

    All methods return a tuple: (db_status, param)
    enum db_status:
     OK: if no error
     ERROR: if database write/read error
     CONST_ERROR: if database constraints error
    param: optionnal returned param depending on method
    """
    def __init__(self, test_mode=False):
        """
        if the .db file doesn't exist create all the tables in the db
        """
        if test_mode == True:
            self.db_tmp_file = tempfile.NamedTemporaryFile()
            self.db_path = self.db_tmp_file.name
        else:
            self.db_path = expanduser('~/.local/share/eclipsebb/eclipse.db')

        if not exists(self.db_path) or test_mode == True:
            logging.info('Creating database schema...')

            # schema declaration is stored in db.sql
            self.exec_script('db.sql')

            logging.info('Database schema created.')

        if test_mode == True:
            # add tests data
            self.exec_script('test_db.sql')

    def exec_script(self, name):
        # script in the engine dir
        cwd = dirname(abspath(__file__))
        sql = open(join(cwd, name), 'r').read()

        db = self.connect()
        db.executescript(sql)
        db.commit()
        db.close()
        
    def connect(self):
        """
        the detect_types param allow us to store python types directly
        in the databse.
        """
        return sqlite3.connect(self.db_path,
                               detect_types=sqlite3.PARSE_DECLTYPES)

    @log
    @fail
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
            # TODO::check that there's actually a transaction with sqlite3
            db.commit()
        except Exception:
            logging.exception("Can't create game {!r} by \
{}".format(game.name, game.creator_id))
            return (db_status.ERROR, None)
        else:
            return (db_status.OK, game_id)
        finally:
            cursor.close()
            db.close()

    @log
    @fail
    def saveGame(self, game):
        """
        update the content of the game row.
        """
        sql = "update games set started=?, ended=?, cur_state=?, \
last_play=?, where id = ?"
        try:
            db = self.connect()
            cursor = db.cursor()

            cursor.execute(sql, (game.started, game.ended, game.cur_state,
                                 game.last_play, game.id_))
            db .commit()
        except Exception:
            logging.exception()
            return (db_status.ERROR, None)
        else:
            return (db_status.OK, None)
        finally:
            cursor.close()
            db.close()

    @log
    @fail
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
            return (db_status.ERROR, None)
        else:
            game_params = cursor.fetchone()
            if game_params is None:
                return (db_status.ERROR, None)
            game = Game.fromDB(**game_params)
            return (db_status.OK, game)
        finally:
            cursor.close()
            db.close()

    @log
    @fail
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
            return (db_status.ERROR, None)
        else:
            players_ids = cursor.fetchall()
            players_ids = [id_[0] for id_ in players_ids]
            return (db_status.OK, players_ids)
        finally:
            cursor.close()
            db.close()

    @log
    @fail
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
            return (db_status.ERROR, None)
        else:
            ext_ids_names = cursor.fetchall()
            ext_ids_names = dict(ext_ids_names)
            return (db_status.OK, ext_ids_names)
        finally:
            cursor.close()
            db.close()

    @log
    @fail
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
            return (db_status.ERROR, None)
        else:
            states_ids = cursor.fetchall()
            states_ids = [id_[0] for id_ in states_ids]
            return (db_status.OK, states_ids)
        finally:
            cursor.close()
            db.close()

    @log
    @fail
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
            return (db_status.ERROR, None)
        else:
            pub_ids = cursor_pub.fetchall()
            pub_ids = [id_[0] for id_ in pub_ids]
            priv_ids = cursor_priv.fetchall()
            priv_ids = [id_[0] for id_ in priv_ids]
            return (db_status.OK, (pub_ids, priv_ids))
        finally:
            cursor_pub.close()
            cursor_priv.close()
            db.close()

    @log
    @fail
    def getMyGamesIds(self, player_id):
        """ return None if error """
        sql = 'SELECT game_id FROM games_players where player_id =?;'
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (player_id,))
        except Exception:
            logging.exception("DBException while fetching games for player \
{}".format(player_id))
            return (db_status.ERROR, None)
        else:
            game_ids = cursor.fetchall()
            game_ids = [id_[0] for id_ in game_ids]
            return (db_status.OK, game_ids)
        finally:
            cursor.close()
            db.close()

    def getPassHash(self, id_, password):
        """ sha1 of the salted password """
        salted_pass = id_[:2] + password
        return hashlib.sha1(salted_pass.encode('utf-8')).hexdigest()

    @log
    @fail
    def createPlayer(self, name, email, password, timezone):
        """
        register new player in database.
        return playerId
        """
        sha1_pass = self.getPassHash(email, password)
        sql = "INSERT INTO players VALUES (NULL, ?, ?, ?, ?)"
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (name, email, sha1_pass, timezone))
            db.commit()
        except sqlite3.IntegrityError:
            logging.debug("Player ({}, {}) already registered".format(name,
                                                                      email))
            return (db_status.CONST_ERROR, None)
        except Exception:
            logging.exception("DBException while creating player with \
name {}".format(name))
            return (db_status.ERROR, None)
        else:
            # the id primary key = rowid in sqlite3
            playerId = cursor.lastrowid
            return (db_status.OK, playerId)
        finally:
            cursor.close()
            db.close()

    @log
    @fail
    def updatePlayer(self, player, to_update):
        """
        update player fields.
        to_update is a dict containing the fields to update with the new values.
        """
        if 'email' not in to_update:
            to_update['email'] = player.email
        if 'timezone' not in to_update:
            to_update['timezone'] = player.timezone
        if 'password' not in to_update:
            to_update['password'] = player.password
        else:
            to_update['password'] = self.getPassHash(to_update['email'],
                                                     to_update['password'])
        sql = 'update players set email=?, timezone=?, password=? \
where id = ?;'
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (to_update['email'],
                                 to_update['timezone'],
                                 to_update['password'],
                                 player.id_))
            db.commit()
        except sqlite3.IntegrityError:
            logging.debug("Email ({}, {}) already \
registered".format(player.name, player.email))
            return (db_status.CONST_ERROR, None)
        except Exception:
            logging.exception("DBException while updating player with \
name {}".format(player.name))
            return (db_status.ERROR, None)
        else:
            return (db_status.OK, None)
        finally:
            cursor.close()
            db.close()

    @log
    @fail
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
            return (db_status.ERROR, None)
        else:
            result = cursor.fetchone()
            if result is None:
                return (db_status.CONST_ERROR, None)
            else:
                player_id = result[0]
                return (db_status.OK, player_id)
        finally:
            cursor.close()
            db.close()

    @log
    @fail
    def loadPlayer(self, player_id):
        """"
        get player info in database, then instanciate a player
        """
        sql = 'select id, name, email, timezone, password from players \
where id = ?'
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql, (player_id, ))
        except Exception:
            logging.exception("DBException while loading player with \
id {}".format(player_id))
            return (db_status.ERROR, None)
        else:
            result = cursor.fetchone()
            if result is None:
                logging.warning("No data found for player with id \
{}".format(player_id))
                return (db_status.ERROR, None)
            else:
                return (db_status.OK, Player(*result))
        finally:
            cursor.close()
            db.close()


    @log
    @fail
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
            return (db_status.ERROR, None)
        else:
            return (db_status.OK, cursor.fetchall())
        finally:
            cursor.close()
            db.close()

    @log
    @fail
    def getTZ(self):
        """ return an ordered list (tzId, tzName) """
        sql = 'SELECT diff, name FROM timezones order by diff;'
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql)
        except Exception:
            logging.exception("DBException while fetching timezones")
            return (db_status.ERROR, None)
        else:
            tz = cursor.fetchall()
            return (db_status.OK, Timezones(tz))
        finally:
            cursor.close()
            db.close()

    @log
    @fail
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
            return (db_status.ERROR, None)
        else:
            state_id = cursor.lastrowid
            return (db_status.OK, state_id)
        finally:
            cursor.close()
            db.close()

    @log
    @fail
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
            return (db_status.ERROR, None)
        else:
            pic_state = cursor.fetchone()
            return (db_status.OK, pickle.loads(pic_state))
        finally:
            cursor.close()
            db.close()

    @log
    @fail
    def getExtensionsInfos(self):
        """ return a list (id, name, desc) """
        sql = 'SELECT id, name, desc FROM extensions;'
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(sql)
        except Exception:
            logging.exception("DBException while fetching extensions")
            return (db_status.ERROR, None)
        else:
            return (db_status.OK, cursor.fetchall())
        finally:
            cursor.close()
            db.close()
