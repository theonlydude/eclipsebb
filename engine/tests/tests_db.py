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
import unittest
import engine.db
from engine.db import DB_STATUS

class DBTests(unittest.TestCase):
    def setUp(self):
        self.db = engine.db.DBInterface(True)

    def tearDown(self):
        del self.db

    def test_db_fail(self):
        """ functions tested:
        change_db_fail
        fail
        """
        # standard call, no error
        status, data = self.db.get_extensions_infos()
        self.assertEqual(status, DB_STATUS.OK)

        # set all db methods to fail
        engine.db.change_db_fail(True)
        status, data = self.db.get_extensions_infos()
        self.assertEqual(status, DB_STATUS.ERROR)

        # check no longer fail
        engine.db.change_db_fail(False)
        status, data = self.db.get_extensions_infos()
        self.assertEqual(status, DB_STATUS.OK)

        # set 'get_timezones' db method to fail
        engine.db.change_db_fail(True, 'get_timezones')
        # get_extensions_infos ok
        status, data = self.db.get_extensions_infos()
        self.assertEqual(status, DB_STATUS.OK)
        # get_timezones error
        status, data = self.db.get_timezones()
        self.assertEqual(status, DB_STATUS.ERROR)
        engine.db.change_db_fail(False)

    def test_game(self):
        """ methods tested:
        create_game
        save_game
        load_game
        get_game_players_ids
        get_game_ext
        get_game_states_ids
        get_pub_priv_games_ids
        get_my_games_ids
        """
        test_game_id = 1
        status, players_ids = self.db.get_game_players_ids(test_game_id)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertTrue(1 in players_ids)
        self.assertTrue(2 in players_ids)

        # in the test game, extensions are:
        # {2: 'developments', 4: 'secret_world', 6: 'ancient_hives'}
        status, game_exts = self.db.get_game_ext(test_game_id)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertTrue(2 in game_exts)
        self.assertTrue(4 in game_exts)
        self.assertTrue(6 in game_exts)
        self.assertFalse(1 in game_exts)
        self.assertFalse(3 in game_exts)
        self.assertFalse(5 in game_exts)

        status, data = self.db.get_game_states_ids(test_game_id)
        self.assertEqual(status, DB_STATUS.OK)

        status, data = self.db.get_pub_priv_games_ids()
        self.assertEqual(status, DB_STATUS.OK)

        test_player_id = 1
        status, data = self.db.get_my_games_ids(test_player_id)
        self.assertEqual(status, DB_STATUS.OK)

    def test_player(self):
        """ methods tested:
        create_player
        update_player
        auth_player
        load_layer
        get_players_infos
        """
        pass

    def test_state(self):
        """ methods tested:
        save_state
        load_state
        """
        pass

    def test_constants(self):
        """ methods tested:
        get_extensions_infos
        get_timezones
        """
        status, data = self.db.get_extensions_infos()
        self.assertEqual(status, DB_STATUS.OK)
        status, data = self.db.get_timezones()
        self.assertEqual(status, DB_STATUS.OK)
