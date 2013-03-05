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


-- create all the tables in the schema
-- put default values for extensions

CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    -- game not started, waiting for players
    started BOOL NOT NULL DEFAULT 0,
    -- game ended
    ended BOOL NOT NULL DEFAULT 0,
    -- difficulty
    level INTEGER NOT NULL,
    -- the state id from table state
    cur_state INTEGER DEFAULT -1,
    -- game joined with password
    private BOOL NOT NULL,
    -- only when private game
    password TEXT,
    ---- all dates in UTC
    -- creation date of the game
    start_date TIMESTAMP NOT NULL,
    -- date last action in the game
    last_play TIMESTAMP DEFAULT NULL,
    -- num players for the game
    num_players INTEGER NOT NULL,
    -- game creator id
    creator_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    timezone INTEGER NOT NULL,
    FOREIGN KEY(timezone) REFERENCES timezones(diff)
);

CREATE TABLE IF NOT EXISTS timezones (
    -- diff in minutes
    diff INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS games_players (
    game_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    FOREIGN KEY(game_id) REFERENCES games(id),
    FOREIGN KEY(player_id) REFERENCES players(id)
);

CREATE TABLE IF NOT EXISTS extensions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    desc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS games_extensions (
    game_id INTEGER NOT NULL,
    extension_id INTEGER NOT NULL,
    FOREIGN KEY(game_id) REFERENCES games(id),
    FOREIGN KEY(extension_id) REFERENCES extensions(id)
);

CREATE TABLE IF NOT EXISTS state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    pickle BLOB NOT NULL,
    FOREIGN KEY(game_id) REFERENCES games(id)
);

CREATE TABLE IF NOT EXISTS races (
    name TEXT PRIMARY KEY
);

-- insert available extensions
INSERT OR IGNORE INTO extensions (name, desc) VALUES('rare_technologies', 'enable rare technologies');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('developments', 'enable developments');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('ancient_worlds', 'enable ancient worlds');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('secret_world', 'put unused ancient worlds in the heap');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('ancient_sdcg', 'enable ancient SDCG');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('ancient_hives', 'enable ancients hives');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('warp_portals', 'enable warp portals');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('new_discoveries', 'add new discoveries');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('predictable_technologies', 'enable predictable technologies');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('turn_order', 'enable direction of play');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('alliances', 'enable alliances');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('small_galaxy', 'enable small galaxy (three players only)');

--insert available timezones
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-12:00 (Baker Island, Howland Island)', -720);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-11:00 (SST - Samoa Standard Time)', -660);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-10:00 (HST - Haway-Aleutian Standard Time)', -600);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-09:30 (Marquesas Islands)', -570);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-09:00 (AKST - Alaska Standard Time)', -540);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-08:00 (PST - Pacific Standard Time)', -480);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-07:00 (MST - Mountain Standard Time)', -420);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-06:00 (CST - Central Standard Time)', -360);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-05:00 (EST - Eastern Standard Time)', -300);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-04:30 (Venezuela)', -270);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-04:00 (AST - Atlantic Standard Time)', -240);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-03:30 (NST - Newfoundland Standard Time)', -210);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-03:00 (Saint-Pierre and Miquelon', -180);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-02:00 (Fernando de Noronha)', -120);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC-01:00 (Cape Verde)', -60);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+00:00 (WET - Western European Time)', 0);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+01:00 (CET - Central European Time)', 60);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+02:00 (EET - Eastern European Time)', 120);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+03:00 (Iraq)', 180);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+03:30 (Iran)', 210);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+04:00 (Russia - Moscow Time)', 240);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+04:30 (Afghanistan)', 270);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+05:00 (Kerguelen Islands)', 300);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+05:30 (India, Sri Lanka)', 330);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+05:45 (Nepal)', 345);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+06:00 (Kyrgyzstan)', 360);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+06:30 (Cocos Islands)', 390);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+07:00 (Laos)', 420);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+08:00 (AWST - Australian Western Standard Time)', 480);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+08:45 (Eucla)', 525);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+09:00 (JST - Japan Standard Time)', 540);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+09:30 (ACST - Australian Central Standard Time)', 570);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+10:00 (AEST - Autralian Eastern Standard Time)', 600);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+10:30 (New South Wales)', 630);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+11:00 (New Caledonia)', 660);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+11:30 (Norfolk Island)', 690);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+12:00 (Wallis and Futuna)', 720);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+12:45 (Chatham Islands)', 765);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+13:00 (Tokelau)', 780);
INSERT OR IGNORE INTO timezones (name, diff) VALUES('UTC+14:00 (Line Islands)', 840);

--insert available races
INSERT OR IGNORE INTO races (name) VALUES('human');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
INSERT OR IGNORE INTO races (name) VALUES('');
