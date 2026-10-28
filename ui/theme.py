"""Shared calm panels and readable text for the HUD, journal and conversations."""
import math
import re
import pygame

BG = (23,36,40)
PANEL = (31,47,50)
CARD = (41,59,60)
TEXT = (232,228,207)
MUTED = (156,178,172)
ACCENT = (130,196,180)
GOLD = (230,194,124)
BORDER = (66,89,87)


def key_hints(text):
    """Mark key names in generated instructions, never in player-entered text."""
    return re.sub(r'(?<!\[)\b(?:WASD|Enter|Esc|Space|Backspace|F11|F[235]|E|J|H|T|M|C|W|R)\b(?!\])', r'[\g<0>]', text)


class KeycapFont:
    """Render explicit [key] hints without changing ordinary text or save names."""

    def __init__(self, font):
        self.preferences = getattr(font, 'preferences', None)
        self.font = font.font if self.preferences is not None else font

    def parts(self, text):
        if self.preferences is not None:
            text = self.preferences.hint(text)
        # WASD expands to the player's four bindings, each in its own keycap.
        text = re.sub(r'\[([^\[\]]+)\]', lambda m: '[' + m[1].replace(' / ', '] [') + ']', text)
        return [(i % 2 == 1, part) for i, part in enumerate(re.split(r'\[([^\[\]]+)\]', text)) if part]

    def part_size(self, key, text):
        width, height = self.font.size(text)
        return (max(height + 6, width + 10), height + 4) if key else (width, height)

    def size(self, text):
        sizes = [self.part_size(key, part) for key, part in self.parts(text)]
        return sum(w for w, _ in sizes), max((h for _, h in sizes), default=self.font.get_height())

    def render(self, text, antialias, color, background=None):
        surface = pygame.Surface(self.size(text), pygame.SRCALPHA)
        if background is not None:
            surface.fill(background)
        light = sum(color[:3]) < 360
        fill = (245, 237, 216) if light else (49, 70, 69)
        edge = (167, 157, 130) if light else (101, 128, 119)
        x = 0
        for key, part in self.parts(text):
            width, height = self.part_size(key, part)
            rect = pygame.Rect(x, (surface.get_height() - height) // 2, width, height)
            if key:
                pygame.draw.rect(surface, edge, rect, border_radius=4)
                face = rect.inflate(-2, -2)
                face.height = max(1, face.height - 1)
                pygame.draw.rect(surface, fill, face, border_radius=3)
            glyph = self.font.render(part, antialias, color)
            surface.blit(glyph, glyph.get_rect(center=rect.center))
            x += width
        return surface

    def __getattr__(self, name):
        return getattr(self.font, name)

    def wrap(self, text, width):
        lines = []
        line = ''
        for word in re.findall(r'(?:\[[^\[\]]+\]|[^\s\[\]])+', text):
            candidate = (line + ' ' + word).strip()
            if line and self.size(candidate)[0] > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        return lines


def hint(surface, font, text, position, color=MUTED, *, width=None):
    """Draw measured inline keycaps; only instructional text opts into markup."""
    font = KeycapFont(font)
    lines = font.wrap(text, width) if width is not None else [text]
    x, y = position
    bounds = pygame.Rect(x, y, 0, 0)
    for line in lines:
        image = font.render(line, True, color)
        rect = surface.blit(image, (x, y))
        bounds.union_ip(rect)
        y += max(font.get_linesize(), image.get_height()) + 2
    return bounds


def hint_footer(surface, panel, font, text, *, margin=22):
    """Keep wrapped control hints inside the panel's bottom edge."""
    font = KeycapFont(font)
    lines = font.wrap(text, panel.width - margin * 2)
    height = sum(max(font.get_linesize(), font.size(line)[1]) + 2 for line in lines)
    y = panel.bottom - height - 10
    bounds = pygame.Rect(panel.x + margin, y, 0, 0)
    for line in lines:
        image = font.render(line, True, MUTED)
        bounds.union_ip(surface.blit(image, (panel.x + margin, y)))
        y += max(font.get_linesize(), image.get_height()) + 2
    return bounds


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
