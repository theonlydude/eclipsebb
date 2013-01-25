# -*- coding: utf-8 -*- 
<%inherit file="menu.mako"/>

<% 
gm =  request.registry.settings['gm']
%>

<h1>My games</h1>

<table>
<tr><td colspan="11">Started games</td></tr>

<tr>
<th>&nbsp;</th>
<th>#</th>
<th>Name</th>
<th># Players</th>
<th>Level</th>
<th>Play as</th>
<th>Start date</th>
<th>Last play</th>
<th>Turn</th>
<th>State</th>
<th>Players</th>
<th>Extensions</th>
</tr>

<!--
id_
name
num_players
level
getPlayer(player_id).getRace()
start_date
last_play
cur_turn
cur_state
players_ids
extensions
-->

% if len(my_games) != 0:

  % for game in my_games:
    ${game.name}
  % endfor

% else:
You currently have no games in progress.
% endif
