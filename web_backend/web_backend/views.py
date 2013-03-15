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

import logging
from validate_email import validate_email
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

# simple helpers
def is_auth(request):
    """ check if the player is authentified """
    return 'auth' in request.session and request.session['auth']

def already_logged(request):
    """ return to home displaying 'already logged' """
    gm =  request.registry.settings['gm']
    player_id = request.session['player_id']
    player = gm.get_player(player_id)
    request.session.flash('Already logged in as '.format(player.name))
    return HTTPFound(location=request.route_url('home'))

def db_read_error(request, msg):
    """ return to home displaying a db read error """
    request.session.flash(('Ooops... Error reading {} '
                           'from database.').format(msg))
    return HTTPFound(location=request.route_url('home'))

def db_write_error(request, msg):
    """ return to home displaying a db write error """
    request.session.flash('Ooops... Error writing {} in database.'.format(msg))
    return HTTPFound(location=request.route_url('home'))

# functions to access values in POST
def get_post_int(request, key):
    """ helper to extract int from POST variables """
    val = request.POST.get(key)
    if val is None:
        return None
    else:
        return int(val)

def get_post_str(request, key):
    """ helper to extract str from POST variables """
    return request.POST.get(key)

def get_post_bool(request, key):
    """ helper to extract bool from POST variables """
    val = request.POST.get(key)
    return val == 'on'

@view_config(route_name='creategame', renderer='creategame.mako')
def view_create_game(request):
    """ create a new game """
    if not is_auth(request):
        return {'auth': False}
    
    gm =  request.registry.settings['gm']

    player = gm.get_player(request.session['player_id'])
    players_infos = gm.get_players_infos()

    if players_infos is None:
        return db_read_error(request, 'players infos')

    return_values = {'auth': True,
                     'player': player,
                     'players_infos': players_infos,
                     'extensions_infos': gm.ext_infos}

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
        for id_, name, _ in gm.ext_infos:
            checked = get_post_bool(request, name)
            if checked:
                extensions[name] = id_

        if not game_name or not num_players or not level:
            request.session.flash("Enter game name, #players and level.")
            return return_values

        if private:
            if password != password2:
                request.session.flash('Passwords not identical.')
                return return_values
            
        status = gm.create_game(creator_id, game_name, level,
                                private, password, num_players,
                                players_ids, extensions)
        if not status:
            return db_write_error(request, 'game')
        else:
            request.session.flash('Game successfuly created.')
            return HTTPFound(location=request.route_url('home'))

    return return_values

@view_config(route_name='mygames', renderer='mygames.mako')
def view_mygames(request):
    """ list player games which are not ended """
    if not is_auth(request):
        return {'auth': False}

    gm =  request.registry.settings['gm']
    (db_ok, my_games) = gm.get_my_games(request.session['player_id'])

    if not db_ok:
        return db_read_error(request, 'games')

    return {'auth': True,
            'my_games': my_games}

@view_config(route_name='joingame', renderer='joingame.mako')
def view_joingame(request):
    """ list public and private not started games """
    if not is_auth(request):
        return {'auth': False}

    gm =  request.registry.settings['gm']
    (db_ok, pub_games, priv_games) = gm.get_pub_priv_games()

    if not db_ok:
        return db_read_error(request, 'games')

    return {'auth': True,
            'pub_games': pub_games,
            'priv_games': priv_games,
            'timezones': gm.timezones}

@view_config(route_name='home', renderer='home.mako')
def view_home(request):
    """ entry point for the users """
    return {'auth': is_auth(request)}

@view_config(route_name='login')
def view_login(request):
    """ allow players to login """
    if is_auth(request):
        return already_logged(request)

    if request.method == 'POST':
        email = get_post_str(request, 'email')
        password = get_post_str(request, 'password')
        if email and password:
            gm = request.registry.settings['gm']
            (db_ok, auth_ok, player_id) = gm.auth_player(email, password)
            if db_ok and auth_ok:
                # load player
                if gm.load_player(player_id) is not None:
                    # update session
                    request.session['auth'] = True
                    request.session['player_id'] = player_id
                    request.session.flash('Login successful.')
                else:
                    logging.error(("Can't load player {} from "
                                   "database").format(player_id))
                    return db_read_error(request, 'player')
            elif db_ok and not auth_ok:
                request.session.flash('Unknown email or password.')
            else:
                return db_read_error(request, 'player authentification')
        else:
            request.session.flash('Enter both email and password.')

    return HTTPFound(location=request.route_url('home'))

def del_(obj, name):
    """ simple helper which delete an attribute only if present """
    if name in obj:
        del obj[name]

@view_config(route_name='logout')
def view_logout(request):
    """ logout player, empty session vars """
    if is_auth(request):
        del_(request.session, 'auth')
        del_(request.session, 'player_id')
        request.session.flash('Logout successful.')
    else:
        request.session.flash('Not logged in.')

    return HTTPFound(location=request.route_url('home'))

@view_config(route_name='register', renderer='register.mako')
def view_register(request):
    """ register new player """
    if is_auth(request):
        return already_logged(request)

    gm = request.registry.settings['gm']
    return_values = {'timezones': gm.timezones}

    if request.method == 'POST':
        # get POST vars
        name = get_post_str(request, 'name')
        email = get_post_str(request, 'email')
        password = get_post_str(request, 'password')
        password2 = get_post_str(request, 'password2')
        tz_id = get_post_int(request, 'timezone')

        # validate no empty field
        if not name or not email or not password or not password2 or not tz_id:
            request.session.flash('Enter name, email, password and timezone.')
            return return_values

        # validate passwords
        if password != password2:
            request.session.flash('Passwords not identical.')
            return return_values

        # validate the email
        if not validate_email(email):
            request.session.flash('Not a valid email.')
            return return_values

        # validate timezone
        if not tz_id in gm.timezones.dict_tz:
            request.session.flash('Not a valid timezone.')
            return return_values

        (db_ok, dup_ok, _) = gm.create_player(name, email, password, tz_id)
        if db_ok and dup_ok:
            request.session.flash('Player successfuly created.')
            return HTTPFound(location=request.route_url('home'))
        elif db_ok and not dup_ok:
            request.session.flash('Already registered name or email.')
        else:
            return db_write_error(request, 'player')

    return return_values

@view_config(route_name='editprofile', renderer='editprofile.mako')
def view_editprofile(request):
    """ allow players to edit their profiles """
    if not is_auth(request):
        return {'auth': False}

    gm = request.registry.settings['gm']
    player = gm.get_player(request.session['player_id'])

    return_values = {'auth': True,
                     'player': player,
                     'timezones': gm.timezones}

    if request.method == 'POST':
        email = get_post_str(request, 'email')
        password = get_post_str(request, 'password')
        password2 = get_post_str(request, 'password2')
        tz_id = get_post_int(request, 'timezone')

        to_update = {}

        if email != player.email:
            to_update['email'] = email
            # validate new email
            if not validate_email(email):
                request.session.flash('Not a valid email.')
                return return_values

        if password and password2:
            if password != password2:
                request.session.flash('Passwords not identical.')
                return return_values
            else:
                to_update['password'] = password

        if tz_id != player.tz_id:
            to_update['timezone'] = tz_id

        if len(to_update) == 0:
            request.session.flash('Nothing to update.')
        else:
            (db_ok, upd_ok) = gm.update_player(player, to_update)
            if db_ok and upd_ok:
                request.session.flash('Player successfuly updated.')
                # update player in gm
                if gm.load_player(player.id_):
                    return HTTPFound(location=request.route_url('home'))
                else:
                    logging.error(("Can't reload player {} from "
                                   "database").format(player.id_))
                    return db_read_error(request, 'player')
            elif db_ok and not upd_ok:
                request.session.flash('Email already in use.')
            else:
                return db_write_error(request, 'player')

    return return_values
