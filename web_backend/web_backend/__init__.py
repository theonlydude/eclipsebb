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

from pyramid_beaker import session_factory_from_settings            
from pyramid.config import Configurator
import pyramid
from engine.game_manager import GamesManager

def includeme(config):
    # to populate threadlocal
    config.begin()

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('mygames', '/mygames')
    config.add_route('joingame', '/joingame')
    config.add_route('creategame', '/creategame')
    config.add_route('editprofile', '/editprofile')

    # we have to do that here instead of in main because main is no called from
    # tests.py
    settings = pyramid.threadlocal.get_current_registry().settings
    
    # instantiate the games manager and add it to the settings so that it
    # can be accessed from the views
    gm = GamesManager()
    settings['gm'] = gm

    config.include('pyramid_beaker')
    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    print(settings)

    config = Configurator(settings=settings)
    config.include('web_backend.includeme')
    config.scan()
    return config.make_wsgi_app()
