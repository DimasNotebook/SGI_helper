import pygame as pg
import pygame.freetype as pgf
pgf.init()
pg.init()
X = pg.display.Info().current_w
Y = pg.display.Info().current_h
BLACK = (0, 0 ,0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
fontname = 'Arial'
texts = []
textdefs = []
font = pgf.SysFont(fontname, 20)
font.pad = True
def _txt(surf, text, size, pos=None, col=(255, 255, 255), align='default'):
    if pos is not None:
        font.render_to(surf, pos, text, col, size=size)
def txt(surf, text, size, pos=None, col=(255, 255, 255), align='default', rect=None):
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
