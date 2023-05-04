import pygame
from pygame.locals import *

class StateDriver:
    def __init__(self, screen):
        self._states = []
        self._screen = screen

    def done(self):
        self._states.pop()
        self.getCurrentState().reactivate()

    def getCurrentState(self):
        try:
            return self._states[len(self._states) - 1]
        except IndexError:
            raise SystemExit  # we're done if theren't any states left

    def getScreenSize(self):
        return self._screen.get_size()

    def quit(self):
        raise SystemExit

    def replace(self, state):
        self._states.pop()
        self.start(state)

    def run(self):
        currentState = self.getCurrentState()
        while(currentState):
            # poll queue
            event = pygame.event.poll()
            while(event.type != NOEVENT):
                if event.type == QUIT:
                    currentState = None
                    break
                elif event.type == KEYUP or event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        #currentState = None
                        #break
                        pass
                    if event.type == KEYUP:
                        currentState.event(event.key, 0)
                    if event.type == KEYDOWN:
                        currentState.event(event.key, 1)
                event = pygame.event.poll()

            self._screen.fill( (0, 0, 0) )
            if currentState:
                currentState.paint(self._screen)
                currentState.update()
                
                currentState = self.getCurrentState()
                
                pygame.display.flip()
                pygame.time.delay(40);

    def start(self, state):
        self._states.append(state)
        self.getCurrentState().activate()

class State:
    def __init__(self, driver):
        self._driver = driver

    def activate(self):
        pass

    def event(self, key, pressed):
        pass

    def paint(self, screen):
        pass

    def reactivate(self):
        pass

    def update(self):
        pass
    
