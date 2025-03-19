import pygame as pg

state_lock = False
pressed = list()
held = dict()
lmb = False
rmb = False
scrollx = 0
scrolly = 0

_config = dict()

def update(events=None):
    global pressed
    global held
    global lmb
    global rmb
    global scrollx
    global scrolly
    pressed.clear()
    lmb = False
    rmb = False
    scrollx = 0
    scrolly = 0
    if events is None: events = pg.event.get()
    for e in events:
        if e.type == pg.KEYDOWN:
            pressed.append(e.key)
        elif e.type == pg.MOUSEBUTTONDOWN:
            if e.button == pg.BUTTON_LEFT:
                lmb = True
            elif e.button == pg.BUTTON_RIGHT:
                rmb = True
        elif e.type == pg.MOUSEWHEEL:
            scrollx = e.x
            scrolly = e.y
    held = pg.key.get_pressed()

def k(key):
    return key in pressed

def h(key):
    return held[key]

def config(key, value=None):
    if value is not None:
        _config.update({key: value})
    return _config[key]
