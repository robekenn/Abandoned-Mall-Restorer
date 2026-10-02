import pygame
from entities.trash import Trash
from mall.store import Store
from game.settings import WORLD_SIZE


class Mall:
    def __init__(self):
        self.size = WORLD_SIZE
        self.opening_area = pygame.Rect(40, 40, 1720, 1020)
        w, h = self.size
        business_specs = [('Pages Bookshop', 100, 5, 'bookshop'),
                          ('Retro Replay', 250, 8, 'bookshop'),
                          ('Bean Street', 450, 12, 'cafe'),
                          ('The Tailor', 700, 16, 'bookshop')]
        self.stores = [Store((100+i*410, 100, 350, 240), name, i == 0, cost, rent, kind)
                       for i, (name, cost, rent, kind) in enumerate(business_specs)]
        self.fountain = pygame.Rect(700, 600, 220, 100)
        self.benches = [pygame.Rect(280, 700, 120, 35), pygame.Rect(1220, 700, 120, 35)]
        self.gates = [pygame.Rect(1760, 40, 32, 1020), pygame.Rect(40, 1060, 1752, 32)]
        self.obstacles = [pygame.Rect(0, 0, w, 40), pygame.Rect(0, h-40, w, 40),
                          pygame.Rect(0, 0, 40, h), pygame.Rect(w-40, 0, 40, h)]
        self.back_wall = pygame.Rect(40, 40, 1720, 300)
        self.obstacles += [s.rect for s in self.stores] + [self.fountain] + self.benches + self.gates + [self.back_wall]
        self.distant_stores = [Store((2000+i*400, 100, 340, 240), name)
                               for i, name in enumerate(['CINEMA', 'RECORDS', 'DEPARTMENT STORE'])]
        self.distant_stores += [Store((100+i*410, 1250, 350, 240), 'SOUTH GALLERY') for i in range(4)]
        positions = [(240,480),(370,550),(500,440),(620,510),(830,450),(1040,480),
                     (1150,560),(1410,450),(1540,620),(1450,820),(1110,870),(940,790),
                     (680,870),(500,780),(220,840)]
        self.floor_tiles = tuple((x+31, y+31)
                                 for x in range(40, 1760, 64)
                                 for y in range(40, 1060, 64)
                                 if not any(w.collidepoint((x+31, y+31)) for w in self.obstacles))
        self.dirty_tiles = set(self.floor_tiles)
        self._initial_cleanup_complete = False
        positions += self._coverage_positions(positions)
        self.trash = [Trash(p, 'dirt' if i % 3 == 0 else 'trash') for i,p in enumerate(positions)]
        self.initial_litter_count = len(self.trash)

    def _coverage_positions(self, seeds):
        """Cover every walkable floor tile with a reachable cleanup task."""
        floor = [p for p in self.floor_tiles if not any(w.collidepoint(p) for w in self.obstacles)]
        candidates = list(floor)
        candidates = [p for p in candidates
                      if self.opening_area.contains(pygame.Rect(p[0]-16, p[1]-16, 32, 32))
                      and not any(w.colliderect(pygame.Rect(p[0]-16, p[1]-16, 32, 32)) for w in self.obstacles)
                      and (p[0]-240)**2+(p[1]-430)**2 > 120**2
                      and all((p[0]-s.position.x)**2+(p[1]-s.position.y)**2 > 90**2 for s in self.stores)]
        coverage = [(p, {i for i,tile in enumerate(floor)
                         if (p[0]-tile[0])**2+(p[1]-tile[1])**2 < 115**2}) for p in candidates]
        uncovered = {i for i,tile in enumerate(floor)
                     if not any((p[0]-tile[0])**2+(p[1]-tile[1])**2 < 115**2 for p in seeds)}
        extra = []
        while uncovered:
            point, covered = max(coverage, key=lambda item: len(item[1] & uncovered))
            if not covered & uncovered:
                raise ValueError('Starting litter does not cover the playable floor')
            extra.append(point)
            uncovered -= covered
        return extra

    @property
    def cleaned_count(self):
        # Unlocks never regress when fresh litter appears at a previously cleaned spot.
        return sum(t.ever_cleaned or t.cleaned for t in self.trash)

    @property
    def active_litter_count(self):
        return sum(not t.cleaned for t in self.trash)

    @property
    def initial_cleanup_complete(self):
        return self._initial_cleanup_complete

    @property
    def cleanliness(self):
        return 1 - len(self.dirty_tiles) / len(self.floor_tiles)

    @property
    def next_store(self):
        return next((s for s in self.stores if not s.restored), None)

    def refresh_businesses(self):
        for i, store in enumerate(self.stores):
            store.available = store.restored or i == 0 or (
                self.initial_cleanup_complete and self.stores[i-1].restored)

    def clean_trash(self, trash):
        if trash.cleaned:
            return False
        trash.cleaned = True
        trash.ever_cleaned = True
        self.dirty_tiles = {p for p in self.dirty_tiles
                            if trash.position.distance_squared_to(p) >= 115**2}
        if all(t.ever_cleaned for t in self.trash):
            self._initial_cleanup_complete = True
        if self.initial_cleanup_complete:
            # Remaining fresh piles retain their dirt even when their patches overlap.
            self.dirty_tiles = {p for p in self.floor_tiles
                                if any(not t.cleaned and t.position.distance_squared_to(p) < 115**2
                                       for t in self.trash)}
        self.refresh_businesses()
        return True

    def respawn_trash(self, trash):
        if not trash.cleaned:
            return False
        trash.cleaned = False
        self.dirty_tiles.update(p for p in self.floor_tiles
                                if trash.position.distance_squared_to(p) < 115**2)
        return True

    def tile_restored(self, center):
        if not self.opening_area.collidepoint(center):
            return False
        key = ((int(center[0])-40)//64*64+71, (int(center[1])-40)//64*64+71)
        return key not in self.dirty_tiles

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
        pygame.draw.rect(surface, (39,53,54), camera.rect(self.back_wall))
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
        if decor == 2:
            art.draw(surface,'mosaic',camera.point((810,790)),(210,125))
        for store in self.stores:
            if store.restored:
                glow = camera.rect(store.rect.inflate(24,40).move(0,20))
                pygame.draw.rect(surface, (172,151,95), glow, 3)
            store.draw(surface,camera,font,art,target is store)
        art.draw(surface,'fountain_clean' if self.initial_cleanup_complete else 'fountain_dirty',
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
