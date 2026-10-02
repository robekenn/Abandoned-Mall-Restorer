"""Sprite atlas loading; paths are independent of the launch directory."""
from pathlib import Path
import pygame

NAMES = (
    'bookshop_dirty', 'bookshop_clean', 'cafe_dirty', 'cafe_clean',
    'trash_bags', 'litter', 'dirt', 'bench_dirty',
    'bench_clean', 'fountain_dirty', 'fountain_clean', 'plant_dirty',
    'plant_clean', 'lamp', 'player', 'mosaic',
)


class Art:
    def __init__(self):
        path = Path(__file__).resolve().parent.parent / 'assets/sprites/mall_atlas.png'
        atlas = pygame.image.load(str(path)).convert_alpha()
        width, height = atlas.get_size()
        self.sprites = {}
        self.cache = {}
        for i, name in enumerate(NAMES):
            x, y = i % 4, i // 4
            # The generated atlas has a few tall props crossing the nominal row edge.
            # Explicit source bounds preserve the lamp globe and fountain spout.
            top, bottom = [(0,330),(330,625),(625,925),(900,height)][y]
            if name == 'fountain_clean': top, bottom = 605, 905
            if name == 'dirt': bottom = 610
            if name == 'plant_dirty': top, bottom = 620, 910
            if name == 'bench_clean': top, bottom = 650, 890
            if name == 'fountain_dirty': top, bottom = 640, 905
            cell = atlas.subsurface(pygame.Rect(x*width//4, top, width//4, bottom-top)).copy()
            bounds = cell.get_bounding_rect(min_alpha=32)
            self.sprites[name] = cell.subsurface(bounds).copy() if bounds.width else cell

    def draw(self, surface, name, center, size):
        key = name, tuple(size)
        if key not in self.cache:
            sprite = self.sprites[name]
            scale = min(size[0]/sprite.get_width(), size[1]/sprite.get_height())
            dimensions = max(1,round(sprite.get_width()*scale)), max(1,round(sprite.get_height()*scale))
            self.cache[key] = pygame.transform.smoothscale(sprite, dimensions)
        image = self.cache[key]
        surface.blit(image, image.get_rect(center=(round(center[0]),round(center[1]))))
