import pygame
from entities.trash import Trash
from mall.store import Store
from game.settings import WORLD_SIZE


class Mall:
    def __init__(self):
        self.size = WORLD_SIZE
        w, h = self.size
        self.stores = [Store((100+i*410, 100, 350, 240), name, i == 0)
                       for i, name in enumerate(["Pages Bookshop", "Retro Replay", "Bean Street", "Coming soon"])]
        self.obstacles = [pygame.Rect(0, 0, w, 40), pygame.Rect(0, h-40, w, 40),
                          pygame.Rect(0, 0, 40, h), pygame.Rect(w-40, 0, 40, h)]
        self.obstacles += [s.rect for s in self.stores]
        self.obstacles += [pygame.Rect(700, 600, 220, 100), pygame.Rect(280, 700, 120, 35),
                           pygame.Rect(1220, 700, 120, 35)]
        positions = [(240,480),(370,550),(500,440),(620,510),(830,450),(1040,480),
                     (1150,560),(1410,450),(1540,620),(1450,820),(1110,870),(940,790),
                     (680,870),(500,780),(220,840)]
        self.trash = [Trash(p, "dirt" if i % 3 == 0 else "trash") for i,p in enumerate(positions)]

    def draw(self, surface, camera, font, target):
        surface.fill((30, 38, 42))
        for x in range(40, self.size[0]-40, 64):
            for y in range(40, self.size[1]-40, 64):
                r = camera.rect((x, y, 63, 63))
                if r.colliderect(surface.get_rect()):
                    c = (111, 116, 107) if (x//64+y//64)%2 else (119, 123, 114)
                    pygame.draw.rect(surface, c, r)
        for wall in self.obstacles[:4]:
            pygame.draw.rect(surface, (55, 66, 68), camera.rect(wall))
        for store in self.stores:
            store.draw(surface, camera, font, target is store)
        fountain = camera.rect(self.obstacles[8])
        pygame.draw.ellipse(surface, (68, 79, 77), fountain)
        pygame.draw.ellipse(surface, (96, 118, 118), fountain.inflate(-20, -20))
        for bench in self.obstacles[9:]:
            pygame.draw.rect(surface, (100, 76, 55), camera.rect(bench), border_radius=5)
        for trash in self.trash:
            trash.draw(surface, camera, target is trash)
