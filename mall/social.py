"""Shared, reachable seating rather than decoration-only dining tables."""
from dataclasses import dataclass
import pygame


@dataclass(eq=False)
class SocialTable:
    position: pygame.Vector2
    seats: tuple
    section: str
    fixture_key: str | None = None

    @property
    def seat_keys(self):
        return tuple(f'{self.fixture_key}_seat_{i}' for i in range(len(self.seats))) if self.fixture_key else (None,)*len(self.seats)

    def sprite(self,decor):
        table=self.fixture_key in decor
        seats=tuple(key in decor for key in self.seat_keys)
        if table and all(seats):return 'social_table'
        if not table and not any(seats):return 'social_table_broken'
        return f'social_table_{int(table)}_{int(seats[0])}{int(seats[1])}'

    @property
    def footprint(self):
        return pygame.Rect(self.position.x-27,self.position.y-19,54,38)


def place_tables(area, floor, obstacles, trash, section, count=2):
    tables=[]
    # Put seats on the existing navigation lattice, clear of cleanup patches.
    for goal in ((area.left+480,area.top+820),(area.right-480,area.top+900))[:count]:
        for p in sorted(floor,key=lambda p:pygame.Vector2(p).distance_squared_to(goal)):
            seats=(pygame.Vector2(p[0]-64,p[1]),pygame.Vector2(p[0]+64,p[1]))
            ordinal=('north','east','garden','commons').index(section)
            table=SocialTable(pygame.Vector2(p[0],p[1]-30),seats,section,f'table_{2*ordinal+len(tables)}')
            if not area.contains(table.footprint.inflate(180,140)):continue
            if any(w.colliderect(table.footprint.inflate(30,30)) for w in obstacles):continue
            if any(table.footprint.inflate(32,32).collidepoint(t.position) for t in trash):continue
            if any(tuple(seat) not in floor or any(w.colliderect(pygame.Rect(seat.x-12,seat.y-14,24,28)) for w in obstacles+[table.footprint]) for seat in seats):continue
            if any(table.position.distance_to(t.position)<240 for t in tables):continue
            tables.append(table);obstacles.append(table.footprint);break
    return tables


# The same two-bay plan as North, fitted to the existing navigation lattice and
# original cleanup spots. Coordinates are relative to each section's floor area.
INDOOR_SEATING = {
    'east': {'tables': ((455,641),(1287,641)), 'fountain': (750,606,220,100),
             'benches': ((395,794,120,35),(1227,794,120,35)), 'bins': ((640,711),(1100,711))},
    'garden': {'tables': ((415,641),(1183,641)), 'fountain': (678,630,220,100),
               'benches': ((355,794,120,35),(1123,794,120,35)), 'bins': ((568,735),(1028,735))},
    'commons': {'tables': ((391,641),(1287,641)), 'fountain': (718,606,220,100),
                'benches': ((331,794,120,35),(1227,794,120,35)), 'bins': ((608,711),(1068,711))},
}


def arrange_gallery(region):
    """Apply the shared seating plan after generating stable legacy litter IDs."""
    plan=INDOOR_SEATING[region.key];left,top=region.area.topleft
    for rect in region.furniture_obstacles:region.obstacles.remove(rect)
    region.fountain.update(pygame.Rect(plan['fountain']).move(left,top))
    for bench,rect in zip(region.benches,plan['benches']):bench.update(pygame.Rect(rect).move(left,top))
    from mall.furniture import bench_footprint,fountain_footprint
    region.furniture_obstacles=[fountain_footprint(region.fountain)]+[bench_footprint(b) for b in region.benches]
    region.obstacles += region.furniture_obstacles
    for bin,point in zip(region.bins,plan['bins']):
        bin.position.update(left+point[0],top+point[1]);bin.rect.center=bin.position
    ordinal=('north','east','garden','commons').index(region.key)
    region.social_tables=[];region.seating_areas=[]
    for i,(x,y) in enumerate(plan['tables']):
        position=pygame.Vector2(left+x,top+y)
        seats=(position+pygame.Vector2(-64,30),position+pygame.Vector2(64,30))
        table=SocialTable(position,seats,region.key,f'table_{2*ordinal+i}')
        region.social_tables.append(table);region.obstacles.append(table.footprint)
        region.seating_areas.append(pygame.Rect(position.x-125,position.y-81,250,340))
    region.plants=[(left+60,top+560),(region.area.right-90,top+(400 if region.key=='commons' else 560)),
                   (region.benches[0].centerx-125,top+810),(region.benches[1].centerx+163,top+810)]
