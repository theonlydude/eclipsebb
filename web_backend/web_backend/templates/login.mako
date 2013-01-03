# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Log in</h1>

<form action="${request.route_url('login')}" method="post">
  <label>Email:</label><br />
  <input type="text" maxlength="100" name="email"><br />
  <label>Password:</label><br />
  <input type="password" maxlength="100" name="password"><br />
  <input type="submit" name="login" value="LOGIN" class="button">
</form>
