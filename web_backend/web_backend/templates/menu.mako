# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

% if auth == True:

<% 
    gm =  request.registry.settings['gm']
    player = gm.getPlayer(request.session['player_id'])
%>

Logged as ${player.name}<br />
<a href="${request.route_url('home')}">Home</a>/
<a href="${request.route_url('mygames')}">My games</a>/
<a href="${request.route_url('joingame')}">Join game</a>/
<a href="${request.route_url('creategame')}">Create new game</a>/
<a href="${request.route_url('editprofile')}">Edit profile</a>/
<a href="${request.route_url('logout')}">logout</a>
<br />

${next.body()}

% else:

<h1>Welcome to Eclipse Board Game Online version</h1>

<a href="${request.route_url('register')}">New user ?</a><br />

<%
  email = request.POST.get('email')
  if not email: email = ""
%>

<form action="${request.route_url('login')}" method="post">
  <input type="text" maxlength="100" name="email"
   placeholder="Email" value="${email}"><br />
  <input type="password" maxlength="100" name="password"
   placeholder="Password"><br />
  <input type="submit" name="add" value="LOGIN" class="button">
</form>

% endif
