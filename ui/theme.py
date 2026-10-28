"""Shared calm panels and readable text for the HUD, journal and conversations."""
import math
import pygame

BG = (23,36,40)
PANEL = (31,47,50)
CARD = (41,59,60)
TEXT = (232,228,207)
MUTED = (156,178,172)
ACCENT = (130,196,180)
GOLD = (230,194,124)
BORDER = (66,89,87)


def frame(surface, rect, color=PANEL, border=True):
    pygame.draw.rect(surface,color,rect,border_radius=9)
    if border:
        pygame.draw.rect(surface,BORDER,rect,1,border_radius=9)


def dim(surface):
    shade = pygame.Surface(surface.get_size(),pygame.SRCALPHA)
    shade.fill((8,16,20,220));surface.blit(shade,(0,0))


def button(surface, rect, label, font, *, enabled=True):
    """Consistent visible affordance for mouse actions and keyboard shortcuts."""
    hovered = enabled and rect.collidepoint(pygame.mouse.get_pos())
    frame(surface, rect, CARD if enabled else PANEL)
    if hovered:
        pygame.draw.rect(surface, ACCENT, rect, 2, border_radius=9)
    text = font.render(label, True, TEXT if enabled else MUTED)
    surface.blit(text, text.get_rect(center=rect.center))


def back_rect(panel):
    return pygame.Rect(panel.right-90, panel.y+14, 70, 32)


def wrap(font, text, width):
    lines=[];line=''
    for word in text.split():
        candidate=(line+' '+word).strip()
        if line and font.size(candidate)[0]>width:
            lines.append(line);line=word
        else:
            line=candidate
    if line:lines.append(line)
    return lines


def clock(seconds):
    seconds=max(0,math.ceil(seconds))
    return f'{seconds//60}:{seconds%60:02}'
