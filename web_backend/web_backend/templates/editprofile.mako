# -*- coding: utf-8 -*- 
<%inherit file="menu.mako"/>

<h1>Edit profile</h1>

<form action="${request.route_url('editprofile')}" method="post">

  Name: ${player.name}<br />

  <label>Email</label>
  <input name="email" type="text" maxlength="100"
   placeholder="Email" value="${player.email}"><br />

  <label>Password</label>
  <input name="password" type="password" maxlength="100"
   placeholder="Password"><br />

  <label>Repeat Password</label>
  <input name="password2" type="password" maxlength="100"
   placeholder="Repeat password"><br />

  <label>Time Zone</label>
  <select name="timezone">
    % for tzId, tzName in timezones.list_tz:
      %if tzId == player.timezone:
        <option value="${tzId}" selected>${tzName}</option>
      %else:
        <option value="${tzId}">${tzName}</option>
      %endif
    % endfor
  </select>
  <br />

  <input type="submit" name="update" value="UPDATE" class="button">
</form>
