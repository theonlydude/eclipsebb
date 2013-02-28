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

# TODO::use custom preloaded db for tests
# TODO::failer && logger in log...

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
        app = main({}, **settings)
        self.testapp = TestApp(app)

    def test_view_home(self):
        """ test by calling the view directly """
        from .views import view_home
        request = testing.DummyRequest()
        response = view_home(request)
        self.assertEqual(response['auth'], False)

    def test_view_logout(self):
        """ test by using TestApp """
        # log in sucessfully
        res = self.testapp.post('/login', {'email': 'adri', 'password': 'adri'})
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertTrue('Login successful.' in res)

        # test success logout
        res = self.testapp.post('/logout')
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertTrue('Logout successful.' in res)

        # test unsuccess logout
        res = self.testapp.post('/logout')
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertTrue('Not logged in.' in res)

    def test_view_login(self):
        """ test by using TestApp """
        # test get page leads to home
        res = self.testapp.get('/login')
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertTrue('/register' in res)
        self.assertTrue('/login' in res)

        # test POST empty email/password
        res = self.testapp.post('/login', {'email': '', 'password': ''})
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertTrue('Enter both email and password.' in res)

        # test POST db error
        import engine.db
        engine.db.change_db_fail(True)

        res = self.testapp.post('/login', {'email': 'pets', 'password': 'pets'})
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertFalse('Login successful.' in res)
        self.assertTrue('Ooops... Error reading player authentification' in res)
        
        engine.db.change_db_fail(False)

        # test POST wrong email/password
        res = self.testapp.post('/login', {'email': 'adri', 'password': 'biere'})
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertTrue('Unknown email or password.' in res)

        # test POST valid email/password - db error loading player
        import engine.db
        engine.db.change_db_fail(True, 'loadPlayer')

        res = self.testapp.post('/login', {'email': 'pets', 'password': 'pets'})
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertFalse('Login successful.' in res)
        self.assertTrue('Ooops... Error reading player from database.' in res)
        
        engine.db.change_db_fail(False)

        # test POST valid email/password - loading player ok
        res = self.testapp.post('/login', {'email': 'adri', 'password': 'adri'})
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertTrue('Login successful.' in res)

        # test already logged
        res = self.testapp.get('/login')
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertTrue('Already logged in as ' in res)

    def test_view_register(self):
        """ test by using TestApp """
        # test already logged
        # test POST valid email/password - loading player ok
        res = self.testapp.post('/login', {'email': 'adri', 'password': 'adri'})
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertTrue('Login successful.' in res)

        res = self.testapp.get('/register')
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertTrue('Already logged in as ' in res)

        res = self.testapp.post('/logout')
        self.assertEqual(res.status_int, 302)
        res = res.follow()
        self.assertEqual(res.status_int, 200)
        self.assertTrue('Logout successful.' in res)
        
