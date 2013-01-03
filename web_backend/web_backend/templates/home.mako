# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Welcome to Eclipse Board Game Web version</h1>

Project: ${project}<br />

<a href="${request.route_url('login')}">login</a>

% if 'auth' in request.session:
AUTHENTICATE !
% else:
NOT AUTHENTICATE !
% endif
