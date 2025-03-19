from pygame import Surface
from pygame.image import load
from pygame.transform import scale
from pygame.mixer import *
from os.path import splitext as ext
init()

class Music:
    def __init__(self, _id: str, intro: str | None, loop: str, name: str, _type: int):
        self.id = _id
        self.intro = intro
        self.loop = loop
        self.name = name
        self.type = _type
        if _type == 1:
            self.typename = 'Biome'
            self.begin = None
        elif _type == 2:
            self.typename = 'Battle'
            self.begin = 'encounter.wav'
        elif _type == 3:
            self.typename = 'Special condition'
            self.begin = None
        else:
            self.typename = 'Other'
            self.begin = None

    def play(self):
        if self.begin is not None:
            music.load('assets/snd/' + self.begin)
            music.play(0)
            if self.intro is not None:
                music.queue('assets/mus/' + self.intro, loops=0)
            music.queue('assets/mus/' + self.loop, loops=-1)
        elif self.intro is not None:
            music.load('assets/mus/' + self.intro)
            music.play(0)
            music.queue('assets/mus/' + self.loop, loops=-1)
        else:
            music.load('assets/mus/' + self.loop)
            music.play(-1)

class CustomSound:
    def __init__(self, pack, __snd):
        self.id = pack + ':' + __snd["file"]
        self.sound = Sound("assets/snd/" + __snd["file"] + '.wav')
        self.name = __snd["name"]

    def play(self, endevent=None):
        if endevent is not None:
            self.sound.get_length()
        self.sound.play()

_spr = dict()
_mus = dict()
_snd = dict()
_mus_playing = None
def load_spr(name: str):
    _spr.update({ext(name)[0]: load('assets/spr/' + name)})

def load_mus(__mus: dict, pack: str):
    _mus.update({pack + ":" + __mus["id"]: Music(pack + ":" + __mus["id"], __mus["intro"], __mus["loop"], __mus["name"], __mus["type"])})

def load_snd(__snd: dict, pack: str):
    _snd.update({pack + ":" + __snd["file"]: CustomSound('built-in', __snd)})

def spr(name: str, size: int | None = None, height: int | None = None) -> Surface:
    if name not in _spr:
        raise ValueError(f'Could not find sprite "{name}". Has the loading been done?')
    if size is not None:
        if height is not None:
            return scale(_spr[name], (size, height))
        else:
            return scale(_spr[name], (size, size))
    else:
        return _spr[name]

def mus_list():
    return _mus

def snd_list():
    return _snd

def play_mus(_id: str | None):
    global _mus_playing
    _mus_playing = _id
    if _id is None:
        music.stop()
        return
    if _id not in _mus:
        raise ValueError(f'Could not find music with ID "{_id}". Has the loading been done?')
    _mus[_id].play()

def current_mus(return_full: bool = False):
    if _mus_playing is None:
        if return_full: return None
        else: return "Nothing"
    if return_full: return _mus[_mus_playing]
    else: return _mus[_mus_playing].name

def snd(_id, _pause=False):
    if _id is None: return
    if _id not in _snd:
        raise ValueError(f'Could not find sound "{_id}". Has the loading been done?')
    _snd[_id].play()
    if _pause:
        play_mus(None)