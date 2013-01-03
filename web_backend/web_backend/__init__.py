from pyramid_beaker import session_factory_from_settings            
from pyramid.config import Configurator
from engine.game_manager import GamesManager

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # create the games manager and add it to the settings so that it
    # can be accessed from the views
    gm = GamesManager()
    settings['gm'] = gm

    session_factory = session_factory_from_settings(settings)

    config = Configurator(settings=settings)
    config.include('pyramid_beaker')
    config.set_session_factory(session_factory)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('register', '/register')

    config.scan()
    return config.make_wsgi_app()
