"""Geometry and interaction for the next arcade; its contents activate on purchase."""
import pygame
from entities.trash import Trash
from entities.trash_bin import TrashBin
from mall.store import Store
from mall.furniture import bench_footprint, fountain_footprint
from mall.delivery import DeliveryPoint
from mall.businesses import opposite_stores
from mall.social import arrange_gallery


def covered_positions(area, floor, obstacles, stores, bins, seeds=(), spawn=None, entrance_buffer=90):
    """Greedily cover every walkable tile with a reachable 115px cleanup patch."""
    candidates = [p for p in floor
                  if area.contains(pygame.Rect(p[0]-16,p[1]-16,32,32))
                  and not any(w.colliderect(pygame.Rect(p[0]-16,p[1]-16,32,32)) for w in obstacles)
                  and (spawn is None or pygame.Vector2(p).distance_squared_to(spawn) > 120**2)
                  and all(s.position.distance_squared_to(p) > entrance_buffer**2 for s in stores)
                  and all(b.position.distance_squared_to(p) > 80**2 for b in bins)]
    coverage = [(p,{i for i,tile in enumerate(floor) if pygame.Vector2(p).distance_squared_to(tile) < 115**2})
                for p in candidates]
    uncovered = {i for i,tile in enumerate(floor)
                 if not any(pygame.Vector2(p).distance_squared_to(tile) < 115**2 for p in seeds)}
    extra = []
    while uncovered:
        point, covered = max(coverage,key=lambda item:len(item[1]&uncovered))
        if not covered & uncovered:
            raise ValueError('Uncovered floor: '+repr([floor[i] for i in uncovered]))
        extra.append(point)
        uncovered -= covered
    return extra


def floor_tiles(area, obstacles):
    return tuple((x+31,y+31) for x in range((area.left-40)//64*64+40,area.right,64)
                 for y in range((area.top-40)//64*64+40,area.bottom,64)
                 if area.collidepoint((x+31,y+31))
                 and not any(w.collidepoint((x+31,y+31)) for w in obstacles))


class RegionalGallery:
    """One configuration drives layouts, opening prerequisites and regional gear."""
    def __init__(self, key, name, area, cost, prerequisite, specs, marker, south=False):
        self.key,self.name,self.cost,self.prerequisite=key,name,cost,prerequisite
        self.unlocked=False
        self.initial_cleanup_complete=False
        self.area=pygame.Rect(area)
        self.position=pygame.Vector2(marker)
        left,top=self.area.topleft
        start=left+224 if south else 1900
        spacing=300 if south else 328
        width=280
        self.stores=[Store((start+i*spacing,top+60,width,240),title,False,price,rent,kind)
                     for i,(title,price,rent,kind) in enumerate(specs)]
        for store in self.stores:store.section_key=key
        self.stores[0].upgrade_shop=key
        self.stores += opposite_stores(key,self.area)
        self.front_wall=pygame.Rect(left+192,self.area.bottom-280,self.area.width-192,280)
        self.back_wall=pygame.Rect(left+(192 if south else 0),top,self.area.width-(192 if south else 0),300)
        self.south_gate=pygame.Rect(left,self.area.bottom,self.area.width,32)
        self.fountain=pygame.Rect(left+788 if key in ('east','commons') else 700,top+560,220,100)
        self.benches=[pygame.Rect(left+288 if key=='east' else left+240,top+660,120,35),
                      pygame.Rect(left+1368 if key=='east' else left+1180,top+660,120,35)]
        self.bins=[TrashBin((b.right+45,b.centery),f'{name} {side} bin') for b,side in zip(self.benches,('west','east'))]
        self.lamps=[((a.rect.right+b.rect.left)//2,top+345) for a,b in zip(self.stores[:5],self.stores[1:5])]
        self.plants=[(left+68,top+540),(self.area.right-80,top+540),(left+568,top+890),(left+1288,top+890)]
        self.delivery=DeliveryPoint((self.area.right-160 if key in ('east','commons') else left+60,top+860),name)
        self.entrance=(left+68,self.area.bottom-60)
        self.gate_rects=[]
        self.furniture_obstacles=[fountain_footprint(self.fountain)]+[bench_footprint(b) for b in self.benches]
        structural=[self.back_wall,self.front_wall]+[store.rect for store in self.stores]
        if key=='east':structural.append(self.south_gate)
        self.obstacles=structural+[b.rect for b in self.bins]+[self.delivery.rect]+self.furniture_obstacles
        self.floor_tiles=floor_tiles(self.area,structural)
        self.trash=[Trash(point,'dirt' if i%3==0 else 'trash') for i,point in enumerate(
            covered_positions(self.area,self.floor_tiles,self.obstacles,self.stores,self.bins,entrance_buffer=72 if south else 90))]
        arrange_gallery(self)

    def ready(self, mall):
        if self.prerequisite=='north':
            return mall.initial_cleanup_complete and all(s.restored for s in mall.north_stores)
        previous=getattr(mall,self.prerequisite)
        return previous.unlocked and previous.initial_cleanup_complete and all(s.restored for s in previous.stores)

    @property
    def label(self):return f'Open {self.name} (${self.cost:,})'

    def draw_marker(self, surface, camera, font, selected):
        if self.unlocked:return
        point=camera.point(self.position)
        pygame.draw.circle(surface,(216,177,104),point,12)
        if selected:pygame.draw.circle(surface,(245,218,156),point,21,2)
        text=font.render(f'{self.name.upper()} / ${self.cost:,}',True,(216,198,158))
        # South-entry labels sit above the marker; avoid covering nearby delivery signage.
        surface.blit(text,text.get_rect(midbottom=(point.x,point.y-25)))


class EastGallery(RegionalGallery):
    def __init__(self):
        super().__init__('east','East gallery',(1792,40,1768,1440),1500,'north',[
            ('Eastgate Workshop',2000,0,'bookshop'),('Vinyl & Company',3000,25,'bookshop'),
            ('The Green Table',4500,40,'cafe'),('Copper Kettle',6000,55,'cafe'),
            ('Secondhand Stars',8000,70,'bookshop')],(1715,800))


def later_galleries():
    garden=RegionalGallery('garden','Garden Arcade',(40,1512,1720,1488),10000,'east',[
        ('Garden Supply',12000,0,'bookshop'),('Seed & Stem',15000,90,'bookshop'),
        ('Little Lantern',18500,115,'bookshop'),('Market Kitchen',22000,145,'cafe'),
        ('Patchwork Studio',26000,180,'bookshop')],(160,1435),True)
    commons=RegionalGallery('commons','Community Commons',(1792,1512,1768,1488),35000,'garden',[
        ('Commons Exchange',40000,0,'bookshop'),('Book Nook',48000,230,'bookshop'),
        ('Radio Room',56000,280,'bookshop'),('Sunday Table',65000,340,'cafe'),
        ('Homeward Goods',75000,410,'bookshop')],(1715,2600),True)
    return garden,commons
