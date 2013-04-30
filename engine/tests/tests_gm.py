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

from datetime import datetime
import logging
import unittest
import engine.db
from engine.game_manager import GamesManager
import engine.util

engine.util.init_logging(test_mode=True)
_LOGGER = logging.getLogger('ecbb.tests')

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
        _LOGGER.info('===BEGIN TEST_DB_ERROR_INIT===')

        engine.db.change_db_fail(True)
        with self.assertRaises(SystemExit):
            self.gm = GamesManager(test_mode=True)
        engine.db.change_db_fail(False)

        _LOGGER.info('===END TEST_DB_ERROR_INIT===')

    def test_util(self):
        """ test utilitarian methods:
        debug
        """
        _LOGGER.info('===BEGIN TEST_UTIL===')

        self.gm.debug('nice test debug message')
        # TODO:: self.assert?? for logs

        _LOGGER.info('===END TEST_UTIL===')

    def test_load_game(self):
        """ methods tested:
        get_game
        load_game
        """
        _LOGGER.info('===BEGIN TEST_LOAD_GAME===')

        # the games ids in the test db
        in_progress_gid = 2
        # ended_gid = 3
        not_a_gid = 666

        ## test load_game/get_game
        # test load/get_game ok
        db_ok, game = self.gm.load_game(in_progress_gid)
        self.assertTrue(db_ok)
        self.assertNotEqual(game, None)

        game = self.gm.get_game(in_progress_gid)

        # test load/get_game invalid gid
        db_ok, game = self.gm.load_game(not_a_gid)
        self.assertTrue(db_ok)
        self.assertEqual(game, None)

        with self.assertRaises(KeyError):
            game = self.gm.get_game(not_a_gid)

        # test load game, check all fields
        db_ok, game = self.gm.load_game(in_progress_gid)
        self.assertTrue(db_ok)
        self.assertEqual(game.id_, 2)
        self.assertEqual(game.name, 'my in-progress test game')
        self.assertEqual(game.started, True)
        self.assertEqual(game.ended, False)
        self.assertEqual(game.level, 2)
        state_id = 2
        self.assertEqual(game.cur_state_id(), state_id)
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
        self.assertEqual(game.players_ids, [1, 2])
        self.assertEqual(game.extensions, {1: 'rare_technologies',
                                           3: 'ancient_worlds',
                                           5: 'ancient_sdcg'})
        self.assertEqual(game.states_ids, [2])
        self.assertEqual(game.last_valid_state_id, None)

        _LOGGER.info('===END TEST_LOAD_GAME===')

    def test_load_game_failed(self):
        """ methods tested:
        load_game
        """
        _LOGGER.info('===BEGIN TEST_LOAD_GAME_FAILED===')

        in_progress_gid = 2

        # test load/get_game db error
        engine.db.change_db_fail(True)
        db_ok, game = self.gm.load_game(in_progress_gid)
        self.assertFalse(db_ok)
        self.assertEqual(game, None)
        engine.db.change_db_fail(False)

        # test load_game, selective db failure
        engine.db.change_db_fail(True, 'load_player')
        db_ok, game = self.gm.load_game(in_progress_gid, force=True)
        self.assertFalse(db_ok)
        engine.db.change_db_fail(True, 'get_game_players_ids')
        db_ok, game = self.gm.load_game(in_progress_gid, force=True)
        self.assertFalse(db_ok)
        engine.db.change_db_fail(True, 'get_game_ext')
        db_ok, game = self.gm.load_game(in_progress_gid, force=True)
        self.assertFalse(db_ok)
        engine.db.change_db_fail(True, 'get_game_states_ids')
        db_ok, game = self.gm.load_game(in_progress_gid, force=True)
        self.assertFalse(db_ok)
        engine.db.change_db_fail(True, 'load_state')
        db_ok, game = self.gm.load_game(in_progress_gid, force=True)
        self.assertFalse(db_ok)
        engine.db.change_db_fail(False)

        # check game has not been loaded
        with self.assertRaises(KeyError):
            game = self.gm.get_game(in_progress_gid)

        _LOGGER.info('===END TEST_LOAD_GAME_FAILED===')

    def test_get_my_games(self):
        """ methods tested:
        get_my_games
        """
        _LOGGER.info('===BEGIN TEST_GET_MY_GAMES===')

        ## list not ended games joined by player 1
        player_1_id = 1
        # the test player has join all the test games : not started,
        # in progress, ended and private.
        db_ok, games = self.gm.get_my_games(player_1_id)
        self.assertTrue(db_ok)
        self.assertEqual(len(games),  3) # not started, in-progress, private

        engine.db.change_db_fail(True)
        db_ok, games = self.gm.get_my_games(player_1_id)
        self.assertFalse(db_ok)
        self.assertEqual(games, None)
        engine.db.change_db_fail(False)

        _LOGGER.info('===END TEST_GET_MY_GAMES===')

    def test_get_pub_priv_games(self):
        """ methods tested:
        get_pub_priv_games
        """
        _LOGGER.info('===BEGIN TEST_GET_PUB_PRIV_GAMES===')

        ## get the not started test games:
        # -'not started' test game is public
        # -'private' test game is private
        db_ok, pub_games, priv_games = self.gm.get_pub_priv_games()
        self.assertTrue(db_ok)
        self.assertEqual(len(pub_games), 1)
        self.assertEqual(len(priv_games), 1)

        engine.db.change_db_fail(True)
        db_ok, pub_games, priv_games = self.gm.get_pub_priv_games()
        self.assertFalse(db_ok)
        self.assertEqual(pub_games, None)
        self.assertEqual(priv_games, None)
        engine.db.change_db_fail(False)

        _LOGGER.info('===END TEST_GET_PUB_PRIV_GAMES===')

    def test_save_game(self):
        """ methods tested:
        load_game
        save_game
        load_game
        """
        _LOGGER.info('===BEGIN TEST_SAVE_GAME===')

        in_progress_gid = 2

        # test load/get_game ok
        db_ok, game = self.gm.load_game(in_progress_gid)
        self.assertTrue(db_ok)
        self.assertNotEqual(game, None)

        ## test updating a game
        # update game
        game.last_play = datetime.now()
        db_ok, upd_ok = self.gm.save_game(game)
        self.assertTrue(db_ok)
        self.assertTrue(upd_ok)

        ## then reloading the saved game
        db_ok, game_mod = self.gm.load_game(in_progress_gid)
        self.assertTrue(db_ok)
        self.assertNotEqual(game_mod, None)
        self.assertEqual(game.last_play, game_mod.last_play)
        self.assertEqual(game.cur_state_id(), game_mod.cur_state_id())

        # updating a game with wrong id
        game_mod.id_ = 666
        db_ok, upd_ok = self.gm.save_game(game_mod)
        self.assertTrue(db_ok)
        self.assertFalse(upd_ok)

        # check db fail
        engine.db.change_db_fail(True, 'save_state')
        db_ok, upd_ok = self.gm.save_game(game)
        self.assertFalse(db_ok)
        engine.db.change_db_fail(False)

        _LOGGER.info('===END TEST_SAVE_GAME===')

    def test_create_game(self):
        """ methods tested:
        create_game
        get_game
        load_game
        """
        _LOGGER.info('===BEGIN TEST_CREATE_GAME===')

        player_1_id = 1
        player_2_id = 2

        ## test creating a new game
        db_ok = self.gm.create_game(creator_id=1, name='game creation test',
                                    level=3, private=True, password='test',
                                    num_players=3, players_ids=[player_1_id,
                                                                player_2_id],
                                    extensions={1: 'rare_technologies',
                                                11: 'alliances'})
        self.assertTrue(db_ok)

        # next game id is 5
        new_game_id = 5
        new_game = self.gm.get_game(new_game_id)

        # reload new game from db
        db_ok, new_game_reload = self.gm.load_game(game_id=5, force=True)
        self.assertTrue(db_ok)

        # check fields are equal
        self.assertEqual(new_game.id_, new_game_reload.id_)
        self.assertEqual(new_game.name, new_game_reload.name)
        self.assertEqual(new_game.started, new_game_reload.started)
        self.assertEqual(new_game.ended, new_game_reload.ended)
        self.assertEqual(new_game.level, new_game_reload.level)
        self.assertEqual(new_game.cur_state_id(),
                         new_game_reload.cur_state_id())
        self.assertEqual(new_game.private, new_game_reload.private)
        self.assertEqual(new_game.password, new_game_reload.password)
        self.assertEqual(new_game.start_date, new_game_reload.start_date)
        self.assertEqual(new_game.last_play, new_game_reload.last_play)
        self.assertEqual(new_game.num_players, new_game_reload.num_players)
        self.assertEqual(new_game.creator_id, new_game_reload.creator_id)
        self.assertEqual(new_game.players_ids, new_game_reload.players_ids)
        self.assertEqual(new_game.extensions, new_game_reload.extensions)
        self.assertEqual(new_game.states_ids, new_game_reload.states_ids)
        self.assertEqual(new_game.last_valid_state_id,
                         new_game_reload.last_valid_state_id)
        self.assertEqual(new_game.cur_state.__dict__,
                         new_game_reload.cur_state.__dict__)

        # db error creating a new game
        engine.db.change_db_fail(True)
        db_ok = self.gm.create_game(1, 'fail test', 3, False, '', 2, [1], {})
        self.assertFalse(db_ok)

        engine.db.change_db_fail(True, 'save_state')
        db_ok = self.gm.create_game(1, 'fail test', 3, False, '', 2, [1], {})
        engine.db.change_db_fail(False)
        self.assertFalse(db_ok)

        _LOGGER.info('===END TEST_CREATE_GAME===')

    def test_getload_player(self):
        """ methods tested:
        load_player
        get_player
        """
        _LOGGER.info('===BEGIN TEST_GETLOAD_PLAYER===')

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

        _LOGGER.info('===END TEST_GETLOAD_PLAYER===')

    def test_get_players_infos(self):
        """ method tested:
        get_players_infos
        """
        _LOGGER.info('===BEGIN TEST_GET_PLAYERS_INFOS===')

        # check ok get_players_infos
        players_infos = self.gm.get_players_infos()
        self.assertEqual(players_infos, [(1, 'test player'),
                                         (2, 'test player dup')])

        # check db error get_players_infos
        engine.db.change_db_fail(True)
        dummy = self.gm.get_players_infos()
        self.assertEqual(dummy, None)
        engine.db.change_db_fail(False)

        _LOGGER.info('===END TEST_GET_PLAYERS_INFOS===')

    def test_auth_player(self):
        """ method tested:
        auth_player
        """
        _LOGGER.info('===BEGIN TEST_AUTH_PLAYER===')

        player_id_1 = 1

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

        _LOGGER.info('===END TEST_AUTH_PLAYER===')

    def test_create_player(self):
        """ methods tested:
        create_player
        """
        _LOGGER.info('===BEGIN TEST_CREATE_PLAYER===')

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

        _LOGGER.info('===END TEST_CREATE_PLAYER===')

    def test_update_player(self):
        """ methods tested:
        update_player
        """
        _LOGGER.info('===BEGIN TEST_UPDATE_PLAYER===')

        # check ok update_player, ok reload
        player_id = 1
        player = self.gm.get_player(player_id)
        self.assertNotEqual(player, None)
        self.assertEqual(player.id_, 1)

        to_update = {'timezone': 120}
        db_ok, upd_ok = self.gm.update_player(player, to_update)
        self.assertTrue(db_ok)
        self.assertTrue(upd_ok)

        # check duplicate update_player
        to_update = {'email': 'test_dup@test.com'}
        db_ok, upd_ok = self.gm.update_player(player, to_update)
        self.assertTrue(db_ok)
        self.assertFalse(upd_ok)

        # check ok update_player, db error reload
        engine.db.change_db_fail(True, 'load_player')
        to_update = {'timezone': 600}
        db_ok, upd_ok = self.gm.update_player(player, to_update)
        self.assertFalse(db_ok)
        self.assertTrue(upd_ok)
        engine.db.change_db_fail(False)

        # check db error update_player
        engine.db.change_db_fail(True)
        to_update = {'timezone': 120}
        db_ok, upd_ok = self.gm.update_player(player, to_update)
        self.assertFalse(db_ok)
        self.assertFalse(upd_ok)
        engine.db.change_db_fail(False)

        _LOGGER.info('===END TEST_UPDATE_PLAYER===')
