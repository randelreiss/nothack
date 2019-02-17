# nothack
Inverse of the typical RPG

Credit for the base of NotHack project to Roger 'Denor' Ostrander, circa 2002 for the Ludum Dare 48 Hour Contest #1.

KNOWN BUGS (as of 2/17/2019)
If player dies after activation of a menu (Sell, Apply, Help, etc.), game abruptly exits with:
Game over!
Traceback (most recent call last):
  File "./nothack.py", line 29, in <module>
    main()
  File "./nothack.py", line 26, in main
    driver.run()
  File "~/Development/NotHack/nothack/states.py", line 51, in run
    currentState.update()
  File "~/Development/NotHack/nothack/inventory.py", line 28, in update
    self._driver.done()
  File "~/Development/NotHack/nothack/states.py", line 11, in done
    self.getCurrentState().reactivate()
  File "~/Development/NotHack/nothack/inventory.py", line 20, in reactivate
    chosen = self._menu.getResult()
AttributeError: 'NoneType' object has no attribute 'getResult'
