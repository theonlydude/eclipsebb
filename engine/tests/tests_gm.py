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

import unittest
import engine.db
from engine.game_manager import GamesManager

class GMTests(unittest.TestCase):
    """ test all the methods defined in the GameManager module """
    def setUp(self):
        """ instanciate the games manager """
        self.gm = GamesManager(test_mode=True)

    def tearDown(self):
        """ delete the game manager to delete the temporary db """
        del self.gm

    def test_db_error_init(self):
        """ test db error in __init__ """
        engine.db.change_db_fail(True)
        with self.assertRaises(SystemExit):
            self.gm = GamesManager(test_mode=True)
        engine.db.change_db_fail(False)

    def test_util(self):
        """ test utilitarian methods:
        debug
        """
        self.gm.debug('nice test debug message')
        # TODO:: self.assert?? for logs

    def test_games(self):
        """ methods tested:
        get_game
        get_my_games
        get_ended_games
        get_pub_priv_games
        create_game
        save_game
        load_game
        """
        return

        # the games ids in the test db
        not_started_gid = 1
        in_progress_gid = 2
        # ended_gid = 3
        not_a_gid = 666

        ## test get_game ok

        ## list not ended games joined by player 1
        player_1_id = 1
        player_2_id = 2
        # the test player has join all the test games : not started,
        # in progress and ended        
        status, games = self.db.get_my_games(player_1_id)
        self.assertEqual(status, DB_STATUS.OK)
        games_ids.sort()
        self.assertEqual(games_ids, [1, 2])

        ## get the not started test games
        # the 'not started' test game is public
        status, games_ids = self.db.get_pub_priv_games_ids()
        self.assertEqual(status, DB_STATUS.OK)
        self.assertEqual(games_ids, ([not_started_gid], []))


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

    def test_players(self):
        """ methods tested:
        load_player
        get_player
        get_players_infos
        auth_player
        create_player
        update_player
        """
        player_id_1 = 1
        not_player_id = 666

        # check ok get_player
        player = self.gm.get_player(player_id_1)
        self.assertEqual(player.id_, player_id_1)

        # check missing get_player
        dummy = self.gm.get_player(not_player_id)
        self.assertEqual(dummy, None)

        # check db error get_player
        engine.db.change_db_fail(True)
        dummy = self.gm._load_player(player_id_1)
        self.assertEqual(dummy, None)
        engine.db.change_db_fail(False)

        # check ok get_players_infos
        players_infos = self.gm.get_players_infos()
        self.assertEqual(players_infos, [(1, 'test player'),
                                         (2, 'test player dup')])

        # check db error get_players_infos
        engine.db.change_db_fail(True)
        dummy = self.gm.get_players_infos()
        self.assertEqual(dummy, None)
        engine.db.change_db_fail(False)

        # check ok auth_player
        email = 'test@test.com'
        password = 'test'
        db_ok, auth_ok, player_id = self.gm.auth_player(email, password)
        self.assertTrue(db_ok)
        self.assertTrue(auth_ok)
        self.assertEqual(player_id, player_id_1)

        # check wrong auth_player
        db_ok, auth_ok, player_id = self.gm.auth_player('', '')
        self.assertTrue(db_ok)
        self.assertFalse(auth_ok)
        self.assertEqual(player_id, None)
        
        # check db error auth_player
        engine.db.change_db_fail(True)
        db_ok, auth_ok, player_id = self.gm.auth_player(email, password)
        self.assertFalse(db_ok)
        self.assertEqual(auth_ok, None)
        self.assertEqual(player_id, None)
        engine.db.change_db_fail(False)

        # check ok create_player
        name = 'new test player'
        email = 'new_test@test.com'
        password = 'test'
        tz_id = 120
        db_ok, dup_ok, player_id = self.gm.create_player(name, email,
                                                         password, tz_id)
        self.assertTrue(db_ok)
        self.assertTrue(dup_ok)
        self.assertEqual(player_id, 3)

        # check duplicate create_player
        db_ok, dup_ok, player_id = self.gm.create_player(name, email,
                                                         password, tz_id)
        self.assertTrue(db_ok)
        self.assertFalse(dup_ok)
        self.assertEqual(player_id, None)

        # check db error create_player
        engine.db.change_db_fail(True)
        db_ok, dup_ok, player_id = self.gm.create_player(name, email,
                                                         password, tz_id)
        self.assertFalse(db_ok)
        self.assertEqual(dup_ok, None)
        self.assertEqual(player_id, None)
        engine.db.change_db_fail(False)

        # check ok update_player, ok reload
        player_id = 3
        player = self.gm.get_player(player_id)
        self.assertNotEqual(player, None)
        self.assertEqual(player.id_, 3)

        to_update = {'timezone': 600}
        db_ok, upd_ok = self.gm.update_player(player, to_update)
        self.assertTrue(db_ok)
        self.assertTrue(upd_ok)

        # check duplicate update_player
        to_update = {'email': 'test@test.com'}
        db_ok, upd_ok = self.gm.update_player(player, to_update)
        self.assertTrue(db_ok)
        self.assertFalse(upd_ok)

        # check ok update_player, db error reload
        engine.db.change_db_fail(True, 'load_player')
        to_update = {'timezone': 120}
        db_ok, upd_ok = self.gm.update_player(player, to_update)
        self.assertFalse(db_ok)
        self.assertTrue(upd_ok)
        engine.db.change_db_fail(False)

        # check db error update_player
        engine.db.change_db_fail(True)
        to_update = {'timezone': 600}
        db_ok, upd_ok = self.gm.update_player(player, to_update)
        self.assertFalse(db_ok)
        self.assertFalse(upd_ok)
        engine.db.change_db_fail(False)
