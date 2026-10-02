import pygame
from entities.trash import Trash
from entities.trash_bin import TrashBin
from mall.store import Store
from mall.section import EastGallery, covered_positions, floor_tiles
from game.settings import WORLD_SIZE


class Mall:
    def __init__(self):
        self.size = WORLD_SIZE
        self.opening_area = pygame.Rect(40, 40, 1720, 1020)
        w, h = self.size
        business_specs = [('Northgate Supplies', 10, 0, 'bookshop'),
                          ('Pages Bookshop', 100, 5, 'bookshop'),
                          ('Retro Replay', 250, 8, 'bookshop'),
                          ('Bean Street', 450, 12, 'cafe'),
                          ('The Tailor', 700, 16, 'bookshop')]
        self.stores = [Store((100+i*328, 100, 280, 240), name, i == 0, cost, rent, kind)
                       for i, (name, cost, rent, kind) in enumerate(business_specs)]
        self.north_stores = list(self.stores)
        self.stores[0].upgrade_shop = 'north'
        self.east = EastGallery()
        self.fountain = pygame.Rect(700, 600, 220, 100)
        self.benches = [pygame.Rect(280, 700, 120, 35), pygame.Rect(1220, 700, 120, 35)]
        self.lamps = [((left.rect.right+right.rect.left)//2, 385)
                      for left,right in zip(self.stores,self.stores[1:])]
        self.plants = [(100,600),(1670,600),(500,920),(1250,920)]
        self.trash_bins = [TrashBin((bench.right+45,bench.centery),name)
                           for bench,name in zip(self.benches,('West trash bin','East trash bin'))]
        self.gates = [pygame.Rect(1760, 40, 32, 1020), pygame.Rect(40, 1060, 1752, 32)]
        self.east_gate = self.gates[0]
        self.obstacles = [pygame.Rect(0, 0, w, 40), pygame.Rect(0, h-40, w, 40),
                          pygame.Rect(0, 0, 40, h), pygame.Rect(w-40, 0, 40, h)]
        self.back_wall = pygame.Rect(40, 40, 1720, 300)
        self.obstacles += [s.rect for s in self.stores] + [self.fountain] + self.benches + self.gates + [self.back_wall] + [d.rect for d in self.trash_bins]
        # Closed sections still have collision geometry and a sealed southern boundary.
        self.obstacles += self.east.obstacles
        self.distant_stores = list(self.east.stores)
        self.distant_stores += [Store((100+i*410,1250,350,240),'SOUTH GALLERY') for i in range(4)]
        positions = [(240,480),(370,550),(500,440),(620,510),(830,450),(1040,480),
                     (1150,560),(1410,450),(1540,620),(1450,820),(1110,870),(940,790),
                     (680,870),(500,780),(220,840)]
        positions = [p for p in positions if not any(d.position.distance_squared_to(p) < 100**2 for d in self.trash_bins)]
        self.floor_tiles = floor_tiles(self.opening_area,self.obstacles)
        self.dirty_tiles = set(self.floor_tiles)
        self._initial_cleanup_complete = False
        positions += self._coverage_positions(positions)
        self.trash = [Trash(p, 'dirt' if i % 3 == 0 else 'trash') for i,p in enumerate(positions)]
        self.initial_litter_count = len(self.trash)
        self.north_trash = list(self.trash)
        self.north_floor_tiles = self.floor_tiles

    def _coverage_positions(self, seeds):
        """Cover every walkable floor tile with a reachable cleanup task."""
        return covered_positions(self.opening_area,self.floor_tiles,self.obstacles,
                                 self.stores,self.trash_bins,seeds,spawn=(240,430))

    @property
    def playable_areas(self):
        return [self.opening_area]+([self.east.area] if self.east.unlocked else [])

    @property
    def recurring_pools(self):
        pools = [self.north_trash] if self.initial_cleanup_complete and self.stores[0].restored else []
        if self.east.unlocked and self.east.initial_cleanup_complete and self.east.stores[0].restored:
            pools.append(self.east.trash)
        return pools

    @property
    def recurring_trash(self):
        return [t for pool in self.recurring_pools for t in pool]

    def unlock_east(self):
        if self.east.unlocked or not self.east.ready(self):
            return False
        self.east.unlocked = True
        gate = self.east_gate
        self.gates.remove(gate)
        self.obstacles.remove(gate)
        self.gates.append(self.east.south_gate)
        self.stores += self.east.stores
        self.distant_stores = [s for s in self.distant_stores if s not in self.east.stores]
        self.floor_tiles += self.east.floor_tiles
        self.dirty_tiles.update(self.east.floor_tiles)
        self.trash += self.east.trash
        self.benches += self.east.benches
        self.trash_bins += self.east.bins
        self.lamps += self.east.lamps
        self.plants += self.east.plants
        self.refresh_businesses()
        return True

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
        for i,store in enumerate(self.north_stores):
            store.available = store.restored or i == 0 or (
                self.initial_cleanup_complete and self.stores[i-1].restored)
        for i,store in enumerate(self.east.stores):
            store.available = self.east.unlocked and (store.restored or i == 0 or (
                self.east.initial_cleanup_complete and self.east.stores[i-1].restored))

    def clean_trash(self, trash):
        if trash.cleaned or trash not in self.trash:
            return False
        trash.cleaned = True
        trash.ever_cleaned = True
        tiles = self.north_floor_tiles if trash in self.north_trash else self.east.floor_tiles
        self.dirty_tiles.difference_update(p for p in tiles
                                          if trash.position.distance_squared_to(p) < 115**2)
        if all(t.ever_cleaned for t in self.north_trash):
            self._initial_cleanup_complete = True
        if self.east.unlocked and all(t.ever_cleaned for t in self.east.trash):
            self.east.initial_cleanup_complete = True
        # Each completed section retains dirt under overlapping fresh piles.
        sections = [(self.north_floor_tiles,self.north_trash,self.initial_cleanup_complete)]
        if self.east.unlocked:
            sections.append((self.east.floor_tiles,self.east.trash,self.east.initial_cleanup_complete))
        for tiles,pool,complete in sections:
            if complete:
                self.dirty_tiles.difference_update(tiles)
                self.dirty_tiles.update(p for p in tiles if any(
                    not t.cleaned and t.position.distance_squared_to(p) < 115**2 for t in pool))
        self.refresh_businesses()
        return True

    def respawn_trash(self, trash):
        if not trash.cleaned or trash not in self.trash:
            return False
        trash.cleaned = False
        tiles = self.north_floor_tiles if trash in self.north_trash else self.east.floor_tiles
        self.dirty_tiles.update(p for p in tiles
                                if trash.position.distance_squared_to(p) < 115**2)
        return True

    def tile_restored(self, center):
        if not any(area.collidepoint(center) for area in self.playable_areas):
            return False
        key = ((int(center[0])-40)//64*64+71, (int(center[1])-40)//64*64+71)
        return key not in self.dirty_tiles

    def draw(self, surface, camera, font, art, target, upgrades):
        surface.fill((27, 36, 40))
        view = surface.get_rect().move(round(camera.offset.x), round(camera.offset.y))
        # Work only on visible tiles, even as the mall grows.
        for x in range(max(40, (view.left-40)//64*64+40), min(self.size[0]-40, view.right+64), 64):
            for y in range(max(40, (view.top-40)//64*64+40), min(self.size[1]-40, view.bottom+64), 64):
                r = camera.rect((x, y, 63, 63))
                center = (x+31, y+31)
                opening = any(area.collidepoint(center) for area in self.playable_areas)
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
        pygame.draw.rect(surface,(39,53,54),camera.rect(self.east.back_wall))
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
        self.east.draw_marker(surface,camera,font,target is self.east)
        if self.east.unlocked:
            art.draw(surface,'fountain_clean' if 'fountain_east' in upgrades.decor else 'fountain_dirty',
                     camera.point(self.east.fountain.center),(245,165))
            if 'mosaic_east' in upgrades.decor:
                art.draw(surface,'mosaic',camera.point((2690,790)),(210,125))
        if 'mosaic' in upgrades.decor:
            art.draw(surface,'mosaic',camera.point((810,790)),(210,125))
        for store in self.stores:
            if store.restored:
                glow = camera.rect(store.rect.inflate(24,40).move(0,20))
                pygame.draw.rect(surface, (172,151,95), glow, 3)
            store.draw(surface,camera,font,art,target is store)
        art.draw(surface,'fountain_clean' if 'fountain' in upgrades.decor else 'fountain_dirty',
                 camera.point(self.fountain.center),(245,165))
        for i,bench in enumerate(self.benches):
            art.draw(surface,'bench_clean' if f'bench_{i}' in upgrades.decor else 'bench_dirty',camera.point(bench.center),(145,85))
        for i,point in enumerate(self.plants):
            art.draw(surface,'plant_clean' if f'plant_{i}' in upgrades.decor else 'plant_dirty',camera.point(point),(65,90))
        for i,point in enumerate(self.lamps):
            art.draw(surface,'lamp' if f'lamp_{i}' in upgrades.decor else 'lamp_off',camera.point(point),(55,95))
        for trash_bin in self.trash_bins:
            trash_bin.draw(surface,camera,art,font,target is trash_bin)
        for trash in self.trash:
            trash.draw(surface,camera,art,target is trash)
