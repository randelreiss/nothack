#!/usr/bin/env python

import asyncio  # for pygbag
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

    print("NotHack by Roger 'Denor' Ostrander, 2019 version by Randel@RandelReiss.com")
    print("Hit the H Key for Help screen...")

    screen = pygame.display.set_mode(screensize, DOUBLEBUF | fs)

    driver = states.StateDriver(screen)
    initial = TitleScreen(driver)
    driver.start(initial)
    asyncio.run( driver.run() )

    # await asyncio.sleep(0)  # very important, and keep it 0

if __name__ == '__main__':
    main()
    #asyncio.run( main() )
