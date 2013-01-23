# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Register</h1>

<%
  name = request.POST.get('name')
  if not name: name = ""
  email = request.POST.get('email')
  if not email: email = ""
%>

<form action="${request.route_url('register')}" method="post">

  <input name="name" type="text" maxlength="100"
   placeholder="Name" value="${name}"><br />

  <input name="email" type="text" maxlength="100"
   placeholder="Email" value="${email}"><br />

  <input name="password" type="password" maxlength="100"
   placeholder="Password"><br />

  <input name="password2" type="password" maxlength="100"
   placeholder="Repeat password"><br />

  <label>Time Zone</label>
  <select name="timezone">
    % for tzId, tzName in timezones.list_tz:
    <option value="${tzId}">${tzName}</option>
    % endfor
  </select>
  <br />

  <input type="submit" name="add" value="ADD" class="button">
</form>
