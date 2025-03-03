import pygame as pg

itemsize = (60, 60)
smallitemsize = (32, 32)
class Item:
    def __init__(self, id: str | None, pack: str, name: str, txt: str, maxstack: int = 64):
        self.id = id
        self.pack = pack
        self.name = name
        if id is None:
            #self.txt = pg.image.load('items/custom.png')
            pass
        else:
                self.txt_orig = pg.image.load(f'items/{pack}/textures/{txt}.png')
                self.txt = pg.transform.scale(self.txt_orig, itemsize)
                self.txt_small = pg.transform.scale(self.txt_orig, smallitemsize)
        self.max = maxstack
        self.OnLoad()

    def OnLoad(self):
        pass

    def OnAdd(self, player, slot):
        pass

    def OnStart(self, player, slot):
        pass

    def OnSub(self, player, slot):
        pass

    def OnEnd(self, player, slot):
        pass

    def OnUse(self, player, slot):
        pass

    def OnUpdate(self):
        pass


def playSound(sound: str):
    pass