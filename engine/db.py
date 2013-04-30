"""
Copyright (C) 2012-2013  manu, adri

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

import hashlib
import logging
import os.path
import pickle
import sqlite3
import sys
import tempfile
import engine.util
from engine.web_types import WebPlayer, Timezones, Game

# status returned by all db methods
DB_STATUS = engine.util.enum(OK=0, ERROR=1, DUP_ERROR=2, NO_ROWS=3)

# allow some queries to fail for unittest
_fail = False
_fail_filter = None

def change_db_fail(activate, filter_=None):
    """ called from tests to force db methods to fail """
    global _fail
    global _fail_filter
    _fail = activate
    _fail_filter = filter_

def fail(fun):
    """
    a decorator allowing db calls to return read/write failure.
    can filter on function name.
    """
    def failer(*args, **kargs):
        """ returned function """
        if _fail and (_fail_filter is None
                      or fun.__name__ == _fail_filter):
            return (DB_STATUS.ERROR, None)
        else:
            return fun(*args, **kargs)

    # to display an usable name in the log decorator
    failer.__name__ = fun.__name__
    return failer

class MockDB(object):
    """ mock db object which raises sqlite3.DatabaseError """
    def cursor(self):
        """ do not return a cursor, raise an error """
        raise sqlite3.DatabaseError

    def executescript(self, script):
        """ do not execute script, raise an error """
        raise sqlite3.DatabaseError

    def close(self):
        """ for the finally close """
        pass

class DBInterface(object):
    """
    Handles the connections to the database

    All methods return a tuple: (DB_STATUS, data)
    enum DB_STATUS:
     OK: if no error
     ERROR: if database write/read error
     DUP_ERROR: if database constraints error
     NO_ROWS: if the query returned no rows
    data: optionnal returned data depending on method

    Has two test modes, one for raising sqlite3 exceptions to test the
    db module itself, and one for returning DB_STATUS.ERROR when
    calling one of its methods to test the correct behavior of modules
    calling the db module in case of a db error.

    For tests, use a temporary database filled with test data.
    """
    def __init__(self, test_mode=False):
        """ if the .db file doesn't exist create all the tables in the db """
        self._logger = logging.getLogger('ecbb.db')

        # for db unittest, to mock the db sqlite3 object
        self._unittest = False

        if test_mode:
            self._logger.info('Starting in TEST mode.')

            # use temporary file to store the db
            self._db_tmp_file = tempfile.NamedTemporaryFile()
            self._db_path = self._db_tmp_file.name
        else:
            db_file_name = '~/.local/share/eclipsebb/eclipse.db'
            self._db_path = os.path.expanduser(db_file_name)

        if not os.path.exists(self._db_path) or test_mode:
            self._logger.info('Creating database schema...')

            # schema declaration is stored in db.sql
            if not self._exec_script('db.sql'):
                sys.exit()

            self._logger.info('Database schema created.')
        else:
            self._logger.info('Database schema already created.')

        if test_mode:
            # add tests data
            self._logger.info('Populating test database.')
            if not self._exec_script('test_db.sql'):
                sys.exit()

    def __del__(self):
        if hasattr(self, '_db_tmp_file'):
            self._db_tmp_file.close()

    def _exec_script(self, name):
        """ execute the sql script located in the eclipsebb/engine directory.
        do not catch exceptions.
        args: name (str) basename of the script
        return:
         OK: True
         ERROR: False
        """
        cwd = os.path.dirname(os.path.abspath(__file__))
        try:
            sql = open(os.path.join(cwd, name), 'r').read()
        except IOError:
            msg = 'Error opening script {} in {}'.format(name, cwd)
            self._logger.exception(msg)
            return False

        self._logger.info('Executing SQL script {} in {}'.format(name, cwd))

        try:
            db = self._connect()
            db.executescript(sql)
            db.commit()
        except sqlite3.DatabaseError:
            msg = 'Error executing SQL script {} in {}'.format(name, cwd)
            self._logger.exception(msg)
            return False
        else:
            msg = 'Success executed SQL script {} in {}'.format(name, cwd)
            self._logger.info(msg)
            return True
        finally:
            if 'db' in locals():
                db.close()
        
    def _connect(self):
        """ the detect_types param of the connect method allow us to store
        python types directly in the database.
        For unittests return a mock db which raises exceptions
        args: None
        return: sqlite3 db object
        """
        if self._unittest:
            return MockDB()
        else:
            return sqlite3.connect(self._db_path,
                                   detect_types=sqlite3.PARSE_DECLTYPES)

    def _get_pass_hash(self, id_, password):
        """ generate the sha1 hash of the salted password.
        args:
          id_ (str): the two first chars of id_ are used for the salt
          password (str): unencrypted password
        return: (str) sha1 of the salted password
        """
        salted_pass = id_[:2] + password
        return hashlib.sha1(salted_pass.encode('utf-8')).hexdigest()

    def set_unittest_to_fail(self, unittest):
        """ set unittest to raise exception when calling db.cursor()
        args: unittest (bool)
        """
        self._unittest = unittest

    @engine.util.log
    @fail
    def create_game(self, game, players_ids):
        """ create a game in the db, the rowid is the game id.
        store the players who joined the game, the selected extensions.
        Do not save the initial state.
        args:
          game: incomplete game object, miss players_ids
          players_ids: [id_1 (int), ..., id_2 (int)]
        return: db_status, complete game
        """
        sql_game = ('INSERT INTO games (name, level, private, password, '
                    'start_date, num_players, creator_id) VALUES '
                    '(?, ?, ?, ?, ?, ?, ?);')
        params_game = (game.name, game.level, game.private, game.password,
                       game.start_date, game.num_players, game.creator_id)
        sql_player = ('INSERT INTO games_players (game_id, player_id) '
                      'VALUES (?, ?);')
        sql_extension = ('INSERT INTO games_extensions (game_id, '
                         'extension_id) VALUES (?, ?);')

        try:
            db = self._connect()
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
            for ext_id in game.extensions:
                cursor.execute(sql_extension, (game_id, ext_id))

            # commit only when everything is inserted
            db.commit()
        except sqlite3.DatabaseError:
            msg = 'Error creating game {!r} by {}'.format(game.name,
                                                          game.creator_id)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            game.id_ = game_id

            msg = ('Game {!r} by {} successfully created with id {}'
                   '').format(game.name, game.creator_id, game.id_)
            self._logger.info(msg)
            return (DB_STATUS.OK, game)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def save_game(self, game):
        """ update the content of the game row.
        args: complete game object
        return: db_status, None
        """
        sql = ('UPDATE games '
               'SET started=?, ended=?, last_play=? '
               'WHERE id = ?;')
        try:
            db = self._connect()
            cursor = db.cursor()

            cursor.execute(sql, (game.started, game.ended,
                                 game.last_play, game.id_))
            db.commit()
        except sqlite3.DatabaseError:
            msg = 'Error saving game {!r} (id{})'.format(game.name, game.id_)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            if cursor.rowcount == 0:
                msg = 'No rows updated for game {}'.format(game.id_)
                self._logger.warning(msg)
                return (DB_STATUS.NO_ROWS, None)
            else:
                msg = 'Game {} successfully updated'.format(game.id_)
                self._logger.info(msg)
                return (DB_STATUS.OK, None)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def load_game(self, game_id):
        """ load a game from the db
        args: game_id (int)
        return: db_status, incomplete Game object

        do not load players ids, extensions ids, states ids, cur state
        """
        sql = ('SELECT * '
               'FROM games '
               'WHERE id = ?;')
        try:
            db = self._connect()
            # to have access to returned row as a dict
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(sql, (game_id, ))
        except sqlite3.DatabaseError:
            msg = 'Error while loading game with id {}'.format(game_id)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            game_params = cursor.fetchone()
            if game_params is None:
                msg = 'Game {} not found in database'.format(game_id)
                self._logger.warning(msg)
                return (DB_STATUS.NO_ROWS, None)

            game = Game.from_db(**game_params)
            msg = 'Game {} successfully loaded from database'.format(game.id_)
            self._logger.info(msg)
            return (DB_STATUS.OK, game)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def get_game_players_ids(self, game_id):
        """ return a list of players ids registered with the game
        args: game_id (int)
        return: db_status, [player_id_1 (int), ..., player_id_n (int)]
        """
        sql = ('SELECT player_id '
               'FROM games_players '
               'WHERE game_id = ?;')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql, (game_id, ))
        except sqlite3.DatabaseError:
            msg = 'Error while getting players for game {}'.format(game_id)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            players_ids = cursor.fetchall()
            players_ids = [id_[0] for id_ in players_ids]
            msg = 'Success loading players ids for game {}'.format(game_id)
            self._logger.info(msg)
            return (DB_STATUS.OK, players_ids)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def get_game_ext(self, game_id):
        """ return the activated extensions for the given game
        args: game_id (int)
        return: db_status, {id (int): name (str)}
        """
        sql = ('SELECT g.extension_id, e.name '
               'FROM games_extensions g, extensions e '
               'WHERE g.extension_id = e.id '
               ' AND g.game_id = ?;')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql, (game_id, ))
        except sqlite3.DatabaseError:
            msg = 'Error while getting extensions for game {}'.format(game_id)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            ext_ids_names = cursor.fetchall()
            ext_ids_names = dict(ext_ids_names)
            msg = 'Success loaded extensions for game {}'.format(game_id)
            self._logger.info(msg)
            return (DB_STATUS.OK, ext_ids_names)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def get_game_states_ids(self, game_id):
        """ return the list of the game's states ids
        args: game_id (int)
        return: db_status, [state_id_1 (int), ..., state_id_n(int)]
        """
        sql = ('SELECT id '
               'FROM state '
               'WHERE game_id = ? '
               'ORDER BY id;')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql, (game_id, ))
        except sqlite3.DatabaseError:
            msg = 'Error while getting states for game {}'.format(game_id)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            states_ids = cursor.fetchall()
            states_ids = [id_[0] for id_ in states_ids]
            msg = 'Success loaded states ids for game {}'.format(game_id)
            self._logger.info(msg)
            return (DB_STATUS.OK, states_ids)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def get_pub_priv_games_ids(self):
        """ return the ids of games not yet started (waiting for players)
        there's two kind of games, public ones joinable to everyone and
        privates ones joinable only if you have the password.
        args: none
        return: db_status, ([pub_game_id_1 (int), ..., pub_game_id_n (int)],
                            [priv_game_id_1 (int), ..., priv_game_id_n (int)])
        """
        sql_pub = ('SELECT id '
                   'FROM games '
                   'WHERE started = 0 '
                   ' AND private = 0 '
                   'ORDER BY name;')
        sql_priv = ('SELECT id '
                    'FROM games '
                    'WHERE started = 0 '
                    ' AND private = 1 '
                    'ORDER BY name;')
        try:
            db = self._connect()
            cursor_pub = db.cursor()
            cursor_pub.execute(sql_pub)
            cursor_priv = db.cursor()
            cursor_priv.execute(sql_priv)
        except sqlite3.DatabaseError:
            self._logger.exception('Error while fetching pub/priv games')
            return (DB_STATUS.ERROR, None)
        else:
            pub_ids = cursor_pub.fetchall()
            pub_ids = [id_[0] for id_ in pub_ids]
            priv_ids = cursor_priv.fetchall()
            priv_ids = [id_[0] for id_ in priv_ids]
            self._logger.info('Success loaded priv/pub games')
            return (DB_STATUS.OK, (pub_ids, priv_ids))
        finally:
            if 'cursor_pub' in locals():
                cursor_pub.close()
            if 'cursor_priv' in locals():
                cursor_priv.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def get_my_games_ids(self, player_id):
        """ return the not-finished games joined by the player
        args: player_id (int)
        return: db_status, [game_id_1 (int), ..., game_id_n (int)]
        """
        sql = ('SELECT gp.game_id '
               'FROM games_players gp, games g '
               'WHERE gp.game_id = g.id '
               ' AND gp.player_id = ? '
               ' AND g.ended = 0;')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql, (player_id,))
        except sqlite3.DatabaseError:
            msg = 'Error while fetching games for player {}'.format(player_id)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            game_ids = cursor.fetchall()
            game_ids = [id_[0] for id_ in game_ids]
            msg = 'Success loaded games for player {}'.format(player_id)
            self._logger.info(msg)
            return (DB_STATUS.OK, game_ids)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def create_player(self, name, email, password, tz_id):
        """ register new player in database.
        args:
          name (str)
          email (str)
          password (str): plain password
          tz_id (int): see db.sql for the list of valid id
        return: db_status, player_id (int)
        """
        sha1_pass = self._get_pass_hash(email, password)
        sql = ('INSERT INTO players '
               'VALUES (NULL, ?, ?, ?, ?)')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql, (name, email, sha1_pass, tz_id))
            db.commit()
        except sqlite3.IntegrityError:
            msg = 'Player ({}, {}) already registered'.format(name, email)
            self._logger.debug(msg)
            return (DB_STATUS.DUP_ERROR, None)
        except sqlite3.DatabaseError:
            msg = 'Error while creating player with name {}'.format(name)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            # the id primary key = rowid in sqlite3
            player_id = cursor.lastrowid
            msg = 'Success created player {} id {}'.format(name, player_id)
            self._logger.info(msg)
            return (DB_STATUS.OK, player_id)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def update_player(self, player, to_update):
        """ update player fields.
        args:
          player: player object
          to_update: dict containing the fields to update with the new values
                     available fields: email (str)
                                       timezone (int): the timezone id
                                       password (str): plain password
        return: db_status, None
        """
        if 'email' not in to_update:
            to_update['email'] = player.email
        if 'timezone' not in to_update:
            to_update['timezone'] = player.tz_id
        if 'password' not in to_update:
            to_update['password'] = player.password
        else:
            to_update['password'] = self._get_pass_hash(to_update['email'],
                                                        to_update['password'])
        sql = ('UPDATE players '
               'SET email=?, timezone=?, password=? '
               'WHERE id = ?;')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql, (to_update['email'],
                                 to_update['timezone'],
                                 to_update['password'],
                                 player.id_))
            db.commit()
        except sqlite3.IntegrityError:
            msg = 'Email ({}, {}) already registered'.format(player.name,
                                                             player.email)
            self._logger.info(msg)
            return (DB_STATUS.DUP_ERROR, None)
        except sqlite3.DatabaseError:
            msg = 'Error updating player with name {}'.format(player.name)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            if cursor.rowcount == 0:
                msg = 'No rows updated for player {}'.format(player.id_)
                self._logger.warning(msg)
                return (DB_STATUS.NO_ROWS, None)
            else:
                msg = 'Success updated player {} infos'.format(player.id_)
                self._logger.info(msg)
                return (DB_STATUS.OK, None)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def auth_player(self, email, password):
        """ check password with the one in database.
        args:
          email (str)
          password (str): plain password
        return: db_status,
                player_id (int) if ok, None otherwise
        """
        sha1_pass = self._get_pass_hash(email, password)
        sql = ('SELECT id '
               'FROM players '
               'WHERE email = ? '
               ' AND password = ?;')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql, (email, sha1_pass))
        except sqlite3.DatabaseError:
            msg = 'Error while auth player with email {}'.format(email)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            result = cursor.fetchone()
            if result is None:
                msg = 'Player {} auth failed (pass={})'.format(email, password)
                self._logger.info(msg)
                return (DB_STATUS.NO_ROWS, None)
            else:
                player_id = result[0]
                msg = 'Success auth player {} id {}'.format(email, player_id)
                self._logger.info(msg)
                return (DB_STATUS.OK, player_id)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def load_player(self, player_id):
        """" get player info in database, then instanciate a player.
        args: player_id (int)
        return: db_status, WebPlayer object
        """
        sql = ('SELECT id, name, email, timezone, password '
               'FROM players '
               'WHERE id = ?;')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql, (player_id, ))
        except sqlite3.DatabaseError:
            msg = 'Error while loading player with id {}'.format(player_id)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            result = cursor.fetchone()
            if result is None:
                msg = 'No data found for player with id {}'.format(player_id)
                self._logger.warning(msg)
                return (DB_STATUS.NO_ROWS, None)
            else:
                msg = 'Success loaded player {}'.format(player_id)
                self._logger.info(msg)
                return (DB_STATUS.OK, WebPlayer(*result))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def get_players_infos(self):
        """ get players infos to be displayed in the game creation page
        args: None
        return: db_status,
                [(id_1, name_1), ..., (id_n, name_n)] ordered by name
        """
        sql = ('SELECT id, name '
               'FROM players '
               'ORDER BY name;')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql)
        except sqlite3.DatabaseError:
            self._logger.exception('Error while fetching players infos')
            return (DB_STATUS.ERROR, None)
        else:
            self._logger.info('Success loaded players infos')
            return (DB_STATUS.OK, cursor.fetchall())
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def save_state(self, game):
        """ pickle the state and store it in the db.
        update the states_ids of the game.
        infos saved in the database for a state:
         -id: uniq increasing id (sqlite rowid)
         -gameid: id of the game hosting the state
         -pickle: pickled string of the state

        args:
         game (Game object)
        return: db_status,
                state_id (int), None if error
        """
        sql = ('INSERT INTO state '
               'VALUES (NULL, ?, ?);')
        try:
            pic_state = pickle.dumps(game.cur_state)
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql, (game.id_, pic_state))
            db.commit()
        except sqlite3.DatabaseError:
            msg = 'Error while saving state for game {}'.format(game.id_)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            state_id = cursor.lastrowid
            game.states_ids.append(state_id)
            msg = 'Success saved state {} for game {}'.format(state_id, game.id_)
            self._logger.info(msg)
            return (DB_STATUS.OK, state_id)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def load_state(self, state_id):
        """ load state from db and unpickle it
        args: state_id (int)
        return: db_status,
                GameState object, None if error
        """
        sql = ('SELECT pickle '
               'FROM state '
               'WHERE id = ?;')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql, (state_id, ))
        except sqlite3.DatabaseError:
            msg = 'Error while loading state {}'.format(state_id)
            self._logger.exception(msg)
            return (DB_STATUS.ERROR, None)
        else:
            data = cursor.fetchone()
            if data is None:
                msg = 'State {} not found in database'.format(state_id)
                self._logger.warning(msg)
                return (DB_STATUS.NO_ROWS, None)
            pic_state = data[0]
            msg = 'Success loaded state {}'.format(state_id)
            self._logger.info(msg)
            return (DB_STATUS.OK, pickle.loads(pic_state))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def get_extensions_infos(self):
        """ get the id, internal name and description of the available
        extensions.
        args: None
        return: db_status,
                [(id_1, name_1, desc_1), ..., (id_n, name_n, desc_n)] no order
        """
        sql = ('SELECT id, name, desc '
               'FROM extensions;')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql)
        except sqlite3.DatabaseError:
            self._logger.exception('Error while fetching extensions infos')
            return (DB_STATUS.ERROR, None)
        else:
            self._logger.info('Success loaded extensions infos')
            return (DB_STATUS.OK, cursor.fetchall())
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()

    @engine.util.log
    @fail
    def get_timezones(self):
        """ get the timezone ids and associated name, ordered by id.
        args: None
        return: db_status,
                [(tz_id_1, tz_name_n), ..., (tz_id_n, tz_name_n)] ordered by id
        """
        sql = ('SELECT diff, name '
               'FROM timezones '
               'ORDER BY diff;')
        try:
            db = self._connect()
            cursor = db.cursor()
            cursor.execute(sql)
        except sqlite3.DatabaseError:
            self._logger.exception('Error while fetching timezones')
            return (DB_STATUS.ERROR, None)
        else:
            tz = cursor.fetchall()
            self._logger.info('Success loaded timezones infos')
            return (DB_STATUS.OK, Timezones(tz))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()
