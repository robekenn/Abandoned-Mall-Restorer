import pygame
from entities.trash import Trash
from entities.trash_bin import TrashBin
from mall.store import Store
from mall.businesses import opposite_stores
from mall.furniture import bench_footprint, fountain_footprint
from mall.delivery import DeliveryPoint
from mall.section import EastGallery, later_galleries, covered_positions, floor_tiles
from game.settings import WORLD_SIZE
from mall.social import SocialTable, place_tables


class Mall:
    def __init__(self):
        self.size = WORLD_SIZE
        self.entrance=pygame.Vector2(52,1063)
        self.entrance_rect=pygame.Rect(12,1005,52,116)
        self.opening_area = pygame.Rect(40, 40, 1720, 1440)
        w, h = self.size
        business_specs = [('Northgate Supplies', 10, 0, 'bookshop'),
                          ('Pages Bookshop', 100, 5, 'bookshop'),
                          ('Retro Replay', 250, 8, 'bookshop'),
                          ('Bean Street', 450, 12, 'cafe'),
                          ('The Tailor', 700, 16, 'bookshop')]
        self.stores = [Store((100+i*328, 100, 280, 240), name, i == 0, cost, rent, kind)
                       for i, (name, cost, rent, kind) in enumerate(business_specs)]
        self.stores += opposite_stores('north',self.opening_area)
        self.north_stores = list(self.stores)
        self.stores[0].upgrade_shop = 'north'
        self.east = EastGallery()
        self.garden,self.commons=later_galleries()
        self.regions=[self.east,self.garden,self.commons]
        self.fountain = pygame.Rect(700, 600, 220, 100)
        self.benches = [pygame.Rect(280, 700, 120, 35), pygame.Rect(1220, 700, 120, 35)]
        self.lamps = [((left.rect.right+right.rect.left)//2, 385)
                      for left,right in zip(self.stores[:5],self.stores[1:5])]
        self.plants = [(100,600),(1670,600),(500,920),(1250,920)]
        self.trash_bins = [TrashBin((bench.right+45,bench.centery),name)
                           for bench,name in zip(self.benches,('West trash bin','East trash bin'))]
        self.gates = [pygame.Rect(1760, 40, 32, 1440), pygame.Rect(40, 1480, 1752, 32)]
        self.east_gate = self.gates[0]
        self.commons_divider=pygame.Rect(1760,1512,32,1488)
        self.east.gate_rects=[self.east_gate]
        self.garden.gate_rects=[self.gates[1]]
        self.commons.gate_rects=[self.commons_divider,self.east.south_gate]
        self.obstacles = [pygame.Rect(0, 0, w, 40), pygame.Rect(0, h-40, w, 40),
                          pygame.Rect(0, 0, 40, h), pygame.Rect(w-40, 0, 40, h)]
        self.boundary_walls = [r.copy() for r in self.obstacles]
        self.back_wall = pygame.Rect(40, 40, 1720, 300)
        self.front_wall=pygame.Rect(232,self.opening_area.bottom-280,1528,280)
        self.delivery = DeliveryPoint((100,900),'North')
        self.furniture_obstacles = [fountain_footprint(self.fountain)]+[bench_footprint(b) for b in self.benches]
        self.obstacles += [s.rect for s in self.stores]+self.gates+[self.back_wall,self.front_wall]
        self.floor_obstacles = list(self.obstacles)
        self.obstacles += [d.rect for d in self.trash_bins]+[self.delivery.rect]+self.furniture_obstacles
        # Closed sections still have collision geometry and a sealed southern boundary.
        self.obstacles += [wall for region in self.regions for wall in region.obstacles]+[self.commons_divider]
        self.distant_stores = [store for region in self.regions for store in region.stores]
        positions = [(240,480),(370,550),(500,440),(620,510),(830,450),(1040,480),
                     (1150,560),(1410,450),(1540,620),(1450,820),(1110,870),(940,790),
                     (680,870),(500,780),(220,840)]
        positions = [p for p in positions if not any(d.position.distance_squared_to(p) < 100**2 for d in self.trash_bins)]
        self.floor_tiles = floor_tiles(self.opening_area,self.floor_obstacles)
        self.dirty_tiles = set(self.floor_tiles)
        self._initial_cleanup_complete = False
        positions += self._coverage_positions(positions)
        self.trash = [Trash(p, 'dirt' if i % 3 == 0 else 'trash') for i,p in enumerate(positions)]
        self.initial_litter_count = len(self.trash)
        self.north_trash = list(self.trash)
        self.north_floor_tiles = list(self.floor_tiles)
        # Generate the original litter IDs first so Continue preserves cleanup progress.
        self._arrange_north_arcade()
        self.social_tables=[]
        for i,x in enumerate((455,1287)):
            table=SocialTable(pygame.Vector2(x,681),
                              (pygame.Vector2(x-64,711),pygame.Vector2(x+64,711)),
                              'north',f'table_{i}')
            self.social_tables.append(table);self.obstacles.append(table.footprint)



    def _arrange_north_arcade(self):
        for footprint in self.furniture_obstacles:self.obstacles.remove(footprint)
        self.fountain.update(750,670,220,100)
        self.benches[0].update(395,834,120,35)
        self.benches[1].update(1227,834,120,35)
        self.furniture_obstacles=[fountain_footprint(self.fountain)]+[bench_footprint(b) for b in self.benches]
        self.obstacles += self.furniture_obstacles
        for bin,position in zip(self.trash_bins,((640,775),(1100,775))):
            bin.position.update(position);bin.rect.center=position
        self.plants=[(100,600),(1670,600),(330,850),(1450,850)]
        self.seating_areas=[pygame.Rect(340,600,250,340),pygame.Rect(1160,600,250,340)]

    def _coverage_positions(self, seeds):
        """Cover every walkable floor tile with a reachable cleanup task."""
        return covered_positions(self.opening_area,self.floor_tiles,self.obstacles,
                                 self.stores,self.trash_bins,seeds,spawn=(240,430))

    @property
    def playable_areas(self):
        return [self.opening_area]+[r.area for r in self.active_regions]

    @property
    def active_regions(self):return [r for r in self.regions if r.unlocked]

    @property
    def barriers(self):
        return self.gates+([self.commons_divider] if not self.commons.unlocked else [])

    @property
    def deliveries(self):return [self.delivery]+[r.delivery for r in self.active_regions]

    def region_for_store(self, store):return next((r for r in self.regions if store in r.stores),None)

    def area_for_store(self, store):
        region=self.region_for_store(store)
        return region.area if region else self.opening_area

    def area_name(self, position):
        return next((r.name for r in self.active_regions if r.area.collidepoint(position)),'North arcade')

    def cleanup_sections(self):
        return [(self.north_floor_tiles,self.north_trash,self.initial_cleanup_complete)]+[
            (r.floor_tiles,r.trash,r.initial_cleanup_complete) for r in self.active_regions]

    @property
    def recurring_pools(self):
        pools=[self.north_trash] if self.initial_cleanup_complete and self.north_stores[0].restored else []
        return pools+[r.trash for r in self.active_regions if r.initial_cleanup_complete and r.stores[0].restored]

    @property
    def recurring_trash(self):return [t for pool in self.recurring_pools for t in pool]

    def unlock_east(self):return self.unlock_section(self.east)

    def unlock_section(self, region):
        if region not in self.regions or region.unlocked or not region.ready(self):return False
        region.unlocked=True
        for gate in region.gate_rects:
            if gate in self.gates:self.gates.remove(gate)
            if gate in self.obstacles:self.obstacles.remove(gate)
        if region is self.east:self.gates.append(self.east.south_gate)
        self.stores += region.stores
        self.distant_stores=[s for s in self.distant_stores if s not in region.stores]
        self.floor_tiles += region.floor_tiles
        self.dirty_tiles.update(region.floor_tiles)
        self.trash += region.trash
        self.benches += region.benches
        self.trash_bins += region.bins
        self.lamps += region.lamps
        self.plants += region.plants
        self.social_tables += place_tables(region.area,region.floor_tiles,self.obstacles,region.trash,region.key)
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
        for region in self.regions:
            for i,store in enumerate(region.stores):
                store.available=region.unlocked and (store.restored or i==0 or (
                    region.initial_cleanup_complete and region.stores[i-1].restored))

    def clean_trash(self, trash):
        if trash.cleaned or trash not in self.trash:
            return False
        trash.cleaned = True
        trash.revision=getattr(trash,'revision',0)+1
        trash.ever_cleaned = True
        tiles = next(tiles for tiles,pool,_ in self.cleanup_sections() if trash in pool)
        self.dirty_tiles.difference_update(p for p in tiles
                                          if trash.position.distance_squared_to(p) < 115**2)
        if all(t.ever_cleaned for t in self.north_trash):
            self._initial_cleanup_complete = True
        for region in self.active_regions:
            if all(t.ever_cleaned for t in region.trash):region.initial_cleanup_complete=True
        sections=self.cleanup_sections()
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
        trash.revision=getattr(trash,'revision',0)+1
        tiles = next(tiles for tiles,pool,_ in self.cleanup_sections() if trash in pool)
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
        for area in self.seating_areas:
            # Bordered floor inlays group furniture without obstructing the concourse.
            pygame.draw.rect(surface,(118,116,91),camera.rect(area),3)
            pygame.draw.rect(surface,(160,155,125),camera.rect(area.inflate(-12,-12)),1)
        for wall in self.boundary_walls:
            pygame.draw.rect(surface,(53,65,65),camera.rect(wall))
        pygame.draw.rect(surface, (39,53,54), camera.rect(self.back_wall))
        pygame.draw.rect(surface,(39,53,54),camera.rect(self.front_wall))
        for region in self.regions:
            pygame.draw.rect(surface,(39,53,54),camera.rect(region.back_wall))
            pygame.draw.rect(surface,(39,53,54),camera.rect(region.front_wall))
        for store in self.distant_stores:
            store.draw(surface,camera,font,art,False)
        # Future galleries can be seen through closed grilles, but are not playable yet.
        for gate in self.barriers:
            r = camera.rect(gate)
            pygame.draw.rect(surface, (32,45,48), r)
            if gate.height > gate.width:
                for y in range(r.top, r.bottom, 12):
                    pygame.draw.line(surface, (100,108,96), (r.left,y), (r.right,y), 3)
            else:
                for x in range(r.left, r.right, 12):
                    pygame.draw.line(surface, (100,108,96), (x,r.top), (x,r.bottom), 3)
        # One shared public entrance, attached to the exterior west wall.
        art.draw(surface,'main_entrance',camera.point(self.entrance_rect.center),(64,128))
        label=font.render('MAIN ENTRANCE',True,(228,216,164))
        surface.blit(label,label.get_rect(midleft=camera.point((74,1008))))
        for region in self.regions:
            if region.ready(self):region.draw_marker(surface,camera,font,target is region)
            if region.unlocked and f'mosaic_{region.key}' in upgrades.decor:
                art.draw(surface,'mosaic',camera.point((region.fountain.centerx,region.fountain.bottom+90)),(210,125))
        if 'mosaic' in upgrades.decor:
            art.draw(surface,'mosaic',camera.point((self.fountain.centerx,self.fountain.bottom+90)),(210,125))
        for store in self.stores:
            if store.restored:
                glow = camera.rect(store.rect.inflate(24,40).move(0,20))
                pygame.draw.rect(surface, (172,151,95), glow, 3)
            store.draw(surface,camera,font,art,target is store)
        self.delivery.draw(surface,camera,art,font)
        for region in self.active_regions:
            region.delivery.draw(surface,camera,art,font)
        for i,point in enumerate(self.plants):
            art.draw(surface,'plant_clean' if f'plant_{i}' in upgrades.decor else 'plant_dirty',camera.point(point),(65,90))
        for i,point in enumerate(self.lamps):
            art.draw(surface,'lamp' if f'lamp_{i}' in upgrades.decor else 'lamp_off',camera.point(point),(55,95))
        for trash_bin in self.trash_bins:
            trash_bin.draw(surface,camera,art,font,target is trash_bin)
        for trash in self.trash:
            trash.draw(surface,camera,art,target is trash)

    def furniture(self, upgrades):
        """Sort tall props by their ground bases alongside people."""
        result = [(fountain_footprint(self.fountain).centery,
                   'fountain_clean' if 'fountain' in upgrades.decor else 'fountain_dirty',
                   self.fountain.center,(245,165))]
        for region in self.active_regions:
            result.append((fountain_footprint(region.fountain).centery,
                           'fountain_clean' if f'fountain_{region.key}' in upgrades.decor else 'fountain_dirty',
                           region.fountain.center,(245,165)))
        result.extend((bench_footprint(b).centery,
                       'bench_clean' if f'bench_{i}' in upgrades.decor else 'bench_dirty',
                       b.center,(145,85)) for i,b in enumerate(self.benches))
        result.extend((t.position.y,t.sprite(upgrades.decor),
                       t.position,(96,72)) for t in self.social_tables)
        return result
