# -*- coding: utf-8 -*- 
<%inherit file="menu.mako"/>

<% 
gm =  request.registry.settings['gm']
%>


<h1>Join game</h1>

<table>
<tr><td colspan="8">Open games</td></tr>
<tr><td colspan="8">&nbsp;</td></tr>

<tr>
<th>&nbsp;</th>
<th>#</th>
<th>Name</th>
<th>Level</th>
<th># Players</th>
<th>Players</th>
<th>Time zone</th>
<th>Start date</th>
</tr>

% if len(pub_games) != 0:
  % for game in pub_games:

<tr>
<td rowspan="${game.num_players}">&nbsp;</td>
<td rowspan="${game.num_players}">${game.id_}</td>
<td rowspan="${game.num_players}">${game.name}</td>
<td rowspan="${game.num_players}">${game.level}</td>
<td rowspan="${game.num_players}">${game.num_players}</td>

<%
    player = gm.getPlayer(game.creator_id)
    tz_desc = timezones.dict_tz[player.timezone]
%>
<td>${player.name}</td>
<td>${tz_desc}</td>
<td rowspan="${game.num_players}"></td>
</tr>

    % for i in range(1, game.num_players):
      % if i < len(game.players_ids):
<%
        player = gm.getPlayer(game.players_ids[i])
        tz_desc = timezones.dict_tz[player.timezone]
%>
<tr>
<td>${player.name}</td>
<td>${tz_desc}</td>
</tr>
      % else:
<tr>
<td><a>Join</a></td>
<td></td>
</tr>
      % endif
    % endfor

  % endfor

% else:
<tr><td colspan="8">There is currently no open game awaiting for players.</td></tr>
<tr><td colspan="8">&nbsp;</td></tr>
% endif

<tr><td colspan="8">Private games</td></tr>
<tr><td colspan="8">&nbsp;</td></tr>

<tr>
<th>&nbsp;</th>
<th>#</th>
<th>Name</th>
<th>Level</th>
<th># Players</th>
<th>Players</th>
<th>Time zone</th>
<th>Start date</th>
</tr>

% if len(priv_games) != 0:
  % for game in priv_games:

<tr>
<td rowspan="${game.num_players}">&nbsp;</td>
<td rowspan="${game.num_players}">${game.id_}</td>
<td rowspan="${game.num_players}">${game.name}</td>
<td rowspan="${game.num_players}">${game.level}</td>
<td rowspan="${game.num_players}">${game.num_players}</td>

<%
    player = gm.getPlayer(game.creator_id)
%>
<td>${player.name}</td>
<td>${player.timezone}</td>
<td rowspan="${game.num_players}"></td>
</tr>

    % for i in range(1, game.num_players):
      % if i < len(game.players_ids):
<%
        player = gm.getPlayer(game.players_ids[i])
%>
<tr>
<td>${player.name}</td>
<td>${player.timezone}</td>
</tr>
      % else:
<tr>
<td><a>Join</a></td>
<td></td>
</tr>
      % endif
    % endfor

  % endfor

% else:
<tr><td colspan="8">There is currently no private game awaiting for players.</td></tr>
<tr><td colspan="8">&nbsp;</td></tr>
% endif


</table>
