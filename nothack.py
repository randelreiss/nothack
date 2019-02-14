#!/usr/bin/env python

import os, sys, random
import pygame
from pygame.locals import *


import states
from titlescreen import TitleScreen

def main():
    random.seed()
    pygame.init()

    screensize = [640,480]
    fs = 0

    if '-fs' in sys.argv or '--fullscreen' in sys.argv:
        fs = FULLSCREEN
    
    screen = pygame.display.set_mode(screensize, DOUBLEBUF | fs)

    driver = states.StateDriver(screen)
    initial = TitleScreen(driver)
    driver.start(initial)
    driver.run()

if __name__ == '__main__':
    main()
