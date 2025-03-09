import pygame as pg
import k
from math import ceil, sin, pi
from utils import *
itemsize = (60, 60)
smallitemsize = (32, 32)
itemsel = None
#lmb = None
screen = None
screentop = None
events = None
items = None
frame = 0

def invinit(_screen, _screentop):
    global screen
    global screentop
    screen = _screen
    screentop = _screentop

def invupdate(_frame, _lmb, _events, _items):
    global frame
    #global lmb
    global events
    global items
    frame = _frame
    #lmb = _lmb
    events = _events
    items = _items
    return itemsel

class Inventory:
    class Item:
        def __init__(self, id: str | None, pack: str, name: str, txt: str, maxstack: int=64):
            self.id = id
            self.pack = pack
            self.name = name
            if id is None:
                self.txt = pg.image.load('items/custom.png')
            else:
                self.txt_orig = pg.image.load(f'items/{pack}/textures/{txt}.png')
                self.txt = pg.transform.scale(self.txt_orig, itemsize)
                self.txt_small = pg.transform.scale(self.txt_orig, smallitemsize)
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
                    if k.k(pg.K_EQUALS) and self.num < self.item.max:
                        self.num += 1
                    elif k.k(pg.K_MINUS):
                        self.num -= 1
                        if self.num < 1:
                            self.set(None)
                if self.item is not None:
                    text = txt(screentop, self.item.name, 24, None, WHITE, 'lu')
                    pg.draw.rect(screentop, BLACK, (pg.mouse.get_pos()[0] - 5, pg.mouse.get_pos()[1] - text.get_height(), text.get_width() + 10, text.get_height()), 0, 5)
                    pg.draw.rect(screentop, WHITE, (pg.mouse.get_pos()[0] - 5, pg.mouse.get_pos()[1] - text.get_height(), text.get_width() + 10, text.get_height()), 2, 5)
                    screentop.blit(text, (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1] - text.get_height()))
                if k.lmb and not k.state_lock:
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
                    #global lmb
                    if k.lmb:
                        k.lmb = False
                        return True
                else:
                    pg.draw.rect(self.surf, BLACK, self.rect)
                pg.draw.rect(self.surf, WHITE, self.rect, 3)
                self.surf.blit(self.item.txt_small, (self.pos[0] + (self.size - self.item.txt_small.get_width()) / 2, self.pos[1] + (self.size - self.item.txt_small.get_height()) / 2))
                return False

        class PackButton:
            def __init__(self, pack, surf, x, absx, absy):
                self.name = pack.name
                self.path = pack.path
                self.surf = surf
                self.r = txt(screen, self.name, 36)
                self.rect = pg.rect.Rect(absx, absy, self.r.get_width() + 20, 60)
                self.srect = pg.rect.Rect(x, 0, self.r.get_width() + 20, 60)
                self.rpos = (x + (self.srect.width - self.r.get_width()) / 2, (self.srect.height - self.r.get_height()) / 2)

            def update(self, x, surfc):
                #res = False
                #rect = self.srect.move(x, 0)
                #rpos = (self.rpos[0] + x, self.rpos[1])
                if self.rect.move(x, 0).collidepoint(pg.mouse.get_pos()) and surfc:
                    #global lmb
                    if k.lmb:
                        k.lmb = False
                        return True
                return False
                #pg.draw.rect(screen, GREEN, self.rect.move(self.rect.x + x, self.rect.y))

            def draw(self, x, surfc, selected):
                rect = self.srect.move(x, 0)
                rpos = (self.rpos[0] + x, self.rpos[1])
                if (self.rect.move(x, 0).collidepoint(pg.mouse.get_pos()) and surfc) or selected:
                    pg.draw.rect(self.surf, (50, 50, 50), rect)
                else:
                    pg.draw.rect(self.surf, BLACK, rect)
                self.surf.blit(self.r, rpos)

        w = 300
        h = 400
        border = 10
        def __init__(self, slot, pos: tuple[int, int, int, int]):
            self.slot = slot
            #lock_state()
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
            self.surfpos = (self.pos[0] + self.border - self.xflip, self.pos[1] + self.border * self.flip - self.h * self.flip + 60 * (not self.flip))
            self.surfy = 0
            self.slots = []
            self.maxy = 0
            self.packs = []
            self.packscreen = pg.Surface((self.w - 10, 55))
            self.packrect = pg.rect.Rect(self.pos[0] + 5 - self.xflip, self.pos[1] - 60 * self.flip + 5 * (not self.flip), self.w - 10, 55)
            self.packx = 0
            #self.packrect = pg.rect.Rect(self.pos[0] + 5, self.pos[1], self.w - 10, 60)
            self.maxpackw = 0
            for pack in items.values():
                self.packs.append(self.PackButton(pack, self.packscreen, self.maxpackw, self.packrect.x + self.maxpackw, self.packrect.y))
                self.maxpackw += self.packs[-1].rect.width
            self.maxpackw -= self.w - 10
            self.selpack = 'built-in'
            self.pack_switch(self.selpack)
            #self.slots = [self.Slot(items["built-in"]["test"], self.surf, self.surfpos, (0, 0))]

        def pack_switch(self, name):
            self.slots.clear()
            for item in enumerate(items[name].items):
                self.slots.append(self.Slot(items[name].items[item[1]], self.surf, self.surfpos,
                                            ((item[0] % 5) * self.Slot.size + 10, (item[0] // 5) * self.Slot.size)))
            self.maxy = ceil(len(self.slots) / 5) * self.Slot.size + 10 - self.surf.get_height()
            self.selpack = name

        def update_slots(self):
            for slot in self.slots:
                 if slot.update(self.surfy + self.border - self.border * self.flip):
                    self.slot.set(slot.item, 1)
                    self.delis()
            for b in self.packs:
                 if b.update(self.packx, self.packrect.collidepoint(pg.mouse.get_pos())):
                     self.pack_switch(b.path)

        def draw_slots(self):
            screen.blit(self.surf, self.surfpos)
            for b in self.packs:
                b.draw(self.packx, self.packrect.collidepoint(pg.mouse.get_pos()), self.selpack == b.path)
            for b in self.packs:
                pg.draw.line(self.packscreen, WHITE, (b.srect.right + self.packx, b.srect.y + 10 - 5 * (not self.flip)),
                             (b.srect.right + self.packx, b.srect.bottom - 10 - 5 * (not self.flip)), 4)
            screen.blit(self.packscreen, self.packrect)

        def update(self):
            for e in events:
                if e.type == pg.MOUSEWHEEL:
                    if self.surf.get_rect().move(self.surfpos).collidepoint(pg.mouse.get_pos()):
                        self.surfy = min(max(-self.maxy, self.surfy + e.y * 4), 0)
                        #self.surfy += e.y * 5
                    elif self.packrect.collidepoint(pg.mouse.get_pos()):
                        self.packx = min(max(self.packx - e.x * 5, -self.maxpackw), 0)
                        #self.packx -= e.x * 5
            self.surf.fill((0, 0, 0))
            self.update_slots()
            if "k_esc" == False:
                #lock_state(True)
                self.delis()

        def draw(self):
            self.packscreen.fill((0, 0, 0))
            if self.flip:
                pg.draw.rect(screen, BLACK, (self.pos[0] - 3 - self.xflip, self.pos[1] - 3 - self.h, self.w + 6, self.h + 6), 0, 10)
                self.draw_slots()
                pg.draw.rect(screen, WHITE, (self.pos[0] - self.xflip, self.pos[1] - self.h, self.w, self.h), 5, 10)
                pg.draw.line(screen, WHITE, (self.pos[0] + 10 - self.xflip, self.pos[1] - 60), (self.pos[0] + self.w - 10 - self.xflip, self.pos[1] - 60), 5)
            else:
                pg.draw.rect(screen, BLACK, (self.pos[0] - 3 - self.xflip, self.pos[1] - 3, self.w + 6, self.h + 6), 0, 10)
                self.draw_slots()
                pg.draw.rect(screen, WHITE, (self.pos[0] - self.xflip, self.pos[1], self.w, self.h), 5, 10)
                pg.draw.line(screen, WHITE, (self.pos[0] + 10 - self.xflip, self.pos[1] + 60), (self.pos[0] + self.w - 10 - self.xflip, self.pos[1] + 60), 5)


        def delis(self):
            global itemsel
            itemsel = None
            #lock_state(True)

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
