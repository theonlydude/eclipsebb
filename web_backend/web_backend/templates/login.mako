# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Log in</h1>

<%
  email = request.POST.get('email')
  if not email: email = ""
%>

<form action="${request.route_url('login')}" method="post">
  <input type="text" maxlength="100" name="email"
   placeholder="Email" value="${email}"><br />
  <input type="password" maxlength="100" name="password"
   placeholder="Password"><br />
  <input type="submit" name="add" value="LOGIN" class="button">
</form>

<a href="${request.route_url('home')}">Return to home</a>
