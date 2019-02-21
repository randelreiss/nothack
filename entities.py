import common
import random
from common import *
from tileengine import TileSprite

try:
	import pygame.mixer as mixer
except ImportError:
	import android.mixer as mixer

mixer.init(44100, -16, 2, 2048)
localVol = common.globalVolume

# sound files
localSoundsDir = common.soundsDirectory
soundFight = mixer.Sound(soundsDirectory+'Hit_LargeAxeImpactStone1.ogg')
soundHumanDie = mixer.Sound(soundsDirectory+'Male_LS_B_Death02.ogg')
soundItemPickup = mixer.Sound(soundsDirectory+'Pickup_Armour_FlakVest2.ogg')
soundPlayerDeath = mixer.Sound(soundsDirectory+'fatmonster_deathroar2.ogg')
soundGameOver = mixer.Sound(soundsDirectory+'magic_spell_cloak04.ogg')
soundStaffTaken = mixer.Sound(soundsDirectory+'magic_crystalenergyshot3.ogg')

EQUIPPABLE = ['weapon', 'armor']

class Character(TileSprite):
    def __init__(self, imageFilename, parent, x, y, stats, isPlayer = 0):
        TileSprite.__init__(self, imageFilename, parent, x, y, isPlayer)
        self.isPlayer = isPlayer
        self._parent = parent
        self.money = 0
        self.level = stats['level']
        self.gender = 'Male'
        self.race = 'Human'
        self.charClass = 'Fighter'
        self.str = stats['str']
        self.dex = stats['dex']
        self.int = stats['int']
        self.xp = 0
        self.inventory = []
        self.equipped = {
            'weapon' : None,
            'armor'  : None,
            }
        self.toHit = float(self.dex) / 20.0
        self.toDodge = float(self.dex) / 80.0
        self.hp = self.maxhp = 0
        self.mp = self.maxmp = 0
        for x in range(self.level):
            self.levelUp()

    def damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self._parent.dead(self)
            if not self.isPlayer:
                localPlayer = self._parent.getPlayer()
                # As Player level, earns gradually less percentage of slain XP
                xpMod = 100 - localPlayer.level
                localPlayer.xp += int((float(xpMod) / 100) * self.xp)
            return 1
        return 0

    def deequip(self, type):
        item = self.equipped.get(type, None)
        if(item):
            if(item.deequip(self)):
                self.message( "The %s has been un-equipped" % item.getName())
                return 1
            self.message("You cannot un-equip the %s" % item.getName())
        return 0

    def drop(self, item):
        okay = 1
        # if it's equipped, de-equip it
        for type in self.equipped.keys():
            if self.equipped[type] == item:
                if(not self.deequip(type)):
                    okay = 0
        if(okay and item.drop(self)):
            self.inventory.remove(item)
            self._parent.addSprite(item)
            self.message("You drop the %s" % item.getName())
            return 1
        self.message("The %s cannot be dropped" % item.getName())
        return 0

    def dropAll(self):
        for item in self.inventory[:]:
            self.drop(item)

    def equip(self, item):
        if(item.equip(self)):
            type = item.getType()
            if self.equipped[type]:
                if(self.deequip(type)):
                    self.equipped[type] = item
                    self.message("The %s is now equipped" % item.getName())
                    return 1
            else:
                self.equipped[type] = item
                self.message("The %s is now equipped" % item.getName())
                return 1
        self.message("You cannot equip the %s" % item.getName())
        return 0

    def giveItem(self, item):
        if(item.take(self)):
            self.inventory.append(item)
            try:
                self._parent.removeSprite(item)
            except ValueError:
                pass
            return 1
        return 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.maxhp:
            self.hp = self.maxhp

    def hit(self, other):
        # see if other connects
        toHit = other.toHit - self.toDodge
        rannum = random.random()
        if rannum < toHit:
            # see what damage it does
            try:
                weapon = other.equipped['weapon']
                dmg = int(random.uniform(weapon.damageMin,
                                         weapon.damageMax +1))
            except KeyError:
                # no weapon
                dmg = 15
            self.message("You are hit for %d damage!" % dmg)
            other.message("You hit for %d damage!" % dmg)
            if(self.damage(dmg)):
                self.message("You die...")
                #other.message("The Adventurer dies!")
                localStats = (self.level, self.gender,
                              self.race, self.charClass)
                other.message("A Level %d %s %s %s Adventurer dies!" % localStats)
                soundHumanDie.set_volume(localVol * 1)
                soundHumanDie.play()
        else:
            self.message("The Adventurer Misses!")
            other.message("You miss!")
            return 0

    def levelUp(self):
        self.maxhp += self.str / 4 + random.random() * 5
        self.maxmp += self.int / 4 + random.random() * 5
        self.hp = self.maxhp
        self.mp = self.maxmp

    def message(self, msg):
        if self.isPlayer:
            self._parent.getParent().message(msg)

    def move(self, dx, dy):
        newX = self._x + dx
        newY = self._y + dy
        if self._parent.moveOk(self, newX, newY):
            self._x += dx
            self._y += dy
            return 1
        return 0

    def occupied(self, intruder):
        return self.hit(intruder)

    def remove(self, item, msg = "You sell the %s"):
        okay = 1
        # if it's equipped, de-equip it
        for type in self.equipped.keys():
            if self.equipped[type] == item:
                if(not self.deequip(type)):
                    okay = 0
        if(okay and item.drop(self)):
            self.inventory.remove(item)
            self.message(msg % item.getName())
            return 1
        self.message("The %s cannot be used" % item.getName())
        return 0

    def use(self, item):
        if(item.use(self)):
            self.remove(item, "You have used up the %s")

class Item(TileSprite):
    def __init__(self, imageFilename, parent, x, y, stats):
        TileSprite.__init__(self, imageFilename, parent, x, y)
        self._stats = stats

    def equip(self, character):
        return 1

    def price(self):
        return int(random.uniform(50, 5000))

    def deequip(self, character):
        return 1

    def drop(self, character):
        self._x = character.getXY()[0]
        self._y = character.getXY()[1]
        return 1

    def getType(self):
        return self._stats.get('type',"generic")

    def getName(self):
        try:
            return self._stats['name']
        except KeyError:
            return None

    def occupied(self, character):
        if(character.giveItem(self)):
            character.message("You pick up the %s" % self.getName())
            return 1
        else:
            character.message("You cannot have the %s" % self.getName())
            return 0

    def take(self, character):
        return 1

    def use(self, character):
        return 0

class Weapon(Item):
    def __init__(self, imageFilename, parent, x, y, stats):
        Item.__init__(self, imageFilename, parent, x, y, stats)
        self._toHitBonus = float(stats.get('toHit', 0)) / 100.0
        self.damageMin = stats.get('damageMin', 0)
        self.damageMax = stats.get('damageMax', 0)
        self._stats['type'] = 'weapon'

    def equip(self, character):
        character.toHit += self._toHitBonus
        return 1

    def deequip(self, character):
        character.toHit -= self._toHitBonus
        return 1

    def getType(self):
        return 'weapon'

class Armor(Item):
    def __init__(self, imageFilename, parent, x, y, stats):
        Item.__init__(self, imageFilename, parent, x, y, stats)
        self._absorb = stats.get('absorb', 0)
        self._toDodgeBonus = float(stats.get('toDodge', 0)) / 100.0

    def equip(self, character):
        character.toDodge += self._toDodgeBonus
        return 1

    def deequip(self, character):
        character.toDodge -= self._toDodgeBonus
        return 1

    def getType(self):
        return 'armor'

class Staff(Item):
    def __init__(self, imageFilename, parent, x, y, stats):
        Item.__init__(self, imageFilename, parent, x, y, stats)

    def equip(self, character):
        return 0

    def take(self, character):
        if character == self._parent.getPlayer():
            msg = ("After all this trouble, you don't even want the "+
                   "stupid thing.")
            character.message(msg)
            return 0
        return 1

    def getType(self):
        return 'staff'

class Potion(Item):
    def __init__(self, imageFilename, parent, x, y, stats):
        Item.__init__(self, imageFilename, parent, x, y, stats)
        self._healingMin = stats.get('healingMin', 0)
        self._healingMax = stats.get('healingMax', 0)

    def use(self, character):
        amount = int (random.uniform(self._healingMin,
                                     self._healingMax))

        character.heal(amount)
        character.inventory.remove(self)
        character.message("You are healed for %d points" % amount)

class Entry(TileSprite):
    def __init__(self, imageFilename, parent, x, y):
        TileSprite.__init__(self, imageFilename, parent, x, y)
        self._player = parent.getPlayer()

    def occupied(self, intruder):
        if intruder == self._player:
            intruder.message("You cannot leave the staff unguarded!")
            return 0
        return 1
