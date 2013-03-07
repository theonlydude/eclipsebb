--Copyright (C) 2012  Emmanuel Gorse, Adrien Durand
--
--This program is free software: you can redistribute it and/or modify
--it under the terms of the GNU General Public License as published by
--the Free Software Foundation, either version 3 of the License, or
--(at your option) any later version.
--
--This program is distributed in the hope that it will be useful,
--but WITHOUT ANY WARRANTY; without even the implied warranty of
--MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
--GNU General Public License for more details.
--
--You should have received a copy of the GNU General Public License
--along with this program.  If not, see <http://www.gnu.org/licenses/>.


-- fill the db with test values

-- test players
INSERT INTO players (id, name, email, password, timezone)
VALUES(1, 'test player', 'test@test.com',
       '74cba914888a2adcf37b871d80d83ecbb4b56712', 600);
INSERT INTO players (id, name, email, password, timezone)
VALUES(2, 'test player dup', 'test_dup@test.com',
       '74cba914888a2adcf37b871d80d83ecbb4b56712', 600);

-- test games
INSERT INTO games (id, name, started, ended, level, cur_state, private,
                   password, start_date, last_play, num_players, creator_id)
VALUES(1, 'my test game', 0, 0, 3, -1, 0, '',
       '2006-06-06 06:06:06.666666', NULL, 3, 1);

INSERT INTO games_players (game_id, player_id)
VALUES(1, 1);
INSERT INTO games_players (game_id, player_id)
VALUES(1, 2);

INSERT INTO games_extensions (game_id, extension_id)
VALUES(1, 2);
INSERT INTO games_extensions (game_id, extension_id)
VALUES(1, 4);
INSERT INTO games_extensions (game_id, extension_id)
VALUES(1, 6);
