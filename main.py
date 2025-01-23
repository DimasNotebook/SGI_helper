import pygame as pg
import pygame.freetype as pgf
import json
import time
from math import ceil
pg.init()
pg.font.init()
pgf.init()
X = pg.display.Info().current_w
Y = pg.display.Info().current_h
window = pg.display.set_mode((X, Y), pg.NOFRAME)
screen = pg.Surface((X, Y))
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
    def __init__(self, name: str | bool, x, y, width=500, default_text: str ='', num: bool =False, positive: bool =False, ):
        self.name = name
        self.pos = (x, y)
        self.num = num
        self.positive = positive
        if num and width == 500:
            self.width = 100
        else:
            self.width = width
        if name is not False:
            self.rname = txt(screen, self.name+':', 48, None, WHITE, align='l')
            self.rect = pg.rect.Rect(x + self.rname.get_width() + 100, y, self.width, 60)
        else:
            self.rect = pg.rect.Rect(x, y, self.width, 60)
        self.writing = False
        self.text = default_text
        self.textpos = 0
        self.textposx = 0
        self.starttimer = time.time()

    def update(self):
        self.timer = time.time() - self.starttimer
        txt(screen, self.name+':', 48, (self.pos[0], self.pos[1] + 30), WHITE, align='l')
        if self.rect.collidepoint(pg.mouse.get_pos()) or self.writing:
            pg.draw.rect(screen, (35, 35, 35), self.rect, 0, 7)
        else:
            pg.draw.rect(screen, BLACK, self.rect, 0, 7)
        pg.draw.rect(screen, WHITE, self.rect, 4, 7)
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
            self.typetxt(screen, ' '+self.text, 48, self.timer, (self.rect[0], self.rect[1] + 30), WHITE, 'l', pg.rect.Rect(self.textposx, 0, self.rect.width, self.rect.height), self.textpos)
        else:
            txt(screen, ' '+self.text, 48, (self.rect[0], self.rect[1] + 30), WHITE, 'l', (0, 0, self.rect.width, self.rect.height))

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
        self.pos = (x, y)
        if name is not False:
            self.rname = txt(screen, self.name+':', 48, None, WHITE, align='l')
            self.rect = pg.rect.Rect(x + self.rname.get_width() + 100, y, 60, 60)
        else:
            self.rect = pg.rect.Rect(x, y, 60, 60)
        self.state = default
        self._of = 15
        self._wi = 10

    def update(self):
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


def _txt(surf, text, size, pos=None, col=(255, 255, 255), align='default'):
    if pos is not None:
        font.render_to(surf, pos, text, col, size=size)
def txt(surf: pg.Surface, text, size, pos=None, col=(255, 255, 255), align='default', rect=None):
    if [surf, text, size, pos, col, align] in textdefs:
        out = texts[textdefs.index([surf, text, size, pos, col, align])]
    else:
        out = font.render(text, col, size=size)
        texts.append(out)
        textdefs.append([surf, text, size, pos, col, align])
    if pos is not None:
        match align:
            case 'lu':
                surf.blit(out[0], pos, rect)
            case 'r' | 'right':
                surf.blit(out[0], (pos[0] - out[1][2], pos[1] - out[1][3] / 2), rect)
            case 'l' | 'left':
                surf.blit(out[0], (pos[0], pos[1] - out[1][3] / 2), rect)
            case 'u' | 'up' | 'top':
                surf.blit(out[0], (pos[0] - out[1][2] / 2, pos[1]), rect)
            case 'd' | 'down' | 'bottom':
                surf.blit(out[0], (pos[0] - out[1][2] / 2, pos[1] - out[1][3]), rect)
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
    state = x
    if state == typing_test:
        global text
        global textpos
        text = ''
        textpos = 0
        pg.key.start_text_input()
    elif state == savesel:
        global saveselbuttons
        global saveselscreen
        saveselscreen = pg.Surface((X - 30, ceil((len(SAVES) + 1) / 2) * 200 + saveselscreenoffset))
        saveselbuttons = [SaveSelButton(0, 'new', saveselscreen)]
        for s in enumerate(SAVES):
            saveselbuttons.append(SaveSelButton(s[0] + 1, s[1], saveselscreen))
    elif state == newsave:
        global fields
        fields = [Textfield('Save name', 50, 150),
                  Checkbox('Radiation mode', 50, 250),
                  Textfield('Name', 50, 450, width=400), Textfield('Max HP', 50, 520, num=True, positive=True)]
    if not escape:
        state_history.append(x)
    reset_timer()
    frame = 0

timerS = time.time()
def reset_timer(x=0):
    global timerS
    timerS = time.time() + x


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
    txt(screen, 'New save creation', 72, (X / 2, 30), GREEN, 'u')
    txt(screen, 'Players', 72, (50, 400), WHITE, 'l')
    for f in fields:
        f.update()

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
    txt(screen, 'oops I think I forgot to make the game', 72, (X/2, Y/2), WHITE, 'c')

def settings():
    txt(screen, 'Settings menu', 72, (X/2, Y/2), WHITE, 'center')

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
    for e in events:
        if e.type == pg.QUIT:
            state = None
        elif e.type == pg.MOUSEBUTTONDOWN:
            if e.button == pg.BUTTON_LEFT:
                lmb = True
        elif e.type == pg.KEYDOWN:
            if e.key == pg.K_ESCAPE and not state_lock:
                state_history.pop(-1)
                if len(state_history) < 1:
                    state = None
                else:
                    stateq(state_history[-1], True)
    if pressed[pg.K_LCTRL] and pressed[pg.K_r]:
        stateq(loading)
    window.fill(BLACK)
    if state is not None:
        screen.fill(BLACK)
        state()
        window.blit(screen, (0, 0))
    else:
        txt(window, 'QUITTING', 72, (X/2, Y/2), WHITE)
    font.render_to(window, (0, 0), 'FPS: '+str(int(clock.get_fps())), GREEN)
    font.render_to(window, (0, 30), 'Text buffer: '+str(len(texts)), GREEN)
    #pg.display.set_caption(str(int(clock.get_fps())))
    pg.display.flip()
    frame += 1
    if state != loading:
        clock.tick(144)
pg.quit()