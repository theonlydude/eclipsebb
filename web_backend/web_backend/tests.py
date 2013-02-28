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

class ViewTests(unittest.TestCase):
    def setUp(self):
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
        from .views import view_home
        request = testing.DummyRequest()
        response = view_home(request)
        self.assertEqual(response['auth'], False)

    def test_view_login(self):
        from .views import view_login

        res = self.testapp.get('/', status=200)
        print(res)
#        request = testing.DummyRequest()
#        response = view_login(request)
#        self.assertEqual(response.status, '302 Found')
#        print(response.__dict__)
