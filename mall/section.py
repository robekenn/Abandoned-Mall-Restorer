"""Geometry and interaction for the next arcade; its contents activate on purchase."""
import pygame
from entities.trash import Trash
from entities.trash_bin import TrashBin
from mall.store import Store


def covered_positions(area, floor, obstacles, stores, bins, seeds=(), spawn=None):
    """Greedily cover every walkable tile with a reachable 115px cleanup patch."""
    candidates = [p for p in floor
                  if area.contains(pygame.Rect(p[0]-16,p[1]-16,32,32))
                  and not any(w.colliderect(pygame.Rect(p[0]-16,p[1]-16,32,32)) for w in obstacles)
                  and (spawn is None or pygame.Vector2(p).distance_squared_to(spawn) > 120**2)
                  and all(s.position.distance_squared_to(p) > 90**2 for s in stores)
                  and all(b.position.distance_squared_to(p) > 80**2 for b in bins)]
    coverage = [(p,{i for i,tile in enumerate(floor) if pygame.Vector2(p).distance_squared_to(tile) < 115**2})
                for p in candidates]
    uncovered = {i for i,tile in enumerate(floor)
                 if not any(pygame.Vector2(p).distance_squared_to(tile) < 115**2 for p in seeds)}
    extra = []
    while uncovered:
        point, covered = max(coverage,key=lambda item:len(item[1]&uncovered))
        if not covered & uncovered:
            raise ValueError('Starting litter does not cover the playable floor')
        extra.append(point)
        uncovered -= covered
    return extra


def floor_tiles(area, obstacles):
    return tuple((x+31,y+31) for x in range((area.left-40)//64*64+40,area.right,64)
                 for y in range((area.top-40)//64*64+40,area.bottom,64)
                 if area.collidepoint((x+31,y+31))
                 and not any(w.collidepoint((x+31,y+31)) for w in obstacles))


class EastGallery:
    cost = 1500
    name = 'East gallery'

    def __init__(self):
        self.unlocked = False
        self.initial_cleanup_complete = False
        self.area = pygame.Rect(1792,40,1768,1020)
        self.position = pygame.Vector2(1715,800)
        self.stores = [Store((1900+i*520,100,400,240),name,False,cost,rent,kind)
                       for i,(name,cost,rent,kind) in enumerate([
                           ('Eastgate Workshop',2000,0,'bookshop'),
                           ('Vinyl & Company',3000,25,'bookshop'),
                           ('The Green Table',4500,40,'cafe')])]
        self.stores[0].upgrade_shop = 'east'
        self.back_wall = pygame.Rect(1792,40,1768,300)
        self.south_gate = pygame.Rect(1792,1060,1768,32)
        self.fountain = pygame.Rect(2580,600,220,100)
        self.benches = [pygame.Rect(2080,700,120,35),pygame.Rect(3160,700,120,35)]
        self.bins = [TrashBin((b.right+45,b.centery),name) for b,name in zip(
            self.benches,('East gallery west bin','East gallery east bin'))]
        self.lamps = [((a.rect.right+b.rect.left)//2,385) for a,b in zip(self.stores,self.stores[1:])]
        self.plants = [(1860,580),(3480,580),(2360,930),(3080,930)]
        self.obstacles = [self.back_wall,self.south_gate,self.fountain]+self.benches
        self.obstacles += [s.rect for s in self.stores]+[b.rect for b in self.bins]
        self.floor_tiles = floor_tiles(self.area,self.obstacles)
        self.trash = [Trash(p,'dirt' if i%3 == 0 else 'trash') for i,p in enumerate(
            covered_positions(self.area,self.floor_tiles,self.obstacles,self.stores,self.bins))]

    def ready(self, mall):
        return all(s.restored for s in mall.north_stores) and mall.initial_cleanup_complete

    @property
    def label(self):
        return 'Open east gallery ($1,500)' if not self.unlocked else 'East gallery open'

    def draw_marker(self, surface, camera, font, selected):
        if self.unlocked:
            return
        point = camera.point(self.position)
        pygame.draw.circle(surface,(216,177,104),point,12)
        if selected:
            pygame.draw.circle(surface,(245,218,156),point,21,2)
        text = font.render('EAST GALLERY / $1,500',True,(216,198,158))
        surface.blit(text,text.get_rect(midright=(point.x-24,point.y)))
