import common
import pygame
import random
import inventory
import entities
import ai
from common import *
from pygame.constants import *
from states import State
from tileengine import TileEngine, TileSprite
from entities import Character

try:
	import pygame.mixer as mixer
	android = False
except ImportError:
	import android.mixer as mixer
	android = True

mixer.init(44100, -16, 2, 2048)
localVol = common.globalVolume

# sound files
localSoundsDir = common.soundsDirectory
soundOpenMenu = mixer.Sound(localSoundsDir + 'door_mysticalopen1.ogg')
soundStartUp = mixer.Sound(localSoundsDir + 'Magic_Appear01.ogg')
soundEnemySpawn = mixer.Sound(localSoundsDir + 'Menu_Cancel01.ogg')
soundCoins = mixer.Sound(localSoundsDir + 'Pickup_Coins01.ogg')
# play start up sound
soundStartUp.set_volume(localVol * 1)
soundStartUp.play()

names = [
    'The Mazes of Mania',
    'The Caverns of Chaos',
    'The Tunnels of Terror',
    'The Subterranian Sanctum of Sin',
    'The Secreted Sanctuary of the Staff',
    'The Abode of Abomination',
    'The Dark Dwellings of Doom',
    'The Hellish Hallways of Horror'
    ]

class PlayingGame(State):
    def __init__(self, driver):
        State.__init__(self, driver)
        self._engine = TileEngine('dungeon.map', driver, self)
        self._font = pygame.font.Font(None, 20);
        self._name = random.choice(names)
        self._messages = [ (0, "Welcome to %s" % self._name) ]
        self._deequip = None
        self._visited = None
        mapinfo = self._engine.getMapInfo()
        self._mapinfo = mapinfo
        self.xp = localXP = 3500
        playerStats = {
            'level' : localXP / 100,
            'str' : 30,
            'dex' : 30,
            'int' : 30,
        }
        self.gender = 'Male'
        self.race = 'Human'
        self.charClass = 'Guardian'
        armorStats = {
            'name'    : '+10 Robes of the Guardian',
            'absorb'  : 20,
            'toDodge' : 10
            }
        weaponStats = {
            'name' : '+10 Flaming Angelic Sword',
            'damageMin' : 25,
            'damageMax' : 75,
            'toHit' : 10,
            }
        weapon = entities.Weapon( 'sword.png',
                                self._engine,
                                0, 0,
                                weaponStats)
        armor = entities.Armor('armor.png',
                                self._engine,
                                0, 0,
                                armorStats)
        self._player = Character('player.png', self._engine,
                                 mapinfo['startx'],
                                 mapinfo['starty'],
                                 playerStats, 1)
        self._player.giveItem(weapon)
        self._player.equip(weapon)
        self._player.giveItem(armor)
        self._player.equip(armor)

        self._engine.addSprite(self._player)
        self._engine.centerOn(self._player)

        staffStats = {
            'name' : 'Terrifyingly Powerful Staff of Glok-Yar'
            }
        self._staff = entities.Staff('staff.png', self._engine,
                                     mapinfo['staffx'],
                                     mapinfo['staffy'],
                                     staffStats)
        self._engine.addSprite(self._staff)

        self._entries = []
        counter = 1
        while counter:
            try:
                entranceX = mapinfo['entranceX%d' % counter]
                entranceY = mapinfo['entranceY%d' % counter]
                entrance = entities.Entry('stairs.png', self._engine,
                                          entranceX, entranceY)
                self._entries.append(entrance)
                self._engine.addSprite(entrance)
                counter += 1
            except KeyError:
                counter = 0

        self._turn = 0
        mixer.music.load(localSoundsDir + '23 - Cold_Mountain_Clouds.ogg')
        mixer.music.set_volume(localVol * 4)
        mixer.music.play(-1)

    def event(self, key, pressed):
        soundOpenMenu.set_volume(localVol * .5)
        turned = 1
        if pressed:
            if key == K_KP8 or key == K_UP:
                self._player.move(0, -1)
            elif key == K_KP2 or key == K_DOWN:
                self._player.move(0, 1)
            elif key == K_KP4 or key == K_LEFT:
                self._player.move(-1, 0)
            elif key == K_KP6 or key == K_RIGHT:
                self._player.move(1, 0)
            elif key == K_KP1:
                self._player.move(-1, 1)
            elif key == K_KP7:
                self._player.move(-1, -1)
            elif key == K_KP9:
                self._player.move(1, -1)
            elif key == K_KP3:
                self._player.move(1, 1)
            elif key == K_u:
                self._deequip = inventory.DeEquip(self._driver,
                                                  self._player, self)
                self._visited = self._deequip
                turned = 0
            elif key == K_e:
                self._visited = inventory.Equip(self._driver,
                                                self._player, self)
            elif key == K_d:
                self._visited = inventory.Drop(self._driver,
                                               self._player, self)
            elif key == K_s:
                self._visited = inventory.Sell(self._driver,
                                               self._player, self)
            elif key == K_a:
                self._visited = inventory.Use(self._driver,
                                              self._player, self)
            elif key == K_h:
                self._visited = inventory.Help(self._driver,
                                              self._player, self)

            elif key == K_b:
                if self._player.money > 250:
                    self._player.money -= 250
                    self.message("You buy a Healing Potion for 250 Gold")
                    potionStats = {
                        'name' : "Healing Potion",
                        'healingMin' : 25,
                        'healingMax' : 150
                        }
                    potion = entities.Potion('armor.png',
                                             self._engine, 0, 0,
                                             potionStats)

                    self._player.giveItem(potion)
                    soundCoins.set_volume(localVol * 1)
                    soundCoins.play()
                else:
                    self.message("You don't have enough Gold to buy a Healing Potion")

            elif key == K_ESCAPE:
                self._driver.done()

            self._engine.centerOn(self._player)
            if turned:
                self.takeTurn()

    def message(self, message):
        try:
            self._messages.append( (self._turn, message) )
        except AttributeError:
            pass # Don't message until self._turn is ready

    def paint(self, screen):
        self._engine.paint(screen)

        self.paintStats(screen,self._player)
        self.paintMessages(screen)

    def paintMessages(self, screen):
        x = 2
        y = 0
        screenSize = self._driver.getScreenSize()
        white = (255, 255, 255)
        right = x + screenSize[0] - 4
        messageImages = []
        for turn, message in self._messages:
            if turn < self._turn - 3: continue
            messageImages.append(self._font.render(message, 0,
                                                   white).convert())
        if messageImages:
            bottom = y + ((messageImages[0].get_size()[1] + 2) *
                          len(messageImages))
            pygame.draw.line(screen, white, (x,y), (right, y))
            pygame.draw.line(screen, white, (right,y),
                             (right, bottom))

            pygame.draw.line(screen, white, (right,bottom),
                             (x, bottom))

            pygame.draw.line(screen, white, (x,bottom),
                             (x,y))
            screen.fill( (64, 64, 192),
                         (x+1, y+1, right-3, bottom-1))
            for image in messageImages:
                screen.blit(image, (x+1, y+1))
                y += image.get_size()[1] + 2

    def paintStats(self,screen, player):
        statsTuple = (player.str, player.dex, player.int, player.hp,
                      player.maxhp, player.mp, player.maxmp, player.money,
					  player.xp)
        line =("The Guardian (Level %d):  "% player.level +
          "STR %d DEX %d INT %d  HP %d(%d) MP %d(%d)  Gold %d  XP %d") % statsTuple

        white = (255, 255, 255)
        stats = self._font.render(line, 0, white).convert()
        screenSize = self._driver.getScreenSize()
        x = 2
        y = screenSize[1] - stats.get_size()[1] - 4
        right = x + screenSize[0] - 4
        bottom = screenSize[1] - 2
        pygame.draw.line(screen, white, (x,y), (right, y))
        pygame.draw.line(screen, white, (right,y), (right, bottom))
        pygame.draw.line(screen, white, (right,bottom), (x, bottom))
        pygame.draw.line(screen, white, (x,bottom), (x, y))
        screen.fill( (64, 64, 192), (x+2, y+2, right-4, bottom-4))
        screen.blit(stats, (x+1, y+1))

    def reactivate(self):
        self._visited = None

    def takeTurn(self):
        self._turn += 1
        chance = float(self._mapinfo['spawnChance']) / 100.0
        picked = random.random()
        if picked < chance:
            adv = ai.createAdventurer(self._entries, self._engine)
            message = "You sense an intruder enter the dungeon"
            self.message(message)
            self._engine.addSprite(adv, 1)

            soundEnemySpawn.set_volume(localVol * 1)
            soundEnemySpawn.play()
        self._engine.takeTurn()


    def update(self):
        if(self._visited):
            self._driver.start(self._visited)

