# -*- coding: utf-8 -*- 
<%inherit file="menu.mako"/>

% if len(attributes['running_games']) > 0:

  % for game in attributes['running_games']:
    ${game.name}
  % endfor

% else:
  You currently have no current game
% endif
