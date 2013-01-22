# -*- coding: utf-8 -*- 
<%inherit file="menu.mako"/>

<h1>Create new game</h1>

<form action="${request.route_url('creategame')}" method="post">

<table>

<tr><td>Name</td><td>
  <input name="name" type="text" maxlength="100"
   placeholder="Name" value="${player.name}'s game">
</td></tr>

<tr><td># players</td><td>
  <input name="num_players" type="radio" value="2" checked>2
  <input name="num_players" type="radio" value="3">3
  <input name="num_players" type="radio" value="4">4
  <input name="num_players" type="radio" value="5">5
</td></tr>

<tr><td>Players</td>

<td>
  <select name="player0">
    <option value="${player.id_}">${player.name}</option>
  </select>
</td><tr>

% for num in range(1,5):
<tr><td></td><td>
  <select name="player${num}">
    <option value="-1" selected>----- Free -----</option>
    % for id, name in players_infos:
    <option value="${id}">${name}</option>
    % endfor
  </select>
</td>
% endfor

<tr><td>Level</td><td>
  <input name="level" type="radio" value="1" checked>1
  <input name="level" type="radio" value="2">2
  <input name="level" type="radio" value="3">3
  <input name="level" type="radio" value="4">4
</td></tr>

<tr><td>Options</td><td>
  <input name="private" type="checkbox">Private game (Only players who know
the password may join that game)
</td></tr>

<tr><td></td><td>
  <input name="password" type="password" maxlength="100"
   placeholder="Password">
</td></tr>
<tr><td></td><td>
  <input name="password2" type="password" maxlength="100"
   placeholder="Repeat password">
</td></tr>

<tr><td>Extensions</td><tr>
    
    % for id, name, desc in extensions_infos:
<tr><td></td><td>
    <input name="${name}" type="checkbox">${desc}
</td>
    % endfor

</table>
  <input type="submit" name="add" value="ADD" class="button">
</form>
