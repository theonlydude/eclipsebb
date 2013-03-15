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
import sqlite3
import unittest
import engine.db
from engine.data_types import GameState
from engine.db import DB_STATUS
from engine.web_types import Game, WebPlayer

class DBTests(unittest.TestCase):
    """ test all the methods defined by the db to access it """
    def setUp(self):
        """ create a new test db for each test """
        self.db = engine.db.DBInterface(True)

    def tearDown(self):
        """ delete the temporary db """
        del self.db

    def test_db_fail(self):
        """ functions tested:
        change_db_fail
        fail
        """
        # standard call, no error
        status, _ = self.db.get_extensions_infos()
        self.assertEqual(status, DB_STATUS.OK)

        # set all db methods to fail
        engine.db.change_db_fail(True)
        status, _ = self.db.get_extensions_infos()
        self.assertEqual(status, DB_STATUS.ERROR)

        # check no longer fail
        engine.db.change_db_fail(False)
        status, _ = self.db.get_extensions_infos()
        self.assertEqual(status, DB_STATUS.OK)

        # set 'get_timezones' db method to fail
        engine.db.change_db_fail(True, 'get_timezones')
        # get_extensions_infos ok
        status, _ = self.db.get_extensions_infos()
        self.assertEqual(status, DB_STATUS.OK)
        # get_timezones error
        status, _ = self.db.get_timezones()
        self.assertEqual(status, DB_STATUS.ERROR)
        engine.db.change_db_fail(False)

    def test_prod(self):
        """ test loading the real db """
        try:
            db = engine.db.DBInterface()
            del db
        except sqlite3.DatabaseError:
            self.assertTrue(False)

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
        # ended_gid = 3
        not_a_gid = 666

        ## get the players who joined the test game 1
        # in the 'not started' test game, players are : [1, 2]
        status, players_ids = self.db.get_game_players_ids(not_started_gid)
        self.assertEqual(status, DB_STATUS.OK)
        # there's no 'order by' in the sql query, so the order is not guaranteed
        players_ids.sort()
        self.assertEqual([1, 2], players_ids)

        ## get the extensions associated with the test game 1
        # in the 'not started' test game, extensions are:
        # {2: 'developments', 4: 'secret_world', 6: 'ancient_hives'}
        status, game_exts = self.db.get_game_ext(not_started_gid)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(game_exts, {2: 'developments',
                                     4: 'secret_world',
                                     6: 'ancient_hives'})

        ## get the states played in the game 1
        # no states, not implemented yet
        status, states_ids = self.db.get_game_states_ids(not_started_gid)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(states_ids, [])

        ## get the not started test games
        # the 'not started' test game is public
        status, games_ids = self.db.get_pub_priv_games_ids()
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(games_ids, ([not_started_gid], []))

        ## list not ended games joined by player 1
        player_1_id = 1
        player_2_id = 2
        # the test player has join all the test games : not started,
        # in progress and ended        
        status, games_ids = self.db.get_my_games_ids(player_1_id)
        self.assertEqual(status, DB_STATUS.OK)
        games_ids.sort()
        self.assertEqual(games_ids, [1, 2])

        ## test loading games
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

        ## test updating a game
        # update game
        game.last_play = datetime.now()
        game.cur_state_id = 666
        status, dummy = self.db.save_game(game)
        self.assertEqual(status, DB_STATUS.OK)

        ## then reloaded the saved game
        status, game_mod = self.db.load_game(in_progress_gid)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(game.last_play, game_mod.last_play)
        self.assertEqual(game.cur_state_id, game_mod.cur_state_id)

        ## test creating a new game
        new_game = Game(creator_id=1, name='game creation test', level=3,
                        private=True, password='test', num_players=3,
                        extensions={1: 'rare_technologies', 11: 'alliances'})
        players_ids = [player_1_id, player_2_id]
        status, new_game = self.db.create_game(new_game, players_ids)
        self.assertEqual(status, DB_STATUS.OK)

        ## then loading it
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

        # test DB_ERROR
        self.db.set_unittest_to_fail(True)
        status, dummy = self.db.create_game(new_game, players_ids)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.save_game(game)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.load_game(in_progress_gid)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.get_game_players_ids(not_started_gid)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.get_game_ext(not_started_gid)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.get_game_states_ids(not_started_gid)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.get_pub_priv_games_ids()
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.get_my_games_ids(player_1_id)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        self.db.set_unittest_to_fail(False)

    def test_player(self):
        """ methods tested:
        create_player
        update_player
        auth_player
        load_layer
        get_players_infos
        """
        not_a_player_id = 666

        ## test creating new player
        player = WebPlayer(None, 'new test player', 'new_test@test.com',
                           120, 'Test01!')
        status, player_id = self.db.create_player(player.name,
                                                  player.email,
                                                  player.password,
                                                  player.tz_id)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertNotEqual(player_id, None)
        player.id_ = player_id

        ## test creating duplicate player with existing player in db
        status, player_id = self.db.create_player(name='test player dup',
                                                  email='test_dup@test.com',
                                                  password='Testest01!',
                                                  tz_id=120)
        self.assertEqual(status, DB_STATUS.CONST_ERROR)
        self.assertEqual(player_id, None)

        ## update the new player
        # dup update
        to_update = {'email': 'test_dup@test.com', 'timezone': 600}
        status, dummy = self.db.update_player(player, to_update)
        self.assertEqual(status, DB_STATUS.CONST_ERROR)

        # check player not updated
        status, reload_player = self.db.load_player(player.id_)
        player.password = self.db._get_pass_hash(player.email, player.password)
        self.assertEqual(player.__dict__, reload_player.__dict__)

        # update ok
        to_update = {'email': 'test_update@test.com'}
        status, dummy = self.db.update_player(player, to_update)
        self.assertEqual(status, DB_STATUS.OK)

        # check update ok
        status, reload_player = self.db.load_player(player.id_)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertNotEqual(player.__dict__, reload_player.__dict__)

        # update empty
        status, dummy = self.db.update_player(player, {})
        self.assertEqual(status, DB_STATUS.OK)

        ## load player
        # load unknow
        status, dummy = self.db.load_player(not_a_player_id)
        self.assertEqual(status, DB_STATUS.NO_ROWS)
        self.assertEqual(dummy, None)

        ## auth player
        status, player_id = self.db.auth_player('missing@test.com', 'xxx')
        self.assertEqual(status, DB_STATUS.NO_ROWS)
        self.assertEqual(player_id, None)

        status, player_id = self.db.auth_player('test@test.com', 'test')
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(player_id, 1)

        ## players infos
        status, players_infos = self.db.get_players_infos()
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(players_infos, [(3, 'new test player'),
                                         (1, 'test player'),
                                         (2, 'test player dup')])

        # test DB_ERROR
        self.db.set_unittest_to_fail(True)
        status, dummy = self.db.create_player(player.name,
                                              player.email,
                                              player.password,
                                              player.tz_id)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.update_player(player, to_update)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.auth_player('test@test.com', 'test')
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.load_player(player.id_)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.get_players_infos()
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        self.db.set_unittest_to_fail(False)

    def test_state(self):
        """ methods tested:
        save_state
        load_state
        """
        # TODO::empty states for now...
        ## save
        game_id = 1
        state = GameState(num_players=2)
        status, state_id = self.db.save_state(game_id, state)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(state_id, 1)

        ## load
        status, state_loaded = self.db.load_state(state_id)
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(state.__dict__, state_loaded.__dict__)

        not_a_state_id = 666
        status, dummy_state = self.db.load_state(not_a_state_id)
        self.assertEqual(status, DB_STATUS.NO_ROWS)
        self.assertEqual(dummy_state, None)

        # test DB_ERROR
        self.db.set_unittest_to_fail(True)
        status, dummy = self.db.save_state(game_id, state)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.load_state(state_id)
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        self.db.set_unittest_to_fail(False)

    def test_constants(self):
        """ methods tested:
        get_extensions_infos
        get_timezones
        """
        status, ext_infos = self.db.get_extensions_infos()
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual([(1, 'rare_technologies', 'enable rare technologies'),
                          (2, 'developments', 'enable developments'),
                          (3, 'ancient_worlds', 'enable ancient worlds'),
                          (4, 'secret_world', ('put unused ancient worlds '
                                               'in the heap')),
                          (5, 'ancient_sdcg', 'enable ancient SDCG'),
                          (6, 'ancient_hives', 'enable ancients hives'),
                          (7, 'warp_portals', 'enable warp portals'),
                          (8, 'new_discoveries', 'add new discoveries'),
                          (9, 'predictable_technologies', ('enable predictable '
                                                           'technologies')),
                          (10, 'turn_order', 'enable direction of play'),
                          (11, 'alliances', 'enable alliances'),
                          (12, 'small_galaxy', ('enable small galaxy (three '
                                                'players only)'))],
                         ext_infos)
        status, timezones = self.db.get_timezones()
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual([(-720, 'UTC-12:00 (Baker Island, Howland Island)'),
                          (-660, 'UTC-11:00 (SST - Samoa Standard Time)'),
                          (-600, ('UTC-10:00 (HST - Haway-Aleutian Standard'
                                  ' Time)')),
                          (-570, 'UTC-09:30 (Marquesas Islands)'),
                          (-540, 'UTC-09:00 (AKST - Alaska Standard Time)'),
                          (-480, 'UTC-08:00 (PST - Pacific Standard Time)'),
                          (-420, 'UTC-07:00 (MST - Mountain Standard Time)'),
                          (-360, 'UTC-06:00 (CST - Central Standard Time)'),
                          (-300, 'UTC-05:00 (EST - Eastern Standard Time)'),
                          (-270, 'UTC-04:30 (Venezuela)'),
                          (-240, 'UTC-04:00 (AST - Atlantic Standard Time)'),
                          (-210, ('UTC-03:30 (NST - Newfoundland Standard '
                                  'Time)')),
                          (-180, 'UTC-03:00 (Saint-Pierre and Miquelon'),
                          (-120, 'UTC-02:00 (Fernando de Noronha)'),
                          (-60, 'UTC-01:00 (Cape Verde)'),
                          (0, 'UTC+00:00 (WET - Western European Time)'),
                          (60, 'UTC+01:00 (CET - Central European Time)'),
                          (120, 'UTC+02:00 (EET - Eastern European Time)'),
                          (180, 'UTC+03:00 (Iraq)'),
                          (210, 'UTC+03:30 (Iran)'),
                          (240, 'UTC+04:00 (Russia - Moscow Time)'),
                          (270, 'UTC+04:30 (Afghanistan)'),
                          (300, 'UTC+05:00 (Kerguelen Islands)'),
                          (330, 'UTC+05:30 (India, Sri Lanka)'),
                          (345, 'UTC+05:45 (Nepal)'),
                          (360, 'UTC+06:00 (Kyrgyzstan)'),
                          (390, 'UTC+06:30 (Cocos Islands)'),
                          (420, 'UTC+07:00 (Laos)'),
                          (480, ('UTC+08:00 (AWST - Australian Western Standard'
                                 ' Time)')),
                          (525, 'UTC+08:45 (Eucla)'),
                          (540, 'UTC+09:00 (JST - Japan Standard Time)'),
                          (570, ('UTC+09:30 (ACST - Australian Central Standard'
                                 ' Time)')),
                          (600, ('UTC+10:00 (AEST - Autralian Eastern Standard'
                                 ' Time)')),
                          (630, 'UTC+10:30 (New South Wales)'),
                          (660, 'UTC+11:00 (New Caledonia)'),
                          (690, 'UTC+11:30 (Norfolk Island)'),
                          (720, 'UTC+12:00 (Wallis and Futuna)'),
                          (765, 'UTC+12:45 (Chatham Islands)'),
                          (780, 'UTC+13:00 (Tokelau)'),
                          (840, 'UTC+14:00 (Line Islands)')],
                         timezones.list_tz)

        # test DB_ERROR
        self.db.set_unittest_to_fail(True)
        status, dummy = self.db.get_extensions_infos()
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        status, dummy = self.db.get_timezones()
        self.assertEqual(status, DB_STATUS.ERROR)
        self.assertEqual(dummy, None)
        self.db.set_unittest_to_fail(False)
