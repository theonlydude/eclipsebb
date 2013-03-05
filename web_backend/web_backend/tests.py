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
        from web_backend import main
        from webtest import TestApp
        from paste.deploy.loadwsgi import appconfig

        # get settings
        settings = appconfig('config:development.ini', 'main', relative_to='.')

        # instanciate app
        app = main({'test_mode': True}, **settings)
        self.testapp = TestApp(app)

        # INFO::to have access to gm from testapp, could be useful:
        #self.testapp.app.registry._settings['gm']

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
#            if test not in res:
#                print('tests_true')
#                print('test=[{}]'.format(test))
#                print('res=[{}]'.format(res))
            self.assertTrue(test in res)
        for test in tests_false:
            # debug
#            if test in res:
#                print('tests_false')
#                print('test=[{}]'.format(test))
#                print('res=[{}]'.format(res))
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
        self.gen_test('/login', ['Login successful.'],
                        post={'email': 'test@test.com', 'password': 'test'})

        # test success logout
        self.gen_test('/logout', ['Logout successful.'])

        # test unsuccess logout
        self.gen_test('/logout', ['Not logged in.'])

    def test_view_login(self):
        """ test by using TestApp """
        # test get page leads to home
        self.gen_test('/login', ['/register', '/login'])

        # test POST empty email/password
        self.gen_test('/login', ['Enter both email and password.'],
                      post={'email': '', 'password': ''})

        # test POST db error
        import engine.db
        engine.db.change_db_fail(True)
        self.gen_test('/login',
                      tests_true=['Ooops... Error reading player authentification'],
                      tests_false=['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})
        engine.db.change_db_fail(False)

        # test POST wrong email/password
        self.gen_test('/login', ['Unknown email or password.'],
                      post={'email': 'test@test.com', 'password': 'qwerty01'})

        # test POST valid email/password - db error loading player
        import engine.db
        engine.db.change_db_fail(True, 'loadPlayer')
        self.gen_test('/login',
                      ['Ooops... Error reading player from database.'],
                      ['Login successful.'],
                      {'email': 'test@test.com', 'password': 'test'})
        engine.db.change_db_fail(False)

        # test POST valid email/password - loading player ok
        self.gen_test('/login', ['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        # test already logged
        self.gen_test('/login', ['Already logged in as '])

    def test_view_register(self):
        """ test by using TestApp """
        # test already logged
        self.gen_test('/login', ['Login successful.'],
                      post={'email': 'test@test.com', 'password': 'test'})

        self.gen_test('/register', ['Already logged in as '])

        self.gen_test('/logout', ['Logout successful.'])

        # test POST empty name/email
        self.gen_test('/register',
                      ['Enter name, email, password and timezone.'],
                      post={'email': 'newplayer@test.com'}, follow=False)

        # test POST password != password2
        self.gen_test('/register',
                      ['Passwords not identical.'],
                      post={'name': 'player1', 'email': 'player1@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty02',
                            'timezone': '120'},
                      follow=False)

        # test POST duplicate name/email
        self.gen_test('/register',
                      ['Already registered name or email.'],
                      post={'name': 'test player', 'email': 'test@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty01',
                            'timezone': '120'},
                      follow=False)

        # test POST db write error
        import engine.db
        engine.db.change_db_fail(True)
        self.gen_test('/register',
                      ['Ooops... Error writing player in database.'],
                      post={'name': 'player1', 'email': 'player1@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty01',
                            'timezone': '120'})
        engine.db.change_db_fail(False)

        # test POST creation ok
        self.gen_test('/register',
                      ['Player successfuly created.'],
                      post={'name': 'player1', 'email': 'player1@test.com',
                            'password': 'qwerty01', 'password2': 'qwerty01',
                            'timezone': '120'})
