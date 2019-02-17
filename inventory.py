import entities
from states import State
from menu import Menu

class InventoryAction(State):
    def __init__(self, driver, player, pgs):
        State.__init__(self, driver)
        self._player = player
        self._pgs = pgs
        self._menu = None

    def action(self, chosen):
        pass

    def inaction(self):
        pass

    def reactivate(self):
        if(self.menu):
            chosen = self._menu.getResult()
            if(chosen[0]):
                self.action(chosen)
            else:
                self.inaction()

    def update(self):
        if self._menu:
            self._driver.done()
        else:
            self.menu()


class DeEquip(InventoryAction):
    def __init__(self, driver, player, pgs):
        InventoryAction.__init__(self, driver, player, pgs)

    def action(self, chosen):
        self._player.deequip(chosen[0])

    def menu(self):
        desc = "%s: %s"
        itemMenu = []
        for type in self._player.equipped.keys():
            item = self._player.equipped[type]
            if(item):
                itemMenu.append( (type, desc % (type, item.getName()),
                                  None) )
            else:
                itemMenu.append( (None, desc % (type, "Nothing"),
                                  None) )
        itemMenu.append( (None, "Um... nevermind", None))
        if(itemMenu):
            self._menu = Menu(self._driver, (5, 5), itemMenu,
                              "Un-equip what?")
            self._driver.start(self._menu)
        else: self._menu = 1

class Drop(InventoryAction):
    def __init__(self, driver, player, pgs):
        InventoryAction.__init__(self, driver, player, pgs)

    def action(self, chosen):
        self._player.drop(chosen[0])

    def menu(self):
        itemMenu = []
        for item in self._player.inventory:
            itemMenu.append( (item, item.getName(), None))
        itemMenu.append( (None, "On second thought, let's not.",
                          None))
        self._menu = Menu(self._driver, (5, 5), itemMenu,
                          "Drop what?")
        self._driver.start(self._menu)
            
class Equip(InventoryAction):
    def __init__(self, driver, player, pgs):
        InventoryAction.__init__(self, driver, player, pgs)

    def action(self, chosen):
        self._player.equip(chosen[0])

    def menu(self):
        itemMenu = []
        for item in self._player.inventory:
            if item.getType() in entities.EQUIPPABLE:
                itemMenu.append( (item, item.getName(), None))
        itemMenu.append( (None, "Nevermind", None) )
        self._menu = Menu(self._driver, (5, 5), itemMenu,
                          "Equip what?")
        self._driver.start(self._menu)

class Sell(InventoryAction):
    def __init__(self, driver, player, pgs):
        InventoryAction.__init__(self, driver, player, pgs)

    def action(self, chosen):
        self._player.deequip(chosen[0])
        self._player.remove(chosen[0])
        self._player.money += chosen[2]

    def menu(self):
        itemMenu = []
        for item in self._player.inventory:
            itemMenu.append( (item, item.getName(), item.price()))
        itemMenu.append( (None, "Nevermind", None))
        self._menu = Menu(self._driver, (5, 5), itemMenu,
                          "What would you like to sell?")
        self._driver.start(self._menu)

class Use(InventoryAction):
    def __init__(self, driver, player, pgs):
        InventoryAction.__init__(self, driver, player, pgs)

    def action(self, chosen):
        self._player.use(chosen[0])

    def menu(self):
        itemMenu = []
        for item in self._player.inventory:
            if item.getType() not in entities.EQUIPPABLE:
                itemMenu.append( (item, item.getName(), None))
        itemMenu.append( (None, "On second thought, let's not.",
                          None))
        self._menu = Menu(self._driver, (5, 5), itemMenu,
                          "Apply what?")
        self._driver.start(self._menu)


class GameOver(InventoryAction):
    def __init__(self, driver, player, pgs, message):
        InventoryAction.__init__(self, driver, player, pgs)
        self._message = message

    def inaction(self):
        self._driver.quit()

    def menu(self):
        menu = [ (None, 'Quit', None),
                 (None, 'Give up', None),
                 (None, 'Go Home', None) ]
        self._menu = Menu(self._driver, (100, 100), menu,
                                         self._message)
        self._driver.start(self._menu)
