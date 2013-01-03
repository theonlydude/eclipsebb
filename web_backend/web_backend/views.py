from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

@view_config(route_name='home', renderer='home.mako')
def view_home(request):
    return {'project': 'Eclipse Board Game Web version'}

@view_config(route_name='login', renderer='login.mako')
def view_login(request):
    if request.method == 'POST':
        if request.POST.get('email') and request.POST.get('password'):
            email = request.POST.get('email')
            password = request.POST.get('password')
            gm = request.registry.settings['gm']
            if gm.authPlayer(email, password):
                # update session
                request.session['auth'] = True

                # redirect to home
                return HTTPFound(location=request.route_url('home'))
            else:
                request.session.flash('Unknown email or password.')
        else:
            request.session.flash('Enter both email and password.')
    return {}

@view_config(route_name='register', renderer='register.mako')
def view_register(request):
    return {}
