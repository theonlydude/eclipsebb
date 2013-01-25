"""
Copyright (C) 2012  Emmanuel Gorse, Adrien Durand

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# an hex has a number of planets, a number id, wormholes, an influence
# token.
# it can also be of a special type, like in the extension
class Hex:
    def __init__(self, id_, wormholes, planets):
        self.id_ = id_
        self.influence = None
        # boolean tuple (true, false, true, true, false, false)
        self.wormholes = wormholes
        self.planets = planets

        # can be rotated when put in game
        self.rotation = None

# a planet 
class Planet:
    def __init__(self, id_, slots):
        self.id_ = id_
        self.slots = slots

# a population slot
class PopSlot:
    def __init__(self, id_, type_, star):
        self.id_ = id_
        # type can be: money, science, material, grey
        self.type_ = type_
        # is the slot starred
        self.star = star
        # the player having a pop cube on the slot
        self.popOwner = None

class Player:
    def __init__(self, name):
        pass

    def setRace(self, race):
        pass

class Ship:
    def __init__(self, id_):
        pass

class Research:
    def __init__(self, id_):
        pass

class ShipUpgrade:
    def __init__(self, id_):
        pass

class Orbital:
    def __init__(self, id_):
        pass

class Monolith:
    def __init__(self, id_):
        pass

class Influence:
    def __init__(self, id_):
        pass

class SettlerShip:
    def __init__(self, id_):
        pass

class GameState:
    """
    the state of the game, to be sent to the client with json:
     -players
     -hexes
     -player ships
     -ancient ships
     -extensions flags
     -researchs
    """
    def __init__(self, id_):
        self.id_ = id_

        # turn 0:
        # 0. installation phase: only once per game, when players
        #                        choose their race

        # turns 1-9, classic turns;
        # 1. action phase
        # 2. battle phase
        # 3. upkeep phase
        # 4. cleanup phase

        # 5. end of the game phase: only once per game
        self.curPhase = 0

        # the game is played in nine turns
        self.curTurn = 0

        # True when the last turn is finished
        self.isFinished = False

        # in a state, store only the actions to apply in order to
        # transition to the next state
        self.curActions = []

    def nextId(self):
        """ every objects in a state must have an uniq id """
        self.topId += 1
        return self.topId

    def exportToJson(self):
        pass

    def isActionValid(self, action):
        pass

    def applyAction(self, action):
        pass


class Action:
    """
    Everything a player does has to be a player action which is applied
    to a game state to generate a new state.
    A player turn can be made of more than one action.
    The same goes to the game, which has to generate an action to
    change a game state.
    This way it's easier to add unit tests to the code.

    All actions can be simplified to:
      move element#xxx from zone#yyy to zone#zzz
    with element being the id of:
     -ship
     -population cube
     -influence token
     -technology tile
     -player tile
    and zone being the id of:
     -technology tiles bag
     -player ship reserve
     -hex
     -ship amelioration slot

    exception#1: the science/money/material tokens don't have 40
    zones for each players. when they move the zones given in the
    action are the old value and the new value.

    exception#2: there's a special action to end a turn

    During a player/game turn, the state keeps track of the available
    science/material/money for the next actions.

    Example:
     player turn:
      -move influence token from influence track to action slot "buy"
      -move science token from 14 to 11
      -move material token from 5 to 6 (use the three sciences
       available to exchange it to 1 material)
      -move material token from 6 to 0
      -move interceptor from player reserve to hex#xxx
      -move interceptor from player reserve to hex#yyy (use the six
       available materials to buy two interceptors)
      -end turn
     game cleanup turn:
      -add newly drawn technology tiles to the supply board
      -move player#1 influence token#1 from action track to influence track
      -...
      -move player#n influence token#m from action track to influence track
      -move player#1 cube#1 from graveyard to population track
      -...
      -move player#n cube#m from graveyard to population track
      -turn player#1 colony ship#1 face up (move it from player used
       slot to available slot)
      -...
      -turn player#n colony ship#m face up
      -turn player#1  face up
      -...
      -turn player#n  face up
      -move round marker one step forward
      -end turn
    """

    def __init__(self, element, oldZone, newZone):
        self.element = element
        self.zone1 = zone1
        self.zone2 = zone2



    

class Extension:
    """ extension interface """
    def __init__(self):
        self.hooks = {}

    def addHooks(self):
        """
        every new rules in the ancient extension is optional, so add
        only hooks corresponding to the rules selected by the players. 
        """
        pass

class AncientExtension:
    def __init__(self):
        pass

class NovaExtension:
    def __init__(self):
        pass


class Sanctuary:
    def __init__(self, id_):
        pass

class Development:
    def __init__(self, id_):
        pass

class Wormhole:
    def __init__(self, id_):
        pass
