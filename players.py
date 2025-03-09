#from utils import *
import time
from gui import Textfield, Checkbox, Button
import k

import rcs
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
    class Int:
        w = 800
        h = 400
        fy = 160
        cy = 240
        title = 'Change bar value'
        cancel_rect = pg.rect.Rect(X / 2 - 300, Y / 2 + 130, 285, 60)
        apply_rect = pg.rect.Rect(X / 2 + 15, Y / 2 + 130, 285, 60)
        br = 10
        def __init__(self, bar):
            self.bar = bar
            self.rect = ((X - self.w) / 2, (Y - self.h) / 2, self.w, self.h)
            self.field = Textfield(screentop, False, X / 2 - 60, self.rect[1] + self.fy, 120, num=True)
            self.box = Checkbox(screentop, 'Don\'t clamp', X / 2, self.rect[1] + self.cy, center=True)
            self.apply = Button(screentop, 'Apply', self.apply_rect)
            self.cancel = Button(screentop, 'Cancel', self.cancel_rect)

        def update(self):
            pg.draw.rect(screentop, BLACK, self.rect, 0, self.br)
            pg.draw.rect(screentop, WHITE, self.rect, 5, self.br)
            txt(screentop, self.title, 48, (X / 2, self.rect[1] + 10), align='u')
            txt(screentop, f'Changing value: {self.bar.player.name} - {self.bar.name}', 36, (X / 2, self.rect[1] + 100), align='u')
            self.field.update()
            self.box.update()
            fv = self.field.text
            if self.cancel.update():
                return False
            if self.apply.update():
                return [self.get(), self.box.state, None, None, None]
            return None

        def get(self):
            if self.field.text != '' and self.field.text != '-': return int(self.field.text)

    class AdvInt:
        w = 800
        h = 400
        f1y = 80
        f2y = 160
        f3y = 240
        cy = 240
        cancel_rect = pg.rect.Rect(X / 2 - 300, Y / 2 + 130, 285, 60)
        apply_rect = pg.rect.Rect(X / 2 + 15, Y / 2 + 130, 285, 60)
        br = 10

        def __init__(self, bar):
            self.bar = bar
            self.rect = ((X - self.w) / 2, (Y - self.h) / 2, self.w, self.h)
            self.field1 = Textfield(screentop, 'Set value', X / 2, self.rect[1] + self.f1y, 120, num=True, center=True)
            self.field2 = Textfield(screentop, 'Change maximum value', X / 2, self.rect[1] + self.f2y, 120, num=True, center=True)
            self.field3 = Textfield(screentop, 'Set auto interval', X / 2 - 60, self.rect[1] + self.f3y, 120, num=True, center=True)
            #self.box = Checkbox(screentop, 'Don\'t clamp', X / 2, self.rect[1] + self.cy, center=True)
            self.apply = Button(screentop, 'Apply', self.apply_rect)
            self.cancel = Button(screentop, 'Cancel', self.cancel_rect)

        def update(self):
            pg.draw.rect(screentop, BLACK, self.rect, 0, self.br)
            pg.draw.rect(screentop, WHITE, self.rect, 5, self.br)
            txt(screentop, self.bar.player.name + ' - ' + self.bar.name, 48, (X / 2, self.rect[1] + 10), align='u')
            #txt(screentop, f'Changing value: {self.bar.player.name} - {self.bar.name}', 36, (X / 2, self.rect[1] + 100),
            #    align='u')
            self.field1.update()
            self.field2.update()
            self.field3.update()
            #self.box.update()
            #fv = self.field.text
            if self.cancel.update():
                return False
            if self.apply.update():
                res = [None, None, None, None, None]
                f1c = self.convert(self.field1.text)
                f2c = self.convert(self.field2.text)
                f3c = self.convert(self.field3.text)
                if f1c != 0: res[2] = f1c
                if f2c != 0: res[3] = f2c
                if f3c != 0: res[4] = f3c
                else: res[4] = False
                return res
            return None

        def convert(self, v):
            if v != '' and v != '-': return int(v)

    class SmallInt:
        w = 220
        h = 150
        br = 10
        def __init__(self, bar, mode):
            self.bar = bar
            self.field = Textfield(screentop, False, X / 2 - 60, Y - 80, 120, num=True)
            self.field.start_writing()
            self.rect = pg.rect.Rect((X - self.w) / 2, Y - self.h, self.w, self.h + self.br)
            self.mode = mode
            match mode:
                case 'c': self.text = 'Changing value'
                case 's': self.text = 'Setting value'
                case 'a': self.text = 'Setting auto for'

        def update(self):
            if k.k(pg.K_RETURN):
                match self.mode:
                    case 'c': return [self.get(), False, None, None, None]
                    case 's': return [None, None, self.get(), None, None]
                    case 'a': return [None, None, None, None, self.get()]
            elif k.k(pg.K_ESCAPE):
                return False
            pg.draw.rect(screentop, BLACK, self.rect, 0, self.br)
            pg.draw.rect(screentop, WHITE, self.rect, 5, self.br)
            txt(screentop, self.text, 24, (X / 2, self.rect[1] + 8), align='u')
            txt(screentop, f'{self.bar.name}', 24, (X / 2, self.rect[1] + 36), align='u')
            self.field.update()

        def get(self):
            if self.field.text != '' and self.field.text != '-': return int(self.field.text)

    animl = 1.5
    def __init__(self, pos, player, name, spr, width: int, height: int=60, maxv: int=100, value=None, col1=(0, 200, 0), col2=(200, 0, 0)):
        self.pos = pos
        self.player = player
        self.name = name
        self.spr = rcs.spr(spr)
        self.width = width
        self.height = height
        self.max = maxv
        if value is not None:
            self.v = value
        else:
            self.v = maxv
        self.col = (col1, col2)
        self.rect = pg.rect.Rect(self.pos[0] + height, self.pos[1], self.width, height)
        self.int = None
        self.auto = False
        self.autovalue = 0
        self.autotimer = 0
        self.animstart = None
        self.animtimer = 0

    def open(self, t: str):
        match t.lower():
            case 's' | 'standard':
                self.int = self.Int(self)
            case 'a' | 'advanced':
                self.int = self.AdvInt(self)
            case 'q' | 'qc' | 'quick' | 'quick change':
                self.int = self.SmallInt(self, 'c')
            case 'qs' | 'quick set':
                self.int = self.SmallInt(self, 's')
            case 'qa' | 'quick advanced' | 'quick auto':
                self.int = self.SmallInt(self, 'a')
            case _:
                raise ValueError('Attribute t must be one of these: "s", "a", "q", "qs", "qa".')
        k.state_lock = True


    def update(self):
        col = self.col[0]
        if self.rect.collidepoint(pg.mouse.get_pos()):
            mult = 0.35
            col = (int(self.col[0][0] + (255 - self.col[0][0]) * mult),
                   int(self.col[0][1] + (255 - self.col[0][1]) * mult),
                   int(self.col[0][2] + (255 - self.col[0][2]) * mult))
            if k.lmb and not k.state_lock:
                self.open('s')
            elif k.rmb and not k.state_lock:
                self.open('a')

        if self.int is not None:
            mult = 0.25 + sin(time.time() * 2) / 4
            col = (int(self.col[0][0] + (255 - self.col[0][0]) * mult),
                   int(self.col[0][1] + (255 - self.col[0][1]) * mult),
                   int(self.col[0][2] + (255 - self.col[0][2]) * mult))

            intres = self.int.update()
            if type(intres) == list:
                if intres[0] is not None:
                    self.set(intres[0], False, not intres[1])
                if intres[2] is not None:
                    self.set(intres[2], True)
                if intres[3] is not None:
                    self.max = intres[3]
                if intres[4] is not None:
                    self.set_auto(intres[4])
                self.int = None
                k.state_lock = False
            elif intres is False:
                self.int = None
                k.state_lock = False

        if self.animstart is not None:
            d = (1 - sin((time.time() - self.animtimer) * (pi / 2) / self.animl)) * (self.animstart - self.v)
            if time.time() - self.animtimer >= self.animl:
                self.animstart = None
        else: d = 0

        if self.auto is not False and self.auto != 0:
            self.autovalue = (time.time() - self.autotimer) / self.auto
            if self.v - self.autovalue > self.max or self.v - self.autovalue < 0:
                self.set_auto(0)

        #txt(screen, self.name, 48, (self.pos[0], self.pos[1] + self.height / 2), align='l')
        if self.v <= 0 and int(time.time() * 4) % 2 == 1:
            txtcol = (255, 0, 0)
        else:
            txtcol = WHITE
        if (self.v - self.autovalue) / self.max > 0.2 or int(time.time() * 4) % 2 == 0:
            screen.blit(self.spr, (self.pos[0], self.pos[1] + self.height / 2 - self.spr.get_height() / 2))
        pg.draw.rect(screen, self.col[1], self.rect, 0, 15)
        pg.draw.rect(screen, col, (self.rect[0], self.pos[1], self.width * ((self.v - self.autovalue + d) / self.max), self.rect[3]), 0, 15)
        txt(screen, str(int(self.v - self.autovalue)).rjust(len(str(self.max - 1)), '0') + '/' + str(self.max), 48, (self.rect[0] + self.width + 20, self.pos[1] + self.height / 2), txtcol, align='l')

    def set(self, value: int | str, do_set: bool =False, clamp: bool =True):
        self.set_auto(None)
        self.animstart = self.v
        self.animtimer = time.time()
        if value == 'max': self.v = self.max
        elif do_set: self.v = value
        elif clamp: self.v = min(max(0, self.v + value), self.max)
        else: self.v += value

    def set_auto(self, value=None):
        self.v = round(self.v - self.autovalue)
        if value is not None: self.auto = value / 100
        self.autotimer = time.time()
        self.autovalue = 0

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
        self.stats = data["stats"]
        self.inv = Inventory(self, self.invSize, (self.pos[0] + self.invOffset[0], self.pos[1] + self.invOffset[1]), self.invSlots, data["inv"])
        if save["rad"]:
            self.bars = [StateBar((self.pos[0] + self.barPos[0][0], self.pos[1] + self.barPos[0][1]), self, 'Health', 'heart',  self.barSize[0], self.barSize[1], data["maxs"][0], self.stats[0]),
                         StateBar((self.pos[0] + self.barPos[1][0], self.pos[1] + self.barPos[1][1]), self, 'Hunger', 'hunger', self.barSize[0], self.barSize[1], data["maxs"][1], self.stats[1]),
                         StateBar((self.pos[0] + self.barPos[2][0], self.pos[1] + self.barPos[2][1]), self, 'Energy', 'energy', self.barSize[0], self.barSize[1], data["maxs"][2], self.stats[2]),
                         StateBar((self.pos[0] + self.barPos[3][0], self.pos[1] + self.barPos[3][1]), self, 'Thirst', 'thirst', self.barSize[0], self.barSize[1], data["maxs"][3], self.stats[3]),
                         StateBar((self.pos[0] + self.barPos[4][0], self.pos[1] + self.barPos[4][1]), self, 'Radiation', 'radiation', self.barSize[0], self.barSize[1], data["maxs"][4], self.stats[4]),
                         StateBar((self.pos[0] + self.barPos[5][0], self.pos[1] + self.barPos[5][1]), self, 'Shield', 'heart', self.barSize[0], self.barSize[1], data["maxs"][5], self.stats[5])]
        else:
            self.bars = [StateBar((self.pos[0] + self.barPos[0][0], self.pos[1] + self.barPos[0][1]), self, 'Health', 'heart',  self.barSize[0], self.barSize[1], data["maxs"][0], self.stats[0]),
                         StateBar((self.pos[0] + self.barPos[1][0], self.pos[1] + self.barPos[1][1]), self, 'Hunger', 'hunger', self.barSize[0], self.barSize[1], data["maxs"][1], self.stats[1]),
                         StateBar((self.pos[0] + self.barPos[2][0], self.pos[1] + self.barPos[2][1]), self, 'Energy', 'energy', self.barSize[0], self.barSize[1], data["maxs"][2], self.stats[2]),
                         StateBar((self.pos[0] + self.barPos[3][0], self.pos[1] + self.barPos[3][1]), self, 'Thirst', 'thirst', self.barSize[0], self.barSize[1], data["maxs"][3], self.stats[3])]

    def update(self):
        for bar in self.bars:
            bar.update()
        self.inv.update()
        txt(screen, self.name, 72, (self.pos[0] + self.namePos[0], self.pos[1] + self.namePos[1]), align='lu')

    def export(self):
        stats = []
        maxs = []
        for bar in self.bars:
            bar.set_auto(0)
            stats.append(bar.v)
            maxs.append(bar.max)
        return {"name": self.name, "stats": stats, "maxs": maxs, "inv": self.inv.export()}


class Player1(Player):
    invOffset = (75, 440)
    invSize = 'full'
    invSlots = (15, 3)
    barPos = ((70, 140), (X / 2 + 70, 140),
              (70, 240), (X / 2 + 70, 240),
              (70, 340), (X / 2 + 70, 340))
    barSize = (400, 60)
    namePos = (40, 40)