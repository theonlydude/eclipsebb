--Copyright (C) 2012-2013  manu, adri
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

-- test games --
-- not started
INSERT INTO games (id, name, started, ended, level, cur_state_id, private,
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

-- in-progress game
INSERT INTO games (id, name, started, ended, level, cur_state_id, private,
                   password, start_date, last_play, num_players, creator_id)
VALUES(2, 'my in-progress test game', 1, 0, 2, -1, 0, '',
       '2006-06-06 06:06:06.666666', '2006-06-16 06:06:06.666666', 2, 2);

INSERT INTO games_players (game_id, player_id)
VALUES(2, 1);
INSERT INTO games_players (game_id, player_id)
VALUES(2, 2);

INSERT INTO games_extensions (game_id, extension_id)
VALUES(2, 1);
INSERT INTO games_extensions (game_id, extension_id)
VALUES(2, 3);
INSERT INTO games_extensions (game_id, extension_id)
VALUES(2, 5);

-- ended game
INSERT INTO games (id, name, started, ended, level, cur_state_id, private,
                   password, start_date, last_play, num_players, creator_id)
VALUES(3, 'my ended test game', 1, 1, 2, -1, 0, '',
       '2006-06-06 06:06:06.666666', '2006-06-16 06:06:06.666666', 2, 1);

INSERT INTO games_players (game_id, player_id)
VALUES(3, 1);
INSERT INTO games_players (game_id, player_id)
VALUES(3, 2);

INSERT INTO games_extensions (game_id, extension_id)
VALUES(3, 1);
INSERT INTO games_extensions (game_id, extension_id)
VALUES(3, 3);
INSERT INTO games_extensions (game_id, extension_id)
VALUES(3, 5);

-- private not started game
INSERT INTO games (id, name, started, ended, level, cur_state_id, private,
                   password, start_date, last_play, num_players, creator_id)
VALUES(4, 'my private test game', 0, 0, 3, -1, 1, 'test',
       '2006-06-06 06:06:06.666666', NULL, 3, 1);

INSERT INTO games_players (game_id, player_id)
VALUES(4, 1);
INSERT INTO games_players (game_id, player_id)
VALUES(4, 2);

INSERT INTO games_extensions (game_id, extension_id)
VALUES(4, 4);
INSERT INTO games_extensions (game_id, extension_id)
VALUES(4, 5);
INSERT INTO games_extensions (game_id, extension_id)
VALUES(4, 6);


-- default empty states
INSERT INTO "state" VALUES(NULL,1,X'800363656E67696E652E646174615F74797065730A47616D6553746174650A7100298171017D710228580B0000006E756D5F706C617965727371034B02580300000069645F71044AFFFFFFFF58080000006375725F7475726E71054B00580B0000006375725F616374696F6E7371065D7107580D000000706C61796572735F6F7264657271085D71095807000000706C6179657273710A7D710B580A0000007475726E5F7068617365710C4E580A00000067616D655F7068617365710D4B0075622E');

INSERT INTO "state" VALUES(NULL,2,X'800363656E67696E652E646174615F74797065730A47616D6553746174650A7100298171017D710228580B0000006E756D5F706C617965727371034B02580300000069645F71044AFFFFFFFF58080000006375725F7475726E71054B00580B0000006375725F616374696F6E7371065D7107580D000000706C61796572735F6F7264657271085D71095807000000706C6179657273710A7D710B580A0000007475726E5F7068617365710C4E580A00000067616D655F7068617365710D4B0075622E');

INSERT INTO "state" VALUES(NULL,3,X'800363656E67696E652E646174615F74797065730A47616D6553746174650A7100298171017D710228580B0000006E756D5F706C617965727371034B02580300000069645F71044AFFFFFFFF58080000006375725F7475726E71054B00580B0000006375725F616374696F6E7371065D7107580D000000706C61796572735F6F7264657271085D71095807000000706C6179657273710A7D710B580A0000007475726E5F7068617365710C4E580A00000067616D655F7068617365710D4B0075622E');

INSERT INTO "state" VALUES(NULL,4,X'800363656E67696E652E646174615F74797065730A47616D6553746174650A7100298171017D710228580B0000006E756D5F706C617965727371034B02580300000069645F71044AFFFFFFFF58080000006375725F7475726E71054B00580B0000006375725F616374696F6E7371065D7107580D000000706C61796572735F6F7264657271085D71095807000000706C6179657273710A7D710B580A0000007475726E5F7068617365710C4E580A00000067616D655F7068617365710D4B0075622E');
