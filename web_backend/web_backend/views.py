from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

@view_config(route_name='home', renderer='home.mako')
def view_home(request):
    return {'project': 'Eclipse Board Game Web @alpha'}

@view_config(route_name='login', renderer='login.mako')
def view_login(request):
    if request.session['auth'] == True:
        msg = 'Already logged in as '+request.session['playerName']
        request.session.flash(msg)
        return HTTPFound(location=request.route_url('home'))

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            gm = request.registry.settings['gm']
            result = gm.DB.authPlayer(email, password)
            if result is not None:
                playerId, playerName = result
                # update session
                request.session['auth'] = True
                request.session['playerId'] = playerId
                request.session['playerName'] = playerName

                # redirect to home
                return HTTPFound(location=request.route_url('home'))
            else:
                request.session.flash('Unknown email or password.')
        else:
            request.session.flash('Enter both email and password.')
    return {}

@view_config(route_name='logout')
def view_logout(request):
    if request.session['auth'] == True:
        request.session['auth'] = False
        del request.session['playerId']
        del request.session['playerName']
        request.session.flash('Logout successful.')
    else:
        request.session.flash('Not logged in.')

    return HTTPFound(location=request.route_url('home'))

@view_config(route_name='register', renderer='register.mako')
def view_register(request):
    gm = request.registry.settings['gm']
    tz = gm.DB.getTZ()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        tz = request.POST.get('timezone')
        if not name or not email or not password or not password2 or not tz:
            request.session.flash('Enter name, email, password and timezone.')
            return {'timezones': tz}

        if password != password2:
            request.session.flash('Passwords not identical.')
            return {'timezones': tz}

        if gm.DB.createPlayer(name, email, password, tz):
            request.session.flash('User successfuly created.')

            # redirect to home
            return HTTPFound(location=request.route_url('home'))
        else:
            request.session.flash('Already registered name or email.')

    return {'timezones': tz}
