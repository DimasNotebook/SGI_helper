from pygame import Surface
from pygame.image import load
from pygame.transform import scale
from os.path import splitext as ext

_spr = dict()
_mus = dict()
_snd = dict()
def load_spr(name: str):
    _spr.update({ext(name)[0]: load('assets/spr/' + name)})

def load_mus(name):
    _mus.update({ext(name)[0]: 'assets/mus/' + name})

def load_snd(name):
    _snd.update({ext(name)[0]: 'assets/snd/' + name})


def spr(name: str, size: int | None = None, height: int | None = None) -> Surface:
    if name not in _spr:
        print(_spr)
        raise ValueError(f'Could not find sprite "{name}". Has the loading been done?')
    if size is not None:
        if height is not None:
            return scale(_spr[name], (size, height))
        else:
            return scale(_spr[name], (size, size))
    else:
        return _spr[name]

def mus(name):
    if name not in _mus:
        raise ValueError(f'Could not find music "{name}". Has the loading been done?')
    return _mus[name]

def snd(name):
    if name not in _snd:
        raise ValueError(f'Could not find sound "{name}". Has the loading been done?')
    return _snd[name]