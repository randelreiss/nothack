import pygame
from pygame.constants import *
import inventory

def loadMap(filename):
    map = []
    mapinfo = {}
    infile = open(filename,'r')
    mode = 0
    for line in infile.readlines():
        line = line.strip()
        if line == '** END OF MAP **':
            mode = 1
            continue
        if(mode):
            key, value = line.split('=')
            mapinfo[key.strip()] = value.strip()
        else:
            map.append(line)
    return map, mapinfo

class TileEngine:
    passable = [ '.' ]
    def __init__(self, mapfile, driver, parent, location = (0,0)):
        self._tiles = {
            '.'  : pygame.image.load( "floor.png" ).convert(),
            '|'  : pygame.image.load( "eastWall.png" ).convert(),
            '-'  : pygame.image.load( "southWall.png" ).convert(),
            '/'  : pygame.image.load( "northWestWall.png" ).convert(),
            '\\' : pygame.image.load( "northEastWall.png" ).convert(),
            '?'  : pygame.image.load( "southEastWall.png" ).convert(),
            '+'  : pygame.image.load( "southWestWall.png" ).convert(),
            '='  : pygame.image.load( "northWall.png" ).convert(),
            '<'  : pygame.image.load( "westWall.png" ).convert(),
            '}'  : pygame.image.load( "northEastWallInternal.png"
                                      ).convert(),
            ']'  : pygame.image.load( "southEastWallInternal.png"
                                      ).convert(),
            '{'  : pygame.image.load( "northWestWallInternal.png"
                                      ).convert(),
            '['  : pygame.image.load( "southWestWallInternal.png"
                                      ).convert(),
           
            }
        self._parent = parent
        self._nothing = pygame.image.load("nothing.png").convert()
        self._driver = driver
        self._sprites = []
        self._player = None
        self._staff = None
        self._npc = []
        self._location = location
        self._map = []
        self._mapinfo = {}
        self._tilewidth = self._tiles['.'].get_size()[0]
        self._tileheight = self._tiles['.'].get_size()[1]

        self._offset = [0, 0]
        self._map, self._mapinfo = loadMap(mapfile)

    def addSprite(self, sprite, npc = 0):
        if len(self._sprites) == 0:
            self._player = sprite
        elif len(self._sprites) == 1 and self._staff == None:
            self._staff = sprite

        if npc:
            self._npc.append(sprite)
        self._sprites.append(sprite)

    def centerOn(self, sprite):
        # convert sprite co-ords to screen co-ords
        screenSize = self._driver.getScreenSize()
        spriteXY = sprite.getXY()
        self._offset[0] = (screenSize[0]/2 - self._location[0] -
                           (spriteXY[0] * self._tilewidth))
        self._offset[1] = (screenSize[1]/2 - self._location[1] -
                           (spriteXY[1] * self._tileheight))

    def dead(self, who):
        who.dropAll()
        if who == self._player:
            msg = "You have been slain - the staff is no longer protected."
            self._driver.start( inventory.GameOver(self._driver,
                                                   self._player,
                                                   self._parent,
                                                   msg))
            print ("Game over!")
        else:
            self.removeSprite(who)

    def getDriver(self):
        return self._driver

    def getMap(self):
        return self._map

    def getMapInfo(self):
        return self._mapinfo

    def getOffset(self):
        return (self._offset)

    def getParent(self):
        return self._parent

    def getPlayer(self):
        return self._player

    def getStaff(self):
        return self._staff

    def getTileSize(self):
        return (self._tilewidth, self._tileheight)

    def move(self, dx, dy):
        width = self._tilewidth
        height = self._tileheight
        self._offset[0] += dx * width
        self._offset[1] += dy * height

    def moveOk(self, enquirer, newx, newy):
        if not self._map[newy][newx] in self.passable:
            return 0
        else:
            result = 1
            for sprite in self._sprites[:]:
                if sprite.getXY() == (newx, newy):
                    result = result and sprite.occupied(enquirer)
            return result

    def paint(self, screen):
        x = self._location[0] + self._offset[0]
        y = self._location[1] + self._offset[1]
        width = self._tilewidth
        height = self._tileheight
        for row in self._map:
            for col in row:
                try:
                    tile = self._tiles[col]
                    screen.blit(tile, (x, y))
                except KeyError:
                    screen.blit(self._nothing, (x, y))
                x += width
            x = self._location[0] + self._offset[0]
            y += height
        for sprite in self._sprites:
            x, y = sprite.getXY()
            left = self._location[0] + self._offset[0]
            top = self._location[1] + self._offset[1]
            x *= self._tilewidth
            y *= self._tileheight
            sprite.paint(screen, (x + left, y + top))

    def parseInfo(self, line):
        key, value = line.split('=')
        self._mapinfo[key.strip()] = value.strip()

    def removeSprite(self, sprite):
        self._sprites.remove(sprite)
        try:
            self._npc.remove(sprite)
        except ValueError:
            pass

    def takeTurn(self):
        for npc in self._npc:
            npc.turn()

class TileSprite:
    def __init__(self, imageFilename, parent, x, y, isPlayer = 0):
        if imageFilename:
            image = pygame.image.load(imageFilename)
            image.set_colorkey( (255, 0, 255), RLEACCEL)
            self._image = image.convert()
        else: self._image = None
        self.isPlayer = isPlayer
        self._parent = parent
        self._x = int(x)
        self._y = int(y)

    def getXY(self):
        return (self._x, self._y)

    def move(self, dx, dy):
        pass

    def paint(self, screen, location):
        if(self._image):
            screen.blit(self._image, location)

    def occupied(self, intruder):
        return 0


