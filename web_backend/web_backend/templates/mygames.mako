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
  <th>Last play</th>
  <th>Turn</th>
  <th>State</th>
  <th>Players</th>
  <th>Race</th>
  <th>Extensions</th>
</tr>

% if len(my_games) != 0:
  % for game in my_games:

<%
    web_player = gm.get_player(game.creator_id)
    game_player = game.cur_state.get_player(game.creator_id)
%>

<tr>
  <td rowspan="${game.num_players}">&nbsp;</td>
  <td rowspan="${game.num_players}">${game.id_}</td>
  <td rowspan="${game.num_players}">${game.name}</td>
  <td rowspan="${game.num_players}">${game.level}</td>
  <td rowspan="${game.num_players}">${game.num_players}</td>
  <td rowspan="${game.num_players}">${game.start_date}</td>
  <td rowspan="${game.num_players}">${game.last_play}</td>
  <td rowspan="${game.num_players}">${game.cur_state.cur_turn}</td>
  <td rowspan="${game.num_players}">${game.cur_state.id_}</td>
  <td>${web_player.name}</td>
    % if game_player is None:
  <td>unassigned yet</td>
    % else:
  <td>${game_player.race}</td>
    % endif
  <td rowspan="${game.num_players}">/
    % for ext in game.extensions:
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
            game_player = game.cur_state.get_player(game.players_ids[i])
%>
<tr>
  <td>${web_player.name}</td>
          % if game_player is None:
  <td>unassigned yet</td>
          % else:
  <td>${game_player.race}</td>
          % endif
</tr>
        % endif
      % else:
<tr>
  <td>not joined</td>
  <td>unassigned yet</td>
</tr>
      % endif
    % endfor

  % endfor

% else:
<tr>
  <td colspan="12">You currently have no games in progress.</td>
</tr>
% endif
</table>
