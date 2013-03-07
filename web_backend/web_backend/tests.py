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
from pyramid.httpexceptions import HTTPFound

# TODO::normalize method/class naming convention

class ViewTests(unittest.TestCase):
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

    def gen_test(self, route, tests_true=[], tests_false=[],
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
        self.gen_test('/login', tests_true=['Login successful.'],
                        post={'email': 'test@test.com', 'password': 'test'})

        # test success logout
        self.gen_test('/logout', tests_true=['Logout successful.'])

        # test unsuccess logout
        self.gen_test('/logout', tests_true=['Not logged in.'])

    def test_view_login(self):
        """ test by using TestApp """
        # test get page leads to home
        self.gen_test('/login', tests_true=['/register', '/login'])

        # test POST empty email/password
        self.gen_test('/login', tests_true=['Enter both email and password.'],
                      post={'email': '', 'password': ''})

        # test POST db error
        import engine.db
        engine.db.change_db_fail(True)
        self.gen_test('/login',
                      tests_true=[('Ooops... Error reading player '
                                   'authentification')],
                      tests_false=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})
        engine.db.change_db_fail(False)

        # test POST wrong email/password
        self.gen_test('/login', tests_true=['Unknown email or password.'],
                      post={'email': 'test@test.com', 'password': 'qwerty01'})

        # test POST valid email/password - db error loading player
        engine.db.change_db_fail(True, 'load_player')
        self.gen_test('/login',
                      tests_true=[('Ooops... Error reading player '
                                   'from database.')],
                      tests_false=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})
        engine.db.change_db_fail(False)

        # test POST valid email/password - loading player ok
        self.gen_test('/login', tests_true=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        # test already logged
        self.gen_test('/login', tests_true=['Already logged in as '])

    def test_view_register(self):
        """ test by using TestApp """
        # test already logged
        self.gen_test('/login', tests_true=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        self.gen_test('/register', tests_true=['Already logged in as '])

        self.gen_test('/logout', tests_true=['Logout successful.'])

        # test POST empty name/email
        self.gen_test('/register',
                      tests_true=['Enter name, email, password and timezone.'],
                      post={'email': 'newplayer@test.com'}, follow=False)

        # test POST password != password2
        self.gen_test('/register',
                      tests_true=['Passwords not identical.'],
                      post={'name': 'new', 'email': 'new@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty02',
                            'timezone': '120'},
                      follow=False)

        # test POST duplicate name/email
        self.gen_test('/register',
                      tests_true=['Already registered name or email.'],
                      post={'name': 'test player', 'email': 'test@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty01',
                            'timezone': '120'},
                      follow=False)

        # test POST db write error
        import engine.db
        engine.db.change_db_fail(True)
        self.gen_test('/register',
                      tests_true=['Ooops... Error writing player in database.'],
                      post={'name': 'new', 'email': 'new@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty01',
                            'timezone': '120'})
        engine.db.change_db_fail(False)

        # test POST creation ok
        self.gen_test('/register',
                      tests_true=['Player successfuly created.'],
                      post={'name': 'new', 'email': 'new@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty01',
                            'timezone': '120'})

    def test_view_editprofile(self):
        """ test by using TestApp """
        # test not auth, display home
        self.gen_test('/editprofile', tests_true=['New user ?'], follow=False)

        # auth
        self.gen_test('/login', tests_true=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        # test POST password != password2
        self.gen_test('/editprofile', tests_true=['Passwords not identical.'],
                      post={'email': 'test@test.com',
                            'password': 'qwerty01',
                            'password2': 'qwerty02',
                            'timezone': 600},
                      follow=False)

        # test POST nothing to update
        self.gen_test('/editprofile', tests_true=['Nothing to update.'],
                      post={'email': 'test@test.com',
                            'timezone': 600},
                      follow=False)

        # test POST update email already in use
        self.gen_test('/editprofile', tests_true=['Email already in use.'],
                      post={'email': 'test_dup@test.com',
                            'timezone': 600},
                      follow=False)

        # test POST db write error
        import engine.db
        engine.db.change_db_fail(True)
        self.gen_test('/editprofile',
                      tests_true=['Ooops... Error writing player in database.'],
                      post={'email': 'new_test@test.com',
                            'timezone': 600})
        engine.db.change_db_fail(False)

        # test POST update all, reload fail
        engine.db.change_db_fail(True, 'load_player')
        self.gen_test('/editprofile',
                      tests_true=["Player successfuly updated.",
                                  ("Ooops... Error reading player "
                                   "from database")],
                      post={'email': 'new_test@test.com',
                            'password': 'qwerty01',
                            'password2': 'qwerty01',
                            'timezone': 240})
        engine.db.change_db_fail(False)

        # test POST update all
        self.gen_test('/editprofile',
                      tests_true=['Player successfuly updated.'],
                      post={'email': 'test@test.com',
                            'password': 'test',
                            'password2': 'test',
                            'timezone': 300})
    def test_view_create_game(self):
        """ test by using TestApp """
        # test not auth, display home
        self.gen_test('/creategame', tests_true=['New user ?'], follow=False)

        # auth
        self.gen_test('/login', tests_true=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        # test display 
        self.gen_test('/creategame',
                      tests_true=['Create new game'],
                      follow=False)

        # test display can't get players infos
        import engine.db
        engine.db.change_db_fail(True)
        self.gen_test('/creategame',
                      tests_true=[('Ooops... Error reading players infos '
                                   'from database.')])
        engine.db.change_db_fail(False)
