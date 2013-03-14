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
from pyramid import testing
import engine.db

class ViewTests(unittest.TestCase):
    """ functionnal tests of the views """
    def setUp(self):
# init the web app in the constructor instead of setUp, to avoid overload.
# currently the most time is spend by nosetest doing its stuffs,
# not running the tests
#    def __init__(self, *args, **kargs):
#        super(ViewTests, self).__init__(*args, **kargs)
        from paste.deploy.loadwsgi import appconfig
        from webtest import TestApp
        from web_backend import main

        # get settings
        settings = appconfig('config:development.ini', 'main', relative_to='.')

        # instanciate app
        app = main({'test_mode': True}, **settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        # manualy delete 'gm' to close temporary db file used by tests
        del self.testapp.app.registry._settings['gm']

    def _gen_test(self, route, tests_true=[], tests_false=[],
                 post=None, follow=True):
        """ test generator """
        if post is not None:
            res = self.testapp.post(route, post)
        else:
            res = self.testapp.get(route)
        if follow:
            self.assertEqual(res.status_int, 302)
            res = res.follow()
            self.assertEqual(res.status_int, 200)

        for test in tests_true:
            # debug
            if test not in res:
                print('tests_true')
                print('test=[{}]'.format(test))
                print('res=[{}]'.format(res))
            self.assertTrue(test in res)
        for test in tests_false:
            # debug
            if test in res:
                print('tests_false')
                print('test=[{}]'.format(test))
                print('res=[{}]'.format(res))
            self.assertTrue(test not in res)

    def test_view_home(self):
        """ test by calling the view directly """
        from .views import view_home
        request = testing.DummyRequest()
        response = view_home(request)
        self.assertEqual(response['auth'], False)

    def test_view_logout(self):
        """ test by using TestApp """
        # log in sucessfully
        self._gen_test('/login', tests_true=['Login successful.'],
                        post={'email': 'test@test.com', 'password': 'test'})

        # test success logout
        self._gen_test('/logout', tests_true=['Logout successful.'])

        # test unsuccess logout
        self._gen_test('/logout', tests_true=['Not logged in.'])

    def test_view_login(self):
        """ test by using TestApp """
        # test get page leads to home
        self._gen_test('/login', tests_true=['/register', '/login'])

        # test POST empty email/password
        self._gen_test('/login', tests_true=['Enter both email and password.'],
                      post={'email': '', 'password': ''})

        # test POST db error
        engine.db.change_db_fail(True)
        self._gen_test('/login',
                      tests_true=[('Ooops... Error reading player '
                                   'authentification')],
                      tests_false=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})
        engine.db.change_db_fail(False)

        # test POST wrong email/password
        self._gen_test('/login', tests_true=['Unknown email or password.'],
                      post={'email': 'test@test.com', 'password': 'qwerty01'})

        # test POST valid email/password - db error loading player
        engine.db.change_db_fail(True, 'load_player')
        self._gen_test('/login',
                      tests_true=[('Ooops... Error reading player '
                                   'from database.')],
                      tests_false=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})
        engine.db.change_db_fail(False)

        # test POST valid email/password - loading player ok
        self._gen_test('/login', tests_true=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        # test already logged
        self._gen_test('/login', tests_true=['Already logged in as '])

    def test_view_register(self):
        """ test by using TestApp """
        # test already logged
        self._gen_test('/login', tests_true=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        self._gen_test('/register', tests_true=['Already logged in as '])

        self._gen_test('/logout', tests_true=['Logout successful.'])

        # test POST empty name/email
        self._gen_test('/register',
                      tests_true=['Enter name, email, password and timezone.'],
                      post={'email': 'newplayer@test.com'}, follow=False)

        # test POST password != password2
        self._gen_test('/register',
                      tests_true=['Passwords not identical.'],
                      post={'name': 'new', 'email': 'new@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty02',
                            'timezone': '120'},
                      follow=False)

        # test POST non valid email
        self._gen_test('/register',
                      tests_true=['Not a valid email.'],
                      post={'name': 'new', 'email': 'invalid test.com@',
                            'password': 'qwerty01', 'password2': 'qwerty01',
                            'timezone': '120'},
                      follow=False)

        # test POST duplicate name/email
        self._gen_test('/register',
                      tests_true=['Already registered name or email.'],
                      post={'name': 'test player', 'email': 'test@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty01',
                            'timezone': '120'},
                      follow=False)

        # test POST db write error
        engine.db.change_db_fail(True)
        self._gen_test('/register',
                      tests_true=['Ooops... Error writing player in database.'],
                      post={'name': 'new', 'email': 'new@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty01',
                            'timezone': '120'})
        engine.db.change_db_fail(False)

        # test POST creation ok
        self._gen_test('/register',
                      tests_true=['Player successfuly created.'],
                      post={'name': 'new', 'email': 'new@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty01',
                            'timezone': '120'})

    def test_view_editprofile(self):
        """ test by using TestApp """
        # test not auth, display home
        self._gen_test('/editprofile', tests_true=['New user ?'], follow=False)

        # auth
        self._gen_test('/login', tests_true=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        # test POST invalid email
        self._gen_test('/editprofile', tests_true=['Not a valid email.'],
                      post={'email': 'invalid test.com@',
                            'password': 'qwerty01',
                            'password2': 'qwerty01',
                            'timezone': 600},
                      follow=False)

        # test POST password != password2
        self._gen_test('/editprofile', tests_true=['Passwords not identical.'],
                      post={'email': 'test@test.com',
                            'password': 'qwerty01',
                            'password2': 'qwerty02',
                            'timezone': 600},
                      follow=False)

        # test POST nothing to update
        self._gen_test('/editprofile', tests_true=['Nothing to update.'],
                      post={'email': 'test@test.com',
                            'timezone': 600},
                      follow=False)

        # test POST update email already in use
        self._gen_test('/editprofile', tests_true=['Email already in use.'],
                      post={'email': 'test_dup@test.com',
                            'timezone': 600},
                      follow=False)

        # test POST db write error
        engine.db.change_db_fail(True)
        self._gen_test('/editprofile',
                      tests_true=['Ooops... Error writing player in database.'],
                      post={'email': 'new_test@test.com',
                            'timezone': 600})
        engine.db.change_db_fail(False)

        # test POST update all, reload fail
        engine.db.change_db_fail(True, 'load_player')
        self._gen_test('/editprofile',
                      tests_true=["Player successfuly updated.",
                                  ("Ooops... Error reading player "
                                   "from database")],
                      post={'email': 'new_test@test.com',
                            'password': 'qwerty01',
                            'password2': 'qwerty01',
                            'timezone': 240})
        engine.db.change_db_fail(False)

        # test POST update all
        self._gen_test('/editprofile',
                      tests_true=['Player successfuly updated.'],
                      post={'email': 'test@test.com',
                            'password': 'test',
                            'password2': 'test',
                            'timezone': 300})
    def test_view_create_game(self):
        """ test by using TestApp """
        # test not auth, display home
        self._gen_test('/creategame', tests_true=['New user ?'], follow=False)

        # auth
        self._gen_test('/login', tests_true=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        # test display 
        self._gen_test('/creategame',
                      tests_true=['Create new game'],
                      follow=False)

        # test display can't get players infos
        engine.db.change_db_fail(True)
        self._gen_test('/creategame',
                      tests_true=[('Ooops... Error reading players infos '
                                   'from database.')])
        engine.db.change_db_fail(False)

        # test POST missing game_name
        self._gen_test('/creategame',
                      tests_true=["Enter game name, #players and level."],
                      post={'num_players': '2',
                            'player0': '1',
                            'player1': '2',
                            'level': '3',
                            'secret_world': 'on',
                            'alliances': 'on'},
                      follow=False)

        # test POST passwords not identical
        self._gen_test('/creategame',
                      tests_true=['Passwords not identical.'],
                      post={'name': "Test game",
                            'num_players': '2',
                            'level': '3',
                            'private': 'on',
                            'password': 'qwerty01',
                            'password2': 'qwerty02',
                            'player0': '1',
                            'player1': '2',
                            'secret_world': 'on',
                            'alliances': 'on'},
                      follow=False)

        # test POST db error
        engine.db.change_db_fail(True, 'create_game')
        self._gen_test('/creategame',
                      tests_true=['Ooops... Error writing game in database.'],
                      post={'name': "Test game",
                            'num_players': '2',
                            'level': '3',
                            'player0': '1'})
        engine.db.change_db_fail(False)

        # test POST ok
        self._gen_test('/creategame',
                      tests_true=['Game successfuly created.'],
                      post={'name': "Test game",
                            'num_players': '2',
                            'level': '3',
                            'player0': '1',
                            'secret_world': 'on',
                            'alliances': 'on'})

    def test_view_joingame(self):
        """ test by using TestApp """
        # test not auth, display home
        self._gen_test('/joingame', tests_true=['New user ?'], follow=False)

        # auth
        self._gen_test('/login', tests_true=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        # test DB not ok 
        engine.db.change_db_fail(True)
        self._gen_test('/joingame',
                      tests_true=['Ooops... Error reading games from database'])
        engine.db.change_db_fail(False)

        # test display 'my test game'
        self._gen_test('/joingame',
                      tests_true=['my test game',
                                  ('There is currently no private game '
                                   'awaiting for players.')],
                      tests_false=[('There is currently no open game awaiting '
                                    'for players.')],
                      follow=False)

    def test_view_mygames(self):
        """ test by using TestApp """
        # test not auth, display home
        self._gen_test('/mygames', tests_true=['New user ?'], follow=False)

        # auth
        self._gen_test('/login', tests_true=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        # test DB not ok 
        engine.db.change_db_fail(True)
        self._gen_test('/mygames',
                      tests_true=['Ooops... Error reading games from database'])
        engine.db.change_db_fail(False)

        # test display 'my test game' and 'my in-progress test game'
        self._gen_test('/mygames',
                      tests_true=['my test game', 'my in-progress test game'],
                      follow=False)

        # create new player and check that he has no games
        self._gen_test('/logout', tests_true=['Logout successful.'])
        self._gen_test('/register',
                      tests_true=['Player successfuly created.'],
                      post={'name': 'new', 'email': 'new@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty01',
                            'timezone': '120'})
        self._gen_test('/login', tests_true=['Login successful.'],
                        post={'email': 'new@test.com', 'password': 'qwerty01'})
        self._gen_test('/mygames',
                      tests_true=['You currently have no games in progress.'],
                      follow=False)
