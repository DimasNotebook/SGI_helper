#from utils import *
from inventory import *
if __name__ == '__main__':
    print('This file can be used as a module only!')
    quit(-1)

def plinit(_screen, _screentop):
    global screen
    global screentop
    screen = _screen
    screentop = _screentop

class StateBar:
    def __init__(self, pos, width: int, height: int=60, maxv: int=100, value=None, col1=(0, 200, 0), col2=(200, 0, 0)):
        self.pos = pos
        self.width = width
        self.max = maxv
        if value is not None:
            self.v = value
        else:
            self.v = maxv
        self.col = (col1, col2)
        self.rect = pg.rect.Rect(self.pos[0], self.pos[1], self.width, height)

    def update(self):
        pg.draw.rect(screen, self.col[1], self.rect, 0, 15)
        pg.draw.rect(screen, self.col[0], (self.pos[0], self.pos[1], self.width * (self.v / self.max), self.rect[3]), 0, 15)


class Player:
    invOffset: tuple
    invSize: str
    invSlots: tuple
    barPos: tuple
    barSize: tuple
    namePos: tuple
    def __init__(self, save, data: dict, pos: tuple[int, int] | list[int, int] | pg.Rect):
        self.orig = data
        self.pos = pos
        self.name = data["name"]
        self.maxhp = data["maxhp"]
        self.stats = data["stats"]
        self.inv = Inventory(self, self.invSize, (self.pos[0] + self.invOffset[0], self.pos[1] + self.invOffset[1]), self.invSlots, data["inv"])
        if save["rad"]:
            self.bars = [StateBar((self.pos[0] + self.barPos[0][0], self.pos[1] + self.barPos[0][1]), self.barSize[0], self.barSize[1], self.maxhp, self.stats[0]),
                         StateBar((self.pos[0] + self.barPos[1][0], self.pos[1] + self.barPos[1][1]), self.barSize[0], self.barSize[1], self.maxhp, self.stats[1]),
                         StateBar((self.pos[0] + self.barPos[2][0], self.pos[1] + self.barPos[2][1]), self.barSize[0], self.barSize[1], self.maxhp, self.stats[2]),
                         StateBar((self.pos[0] + self.barPos[3][0], self.pos[1] + self.barPos[3][1]), self.barSize[0], self.barSize[1], self.maxhp, self.stats[3]),
                         StateBar((self.pos[0] + self.barPos[4][0], self.pos[1] + self.barPos[4][1]), self.barSize[0], self.barSize[1], self.maxhp, self.stats[4]),
                         StateBar((self.pos[0] + self.barPos[5][0], self.pos[1] + self.barPos[5][1]), self.barSize[0], self.barSize[1], self.maxhp, self.stats[5])]
        else:
            self.bars = [StateBar((self.pos[0] + self.barPos[0][0], self.pos[1] + self.barPos[0][1]), self.barSize[0], self.barSize[1], self.maxhp, self.stats[0]),
                         StateBar((self.pos[0] + self.barPos[1][0], self.pos[1] + self.barPos[1][1]), self.barSize[0], self.barSize[1], self.maxhp, self.stats[1]),
                         StateBar((self.pos[0] + self.barPos[2][0], self.pos[1] + self.barPos[2][1]), self.barSize[0], self.barSize[1], self.maxhp, self.stats[2]),
                         StateBar((self.pos[0] + self.barPos[3][0], self.pos[1] + self.barPos[3][1]), self.barSize[0], self.barSize[1], self.maxhp, self.stats[3])]

    def update(self):
        for bar in self.bars:
            bar.update()
        self.inv.update()
        txt(screen, self.name, 72, (self.pos[0] + self.namePos[0], self.pos[1] + self.namePos[1]), align='lu')

    def export(self):
        stats = []
        for bar in self.bars:
            stats.append(bar.v)
        return {"name": self.name, "maxhp": self.maxhp, "stats": stats, "inv": self.inv.export()}


class Player1(Player):
    invOffset = (75, 440)
    invSize = 'full'
    invSlots = (15, 3)
    barPos = ((70, 140), (X / 2 + 70, 140), (70, 260), (X / 2 + 70, 260), (70, 380), (X / 2 + 70, 380))
    barSize = (450, 60)
    namePos = (40, 40)