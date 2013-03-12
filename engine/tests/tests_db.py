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

from datetime import datetime
import logging
import unittest
import engine.db
from engine.db import DB_STATUS
from engine.web_types import Game

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
        get_game_players_ids
        get_game_ext
        get_game_states_ids
        get_pub_priv_games_ids
        get_my_games_ids
        create_game
        save_game
        load_game
        """
        # the games ids in the test db
        not_started_gid = 1
        in_progress_gid = 2
        ended_gid = 3
        not_a_gid = 666

        # in the 'not started' test game, players are : [1, 2]
        status, players_ids = self.db.get_game_players_ids(not_started_gid)
        self.assertEqual(status, DB_STATUS.OK)
        # there's no 'order by' in the sql query, so the order is not guaranteed
        players_ids.sort()
        self.assertEqual([1, 2], players_ids)

        # in the 'not started' test game, extensions are:
        # {2: 'developments', 4: 'secret_world', 6: 'ancient_hives'}
        status, game_exts = self.db.get_game_ext(not_started_gid)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(game_exts, {2: 'developments',
                                     4: 'secret_world',
                                     6: 'ancient_hives'})

        # no states, not implemented yet
        status, states_ids = self.db.get_game_states_ids(not_started_gid)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(states_ids, [])

        # the 'not started' test game is public
        status, games_ids = self.db.get_pub_priv_games_ids()
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(games_ids, ([not_started_gid], []))

        player_1_id = 1
        player_2_id = 2
        # the test player has join all the test games : not started,
        # in progress and ended        
        status, games_ids = self.db.get_my_games_ids(player_1_id)
        self.assertEqual(status, DB_STATUS.OK)
        games_ids.sort()
        self.assertEqual(games_ids, [1, 2])
        
        # game loading
        status, game = self.db.load_game(not_a_gid)
        self.assertEqual(status, DB_STATUS.NO_ROWS)
        self.assertEqual(game, None)

        status, game = self.db.load_game(in_progress_gid)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(game.id_, 2)
        self.assertEqual(game.name, 'my in-progress test game')
        self.assertEqual(game.started, True)
        self.assertEqual(game.ended, False)
        self.assertEqual(game.level, 2)
        self.assertEqual(game.cur_state_id, -1)
        self.assertEqual(game.private, False)
        self.assertEqual(game.password, '')
        start_date = datetime.strptime('2006-06-06 06:06:06.666666',
                                       '%Y-%m-%d %H:%M:%S.%f')
        self.assertEqual(game.start_date, start_date)
        last_play = datetime.strptime('2006-06-16 06:06:06.666666',
                                      '%Y-%m-%d %H:%M:%S.%f')
        self.assertEqual(game.last_play, last_play)
        self.assertEqual(game.num_players, 2)
        self.assertEqual(game.creator_id, 2)
        # loaded by the gm, not db, so must be empty
        self.assertEqual(game.players_ids, [])
        self.assertEqual(game.extensions, {})
        self.assertEqual(game.state_ids, [])
        self.assertEqual(game.last_valid_state_id, None)

        # update game
        game.last_play = datetime.now()
        game.cur_state_id = 666
        status, dummy = self.db.save_game(game)
        self.assertEqual(status, DB_STATUS.OK)

        status, game_mod = self.db.load_game(in_progress_gid)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(game.last_play, game_mod.last_play)
        self.assertEqual(game.cur_state_id, game_mod.cur_state_id)

        # create game
        new_game = Game(creator_id=1, name='game creation test', level=3,
                        private=True, password='test', num_players=3,
                        extensions={1: 'rare_technologies', 11: 'alliances'})
        players_ids = [player_1_id, player_2_id]
        status, new_game = self.db.create_game(new_game, players_ids)
        self.assertEqual(status, DB_STATUS.OK)

        status, new_game_reload = self.db.load_game(new_game.id_)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(new_game.id_, new_game_reload.id_)
        self.assertEqual(new_game.name, new_game_reload.name)
        self.assertEqual(new_game.started, new_game_reload.started)
        self.assertEqual(new_game.ended, new_game_reload.ended)
        self.assertEqual(new_game.level, new_game_reload.level)
        self.assertEqual(new_game.cur_state_id, new_game_reload.cur_state_id)
        self.assertEqual(new_game.private, new_game_reload.private)
        self.assertEqual(new_game.password, new_game_reload.password)
        self.assertEqual(new_game.start_date, new_game_reload.start_date)
        self.assertEqual(new_game.last_play, new_game_reload.last_play)
        self.assertEqual(new_game.num_players, new_game_reload.num_players)
        self.assertEqual(new_game.creator_id, new_game_reload.creator_id)
        # load_game returns an incomplete game
        self.assertNotEqual(new_game.players_ids, new_game_reload.players_ids)
        self.assertNotEqual(new_game.extensions, new_game_reload.extensions)
        # TODO::no states for now
        self.assertEqual(new_game.state_ids, new_game_reload.state_ids)
        self.assertEqual(new_game.last_valid_state_id,
                         new_game_reload.last_valid_state_id)
        self.assertEqual(new_game.cur_state.__dict__,
                         new_game_reload.cur_state.__dict__)
 
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
