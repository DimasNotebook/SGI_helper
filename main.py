import os
import shutil
import pygame as pg
import pygame.freetype as pgf
import json
import time
import importlib.util
from math import ceil, sin
from os import listdir
from os.path import join, isdir as osjoin, isdir
import k
from item import Item
from players import *
from utils import *
import rcs
from inventory import *
from gui import *
pg.init()
pg.font.init()
pgf.init()
window = pg.display.set_mode((X, Y), pg.NOFRAME)
screen = pg.Surface((X, Y))
screeny = 0
screentop = pg.Surface((X, Y), pg.SRCALPHA)
VERSION = "2.0"
_DEBUG = dict()
invinit(screen, screentop)
plinit(screen, screentop)
fields = []
barbuttons = ((pg.K_q, pg.K_w, pg.K_a, pg.K_s, pg.K_z, pg.K_x),
              (pg.K_e, pg.K_r, pg.K_d, pg.K_f, pg.K_c, pg.K_v),
              (pg.K_t, pg.K_y, pg.K_g, pg.K_h, pg.K_b, pg.K_n),
              (pg.K_u, pg.K_i, pg.K_j, pg.K_k, pg.K_m, pg.K_COMMA),
              (pg.K_o, pg.K_p, pg.K_l, pg.K_SEMICOLON, pg.K_PERIOD, pg.K_SLASH))
barbuttons = [["q", "w", "e", "r", "t", "y"],
              ["a", "s", "d", "f", "g", "h"],
              ["z", "x", "c", "v", "b", "n"]]
barbuttons = [["q", "w", "a", "s", "z", "x"],
              ["e", "r", "d", "f", "c", "v"],
              ["t", "y", "g", "h", "b", "n"],
              ["u", "i", "j", "k", "m", ","],
              ["o", "p", "l", ";", ".", "/"]]
SAVE_FILE_TEMPLATE = {
    "version": "2.0",
    "percentage": False,
    "radPercentage": True,
    "layout": barbuttons,
    "saves": []
}
mus_list = ['built-in:menu',    'built-in:desert',     'built-in:forest',
            'built-in:night',   'built-in:battle',     'built-in:boss_dialog',
            'built-in:sea',     'built-in:seabattle',  None]
sfx_list = ['built-in:congrats', 'built-in:death',  'built-in:pause',
            'built-in:encounter','built-in:pause',  None,
            None, None, None]

clock = pg.time.Clock()
pg.key.set_repeat(500, 50)
itemsize = (60, 60)
items = dict()

class ItemPack:
    def __init__(self, name):
        self.path = name
        with open(f'items/{name}/pack.json') as f:
            self.data = json.loads(f.read())
        self.name = self.data["name"]
        self.items = {}
        for item in self.data["items"]:
            if not "texture" in item:
                item.update({"texture": item["id"]})
            self.items.update({item["id"]: Item(item["id"], name, item["name"], item["texture"], item["maxstack"])})


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
            if not "texture" in item:
                item.update({"texture": item["id"]})
            _items.update({item["id"]: Inventory.Item(item["id"], packname, item["name"], item["texture"], item["maxstack"])})
        items.update({packname: _items})
    return packs

def DEBUG(keys: dict):
    for i in keys:
        _DEBUG.update({i: str(keys[i])})

def save_file(data: dict, layout):
    shutil.copyfile('save.json', 'save.backup.json')
    f = open('save.json', 'w', encoding='utf-8')
    _data = {
        "version": VERSION,
        "percentage": k.config("percentage"),
        "radPercentage": k.config("radPercentage"),
        "layout": layout,
        "saves": data
    }
    json.dump(_data, f, indent=4)
    f.close()

def stateq(x, escape: bool=False):
    global state
    global frame
    global state_history
    global state_lock
    global screeny
    global backbtn
    if state == game:
        save_to_list(save)
        rcs.play_mus(None)
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
            backbtn = Button(screen, '<', (40, 20, 60, 60))
        else:
            stateq(newsave)
            state_history.pop(-1)
    elif state == newsave:
        global fields
        fields = {"name": Textfield(screen, 'Save name', 50, 150),
                  "rad": Checkbox(screen, 'Radiation mode', 50, 250),
                  "players": [PlayerField(50, 350)],
                  "add": AddPlayerButton(50, 590),
                  "done": DoneButton(130, 590)}
        backbtn = Button(screen, '<', (40, 20, 60, 60))
    elif state == game:
        #global itemsel
        #itemsel = None
        global players
        match len(save["players"]):
            case 1:
                # players = [Player1(save, save["players"][0], (0, 0))]
                players = [Player1(save, save["players"][0], (0, 0, X, Y - 100))]
            case 2:
                if save["rad"]: players = [Player2rad(save, save["players"][0], (0, 0, X, Y / 2 - 50)),
                           Player2rad(save, save["players"][1], (0, Y / 2 - 50, X, Y / 2 - 50))]
                else: players = [Player2(save, save["players"][0], (0, 0, X, Y / 2 - 50)),
                           Player2(save, save["players"][1], (0, Y / 2 - 50, X, Y / 2 - 50))]
        global control_bar
        control_bar = ControlBar(screen, (0, Y - 100, X, 100))
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
        global SAVE_FILE
        global SAVES
        global barbuttons
        try:
            file = open('save.json', 'r', encoding='utf-8')
            SAVE_FILE = json.load(file)
            SAVES = SAVE_FILE["saves"]
            barbuttons = SAVE_FILE["layout"]
            k.config("percentage", SAVE_FILE["percentage"])
            k.config("radPercentage", SAVE_FILE["radPercentage"])
            file.close()
        except:
            file = open('save.json', 'w')
            json.dump(SAVE_FILE_TEMPLATE, file, indent=4)
            SAVE_FILE = SAVE_FILE_TEMPLATE
            SAVES = []
            k.config("percentage", SAVE_FILE["percentage"])
            k.config("radPercentage", SAVE_FILE["radPercentage"])
            file.close()
    elif frame == 2:
        text = '2'
    elif frame == 3:
        text = 'sprites'
        for spr in os.listdir('assets/spr'): rcs.load_spr(spr)
        mus_file = open('assets/music.json', 'r', encoding='utf-8')
        mus_json = json.load(mus_file)
        mus_file.close()
        for mus in mus_json["music"]: rcs.load_mus(mus, 'built-in')
        snd_file = open('assets/sound.json', 'r', encoding='utf-8')
        snd_json = json.load(snd_file)
        snd_file.close()
        for snd in snd_json["sounds"]: rcs.load_snd(snd, 'built-in')
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
    # for e in events:
    #     if e.type == pg.KEYDOWN:
    #         if e.key == pg.K_s:
    #             stateq(settings)
    #         elif e.key == pg.K_SPACE:
    #             stateq(savesel)
    #         elif e.key == pg.K_t:
    #             stateq(typing_test)
    if k.k(pg.K_s):         stateq(settings)
    elif k.k(pg.K_SPACE):   stateq(savesel)
    elif k.k(pg.K_t):       stateq(typing_test)
    elif k.k(pg.K_ESCAPE):  stateq(save_to_file)
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
            pass
    saveselscreenpos = max(min(saveselscreenpos - k.scrolly * 10, saveselscreen.get_height() - Y), 0)
    txt(screen, 'Select a save file', 72, (X / 2, 10), WHITE, 'u')
    if backbtn.update() or k.k(pg.K_ESCAPE):
        stateq(mainmenu)
    saveselscreen.fill(BLACK)
    for s in saveselbuttons:
        res = s.update()
        if res == 'newsave':
            stateq(newsave)
        elif res is not None:
            global save
            save = res
            stateq(game)
    screen.blit(saveselscreen, (0, saveselscreenoffset), (0, saveselscreenpos + saveselscreenoffset, X, Y - saveselscreenoffset))
    pg.draw.rect(screen, (35, 35, 35), (X - 30, saveselscreenoffset, 30, Y - saveselscreenoffset))

def newsave():
    global screeny
    screeny = screeny + k.scrolly * 7
    screeny = min(max(screeny, -fields["add"].orig[1] + Y - 100), 0)
    #txt(screen, 'Players', 72, (50, 400), WHITE, 'l')
    fields["name"].update()
    fields["rad"].update()
    fields["add"].update()
    for f in fields["players"]:
        f.update()
    if fields["done"].update():
        players = []
        for f in fields["players"]:
            players.append(f.export())
        global save
        save = {"index": 0,
                "name": fields["name"].text,
                "rad": fields["rad"].state,
                "day": 1,
                "last": time.time(),
                "players": players}
        SAVES.insert(0, save)
        stateq(game)
    pg.draw.rect(screen, BLACK, (0, 0, X, 130))
    txt(screen, 'New save creation', 72, (X / 2, 30), GREEN, 'u')
    if backbtn.update() or k.k(pg.K_ESCAPE):
        if len(SAVES) > 0:
            stateq(savesel)
        else:
            stateq(mainmenu)

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
    if k.k(pg.K_ESCAPE):
        stateq(mainmenu)

# def gameOld():
#     if len(save["players"]) == 1:
#         txt(screen, save["players"][0]["name"], 72, (50, 50), align='lu')
#     elif len(save["players"]) == 2:
#         txt(screen, '2 pl', 72, (X/2, Y/2))
#     else:
#         txt(screen, 'The save file is corrupted!', 72, (X/2, Y/2), (255, 255*int(frame / 30 % 2), 255*int(frame / 30 % 2)))
#         txt(screen, 'Press ESC to quit', 48, (X/2, Y/2+100))
#
#     for bar in bars:
#         bar.update()
#     inv.update()
#     if itemsel is not None:
#         itemsel.update()
#     pg.draw.line(screen, WHITE, (0, Y - 100), (X, Y - 100), 10)
#     txt(screen, save["name"] + ': DAY ' + str(save["day"]), 72, (50, Y - 50), align='l')

def game():
    if True:
        pass
    else:
        txt(screen, 'The save file is corrupted!', 72, (X/2, Y/2), (255, 255*int(frame / 30 % 2), 255*int(frame / 30 % 2)))
        txt(screen, 'Press ESC to quit', 48, (X/2, Y/2+100))

    if not k.state_lock and k.h(pg.K_LCTRL):
        if k.k(pg.K_EQUALS):
            save["day"] += 1
        elif k.k(pg.K_MINUS):
            save["day"] -= 1

    for p, player in enumerate(players):
        for b, button in enumerate(barbuttons[p][:4 + 2 * save["rad"]]):
            if k.k(pg.key.key_code(button)):
                for _p in players:
                    for _b in _p.bars:
                        _b.int = None
                if k.h(pg.K_LCTRL) and k.h(pg.K_LSHIFT):
                    player.bars[b].open('qa')
                elif k.h(pg.K_LSHIFT):
                    player.bars[b].set('max')
                elif k.h(pg.K_LCTRL):
                    player.bars[b].open('qs')
                else:
                    player.bars[b].open('q')

    if not k.state_lock:
        if k.k(pg.K_0):
            rcs.play_mus(None)
        for key in range(9):
            if mus_list[key] is None:
                continue
            if k.k(pg.key.key_code(str(key + 1))):
                if k.h(pg.K_LSHIFT) or k.h(pg.K_RSHIFT):
                    rcs.snd(sfx_list[key])
                else:
                    rcs.play_mus(mus_list[key])

    if itemsel is not None:
        itemsel.update()
    for player in players:
        player.update()
    if len(players) == 2:
        pg.draw.line(screen, WHITE, (0, Y / 2 - 50 - 20 * save["rad"]), (X, Y / 2 - 50 - 20 * save["rad"]), 10)
    if itemsel is not None:
        itemsel.draw()
    if control_bar.update(save) or (k.k(pg.K_ESCAPE) and not k.state_lock):
        stateq(savesel, True)

def settings():
    txt(screen, 'Would you look at this beautiful', 72, (X/2, Y/2 - 50))
    txt(screen, 'settings menu', 72, (X/2, Y/2 + 50))
    txt(screen, 'Press ESC to return to the main menu', 48, (X/2, Y/2 + 200))

def save_to_list(_save):
    for player in enumerate(players):
        _save["players"][player[0]] = player[1].export()
    SAVES[_save["index"]] = _save

def save_to_file():
    txt(screen, "Saving...", 72, (X/2, Y/2))
    save_file(SAVES, barbuttons)
    stateq(None)

lctime = -1

DEBUG_SAVE = 1
_state_list = ['loading', 'mainmenu', 'savesel', 'game', 'settings']
state = loading
state_history = []
state_lock = False
frame = 0
while state is not None:
    timer = time.time() - timerS
    events = pg.event.get()
    pressed = pg.key.get_pressed()
    #lmb = False
    k_esc = False
    for e in events:
        if e.type == pg.QUIT:
            stateq(save_to_file)
        elif e.type == pg.MOUSEBUTTONDOWN:
            if e.button == pg.BUTTON_LEFT:
                pass #lmb = True
        elif e.type == pg.KEYDOWN:
            if e.key == pg.K_ESCAPE:
                if not k.state_lock and 'Atlantic ocean' == 'the capital of Rome':
                    state_history.pop(-1)
                    if len(state_history) < 1:
                        stateq(save_to_file)
                    else:
                        stateq(state_history[-1], True)
                k_esc = True
    if pressed[pg.K_LCTRL] and pressed[pg.K_r]:
        stateq(loading)
    k.update(events)
    #print(k.k(pg.K_RETURN))
    #invupdate(frame, lmb, events, items, itemsel)
    global itemsel
    itemsel = invupdate(frame, None, events, items)
    guiupdate(screen, screeny, fields, None, pressed, events)
    window.fill(BLACK)
    if state is not None:
        screen.fill(BLACK)
        screentop.fill((0, 0, 0, 0))
        state()
        window.blit(screen, (0, 0))
        window.blit(screentop, (0, 0))
    else:
        txt(window, 'QUITTING', 72, (X/2, Y/2), WHITE)
    if False:
        font.render_to(window, (0, 0), 'FPS: '+str(int(clock.get_fps())), GREEN)
        font.render_to(window, (0, 30), 'Text buffer: '+str(len(texts)), GREEN)
        for i in enumerate(_DEBUG):
            text = font.render('(DEBUG) ' + i[1] + ': ' + _DEBUG[i[1]], GREEN)
            pg.draw.rect(window, (0, 0, 0, 128), text[1].move(0, 60 + 30 * i[0] - text[1].y))
            window.blit(text[0], (0, 60 + 30 * i[0]))
    pg.display.flip()
    frame += 1
    if state != loading:
        clock.tick(144)
pg.quit()