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
    cur_state INTEGER,
    ended BOOL NOT NULL,
    FOREIGN KEY(cur_state) REFERENCES state(id)
);

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
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

-- insert available extensions
INSERT OR IGNORE INTO extensions (name, desc) VALUES('rare_technologies', 'enable rare technologies');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('developments', 'enable developments');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('ancient_worlds', 'enable ancient worlds');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('secret_world', 'put unused ancient worlds in the heap');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('ancient_sdcg', 'enable ancient SDCG');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('ancient_hives', 'enable ancients hives');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('warp_portals', 'enable warp portals');
INSERT OR IGNORE INTO EXTENSIONS (name, desc) VALUES('new_discoveries', 'add new discoveries');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('predictable_technologies', 'enable predictable technologies');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('turn_order', 'enable direction of play');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('alliances', 'enable alliances');
INSERT OR IGNORE INTO extensions (name, desc) VALUES('small_galaxy', 'enable small galaxy (three players only');
