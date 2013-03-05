# -*- coding: utf-8 -*- 
<%inherit file="menu.mako"/>

<% 
gm =  request.registry.settings['gm']
%>

<h1>My games</h1>

<table>
<tr><td colspan="12">My games</td></tr>

<tr>
<th>&nbsp;</th>
<th>#</th>
<th>Name</th>
<th>Level</th>
<th># Players</th>
<th>Start date</th>
<th>Play as</th>
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

<%
  web_player = gm.get_player(game.creator_id)
  game_player = game.get_player(game.creator_id)
%>

<tr>
<td rowspan="${game.num_players}">&nbsp;</td>
<td rowspan="${game.num_players}">${game.id_}</td>
<td rowspan="${game.num_players}">${game.name}</td>
<td rowspan="${game.num_players}">${game.level}</td>
<td rowspan="${game.num_players}">${game.num_players}</td>
<td rowspan="${game.num_players}">${game.start_date}</td>
<td rowspan="${game.num_players}">${game.last_play}</td>
<td rowspan="${game.num_players}">${game.cur_turn}</td>
<td rowspan="${game.num_players}">${game.cur_state}</td>
<td>${web_player.name}</td>
<td>${game_player.race}</td>
<td rowspan="${game.num_players}">/
    % for ext in game.extensions.values():
${ext} /
    % endfor
</td>
</tr>

    ## loop through remaining players
    % for i in range(game.num_players):
      % if i < len(game.players_ids):
        % if game.players_ids[i] != game.creator_id:
<%
          web_player = gm.get_player(game.players_ids[i])
          game_player = game.get_player(game.players_ids[i])
%>
<tr>
<td>${web_player.name}</td>
<td>${game_player.race}</td>
</tr>
        % endif
      % else:
<tr>
<td><a>Join</a></td>
<td></td>
</tr>
      % endif
    % endfor

  % endfor

% else:
You currently have no games in progress.
% endif
