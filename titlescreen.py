import pygame
from pygame.constants import *
from states import State, StateDriver
from menu import Menu
from playinggame import PlayingGame

class TitleScreen(State):
  def __init__(self, driver):
      State.__init__(self, driver)
      self._title = pygame.image.load("title.png").convert()
      mainMenu = [ (1, 'Start Game', 0), (2, 'Quit',0) ]
      self._menu = Menu(driver, (5, 400), mainMenu, None,  self)
      self._shownMenu = 0

  def paint(self, screen):
      screen.blit(self._title, (0,0))

  def reactivate(self):
    if(self._menu):
      result = self._menu.getResult()
      if result[0] == 1:
          self._menu = None
          self._driver.start(PlayingGame(self._driver))
      elif result[0] == 2 or result[0] == None:
          self._menu = None
          self._driver.done()
      else:
          print (result)
    else:
      self._driver.done()

  def update(self):
      if not self._shownMenu:
          self._driver.start(self._menu)
          self._shownMenu = 1
