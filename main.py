import shutil
import pygame as pg
import pygame.freetype as pgf
import json
import time
import importlib.util
from math import ceil, sin
from os import listdir
from os.path import join, isdir as osjoin, isdir
from item import Item
pg.init()
pg.font.init()
pgf.init()
X = pg.display.Info().current_w
Y = pg.display.Info().current_h
window = pg.display.set_mode((X, Y), pg.NOFRAME)
screen = pg.Surface((X, Y))
screeny = 0
screentop = pg.Surface((X, Y), pg.SRCALPHA)
saveselscreen = pg.Surface((X - 30, 300))
saveselscreenpos = 0
saveselscreenoffset = 100

BLACK = (0, 0 ,0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
fontname = 'Arial'
font = pgf.SysFont(fontname, 20)
font.pad = True
texts = []
textdefs = []
clock = pg.time.Clock()
pg.key.set_repeat(500, 50)
itemsize = (60, 60)

class SaveSelButton:
    def __init__(self, num: int, save, surf: pg.Surface):
        self.surf = surf
        self.num = num
        self.save = save
        if save == 'new':
            self.new = True
        else:
            self.new = False
            self.name = self.save["name"]
            self.playernames = []
            for i in self.save["players"]:
                self.playernames.append(i["name"])
            self.playertext = 'PLAYERS: '
            for i in self.playernames:
                self.playertext += i + ', '
            self.playertext = self.playertext[:-2]
            self.rad = self.save["rad"]
        self.x = 20 + (num % 2) * self.surf.get_width() / 2
        self.y = 20 + int(num / 2) * 200 + saveselscreenoffset
        self.pos = (self.x, self.y, self.surf.get_width() / 2 - 40, 160)
        self.rect = pg.rect.Rect(self.x, self.y, self.surf.get_width() / 2 - 40, 160)

    def update(self):
        self.rect.y = self.y - saveselscreenpos
        if self.rect.collidepoint(pg.mouse.get_pos()):
            if pg.mouse.get_pressed()[0]:
                if self.new:
                    stateq(newsave)
                else:
                    global save
                    save = self.save
                    stateq(game)
            pg.draw.rect(self.surf, (35, 35, 35), self.pos, 0, 10)
        if self.new:
            pg.draw.rect(self.surf, GREEN, self.pos, 5, 10)
            txt(self.surf, '+', 108, (self.x + self.rect.width / 2, self.y + self.rect.height / 2), GREEN)
        else:
            pg.draw.rect(self.surf, WHITE, self.pos, 5, 10)
            txt(self.surf, self.name, 48, (self.x + self.rect.width / 2, self.y + 10), WHITE, 'u')
            txt(self.surf, self.playertext, 24, (self.x + 15, self.y + 90), align='l')
            txt(self.surf, 'DAY ' + str(self.save["day"]), 24, (self.x + 15, self.y + 130), align='l')
            if self.rad:
                self.surf.blit(spr_radiation, (self.x + self.rect.width - 15 - spr_radiation.get_width(), self.y + 15))

class Textfield:
    def __init__(self, surf: pg.Surface, name: str | bool, x, y, width=500, default_text: str ='', num: bool =False, positive: bool =False, ):
        self.name = name
        self.surf = surf
        self.orig = (x, y)
        self.pos = [x, y]
        self.num = num
        self.positive = positive
        if num and width == 500:
            self.width = 100
        else:
            self.width = width
        if name is not False:
            self.rname = txt(self.surf, self.name+':', 48, None, WHITE, align='l')
            self.rect = pg.rect.Rect(x + self.rname.get_width() + 100, y, self.width, 60)
        else:
            self.rect = pg.rect.Rect(x, y, self.width, 60)
        self.writing = False
        self.text = default_text
        self.textpos = 0
        self.textposx = 0
        self.starttimer = time.time()

    def update(self, y = None):
        if y is not None:
            self.pos[1] = y
        else:
            self.pos[1] = self.orig[1] + screeny
        self.rect.y = self.pos[1]
        self.timer = time.time() - self.starttimer
        txt(self.surf, self.name+':', 48, (self.pos[0], self.pos[1] + 30), WHITE, align='l')
        if self.rect.collidepoint(pg.mouse.get_pos()) or self.writing:
            pg.draw.rect(self.surf, (35, 35, 35), self.rect, 0, 7)
        else:
            pg.draw.rect(self.surf, BLACK, self.rect, 0, 7)
        pg.draw.rect(self.surf, WHITE, self.rect, 4, 7)
        if lmb:
            if not self.writing and self.rect.collidepoint(pg.mouse.get_pos()):
                pg.key.start_text_input()
                pg.key.set_text_input_rect(self.rect)
                self.writing = True
                self.textpos = len(self.text)
                self.starttimer = time.time()
        if self.writing and (lmb or pressed[pg.K_RETURN]) and not self.rect.collidepoint(pg.mouse.get_pos()):
            self.writing = False
            pg.key.stop_text_input()
        if self.writing:
            pg.key.start_text_input()
            self.text, self.textpos, changed = self.typing_events(self.text, self.textpos, self.num, self.positive)
            if changed:
                self.starttimer = time.time() + 0.5
            self.typetxt(self.surf, ' '+self.text, 48, self.timer, (self.rect[0], self.rect[1] + 30), WHITE, 'l', pg.rect.Rect(self.textposx, 0, self.rect.width, self.rect.height), self.textpos)
        else:
            txt(self.surf, ' '+self.text, 48, (self.rect[0], self.rect[1] + 30), WHITE, 'l', (0, 0, self.rect.width, self.rect.height))

    def typetxt(self, surf: pg.Surface, text, size, timer, pos=None, col=(255, 255, 255), align='default', rect: pg.Rect | None =None, textpos=0):
        out = font.render(text, col, size=size)
        if pos is not None:
            # Checking that the line is not outside the textbox
            textposx = font.render(text[:textpos + 1], col, size=size)[1][2] - rect[0]
            if rect is not None:
                if textposx > rect[2] - 10:
                    rect.x += textposx - (rect[2] - 10)
                    textposx = rect[2] - 10
                elif textposx < 10:
                    rect.x += textposx - 10
                    textposx = 10
            self.textposx = rect[0]
            if align == 'l':
                surf.blit(out[0], (pos[0], pos[1] - out[1][3] / 2), rect)
            elif align == 'd':
                surf.blit(out[0], (pos[0] - out[1][2] / 2, pos[1] - out[1][3]), rect)
            else:
                surf.blit(out[0], (pos[0] - out[1][2] / 2, pos[1] - out[1][3] / 2), rect)
        if (timer * 2) % 2 < 1 or timer < 0:
            pg.draw.line(surf, WHITE, (pos[0] + textposx, pos[1] - 20), (pos[0] + textposx, pos[1] + 20), 2)
        del rect
        return out[0]

    def typing_events(self, text='', textpos=0, fint=False, fpos=False):
        changed = False
        for e in events:
            if e.type == pg.TEXTINPUT:
                if not fint or e.text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or (e.text == '-' and textpos == 0 and not fpos):
                    text = text[:textpos] + e.text + text[textpos:]
                    textpos += 1
                changed = True
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_BACKSPACE:
                    if len(text) > 0 and textpos > 0:
                        text = text[:textpos - 1] + text[textpos:]
                        textpos -= 1
                    changed = True
                elif e.key == pg.K_DELETE:
                    if len(text) > 0 and textpos < len(text):
                        text = text[:textpos] + text[textpos + 1:]
                    changed = True
                elif e.key == pg.K_LEFT:
                    if textpos > 0:
                        textpos -= 1
                    changed = True
                elif e.key == pg.K_RIGHT:
                    if textpos < len(text):
                        textpos += 1
                    changed = True
                elif e.key == pg.K_DOWN or e.key == pg.K_END:
                    textpos = len(text)
                elif e.key == pg.K_UP or e.key == pg.K_HOME:
                    textpos = 0
        return text, textpos, changed

class Checkbox:
    def __init__(self, name: str | bool, x: int, y: int, default: bool =False):
        self.name = name
        self.orig = (x, y)
        self.pos = [x, y]
        if name is not False:
            self.rname = txt(screen, self.name+':', 48, None, WHITE, align='l')
            self.rect = pg.rect.Rect(x + self.rname.get_width() + 100, y, 60, 60)
        else:
            self.rect = pg.rect.Rect(x, y, 60, 60)
        self.state = default
        self._of = 15
        self._wi = 10

    def update(self, y = None):
        if y is not None:
            self.pos[1] = y
        else:
            self.pos[1] = self.orig[1] + screeny
        self.rect.y = self.pos[1]
        if self.name is not False:
            txt(screen, self.name + ':', 48, (self.pos[0], self.pos[1] + 30), WHITE, align='l')
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(screen, (35, 35, 35), self.rect, 0, 7)
            if lmb:
                self.state = not self.state
        else:
            pg.draw.rect(screen, BLACK, self.rect, 0, 7)
        pg.draw.rect(screen, WHITE, self.rect, 4, 7)
        if self.state:
            #screen.blit(spr_tick, self.rect)
            pg.draw.line(screen, WHITE, (self.rect[0] + self._of, self.rect[1] + self._of), (self.rect.right - self._of, self.rect.bottom - self._of), self._wi)
            pg.draw.line(screen, WHITE, (self.rect[0] + self._of, self.rect.bottom - self._of), (self.rect.right - self._of, self.rect[1] + self._of), self._wi)

    def __str__(self):
        return self.state

class AddPlayerButton:
    def __init__(self, x: int, y: int):
        self.orig = [x, y]
        self.pos = [x, y]
        self.rect = pg.rect.Rect(x, y, 60, 60)
        self._of = 15
        self._wi = 10

    def update(self, y = None):
        if y is not None:
            self.pos[1] = y + screeny
        else:
            self.pos[1] = self.orig[1] + screeny
        self.rect.y = self.pos[1]
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(screen, (35, 35, 35), self.rect, 0, 7)
            global lmb
            if lmb:
                fields["players"].append(PlayerField(50, len(fields["players"]) * 240 + 350))
                self.move(240)
                lmb = False
        else:
            pg.draw.rect(screen, BLACK, self.rect, 0, 7)
        pg.draw.rect(screen, WHITE, self.rect, 4, 7)
        txt(screen, '+', 72, (self.pos[0] + 30, self.pos[1] + 30))

    def move(self, x):
        self.orig[1] += x

class PlayerField:
    class DelButton:
        def __init__(self, x: int, y: int):
            self.pos = [x, y]
            self.rect = pg.rect.Rect(x, y, 60, 60)
            self._of = 15
            self._wi = 10

        def update(self, y = None):
            if y is not None:
                self.pos[1] = y
                self.rect.y = self.pos[1]
            if self.rect.collidepoint(pg.mouse.get_pos()):
                pg.draw.rect(screen, (35, 35, 35), self.rect, 0, 7)
                global lmb
                if lmb:
                    lmb = False
                    return True
            else:
                pg.draw.rect(screen, BLACK, self.rect, 0, 7)
            pg.draw.rect(screen, WHITE, self.rect, 4, 7)
            pg.draw.line(screen, WHITE, (self.pos[0] + 15, self.pos[1] + 30), (self.pos[0] + 45, self.pos[1] + 30), 6)
            return False

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.name = Textfield(screen, 'Name', self.x + 50, self.y + 80, width=400)
        self.hp = Textfield(screen, 'Max HP', self.x + 50, self.y + 150, num=True, positive=True)
        self.btn = self.DelButton(self.x, self.y + 10)

    def update(self):
        self.y = 350 + screeny + fields["players"].index(self) * 240
        if self.btn.update(self.y + 10):
            fields["players"].remove(self)
            fields["add"].move(-240)
            return
        txt(screen, 'Player ' + str(fields["players"].index(self)), 72, (self.x + 80, self.y), align='lu')
        self.name.update(self.y + 80)
        self.hp.update(self.y + 150)

class StateBar:
    def __init__(self, pos, width: int, height: int=60, maxv: int=100, value=None, col1=(0, 200, 0), col2=(200, 0, 0)):
        self.pos = pos
        self.width = width
        self.max = maxv
        if value is not None:
            self.v = value
        else:
            self.v = maxv / 2
        self.col = (col1, col2)
        self.rect = pg.rect.Rect(self.pos[0], self.pos[1], self.width, height)

    def update(self):
        pg.draw.rect(screen, self.col[1], self.rect, 0, 15)
        pg.draw.rect(screen, self.col[0], (self.pos[0], self.pos[1], self.width * (self.v / self.max), self.rect[3]), 0, 15)

class Inventory:
    class Item:
        def __init__(self, id: str | None, pack: str, name: str, maxstack: int=64):
            self.id = id
            self.pack = pack
            self.name = name
            if id is None:
                self.txt = pg.image.load('items/custom.png')
            else:
                self.txt_small = pg.image.load(f'items/{pack}/textures/{id}.png')
                self.txt = pg.transform.scale(self.txt_small, itemsize)
            self.max = maxstack

    slotsize = 100
    slotw = 10
    slotoff = slotsize - slotw
    class Invslot:
        def __init__(self, parent, rect: tuple[int, int, int, int], item=None, amount=0):
            self.rect = rect
            self.crect = pg.rect.Rect(rect[0] + Inventory.slotw / 2, rect[1] + Inventory.slotw / 2,
                                      rect[2] - Inventory.slotw, rect[3] - Inventory.slotw)
            self.item = item
            self.num = amount
            self.parent = parent

        def set(self, item, amount=1):
            self.item = item
            if item is None:
                self.num = 0
            else:
                self.num = min(amount, item.max)

        def update(self):
            fill = BLACK
            if self.crect.collidepoint(pg.mouse.get_pos()):
                fill = (35, 35, 35)
                if self.item is not None:
                    for e in events:
                        if e.type == pg.KEYDOWN:
                            if e.key == pg.K_EQUALS and self.num < self.item.max:
                                self.num += 1
                            elif e.key == pg.K_MINUS:
                                self.num -= 1
                                if self.num < 1:
                                    self.set(None)
                if self.item is not None:
                    text = txt(screentop, self.item.name, 24, None, WHITE, 'lu')
                    pg.draw.rect(screentop, BLACK, (pg.mouse.get_pos()[0] - 5, pg.mouse.get_pos()[1] - text.get_height(), text.get_width() + 10, text.get_height()), 0, 5)
                    pg.draw.rect(screentop, WHITE, (pg.mouse.get_pos()[0] - 5, pg.mouse.get_pos()[1] - text.get_height(), text.get_width() + 10, text.get_height()), 2, 5)
                    screentop.blit(text, (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1] - text.get_height()))
                if lmb:
                    if self.item is None:
                        global itemsel
                        if itemsel is not None:
                            if itemsel.slot == self:
                                itemsel.delis()
                            else:
                                itemsel = Inventory.ItemSelect(self, (self.rect[0], self.rect[0] + self.rect[2], self.rect[1], self.rect[1] + self.rect[3]))
                        else:
                            itemsel = Inventory.ItemSelect(self, (self.rect[0], self.rect[0] + self.rect[2], self.rect[1], self.rect[1] + self.rect[3]))
                    else:
                        self.item.OnUse(self.parent.player, self)
                        self.num -= 1
                        if self.num < 1:
                            self.set(None)

            else:
                pass
            if itemsel is not None:
                if itemsel.slot == self:
                    fill = [abs(sin(frame / 100)) * 60] * 3
            pg.draw.rect(screen, fill, self.crect)
            pg.draw.rect(screen, WHITE, self.rect, Inventory.slotw)
            if self.item is not None:
                screen.blit(self.item.txt, (self.rect[0] + (self.rect[2] - self.item.txt.get_width()) / 2,
                                            self.rect[1] + (self.rect[3] - self.item.txt.get_height()) / 2))
                if self.num > 1:
                    txt(screen, str(self.num), 24, (self.rect[0] + self.rect[2] - 12,
                                                    self.rect[1] + self.rect[3] - 7), BLACK, 'rd')
                    txt(screen, str(self.num), 24, (self.rect[0] + self.rect[2] - 15,
                                                    self.rect[1] + self.rect[3] - 10), WHITE, 'rd')

    class ItemSelect:
        class Slot:
            size = 50
            def __init__(self, item, source, surfpos, pos):
                self.item = item
                self.source = source
                self.surf = source
                self.orig = pos
                self.pos = list(pos)
                self.surfpos = surfpos
                self.rect = [self.pos[0], self.pos[1], self.size, self.size]
                self.collide = pg.rect.Rect(self.pos[0] + surfpos[0], self.pos[1] + surfpos[1], self.size, self.size)
                #self.select = False

            def update(self, surfy):
                self.pos[1] = self.orig[1] + surfy
                self.rect[1] = self.pos[1]
                self.collide.y = self.pos[1] + self.surfpos[1]
                if self.collide.collidepoint(pg.mouse.get_pos()) and self.surf.get_rect().move(self.surfpos).collidepoint(pg.mouse.get_pos()):
                    pg.draw.rect(self.surf, (60, 60, 60), self.rect)
                    text = txt(screentop, self.item.name, 24, None, WHITE, 'lu')
                    pg.draw.rect(screentop, BLACK, (pg.mouse.get_pos()[0] - 5, pg.mouse.get_pos()[1] - text.get_height(), text.get_width() + 10, text.get_height()), 0, 5)
                    pg.draw.rect(screentop, WHITE, (pg.mouse.get_pos()[0] - 5, pg.mouse.get_pos()[1] - text.get_height(), text.get_width() + 10, text.get_height()), 2, 5)
                    screentop.blit(text, (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1] - text.get_height()))
                    if lmb:
                        return True
                else:
                    pg.draw.rect(self.surf, BLACK, self.rect)
                pg.draw.rect(self.surf, WHITE, self.rect, 3)
                self.surf.blit(self.item.txt_small, (self.pos[0] + (self.size - self.item.txt_small.get_width()) / 2, self.pos[1] + (self.size - self.item.txt_small.get_height()) / 2))
                return False

        w = 300
        h = 400
        border = 10
        def __init__(self, slot, pos: tuple[int, int, int, int]):
            self.slot = slot
            lock_state()
            if pos[3] > Y / 2:
                self.pos = [None, pos[2]]
                self.flip = True
            else:
                self.pos = [None, pos[3]]
                self.flip = False
            if pos[0] + self.w > X - 50:
                self.pos[0] = pos[1]
                self.xflip = self.w
            else:
                self.pos[0] = pos[0]
                self.xflip = 0
            self.surf = pg.Surface((self.w - self.border * 2, self.h - self.border - 60))
            self.surfpos = (self.pos[0] + self.border - self.xflip, self.pos[1] + self.border - self.h * bool(self.flip))
            self.surfy = 0
            self.slots = []
            self.maxy = 0
            self.pack_switch('built-in')
            #self.slots = [self.Slot(items["built-in"]["test"], self.surf, self.surfpos, (0, 0))]

        def pack_switch(self, name):
            self.slots.clear()
            for item in enumerate(items[name].items):
                self.slots.append(self.Slot(items[name].items[item[1]], self.surf, self.surfpos,
                                            ((item[0] % 5) * self.Slot.size + 10, (item[0] // 5) * self.Slot.size)))
            self.maxy = ceil(len(self.slots) / 5) * self.Slot.size + 10 - self.surf.get_height()

        def update_slots(self):
            for slot in self.slots:
                 if slot.update(self.surfy):
                    self.slot.set(slot.item, 1)
                    self.delis()
            screen.blit(self.surf, self.surfpos)

        def update(self):
            for e in events:
                if e.type == pg.MOUSEWHEEL:
                    if self.surf.get_rect().move(self.surfpos).collidepoint(pg.mouse.get_pos()):
                        #self.surfy = min(max(-self.maxy, self.surfy + e.y * 4), 0)
                        self.surfy += e.y * 5
            self.surf.fill((0, 0, 0))
            if self.flip:
                pg.draw.rect(screen, BLACK, (self.pos[0] - 3 - self.xflip, self.pos[1] - 3 - self.h, self.w + 6, self.h + 6), 0, 10)
                pg.draw.rect(screen, WHITE, (self.pos[0] - self.xflip, self.pos[1] - self.h, self.w, self.h), 5, 10)
                self.update_slots()
                pg.draw.line(screen, WHITE, (self.pos[0] + 10 - self.xflip, self.pos[1] - 60), (self.pos[0] + self.w - 10 - self.xflip, self.pos[1] - 60), 5)
            else:
                pg.draw.rect(screen, BLACK, (self.pos[0] - 3 - self.xflip, self.pos[1] - 3, self.w + 6, self.h + 6), 0, 10)
                pg.draw.rect(screen, WHITE, (self.pos[0] - self.xflip, self.pos[1], self.w, self.h), 5, 10)
            if k_esc:
                lock_state(True)
                self.delis()

        def delis(self):
            global itemsel
            itemsel = None
            lock_state(True)

    def __init__(self, player, size, pos, slots, inventory: list=[]):
        self.size = size
        self.pos = pos
        self.invsize = slots
        self.player = player
        inv = [[None, 0]] * (slots[0] * slots[1])
        for i in enumerate(inventory):
            if i[0] > len(inv):
                break
            #inv[i[0]] = [items[i[1]["pack"]][i[1]["id"]], i[1]["amount"]]
            inv[i[0]] = [items[i[1]["pack"]].items[i[1]["id"]], i[1]["amount"]]
        self.slots = []
        for y in range(slots[1]):
            for x in range(slots[0]):
                item = inv[x + y * slots[0]]
                self.slots.append(self.Invslot(self, (x*self.slotoff + pos[0], y*self.slotoff + pos[1], self.slotsize, self.slotsize),
                                              item[0], item[1]))

    def update(self):
        for slot in self.slots:
            slot.update()

    def export(self):
        inv = []
        for slot in self.slots:
            if slot.item is not None:
                inv.append({"pack": slot.item.pack, "id": slot.item.id, "amount": slot.num})
        return inv

class ItemPack:
    def __init__(self, name):
        self.name = name
        with open(f'items/{name}/pack.json') as f:
            self.data = json.loads(f.read())
        self.items = {}
        for item in self.data["items"]:
            self.items.update({item["id"]: Item(item["id"], name, item["name"], item["maxstack"])})


# thanks to ChatGPT ^^
def load_packs():
    packs = {}
    for filename in [name for name in listdir('items') if isdir('items/' + name)]:
        packs.update({filename: ItemPack(filename)})
        # filename = filename + '/pack'
        # mod_path = join('items', filename)
        # spec = importlib.util.spec_from_file_location(mod_name, mod_path)
        # mod = importlib.util.module_from_spec(spec)
        # spec.loader.exec_module(mod)

    #global items
    items = {}
    for packname in packs:
        try:
            f = open('items/' + packname + '/pack.json')
        except:
            continue
        WHY_DO_I_HAVE_TO_DO_THIS = f.read()
        pack = json.loads(WHY_DO_I_HAVE_TO_DO_THIS)
        _items = {}
        for item in pack["items"]:
            _items.update({item["id"]: Inventory.Item(item["id"], packname, item["name"], item["maxstack"])})
        items.update({packname: _items})
    return packs

def save_file(data: dict):
    shutil.copyfile('save.json', 'save.backup.json')
    f = open('save.json', 'w')
    data = json.dumps(data, indent=4)
    f.write(data)
    f.close()

def _txt(surf, text, size, pos=None, col=(255, 255, 255), align='default'):
    if pos is not None:
        font.render_to(surf, pos, text, col, size=size)
def txt(surf: pg.Surface, text, size, pos=None, col=(255, 255, 255), align='default', rect=None):
    if [surf, text, size, pos, col, align] in textdefs and False:
        out = texts[textdefs.index([surf, text, size, pos, col, align])]
    else:
        out = font.render(text, col, size=size)
        #texts.append(out)
        #textdefs.append([surf, text, size, pos, col, align])
    if pos is not None:
        match align:
            case 'lu':
                surf.blit(out[0], pos, rect)
            case 'ld':
                surf.blit(out[0], (pos[0], pos[1] - out[1][3]), rect)
            case 'r' | 'right':
                surf.blit(out[0], (pos[0] - out[1][2], pos[1] - out[1][3] / 2), rect)
            case 'l' | 'left':
                surf.blit(out[0], (pos[0], pos[1] - out[1][3] / 2), rect)
            case 'u' | 'up' | 'top':
                surf.blit(out[0], (pos[0] - out[1][2] / 2, pos[1]), rect)
            case 'd' | 'down' | 'bottom':
                surf.blit(out[0], (pos[0] - out[1][2] / 2, pos[1] - out[1][3]), rect)
            case 'rd':
                surf.blit(out[0], (pos[0] - out[1][2], pos[1] - out[1][3]), rect)
            case _:
                surf.blit(out[0], (pos[0] - out[1][2] / 2, pos[1] - out[1][3] / 2), rect)
    return out[0]

def txtr(surf, text, font, pos, col=(255, 255, 255), align='default'):
    out = font.render(text, True, col)
    surf.blit(out, pos)
    return out

def stateq(x, escape: bool=False):
    global state
    global frame
    global state_history
    global state_lock
    global screeny
    screeny = 0
    state = x
    if state == typing_test:
        global text
        global textpos
        text = ''
        textpos = 0
        pg.key.start_text_input()
    elif state == savesel:
        if len(SAVES) > 0:
            global saveselbuttons
            global saveselscreen
            saveselscreen = pg.Surface((X - 30, ceil((len(SAVES) + 1) / 2) * 200 + saveselscreenoffset))
            saveselbuttons = [SaveSelButton(0, 'new', saveselscreen)]
            for s in enumerate(SAVES):
                saveselbuttons.append(SaveSelButton(s[0] + 1, s[1], saveselscreen))
        else:
            stateq(newsave)
            state_history.pop(-1)
    elif state == newsave:
        global fields
        fields = {"name": Textfield(screen, 'Save name', 50, 150),
                  "rad": Checkbox('Radiation mode', 50, 250),
                  "players": [PlayerField(50, 350)],
                  "add": AddPlayerButton(50, 590)}
    elif state == game:
        global bars
        bars = [StateBar((200, 175), 450),
                StateBar((X / 2 + 200, 175), 450),
                StateBar((200, 300), 450),
                StateBar((X / 2 + 200, 300), 450)]
        global inv
        inv = Inventory(0, 'full', (90, 450), (15, 3), save["players"][0]["inv"])
        global itemsel
        itemsel = None
    if not escape:
        state_history.append(x)
    reset_timer()
    frame = 0

timerS = time.time()
def reset_timer(x=0):
    global timerS
    timerS = time.time() + x

def lock_state(unlock=False):
    global state_lock
    state_lock = not unlock


def loading():
    text = 'nothing'
    complete = False
    last = 10
    if frame == 0:
        text = 'fonts'
        global f72
        global f48
        global f24
        f72 = pg.font.SysFont(fontname, 72)
        f48 = pg.font.SysFont(fontname, 48)
        f24 = pg.font.SysFont(fontname, 24)
    elif frame == 1:
        text = 'save file'
        global SAVES
        try:
            file = open('save.json', 'r')
            aaaah_shoot = file.read()
            SAVES = json.loads(aaaah_shoot)
            file.close()
        except:
            file = open('save.json', 'w')
            file.write('[]')
            SAVES = []
            file.close()
    elif frame == 2:
        text = '2'
    elif frame == 3:
        text = 'sprites'
        global spr_radiation
        spr_radiation = txt(screen, '(R)', 36, align='lu')

    elif frame == 4:
        global items
        items = load_packs()
    elif frame == 4 and False:
        text = 'items'
        #global items
        items = {}
        for packname in [name for name in listdir('items') if isdir('items/' + name)]:
            try:
                f = open('items/' + packname + '/pack.json')
            except:
                continue
            WHY_DO_I_HAVE_TO_DO_THIS = f.read()
            pack = json.loads(WHY_DO_I_HAVE_TO_DO_THIS)
            _items = {}
            for item in pack["items"]:
                _items.update({item["id"]: Inventory.Item(item["id"], packname, item["name"], item["maxstack"])})
            # for i in range(1, 64):
            #     for item in pack["items"]:
            #         _items.update({item["id"] + str(i): Inventory.Item(item["id"], packname, item["name"], item["maxstack"])})
            items.update({packname: _items})
        print(items)

    elif frame > last:
        complete = True
        global lctime
        if lctime == -1:
            lctime = timer
        if timer > lctime + 1:
            stateq(mainmenu)
    if not complete:
        txt(screen, 'Loading...', 72, (X/2, Y/2), WHITE)
        txt(screen, 'Loading '+text+' ('+str(frame)+')', 48, (X/2, Y*0.6), WHITE)
    else:
        txt(screen, 'Loading complete', 72, (X/2, Y/2), GREEN)


def mainmenu():
    for e in events:
        if e.type == pg.KEYDOWN:
            if e.key == pg.K_s:
                stateq(settings)
            elif e.key == pg.K_SPACE:
                stateq(savesel)
            elif e.key == pg.K_t:
                stateq(typing_test)
    txt(screen, 'SGI Helper 2.0', 72, (X/2, Y/5), WHITE)
    txt(screen, 'this is a placeholder menu', 24, (X/2, Y*0.3), WHITE)
    txt(screen, 'Press s to enter the settings menu', 48, (10, Y*0.5), WHITE, 'l')
    txt(screen, 'Press SPACE to enter the save select menu', 48, (10, Y*0.6), WHITE, 'l')
    txt(screen, 'Press ALT+F4 to quit because I\'m too lazy to make an exit button', 48, (10, Y*0.7), WHITE, 'l')
    font.render_to(screen, (0, 20), 'This is a test!', WHITE, size=20)


def savesel():
    global saveselscreenpos
    for e in events:
        if e.type == pg.MOUSEWHEEL:
            saveselscreenpos = min(max(saveselscreenpos - e.y * 10, 0), saveselscreen.get_height() - Y)
    txt(screen, 'Select a save file', 72, (X / 2, 10), WHITE, 'u')
    saveselscreen.fill(BLACK)
    for s in saveselbuttons:
        s.update()
    screen.blit(saveselscreen, (0, saveselscreenoffset), (0, saveselscreenpos + saveselscreenoffset, X, Y - saveselscreenoffset))
    pg.draw.rect(screen, (35, 35, 35), (X - 30, saveselscreenoffset, 30, Y - saveselscreenoffset))

def newsave():
    global screeny
    for e in events:
        if e.type == pg.MOUSEWHEEL:
            screeny = screeny + e.y * 7
    screeny = min(max(screeny, -fields["add"].orig[1] + Y - 100), 0)
    #txt(screen, 'Players', 72, (50, 400), WHITE, 'l')
    fields["name"].update()
    fields["rad"].update()
    fields["add"].update()
    for f in fields["players"]:
        f.update()
    pg.draw.rect(screen, BLACK, (0, 0, X, 130))
    txt(screen, 'New save creation', 72, (X / 2, 30), GREEN, 'u')

def typing_test(pos=None):
    global text
    global textpos
    for e in events:
        if e.type == pg.TEXTINPUT:
            text = text[:textpos] + e.text + text[textpos:]
            textpos += 1
        elif e.type == pg.KEYDOWN:
            if e.key == pg.K_BACKSPACE:
                if len(text) > 0 and textpos > 0:
                    text = text[:textpos - 1] + text[textpos:]
                    textpos -= 1
            elif e.key == pg.K_DELETE:
                if len(text) > 0 and textpos < len(text):
                    text = text[:textpos] + text[textpos + 1:]
            elif e.key == pg.K_LEFT:
                if textpos > 0:
                    textpos -= 1
            elif e.key == pg.K_RIGHT:
                if textpos < len(text):
                    textpos += 1
    ltext = txt(screen, text[:textpos], 72)
    rtext = txt(screen, text[textpos:], 72)
    txt(screen, text, 72, (10, Y/2), WHITE, 'l')
    txt(screen, '|', 72, (10 + ltext.get_width() - 10, Y/2), WHITE, 'l')

def game():
    if len(save["players"]) == 1:
        txt(screen, save["players"][0]["name"], 72, (50, 50), align='lu')
    elif len(save["players"]) == 2:
        txt(screen, '2 pl', 72, (X/2, Y/2))
    else:
        txt(screen, 'The save file is corrupted!', 72, (X/2, Y/2), (255, 255*int(frame / 30 % 2), 255*int(frame / 30 % 2)))
        txt(screen, 'Press ESC to quit', 48, (X/2, Y/2+100))

    for bar in bars:
        bar.update()
    inv.update()
    if itemsel is not None:
        itemsel.update()
    pg.draw.line(screen, WHITE, (0, Y - 100), (X, Y - 100), 10)
    txt(screen, save["name"] + ': DAY ' + str(save["day"]), 72, (50, Y - 50), align='l')

def settings():
    txt(screen, 'Settings menu', 72, (X/2, Y/2), WHITE, 'center')

def save_to_file():
    txt(screen, "Saving...", 72, (X/2, Y/2))
    for _save in SAVES:
        _save["players"][0]["inv"] = inv.export()
    save_file(SAVES)

lctime = -1

_state_list = ['loading', 'mainmenu', 'savesel', 'game', 'settings']
state = loading
state_history = []
state_lock = False
frame = 0
while state is not None:
    timer = time.time() - timerS
    events = pg.event.get()
    pressed = pg.key.get_pressed()
    lmb = False
    k_esc = False
    for e in events:
        if e.type == pg.QUIT:
            stateq(save_file)
        elif e.type == pg.MOUSEBUTTONDOWN:
            if e.button == pg.BUTTON_LEFT:
                lmb = True
        elif e.type == pg.KEYDOWN:
            if e.key == pg.K_ESCAPE:
                if not state_lock:
                    state_history.pop(-1)
                    if len(state_history) < 1:
                        stateq(save_to_file)
                    else:
                        stateq(state_history[-1], True)
                k_esc = True
    if pressed[pg.K_LCTRL] and pressed[pg.K_r]:
        stateq(loading)
    window.fill(BLACK)
    if state is not None:
        screen.fill(BLACK)
        screentop.fill((0, 0, 0, 0))
        state()
        window.blit(screen, (0, 0))
        window.blit(screentop, (0, 0))
    else:
        txt(window, 'QUITTING', 72, (X/2, Y/2), WHITE)
    font.render_to(window, (0, 0), 'FPS: '+str(int(clock.get_fps())), GREEN)
    font.render_to(window, (0, 30), 'Text buffer: '+str(len(texts)), GREEN)
    if state == newsave:
        font.render_to(window, (0, 60), 'DEBUG: ' + str(screeny) + ' / ' + str(fields["add"].rect.y), GREEN)
    #pg.display.set_caption(str(int(clock.get_fps())))
    pg.display.flip()
    frame += 1
    if state != loading:
        clock.tick(144)
pg.quit()