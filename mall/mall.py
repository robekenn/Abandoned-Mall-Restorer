import pygame
from entities.trash import Trash
from mall.store import Store
from game.settings import WORLD_SIZE


class Mall:
    def __init__(self):
        self.size = WORLD_SIZE
        self.opening_area = pygame.Rect(40, 40, 1720, 1020)
        w, h = self.size
        self.stores = [Store((100+i*410, 100, 350, 240), name, i == 0)
                       for i, name in enumerate(['Pages Bookshop', 'Retro Replay', 'Bean Street', 'The Tailor'])]
        self.fountain = pygame.Rect(700, 600, 220, 100)
        self.benches = [pygame.Rect(280, 700, 120, 35), pygame.Rect(1220, 700, 120, 35)]
        self.gates = [pygame.Rect(1760, 40, 32, 1020), pygame.Rect(40, 1060, 1752, 32)]
        self.obstacles = [pygame.Rect(0, 0, w, 40), pygame.Rect(0, h-40, w, 40),
                          pygame.Rect(0, 0, 40, h), pygame.Rect(w-40, 0, 40, h)]
        self.obstacles += [s.rect for s in self.stores] + [self.fountain] + self.benches + self.gates
        self.distant_stores = [Store((2000+i*400, 100, 340, 240), name)
                               for i, name in enumerate(['CINEMA', 'RECORDS', 'DEPARTMENT STORE'])]
        self.distant_stores += [Store((100+i*410, 1250, 350, 240), 'SOUTH GALLERY') for i in range(4)]
        positions = [(240,480),(370,550),(500,440),(620,510),(830,450),(1040,480),
                     (1150,560),(1410,450),(1540,620),(1450,820),(1110,870),(940,790),
                     (680,870),(500,780),(220,840)]
        self.trash = [Trash(p, 'dirt' if i % 3 == 0 else 'trash') for i,p in enumerate(positions)]

    @property
    def cleaned_count(self):
        return sum(t.cleaned for t in self.trash)

    def tile_restored(self, center):
        point = pygame.Vector2(center)
        return any(t.cleaned and point.distance_squared_to(t.position) < 115**2 for t in self.trash)

    @staticmethod
    def sign(surface, camera, font, text, position, color=(171, 180, 162)):
        label = font.render(text, True, color)
        point = camera.point(position)
        rect = label.get_rect(center=(round(point.x), round(point.y)))
        pygame.draw.rect(surface, (32, 45, 47), rect.inflate(24, 16))
        surface.blit(label, rect)

    def draw(self, surface, camera, font, art, target, decor):
        surface.fill((27, 36, 40))
        cleaned = self.cleaned_count
        view = surface.get_rect().move(round(camera.offset.x), round(camera.offset.y))
        # Work only on visible tiles, even as the mall grows.
        for x in range(max(40, (view.left-40)//64*64+40), min(self.size[0]-40, view.right+64), 64):
            for y in range(max(40, (view.top-40)//64*64+40), min(self.size[1]-40, view.bottom+64), 64):
                r = camera.rect((x, y, 63, 63))
                center = (x+31, y+31)
                opening = self.opening_area.collidepoint(center)
                restored = opening and self.tile_restored(center)
                parity = (x//64+y//64)%2
                color = ((142,146,124) if parity else (153,155,133)) if restored else ((79,91,87) if parity else (86,97,91))
                if not opening:
                    color = (49, 61, 62) if parity else (54, 65, 65)
                pygame.draw.rect(surface, color, r)
                pygame.draw.line(surface, (160,162,140) if restored else (101,110,99), r.topleft, r.topright)
                if not restored:
                    if (x*7+y*11)%13 < 5:
                        pygame.draw.line(surface,(65,76,72),(r.x+15,r.y+20),(r.x+33,r.y+25),2)
                    if (x//64+3*y//64)%9 == 0:
                        pygame.draw.lines(surface, (48,62,61), False,
                                          [(r.x+18,r.y+4),(r.x+22,r.y+14),(r.x+17,r.y+22)], 2)
        # Faded wayfinding inlays make the generous concourse read as public space.
        for rect in [(40, 400, 1720, 6), (40, 948, 1720, 6), (80, 400, 6, 554)]:
            pygame.draw.rect(surface, (118, 116, 91), camera.rect(rect))
        for wall in self.obstacles[:4]:
            pygame.draw.rect(surface,(53,65,65),camera.rect(wall))
        for store in self.distant_stores:
            store.draw(surface,camera,font,art,False)
        # Future galleries can be seen through closed grilles, but are not playable yet.
        for gate in self.gates:
            r = camera.rect(gate)
            pygame.draw.rect(surface, (32,45,48), r)
            if gate.height > gate.width:
                for y in range(r.top, r.bottom, 12):
                    pygame.draw.line(surface, (100,108,96), (r.left,y), (r.right,y), 3)
            else:
                for x in range(r.left, r.right, 12):
                    pygame.draw.line(surface, (100,108,96), (x,r.top), (x,r.bottom), 3)
        self.sign(surface,camera,font,'EAST GALLERY / SEALED', (1650,780))
        self.sign(surface,camera,font,'SOUTH GALLERY / SEALED', (810,1030))
        self.sign(surface,camera,font,'NORTH ARCADE', (850,380), (205,190,139))
        self.sign(surface,camera,font,'MAIN ENTRANCE', (235,965))
        # A neglected directory, large enough to imply an entire complex beyond this wing.
        r = camera.rect((90, 760, 80, 120))
        pygame.draw.rect(surface, (33,48,48), r)
        pygame.draw.rect(surface, (126,133,115), r.inflate(-8,-8))
        for dx,dy,w,h in [(12,15,24,30),(42,15,22,30),(12,52,24,40),(42,52,22,40)]:
            pygame.draw.rect(surface, (78,99,96), (r.x+dx,r.y+dy,w,h), 3)
        pygame.draw.rect(surface, (205,180,109), (r.x+14,r.y+18,5,5))
        if decor == 2:
            art.draw(surface,'mosaic',camera.point((810,790)),(210,125))
        for store in self.stores:
            if store.restored:
                glow = camera.rect(store.rect.inflate(24,40).move(0,20))
                pygame.draw.rect(surface, (172,151,95), glow, 3)
            store.draw(surface,camera,font,art,target is store)
        art.draw(surface,'fountain_clean' if cleaned == len(self.trash) else 'fountain_dirty',
                 camera.point(self.fountain.center),(245,165))
        for bench in self.benches:
            art.draw(surface,'bench_clean' if cleaned>=5 else 'bench_dirty',camera.point(bench.center),(145,85))
        for point in [(100,600),(1670,600),(500,920),(1250,920)]:
            art.draw(surface,'plant_clean' if decor else 'plant_dirty',camera.point(point),(65,90))
        if decor:
            for point in [(470,370),(880,370),(1290,370),(160,950)]:
                art.draw(surface,'lamp',camera.point(point),(55,95))
        for trash in self.trash:
            trash.draw(surface,camera,art,target is trash)
