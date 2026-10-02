"""Small, hand-authored pixel sprites; no atlas download is required."""
import pygame

PALETTE = {
    'ink': '#29383b', 'shadow': '#455354', 'stone': '#7d8880',
    'light': '#bdbea4', 'cream': '#e4d6a4', 'wood': '#856448',
    'rust': '#ac784f', 'teal': '#548b83', 'green': '#709657',
    'leaf': '#a5bf65', 'water': '#71afbc', 'blue': '#426b83',
    'skin': '#d6a875', 'gold': '#dfb45e',
}


def canvas(size=(24, 24)):
    return pygame.Surface(size, pygame.SRCALPHA)


def box(s, color, rect):
    pygame.draw.rect(s, PALETTE[color], rect)


def store(kind, clean):
    s = canvas((48, 40))
    box(s, 'ink', (1, 2, 46, 36))
    box(s, 'teal' if clean else 'shadow', (3, 4, 42, 32))
    box(s, 'cream' if clean else 'stone', (4, 5, 40, 6))
    box(s, 'ink', (5, 16, 15, 18))
    box(s, 'ink', (28, 16, 15, 18))
    box(s, 'gold' if clean else 'stone', (7, 18, 11, 13))
    box(s, 'gold' if clean else 'stone', (30, 18, 11, 13))
    box(s, 'ink', (21, 16, 6, 20))
    box(s, 'water' if clean else 'shadow', (22, 18, 4, 12))
    box(s, 'cream', (25, 28, 1, 1))
    if clean:
        for x in range(4, 44, 5):
            box(s, 'rust' if kind == 'cafe' else 'teal', (x, 12, 3, 3))
        if kind == 'bookshop':
            for x in (8, 11, 14, 31, 34, 37):
                box(s, 'wood' if x % 2 else 'teal', (x, 24, 2, 5))
            box(s, 'wood', (7, 29, 11, 1))
            box(s, 'wood', (30, 29, 11, 1))
        else:
            for x in (9, 33):
                box(s, 'cream', (x, 25, 5, 3))
                box(s, 'rust', (x, 28, 5, 1))
    else:
        for x in (5, 28):
            box(s, 'wood', (x, 20, 15, 4))
            box(s, 'rust', (x, 28, 15, 3))
            box(s, 'light', (x + 2, 21, 1, 1))
            box(s, 'light', (x + 12, 29, 1, 1))
        box(s, 'rust', (37, 7, 5, 2))
        box(s, 'stone', (3, 33, 5, 2))
    box(s, 'light' if clean else 'stone', (0, 37, 48, 3))
    return s


def prop(name):
    s = canvas()
    if name.startswith('bench'):
        clean = name.endswith('clean')
        box(s, 'ink', (2, 7, 20, 12))
        for y in (8, 11, 15):
            box(s, 'rust' if clean else 'wood', (3, y, 18, 2))
        if not clean:
            box(s, 'ink', (13, 8, 4, 5))
        for x in (4, 18):
            box(s, 'shadow', (x, 17, 2, 5))
    elif name.startswith('fountain'):
        clean = name.endswith('clean')
        box(s, 'ink', (3, 12, 18, 10))
        box(s, 'stone', (1, 13, 22, 6))
        box(s, 'water' if clean else 'shadow', (3, 14, 18, 3))
        box(s, 'light', (4, 20, 16, 2))
        box(s, 'stone', (10, 7, 4, 8))
        box(s, 'light', (7, 6, 10, 3))
        if clean:
            box(s, 'water', (11, 2, 2, 5))
            box(s, 'cream', (11, 2, 1, 2))
            box(s, 'cream', (5, 15, 3, 1))
        else:
            box(s, 'wood', (5, 15, 4, 1))
            box(s, 'rust', (15, 16, 3, 1))
    elif name.startswith('plant'):
        box(s, 'ink', (6, 14, 12, 8))
        box(s, 'rust', (7, 16, 10, 5))
        box(s, 'wood', (6, 14, 12, 2))
        box(s, 'wood', (11, 6, 2, 9))
        if name.endswith('clean'):
            for rect in ((5, 6, 7, 6), (10, 3, 7, 7), (13, 8, 7, 6)):
                box(s, 'green', rect)
            box(s, 'leaf', (10, 4, 4, 3))
            box(s, 'leaf', (6, 7, 3, 2))
        else:
            box(s, 'wood', (7, 7, 5, 2))
            box(s, 'rust', (13, 4, 3, 4))
    elif name in ('lamp','lamp_off'):
        box(s, 'ink', (9, 20, 7, 3))
        box(s, 'shadow', (11, 7, 3, 14))
        box(s, 'ink', (7, 2, 11, 6))
        box(s, 'gold' if name == 'lamp' else 'stone', (9, 3, 7, 4))
        box(s, 'cream' if name == 'lamp' else 'shadow', (10, 3, 2, 3))
        box(s, 'shadow', (9, 1, 7, 1))
    elif name == 'dumpster':
        box(s, 'ink', (2, 9, 20, 12))
        box(s, 'teal', (3, 11, 18, 8))
        box(s, 'shadow', (1, 7, 22, 4))
        box(s, 'stone', (3, 7, 18, 1))
        box(s, 'cream', (9, 13, 6, 4))
        box(s, 'green', (11, 14, 2, 2))
        box(s, 'ink', (4, 21, 3, 2))
        box(s, 'ink', (17, 21, 3, 2))
    elif name == 'trash_bags':
        for x, y in ((2, 9), (11, 5)):
            box(s, 'ink', (x, y + 3, 10, 10))
            box(s, 'shadow', (x + 1, y + 2, 8, 9))
            box(s, 'stone', (x + 2, y + 3, 2, 4))
            box(s, 'ink', (x + 3, y, 4, 2))
    elif name == 'litter':
        box(s, 'ink', (2, 12, 8, 6))
        box(s, 'cream', (3, 12, 7, 5))
        box(s, 'stone', (5, 14, 3, 1))
        box(s, 'rust', (14, 9, 4, 8))
        box(s, 'light', (13, 8, 6, 2))
        box(s, 'teal', (17, 18, 5, 3))
    elif name == 'dirt':
        for rect in ((2, 11, 8, 4), (7, 9, 10, 8), (16, 12, 6, 3), (5, 18, 2, 1)):
            box(s, 'wood', rect)
        box(s, 'rust', (9, 12, 4, 2))
    elif name == 'mosaic':
        box(s, 'ink', (1, 1, 22, 22))
        box(s, 'cream', (2, 2, 20, 20))
        for y in range(4, 21, 4):
            for x in range(4, 21, 4):
                box(s, 'teal' if (x + y) % 8 else 'gold', (x, y, 2, 2))
        box(s, 'rust', (9, 9, 6, 6))
        box(s, 'gold', (11, 11, 2, 2))
    return s


def worker(facing, frame):
    """16x24 worker: idle, left stride, passing pose, right stride."""
    s = canvas((16, 24))
    stride = (0, -1, 0, 1)[frame]
    bob = 1 if frame in (1, 3) else 0
    # Legs are separate so each stride visibly alternates boots.
    for x, offset in ((5, stride), (9, -stride)):
        box(s, 'blue', (x, 16 + bob, 3, 5 + offset))
        box(s, 'ink', (x - (1 if facing == 'left' else 0), 20 + bob + offset, 4, 2))
    box(s, 'ink', (4, 9 + bob, 8, 8))
    box(s, 'teal', (5, 10 + bob, 6, 6))
    box(s, 'gold', (5, 11 + bob, 1, 4))
    box(s, 'gold', (10, 11 + bob, 1, 4))
    for x, offset in ((2, -stride), (12, stride)):
        box(s, 'teal', (x, 10 + bob + offset, 2, 5))
        box(s, 'skin', (x, 14 + bob + offset, 2, 2))
    box(s, 'ink', (4, 2 + bob, 8, 8))
    box(s, 'skin' if facing != 'up' else 'wood', (5, 4 + bob, 6, 5))
    box(s, 'rust', (4, 2 + bob, 8, 3))
    box(s, 'gold', (5, 2 + bob, 5, 1))
    if facing == 'down':
        box(s, 'ink', (6, 6 + bob, 1, 1))
        box(s, 'ink', (9, 6 + bob, 1, 1))
    elif facing in ('left', 'right'):
        x = 4 if facing == 'left' else 11
        box(s, 'skin', (x, 5 + bob, 2, 3))
        box(s, 'ink', (x, 5 + bob, 1, 1))
        box(s, 'rust', (x, 3 + bob, 2, 1))
    return s


class Art:
    def __init__(self):
        self.sprites = {}
        self.cache = {}
        for kind in ('bookshop', 'cafe'):
            for state in ('dirty', 'clean'):
                self.sprites[f'{kind}_{state}'] = store(kind, state == 'clean')
        for name in ('trash_bags', 'litter', 'dirt', 'bench_dirty', 'bench_clean',
                     'fountain_dirty', 'fountain_clean', 'plant_dirty', 'plant_clean', 'lamp', 'lamp_off', 'dumpster', 'mosaic'):
            self.sprites[name] = prop(name)
        for facing in ('down', 'up', 'left', 'right'):
            for frame in range(4):
                self.sprites[f'player_{facing}_{frame}'] = worker(facing, frame)

    def draw(self, surface, name, center, size):
        key = name, tuple(size)
        if key not in self.cache:
            sprite = self.sprites[name]
            # Integer nearest-neighbor scaling keeps every source pixel square.
            scale = max(1, int(min(size[0] / sprite.get_width(), size[1] / sprite.get_height())))
            dimensions = sprite.get_width() * scale, sprite.get_height() * scale
            self.cache[key] = pygame.transform.scale(sprite, dimensions)
        image = self.cache[key]
        surface.blit(image, image.get_rect(center=(round(center[0]), round(center[1]))))
