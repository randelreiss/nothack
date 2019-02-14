import pygame
from pygame.constants import *
from states import State

CURSOR = '>'

class Menu(State):
    def __init__(self, driver, location, options, header = None, slave
                 = None, default = 0):
        State.__init__(self, driver)
        if default >= len(options): default = 0
        self._header = header
        self._options = options
        self._current = default
        self._chosen = options[default]
        self._slave = slave
        self._location = location
        self._font = pygame.font.Font(None, 20);
        self.setupImages()

    def event(self, key, pressed):
        if pressed:
            if key == K_KP8:
                self._current -= 1
                if self._current < 0:
                    self._current = len(self._options) - 1
            elif key == K_KP2:
                self._current += 1
                if self._current >= len(self._options):
                    self._current = 0
            elif key == K_KP_ENTER:
                self._driver.done()
            elif key == K_ESCAPE:
                self._chosen = (None, None, None)
                self._driver.done()
            self._chosen = self._options[self._current]

    def getResult(self):
        return self._chosen

    def paint(self, screen):
        if(self._slave):
            self._slave.paint(screen)

        leftmost = self._location[0]
        spacing = self._font.get_linesize()
        x = leftmost + self._cursor.get_size()[0] + 3
        y = self._location[1]

        if self._header:
            screen.blit(self._header, (leftmost, y))
            y += self._images[0][0].get_size()[1] + spacing
        
        counter = 0
        for item, price in self._images:
            if counter == self._current:
                screen.blit(self._cursor, (leftmost, y))
            if(price):
                screen.blit(price, (x + item.get_size()[0] + 10, y))
            screen.blit(item, (x,y))
            y += item.get_size()[1] + spacing
            counter += 1

    def setupImages(self):
        self._images = []
        white = (255, 255, 255)
        for item, text, price in self._options:
            itemImg = self._font.render(text, 0,
                                        white).convert()
            if(price):
                priceImg = self._font.render("%d" % price, 0,
                                             white).convert()
            else:
                priceImg = None
                
            self._images.append((itemImg, priceImg))
        self._cursor = self._font.render(CURSOR, 0,
                                         white).convert()
        if self._header:
            self._header = self._font.render(self._header, 0,
                                             white).convert()
        
        
