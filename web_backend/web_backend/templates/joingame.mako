# -*- coding: utf-8 -*- 
<%inherit file="menu.mako"/>

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
<%
  num_players = len(game.players)
%>

<tr>
<td rowspan="${num_players}">&nbsp;</td>
<td rowspan="${num_players}"></td>
<td rowspan="${num_players}"></td>
<td rowspan="${num_players}"></td>
<td rowspan="${num_players}"></td>
<td></td>
<td></td>
<td rowspan="${num_players}"></td>
</tr>


% endfor

% else:
<tr><td colspan="8">There is currently no open game awaiting for players.</td></tr>
<tr><td colspan="8">&nbsp;</td></tr>
% endif

<h2>Private games</h2>

<table>
</table>
