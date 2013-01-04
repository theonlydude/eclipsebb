# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Welcome to Eclipse Board Game Online version</h1>

Project: ${project}<br />

% if 'auth' in request.session and request.session['auth'] == True:
AUTHENTICATED !<br />
<%
  playerId = request.session['playerId']
  playerName = request.session['playerName']
%>
Player id = ${playerId}<br />
Player name = ${playerName}<br />
<a href="${request.route_url('logout')}">logout</a>
% else:
NOT AUTHENTICATED !<br />
<a href="${request.route_url('register')}">register</a><br />
<a href="${request.route_url('login')}">login</a><br />
% endif
