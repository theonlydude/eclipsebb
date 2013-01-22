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

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
import logging

# simple helpers
def is_auth(request):
    return 'auth' in request.session and request.session['auth'] == True

def already_logged(request):
    """ return to home displaying 'already logged' """
    gm =  request.registry.settings['gm']
    player_id = request.session['player_id']
    player = gm.getPlayer(player_id)
    msg = 'Already logged in as ' + player.name
    request.session.flash(msg)
    return HTTPFound(location=request.route_url('home'))

def db_read_error(request, msg):
    request.session.flash('Error reading {} from database'.format(msg))
    return HTTPFound(location=request.route_url('home'))

def db_write_error(request, msg):
    request.session.flash('Error writing {} in database'.format(msg))
    return HTTPFound(location=request.route_url('home'))

# functions to access values in POST
def get_post_int(request, key):
    val = request.POST.get(key)
    if val is None:
        return None
    else:
        return int(val)

def get_post_str(request, key):
    return request.POST.get(key)

def get_post_bool(request, key):
    val = request.POST.get(key)
    return val == 'on'

@view_config(route_name='creategame', renderer='creategame.mako')
def view_create_game(request):
    if not is_auth(request):
        return {'auth': False}
    
    gm =  request.registry.settings['gm']
    extensions_infos = gm.DB.getExtensionsInfos()

    if extensions_infos is None:
        return db_read_error(request, 'extensions infos')

    if request.method == 'POST':
        game_name = get_post_str(request, 'name')
        num_players = get_post_int(request, 'num_players')
        creator_id = get_post_int(request, 'player0')
        level = get_post_int(request, 'level')
        private = get_post_bool(request, 'private')
        password = get_post_str(request, 'password')
        password2 = get_post_str(request, 'password2')

        # players is a tab of players ids
        players_ids = []
        for i in range(5):
            players_ids.append(get_post_int(request, 'player{}'.format(i)))

        # extensions is a dict of name->id
        extensions = {}
        for id_, name, desc in extensions_infos:
            checked = get_post_bool(request, name)
            if checked == True:
                extensions[name] = id_

        if not game_name or not num_players or not level:
            request.session.flash("Enter game's name, #players and level")
        else:
            passwd_checked = True
            if private == True:
                if password != password2:
                    request.session.flash('Passwords not identical.')
                    passwd_checked = False
            
            if passwd_checked == True:
                game_id = gm.createGame(creator_id, game_name, level,
                                        private, password, num_players,
                                        players_ids, extensions)
                if game_id is None:
                    db_write_error(request, 'game')
                else:
                    request.session.flash('Game successfuly create.')
                    return HTTPFound(location=request.route_url('home'))

    gm =  request.registry.settings['gm']
    player = gm.getPlayer(request.session['player_id'])
    players_infos = gm.DB.getPlayersInfos()

    if players_infos is None:
        return db_read_error(request, 'players infos')

    return {'auth': True,
            'player': player,
            'players_infos': players_infos,
            'extensions_infos': extensions_infos}

@view_config(route_name='mygames', renderer='mygames.mako')
def view_mygames(request):
    if not is_auth(request):
        return {'auth': False}

    # get player running games
    gm =  request.registry.settings['gm']
    player = gm.getPlayer(request.session['player_id'])
    #running_games = gm.getRunningGames(player.id_)
    running_games = []
    return {'auth': True,
            'running_games': running_games}

@view_config(route_name='joingame', renderer='joingame.mako')
def view_joingame(request):
    if not is_auth(request):
        return {'auth': False}

    gm =  request.registry.settings['gm']

    pub_games, priv_games = gm.getPubPrivGames()

    if pub_games is None or priv_games is None:
        return db_read_error(request, 'games')

    return {'auth': True,
            'pub_games': pub_games,
            'priv_games': priv_games}

@view_config(route_name='home', renderer='home.mako')
def view_home(request):
    return {'auth': is_auth(request)}

@view_config(route_name='login')
def view_login(request):
    if is_auth(request):
        return already_logged(request)

    if request.method == 'POST':
        email = get_post_str(request, 'email')
        password = get_post_str(request, 'password')
        if email and password:
            gm = request.registry.settings['gm']
            player_id = gm.DB.authPlayer(email, password)
            if player_id is not None:
                # load player
                if gm.loadPlayer(player_id) is not None:
                    # update session
                    request.session['auth'] = True
                    request.session['player_id'] = player_id
                    request.session.flash('Login successful.')
                else:
                    logging.error("Can't load player {} from \
database".format(player_id))
                    return db_read_error(request, 'player')
            else:
                request.session.flash('Unknown email or password.')
        else:
            request.session.flash('Enter both email and password.')

    return HTTPFound(location=request.route_url('home'))

def del_(obj, name):
    if name in obj:
        del obj[name]

@view_config(route_name='logout')
def view_logout(request):
    if is_auth(request):
        del_(request.session, 'auth')
        del_(request.session, 'player_id')
        request.session.flash('Logout successful.')
    else:
        request.session.flash('Not logged in.')

    return HTTPFound(location=request.route_url('home'))

@view_config(route_name='register', renderer='register.mako')
def view_register(request):
    if is_auth(request):
        return already_logged(request)

    if request.method == 'POST':
        name = get_post_str(request, 'name')
        email = get_post_str(request, 'email')
        password = get_post_str(request, 'password')
        password2 = get_post_str(request, 'password2')
        tz = get_post_str(request, 'timezone')
        if not name or not email or not password or not password2 or not tz:
            request.session.flash('Enter name, email, password and timezone.')
        else:
            if password != password2:
                request.session.flash('Passwords not identical.')
            else:
                gm = request.registry.settings['gm']
                if gm.DB.createPlayer(name, email, password, tz):
                    request.session.flash('User successfuly created.')
                    return HTTPFound(location=request.route_url('home'))
                else:
                    request.session.flash('Already registered name or email.')

    gm = request.registry.settings['gm']
    tzs = gm.DB.getTZ()
    if tzs is None:
        return db_read_error(request, 'timezones')
    return {'timezones': tzs}
