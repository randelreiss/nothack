import random
import entities
import inventory
from tileengine import TileEngine

class BreakIt(Exception): pass

class Node:
    def __init__(self, tileMap, location, parent, searchedlist,
                 depth):
        self.map = tileMap
        self.searched = searchedlist
        self.x = location[0]
        self.y = location[1]
        self.location = location
        self.parent = parent
        self.depth = depth
        self.cost = depth

    def __cmp__(self, other):
        if(other):
            if self.cost > other.cost:
                return 1
            elif self.cost < other.cost:
                return -1
            else:
                return 0
        else: return 1

    def createChild(self, nextX, nextY):
        self.searched.append( (nextX, nextY) )
        return Node( self.map, (nextX, nextY), self,
                     self.searched, self.depth+1)

    def estCost(self, goal):
        dx = self.x - goal[0]
        dy = self.y - goal[1]
        dist = math.sqrt(dx * dx + dy * dy)
        return dist + self.cost

    def expand(self):
        children = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nextX = self.x +dx
                nextY = self.y +dy
                parent = self.parent
                if nextX == self.x and nextY == self.y:
                    continue
                if parent and nextX == parent.x and nextY == parent.y:
                    continue
                if not self.map[nextY][nextX] in TileEngine.passable:
                    continue
                if (nextX, nextY) in self.searched:
                    continue
                children.append(self.createChild(nextX, nextY))
        return children

    def isGoal(self, goal):
        if (self.x == goal[0] and
            self.y == goal[1]): return 1
        return 0

def getPath(tileMap, startLocation, endLocation):
    searched = [ startLocation ]
    nodes = [ Node(tileMap, startLocation, None, searched, 0) ]
    node = None
    while nodes:
        node = nodes.pop(0)
        if node.isGoal(endLocation):
            break
        nodes.extend(node.expand())
        nodes.sort()
    path = [ node.location ]
    while(node.parent != None):
        path.append(node.parent.location)
        node = node.parent
    path.reverse()
    return path

class Adventurer(entities.Character):
    def __init__(self, imageFilename, parent, x, y, stats):
        entities.Character.__init__(self, imageFilename, parent, x, y,
                                    stats)
        self.route = []
        self.hasStaff = 0
        self._started = (x, y)

    def occupied(self, intruder):
        player = self._parent.getPlayer()
        if intruder == player:
            # we're under attack!
            return self.hit(intruder)
        elif intruder.hasStaff:
            return self.hit(intruder)
        elif self.hasStaff:
            return self.hit(intruder)

    def turn(self):
        if not self.route:
            if self.hasStaff:
                self.route = getPath(self._parent.getMap(),
                                     (self._x, self._y),
                                     self._started)
                self.route.pop(0)
            else:
                staffX = self._parent.getStaff().getXY()[0]
                staffY = self._parent.getStaff().getXY()[1]
                self.route = getPath(self._parent.getMap(),
                                     (self._x, self._y),
                                     (staffX, staffY))
                self.route.pop(0)
        if(self.route != []):
            routeX = self.route[0][0]
            routeY = self.route[0][1]
            try:
                for dx in range(-1, 2):
                    nextX = self._x + dx
                    for dy in range(-1, 2):
                        nextY = self._y + dy
                        if (nextX == routeX and
                            nextY == routeY):
                            if(self.move(dx, dy)):
                                self.route.pop(0)
                                raise BreakIt
            except BreakIt:
                pass

        if not self.hasStaff:
            for item in self.inventory:
                if item.getType() == 'staff':
                    self.hasStaff = 1
        else:
            if (self._x == self._started[0] and
                self._y == self._started[1]):
                msg = ("The staff has escaped your guardianship - "+
                       "You have failed.")
                self._parent.getDriver().start(
                 inventory.GameOver(self._parent.getDriver(),
                                    None,
                                    None,
                                    msg))

def createAdventurer(entrances, engine):
    chosen = random.choice(entrances)

    gender = [
        'Male', 'Male', 'Male',
        'Male', 'Male',
        'Female', 'Female',
        'Female' ]
    race = [
        'Human', 'Human', 'Human',
        'Elf', 'Elf',
        'Dwarf', 'Dwarf',
        'Halfling' ]
    charClass = [
        'Fighter', 'Fighter', 'Fighter',
        'Warrior', 'Warrior',
        'Rogue', 'Theif',
        'Wizard' ]
    weapons = [
        '+%d Bastard Sword', '+%d Long Sword', '+%d Short Sword',
        '+%d Steel Dagger', '+%d Daedric Long Sword',
        '+%d Rusted Sword', '+%d Sword-shaped Mace',
        '+%d Ordinary Sword' ]
    armor = [
        '+%d Leather Armor', '+%d Blessed Plate Mail',
        '+%d Chainmail Armor', '+%d Angelic Plate Mail',
        '+%d Adventurer\'s clothing', '+%d Birthday Suit',
        '+%d Nondescript Armor' ]
    weaponPlus = int(random.uniform(1, 13))
    armorPlus = int(random.uniform(1, 13))
    weaponStats = {
        'name' : random.choice(weapons) % weaponPlus,
        'damageMin' : 15 + weaponPlus,
        'damageMax' : 65 + weaponPlus,
        'toHit' : weaponPlus,
        }
    armorStats = {
        'name' : random.choice(armor) % armorPlus,
        'absorb' : 10 + armorPlus,
        'toDodge' : 10 + armorPlus,
        }
    localXP = int(random.uniform(20, 30)) * 100
    randomStats = {
        'level' : localXP / 100,
        'str' : int(random.uniform(10, 20)),
        'dex' : int(random.uniform(10, 20)),
        'int' : int(random.uniform(10, 20)),
        }
    x = chosen.getXY()[0]
    y = chosen.getXY()[1]
    adventurer = Adventurer('adventurer.png', engine, x, y, randomStats)
    adventurer.gender = random.choice(gender)
    adventurer.race = random.choice(race)
    adventurer.charClass = random.choice(charClass)
    weapon = entities.Weapon('sword.png', engine, 0, 0, weaponStats)
    armor = entities.Armor('armor.png', engine, 0, 0, armorStats)
    adventurer.giveItem(weapon)
    adventurer.giveItem(armor)
    adventurer.equip(weapon)
    adventurer.equip(armor)
    return adventurer
