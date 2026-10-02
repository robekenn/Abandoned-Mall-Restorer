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

    @property
    def cleaned_count(self):
        return sum(t.cleaned for t in self.trash)

    def draw(self, surface, camera, font, art, target, decor):
        surface.fill((30,38,42))
        cleaned = self.cleaned_count
        warm = cleaned >= 10
        for x in range(40,self.size[0]-40,64):
            for y in range(40,self.size[1]-40,64):
                r = camera.rect((x,y,63,63))
                if r.colliderect(surface.get_rect()):
                    parity = (x//64+y//64)%2
                    color = ((159,151,130) if parity else (170,162,140)) if warm else ((104,111,103) if parity else (117,121,108))
                    pygame.draw.rect(surface,color,r)
                    pygame.draw.line(surface,(185,177,155) if warm else (131,135,119),r.topleft,r.topright)
                    # Scuffs fade as cleanup progresses; tiles remain worn until restoration.
                    if (x*7+y*11)%13 < max(0,8-cleaned):
                        pygame.draw.line(surface,(91,94,80),(r.x+15,r.y+20),(r.x+33,r.y+25),2)
        for wall in self.obstacles[:4]:
            r = camera.rect(wall)
            pygame.draw.rect(surface,(53,65,65),r)
            pygame.draw.rect(surface,(80,91,85),r,3)
        if decor == 2:
            art.draw(surface,'mosaic',camera.point((810,790)),(210,125))
        for store in self.stores:
            store.draw(surface,camera,font,art,target is store)
        art.draw(surface,'fountain_clean' if cleaned == len(self.trash) else 'fountain_dirty',
                 camera.point(self.obstacles[8].center),(245,165))
        for bench in self.obstacles[9:]:
            art.draw(surface,'bench_clean' if cleaned>=5 else 'bench_dirty',camera.point(bench.center),(145,85))
        for point in [(100,600),(1670,600),(500,920),(1250,920)]:
            art.draw(surface,'plant_clean' if decor else 'plant_dirty',camera.point(point),(65,90))
        if decor:
            for point in [(470,370),(880,370),(1290,370),(160,950)]:
                art.draw(surface,'lamp',camera.point(point),(55,95))
        for trash in self.trash:
            trash.draw(surface,camera,art,target is trash)
