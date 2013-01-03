# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Log in</h1>

<form action="${request.route_url('login')}" method="post">
  <input type="text" maxlength="100" name="email">
  <input type="password" maxlength="100" name="password">
  <input type="submit" name="add" value="ADD" class="button">
</form>
