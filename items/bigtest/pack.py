from item import *

# All items in item packs inherit from the item class
class functional(Item):
    # OnLoad - called when the item is being initialized
    def OnLoad(self):
        playSound('appear')
