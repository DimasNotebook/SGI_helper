import pygame as pg
import k
import time

import rcs
from utils import *
saveselscreen = pg.Surface((X - 30, 300))
saveselscreenpos = 0
saveselscreenoffset = 100

def guiupdate(_screen, _screeny, _fields, _lmb, _pressed, _events):
    global screen
    global screeny
    global fields
    #global lmb
    #global pressed
    global events
    screen = _screen
    screeny = _screeny
    fields = _fields
    #lmb = _lmb
    #pressed = _pressed
    events = _events

class Button:
    bdr = 5
    width = 5
    def __init__(self, surf, text: str | None, rect: pg.Rect | tuple[int, int, int, int] | tuple[int, int], img=None):
        self.text = text
        if text is not None:
            self.rtext = txt(screen, self.text, 48)
        elif img is not None:
            self.img = img
        else:
            raise ValueError('At least one of text/img attributes must be present.')
        if type(rect) == pg.Rect: self.rect = rect
        elif len(rect) == 4: self.rect = pg.rect.Rect(rect)
        elif len(rect) == 2: self.rect = pg.rect.Rect(rect[0], rect[1], self.rtext.get_width() + 20, self.rtext.get_height + 10)
        else: raise ValueError('Rect must either be a pg.Rect or a tuple: (x, y, width, height) or (x, y).')
        self.surf = surf

    def update(self):
        res = False
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(self.surf, (35, 35, 35), self.rect, 0, self.bdr)
            if k.lmb:
                k.lmb = False
                res = True
        else:
            pg.draw.rect(self.surf, BLACK, self.rect, 0, self.bdr)
        pg.draw.rect(self.surf, WHITE, self.rect, self.width, self.bdr)
        if self.text is not None:
            self.surf.blit(self.rtext, (self.rect[0] + (self.rect[2] - self.rtext.get_width()) / 2, self.rect[1] + (self.rect[3] - self.rtext.get_height()) / 2))
        else:
            self.surf.blit(self.img, (self.rect[0] + (self.rect[2] - self.img.get_width()) / 2, self.rect[1] + (self.rect[3] - self.img.get_height()) / 2))
        return res

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
                    return 'newsave'
                else:
                    self.save.update({"index": self.num - 1})
                    return self.save
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
                self.surf.blit(rcs.spr('radiation'), (self.x + self.rect.width - 15 - rcs.spr('radiation').get_width(), self.y + 15))
        return None

class Textfield:
    def __init__(self, surf: pg.Surface, name: str | bool, x, y, width=500, default_text: str ='', num: bool =False, positive: bool =False, center: bool =False):
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
            self.rname = txt(screen, self.name+':', 48, None, WHITE, align='l')
            self.rect = pg.rect.Rect(x + self.rname.get_width() + 100, y, self.width, 60)
            if center:
                self.pos[0] = x - (self.rect[2] + self.rname.get_width() + 100) / 2
                self.rect.x = self.pos[0] + self.rname.get_width() + 100
        else:
            if center: self.pos = [x - 60 / 2, y]
            self.rect = pg.rect.Rect(self.pos[0], y, self.width, 60)
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
        if self.name is not False:
            txt(self.surf, self.name+':', 48, (self.pos[0], self.pos[1] + 30), WHITE, align='l')
        if self.rect.collidepoint(pg.mouse.get_pos()) or self.writing:
            pg.draw.rect(self.surf, (35, 35, 35), self.rect, 0, 7)
        else:
            pg.draw.rect(self.surf, BLACK, self.rect, 0, 7)
        pg.draw.rect(self.surf, WHITE, self.rect, 4, 7)
        if k.lmb:
            if not self.writing and self.rect.collidepoint(pg.mouse.get_pos()):
                self.start_writing()
        if self.writing and (k.lmb or k.h(pg.K_RETURN)) and not self.rect.collidepoint(pg.mouse.get_pos()):
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

    def start_writing(self):
        pg.key.start_text_input()
        pg.key.set_text_input_rect(self.rect)
        self.writing = True
        self.textpos = len(self.text)
        self.starttimer = time.time()

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
    def __init__(self, surf, name: str | bool, x: int, y: int, default: bool =False, center: bool =False):
        self.surf = surf
        self.name = name
        self.center = center
        self.orig = (x, y)
        self.pos = [x, y]
        if name is not False:
            self.rname = txt(screen, self.name+':', 48, None, WHITE, align='l')
            self.rect = pg.rect.Rect(x + self.rname.get_width() + 100, y, 60, 60)
            if center:
                self.pos[0] = x - (self.rect[2] + self.rname.get_width() + 100) / 2
                self.rect.x = self.pos[0] + self.rname.get_width() + 100
        else:
            if center: self.pos = [x - 60 / 2, y]
            self.rect = pg.rect.Rect(self.pos[0], y, 60, 60)
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
            txt(self.surf, self.name + ':', 48, (self.pos[0], self.pos[1] + 30), WHITE, align='l')
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(self.surf, (35, 35, 35), self.rect, 0, 7)
            if k.lmb:
                self.state = not self.state
        else:
            pg.draw.rect(self.surf, BLACK, self.rect, 0, 7)
        pg.draw.rect(self.surf, WHITE, self.rect, 4, 7)
        if self.state:
            #screen.blit(spr_tick, self.rect)
            pg.draw.line(self.surf, WHITE, (self.rect[0] + self._of, self.rect[1] + self._of), (self.rect.right - self._of, self.rect.bottom - self._of), self._wi)
            pg.draw.line(self.surf, WHITE, (self.rect[0] + self._of, self.rect.bottom - self._of), (self.rect.right - self._of, self.rect[1] + self._of), self._wi)

    def __str__(self):
        return self.state


class AddPlayerButton:
    def __init__(self, x: int, y: int):
        self.orig = [x, y]
        self.pos = [x, y]
        self.rect = pg.rect.Rect(x, y, 60, 60)
        self._of = 15
        self._wi = 10

    def update(self, hide, y = None):
        if y is not None:
            self.pos[1] = y + screeny
        else:
            self.pos[1] = self.orig[1] + screeny
        self.rect.y = self.pos[1]
        if not hide:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                pg.draw.rect(screen, (35, 35, 35), self.rect, 0, 7)
                #global lmb
                if k.lmb:
                    fields["players"].append(PlayerField(50, len(fields["players"]) * 240 + 350))
                    self.move(240)
                    k.lmb = False
            else:
                pg.draw.rect(screen, BLACK, self.rect, 0, 7)
            pg.draw.rect(screen, WHITE, self.rect, 4, 7)
            txt(screen, '+', 72, (self.pos[0] + 30, self.pos[1] + 30))

    def move(self, x):
        self.orig[1] += x


class DoneButton:
    def __init__(self, x: int, y: int):
        self.rect = pg.rect.Rect(x, y, 240, 60)

    def update(self):
        self.rect.y = fields["add"].rect.y
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(screen, (35, 35, 35), self.rect, 0, 7)
            #global lmb
            if k.lmb:
                return True
        else:
            pg.draw.rect(screen, BLACK, self.rect, 0, 7)
        pg.draw.rect(screen, GREEN, self.rect, 4, 7)
        txt(screen, 'Create', 48, (self.rect.x + 120, self.rect.y + 30), GREEN)
        return False


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
                #global lmb
                if k.lmb:
                    k.lmb = False
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
        self.hp = Textfield(screen, 'Max HP', self.x + 50, self.y + 150, 110, '100', True, True)
        self.btn = self.DelButton(self.x, self.y + 10)

    def update(self):
        self.y = 350 + screeny + fields["players"].index(self) * 240
        if self.btn.update(self.y + 10):
            fields["players"].remove(self)
            fields["add"].move(-240)
            return
        txt(screen, 'Player ' + str(fields["players"].index(self) + 1), 72, (self.x + 80, self.y), align='lu')
        self.name.update(self.y + 80)
        self.hp.update(self.y + 150)

    def export(self):
        return {"name": self.name.text, "stats": [int(self.hp.text), 100, 100, 100, 0, 100], "maxs": [int(self.hp.text), 100, 100, 100, 100, 100], "inv": []}


class SaveSettingMenu:
    w = 400
    h = 500
    def __init__(self, surf, save):
        self.surf = surf
        self.save = save
        self.rect = pg.rect.Rect((X - self.w) / 2, (Y - self.h) / 2, self.w, self.h)
        self.borderrect = (self.rect.x - 5, self.rect.y - 5, self.w + 10, self.h + 10)
        self.donebtn = Button(self.surf, 'Dang it!', (self.rect.x + 50, self.rect.bottom - 80, self.w - 100, 60))

    def update(self):
        pg.draw.rect(self.surf, BLACK, self.borderrect, 0, 10)
        pg.draw.rect(self.surf, WHITE, self.rect, 5, 10)
        txt(self.surf, 'Oops', 72, (self.rect.centerx, self.rect.centery - 160))
        txt(self.surf, 'looks like you forgot', 36, (self.rect.centerx, self.rect.centery - 80))
        txt(self.surf, 'to update your game', 36, (self.rect.centerx, self.rect.centery - 30))
        txt(self.surf, '(settings menus will be', 24, (self.rect.centerx, self.rect.centery + 30))
        txt(self.surf, 'implemented in 2.1)', 24, (self.rect.centerx, self.rect.centery + 60))
        if self.donebtn.update() or k.k(pg.K_ESCAPE, True):
            return True

class MusSelect:
    class Selector:
        class Button:
            def __init__(self, surf, rect, absrect, mus, sound=False):
                self.surf = surf
                self.rect = pg.rect.Rect(rect)
                self.absrect = pg.rect.Rect(absrect)
                self.mus = mus
                self.sound = sound
                if mus is None:
                    self.col = RED
                elif sound:
                    self.col = WHITE
                else:
                    match mus.type:
                        case 1: self.col = (78, 245, 123)
                        case 2: self.col = (242, 136, 148)
                        case 3: self.col = (136, 198, 242)
                        case _: self.col = WHITE

            def update(self, y, hovering):
                rect = self.rect.move(0, y)
                absrect = self.absrect.move(0, y)
                if absrect.collidepoint(pg.mouse.get_pos()) and hovering:
                    pg.draw.rect(self.surf, (35, 35, 35), rect, 0, 6)
                    if k.lmb:
                        if self.mus is None: rcs.play_mus(None)
                        elif self.sound: rcs.snd(self.mus.id)
                        else: rcs.play_mus(self.mus.id)
                        return True
                else:
                    pg.draw.rect(self.surf, BLACK, rect, 0, 6)
                pg.draw.rect(self.surf, self.col, rect, 5, 6)
                if self.mus is None:
                    txt(self.surf, 'Turn off', 24, rect.center)
                else:
                    txt(self.surf, self.mus.name, 24, rect.center)

        bb = 20
        bh = 50
        def __init__(self, surf, rect, sound=False):
            self.rect = pg.rect.Rect(rect)
            self.surf = surf
            self.subsurf = pg.Surface((self.rect.width - 20, self.rect.height))
            self.y = 0
            self.sound = sound
            if sound:
                self.buttons = list()
                for i, snd in enumerate(rcs.snd_list().values()):
                    self.buttons.append(self.Button(self.subsurf,
                                                    (self.bb, (self.bh + 10) * i + self.bb, self.subsurf.get_width() - self.bb * 2, self.bh),
                                                    (self.rect.x + 10 + self.bb, self.rect.y + (self.bh + 10) * i + self.bb, self.subsurf.get_width() - self.bb * 2, self.bh),
                                                    snd, True))
            else:
                self.buttons = [self.Button(self.subsurf,(self.bb, self.bb, self.subsurf.get_width() - self.bb * 2, self.bh),
                                                    (self.rect.x + 10 + self.bb, self.rect.y + self.bb, self.subsurf.get_width() - self.bb * 2, self.bh),
                                                    None)]
                for i, mus in enumerate(rcs.mus_list().values(), 1):
                    self.buttons.append(self.Button(self.subsurf,
                                                    (self.bb, (self.bh + 10) * i + self.bb, self.subsurf.get_width() - self.bb * 2, self.bh),
                                                    (self.rect.x + 10 + self.bb, self.rect.y + (self.bh + 10) * i + self.bb, self.subsurf.get_width() - self.bb * 2, self.bh),
                                                    mus))

        def update(self):
            self.y = max(min(self.y - k.scrolly * 5, len(self.buttons) * (self.bh + 10) + self.bb - self.rect.height), 0)
            self.subsurf.fill(BLACK)
            if k.k(pg.K_ESCAPE, True):
                return False
            for b in self.buttons:
                if b.update(-self.y, self.rect.collidepoint(pg.mouse.get_pos())):
                    return True
            if k.lmb:
                return False

            pg.draw.rect(self.surf, BLACK, self.rect, 0, 10)
            self.surf.blit(self.subsurf, (self.rect.x + 10, self.rect.y))
            pg.draw.rect(self.surf, WHITE, self.rect, 5, 10)

    bd = 6
    def __init__(self, surf, rect):
        self.surf = surf
        self.rect = pg.rect.Rect(rect)
        self.sel = None

    def update(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(self.surf, (35, 35, 35), self.rect, 0, self.bd)
            if k.lmb and not k.state_lock:
                self.sel = self.Selector(self.surf, (self.rect.x, self.rect.y - 500, self.rect.width, 500))
                k.state_lock = True
                k.lmb = False
        else:
            pg.draw.rect(self.surf, BLACK, self.rect, 0, self.bd)
        if self.sel is not None:
            if self.sel.update() is not None:
                self.sel = None
                k.state_lock = False
        txt(self.surf, rcs.current_mus(), 24, (self.rect.centerx - 17, self.rect.centery))
        pg.draw.polygon(self.surf, WHITE, ((self.rect.right - 35, self.rect.centery + 5),
                                           (self.rect.right - 15, self.rect.centery + 5),
                                           (self.rect.right - 25, self.rect.centery - 5)))
        pg.draw.rect(self.surf, WHITE, self.rect, 5, self.bd)

class ControlBar:
    musw = 400
    def __init__(self, surf: pg.Surface, rect):
        self.surf = surf
        self.rect = pg.rect.Rect(rect)
        self.btnsize = self.rect.height - 40
        self.quitbtn = Button(surf, None,
            (self.rect.right - 20 - self.btnsize, int(self.rect.centery - self.btnsize / 2), self.btnsize, self.btnsize),
            rcs.spr('save_and_quit', self.btnsize - 10))
        self.setsbtn = Button(surf, None,
                              (self.rect.right - 40 - self.btnsize * 2, int(self.rect.centery - self.btnsize / 2),
                               self.btnsize, self.btnsize),
                              rcs.spr('settings', self.btnsize - 10))
        self.sfxbtn = Button(surf, None,
                              (self.rect.right - 60 - self.btnsize * 3, int(self.rect.centery - self.btnsize / 2),
                               self.btnsize, self.btnsize),
                              rcs.spr('sfx', self.btnsize - 10))
        self.musselect = MusSelect(surf, (self.rect.right - 80 - self.btnsize * 3 - self.musw, self.rect.y + 20, self.musw, self.btnsize))
        self.sfxselect = None
        self.setsmenu = None

    def update(self, save):
        pg.draw.line(screen, WHITE, (0, self.rect.y), (self.rect.width, self.rect.y), 10)
        text = txt(screen, save["name"] + ': DAY ' + str(save["day"]), 72)
        if text.get_width() > self.rect.right - 80 - self.btnsize * 3 - self.musw - 60:
            txt(screen, 'DAY ' + str(save["day"]), 72, (self.rect.centerx / 2, self.rect.centery))
            if save["day"] < 0:
                txt(screen, '???????', 24, (self.rect.centerx / 2 + 150, self.rect.y + 10), align='lu')
        else:
            screen.blit(text, (50, self.rect.centery - text.get_height() / 2))
        self.musselect.update()
        if self.quitbtn.update():
            return True
        if self.setsbtn.update():
            self.setsmenu = SaveSettingMenu(self.surf, save)
            k.state_lock = True
            k.lmb = False
        if self.sfxbtn.update() and not k.state_lock:
            self.sfxselect = MusSelect.Selector(self.surf, (self.sfxbtn.rect.right - self.musselect.rect.width, self.sfxbtn.rect.y - 500, self.musselect.rect.width, 500), True)
            k.state_lock = True
            k.lmb = False
        if self.sfxselect is not None:
            if self.sfxselect.update() is not None:
                self.sfxselect = None
                k.state_lock = False
        if self.setsmenu is not None:
            if self.setsmenu.update():
                self.setsmenu = None
                k.state_lock = False
        return False