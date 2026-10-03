"""Three initial owner projects followed by paced, repeatable community favors."""
from dataclasses import dataclass
import pygame
import random
from systems.favors import FAVORS
from mall.businesses import OPPOSITE


OWNERS = {'Pages Bookshop':'Mara','Retro Replay':'Jules','Bean Street':'Iris','The Tailor':'Theo',
          'Vinyl & Company':'Remy','The Green Table':'Ada',
          'Copper Kettle':'Nell','Secondhand Stars':'Otto','Seed & Stem':'Fern','Little Lantern':'Sol',
          'Market Kitchen':'Rosa','Patchwork Studio':'Em','Book Nook':'Wren','Radio Room':'Cal',
          'Sunday Table':'Eli','Homeward Goods':'Hazel'}
SUPPLIES = {'Pages Bookshop':'new books','Retro Replay':'game cartridges',
            'Bean Street':'coffee cups','The Tailor':'fabric rolls',
            'Vinyl & Company':'records','The Green Table':'herb pots',
            'Copper Kettle':'tea tins','Secondhand Stars':'donated treasures','Seed & Stem':'seed packets',
            'Little Lantern':'lamp shades','Market Kitchen':'recipe cards','Patchwork Studio':'fabric squares',
            'Book Nook':'reading sets','Radio Room':'speaker parts','Sunday Table':'table linens','Homeward Goods':'homewares'}
DISPLAY_ITEMS = {
    'Pages Bookshop': ('New novel','Travel guide','Rare edition'),
    'Retro Replay': ('New release','Classic game','Collector set'),
    'Bean Street': ('House blend','Morning mug','Gift tin'),
    'The Tailor': ('Linen shirt','Everyday scarf','Evening coat'),
    'Vinyl & Company': ('New album','Old favorite','Limited pressing'),
    'The Green Table': ('Fresh basil','Kitchen mint','Herb basket'),
    'Copper Kettle': ('Green tea','Copper mug','Tea sampler'),
    'Secondhand Stars': ('Small treasure','Old favorite','Rare find'),
    'Seed & Stem': ('Wildflowers','Garden herbs','Seed bundle'),
    'Little Lantern': ('Desk lamp','Night light','Warm lantern'),
    'Market Kitchen': ('Local recipe','Bread board','Family cookbook'),
    'Patchwork Studio': ('Cotton square','Thread set','Patchwork quilt'),
    'Book Nook': ('Short story','Picture book','Reading set'),
    'Radio Room': ('Pocket radio','Record player','Speaker set'),
    'Sunday Table': ('Tea cup','Table cloth','Serving bowl'),
    'Homeward Goods': ('Woven basket','Small vase','Home keepsake'),
}

for businesses in OPPOSITE.values():
    for name,_,_,_,owner,supplies in businesses:
        OWNERS[name]=owner;SUPPLIES[name]=supplies
        DISPLAY_ITEMS[name]=(supplies.title(),'Neighbor’s choice','Special collection')

def work_desk(store):
    return store.position+pygame.Vector2(90,80 if store.facing=='down' else -80)

PROJECTS = (
    ('A fresh start','Collect our supplies from the signed delivery station.',
     'Welcoming display',0.5,50),
    ('A window worth stopping for','Arrange a window display using our shelf plan. Press E at the blue worktable.',
     'Curated window',1,100),
    ('Hello, neighbors','Set up our welcome sign with Hold E, and say hello to three different shoppers.',
     'Neighborhood favorite',2,200),
)


@dataclass(eq=False)
class RequestSpot:
    position: pygame.Vector2
    title: str
    kind: str
    duration: float = 0
    progress: float = 0
    completed: bool = False

    @property
    def label(self):
        return ('Hold E: ' if self.duration else '')+self.title

    def draw(self, surface, camera, art, font, selected):
        point = camera.point(self.position)
        if self.kind != 'parcel':
            art.draw(surface,'request_'+self.kind,(point.x+48,point.y-16),(48,48))
        if not self.completed:
            pygame.draw.circle(surface,(130,196,209),point,8,2)
        if selected:
            pygame.draw.circle(surface,(230,211,139),point,20,2)
        if self.duration and self.progress and not self.completed:
            rect = pygame.Rect(point.x+24,point.y-48,48,5)
            pygame.draw.rect(surface,(38,56,57),rect)
            pygame.draw.rect(surface,(160,207,151),(rect.x,rect.y,round(rect.width*self.progress/self.duration),5))


class OwnerRequests:
    INTERVAL = 180.0
    RECURRING_MIN = 180.0
    RECURRING_MAX = 600.0

    def __init__(self):
        self.store = None
        self.spots = []
        self.parcel = False
        self.greetings = set()
        self.delivery_name = ''
        self.favor = None
        self.progress = 0
        self.area = None

    def eligible(self, store):
        return store.restored and not store.upgrade_shop and store.request_wait <= 0

    def update(self, dt, mall):
        newly_ready = []
        for store in mall.stores:
            if store.restored and not store.upgrade_shop:
                before = store.request_wait
                store.request_wait = max(0,store.request_wait-dt)
                if before > 0 and store.request_wait == 0:
                    newly_ready.append(store)
        return newly_ready

    @property
    def project(self):
        return self.details(self.store) if self.store else None

    def next_favor(self, store):
        return FAVORS[(store.recurring_completed+list(OWNERS).index(store.name))%len(FAVORS)]

    def details(self, store):
        if store.request_level>=len(PROJECTS):
            favor=self.favor if self.store is store and self.favor else self.next_favor(store)
            scale={'north':1,'east':2,'garden':4,'commons':6}[store.section_key]
            return favor.title,favor.lore,'Community favor',favor.bonus,favor.cash*scale
        title,description,improvement,bonus,reward = PROJECTS[store.request_level]
        if store.request_level == 0:
            description = f'Our {SUPPLIES[store.name]} arrived. Bring them from our section’s signed delivery station so we can welcome our first customers.'
        return title,description,improvement,bonus,reward

    def accept(self, store, mall):
        if self.store or store not in mall.stores or not self.eligible(store):
            return False
        self.store = store
        self.parcel = False
        self.greetings.clear()
        self.area=mall.area_for_store(store)
        self.progress=0
        self.favor=self.next_favor(store) if store.request_level>=len(PROJECTS) else None
        region=mall.region_for_store(store)
        depot=region.delivery if region else mall.delivery
        self.delivery_name=depot.name
        if self.favor:
            self.spots=self.favor_spots(mall,region,depot)
            return True
        if store.request_level == 0:
            self.spots = [RequestSpot(depot.position.copy(),f'Collect {SUPPLIES[store.name]}','parcel')]
        elif store.request_level == 1:
            self.spots = [RequestSpot(work_desk(store),'Arrange the window display','display')]
        else:
            self.spots = [RequestSpot(work_desk(store),'Set up welcome sign','sign',2)]
        return True

    def favor_spots(self, mall, region, depot):
        mode=self.favor.mode
        if mode in ('collect','sell','greet'):return []
        benches=region.benches if region else mall.benches[:2]
        fountain=region.fountain if region else mall.fountain
        desired=[(b.centerx,b.bottom+55) for b in benches]+[(fountain.centerx,fountain.bottom+110)]
        safe=[point for point in mall.floor_tiles if self.area.collidepoint(point) and not any(
            wall.colliderect(pygame.Rect(point[0]-16,point[1]-16,32,32)) for wall in mall.obstacles)]
        positions=[pygame.Vector2(min(safe,key=lambda p:pygame.Vector2(p).distance_squared_to(q))) for q in desired]
        spot=lambda point,title,kind,duration=0:RequestSpot(pygame.Vector2(point),title,kind,duration)
        desk=work_desk(self.store)
        if mode=='lost':return [spot(positions[0],'Collect the lost sketchbook','keepsake')]
        if mode=='memories':return [spot(p,f'Collect photograph {i+1}','keepsake') for i,p in enumerate(positions)]
        if mode=='polish':return [spot(p,f'Polish nameplate {i+1}','plaque',2) for i,p in enumerate(positions[:2])]
        if mode=='display':return [spot(desk,'Arrange the maker’s window','display')]
        if mode=='welcome':return [spot(desk,'Prepare the welcome board','sign',1.5)]
        if mode=='repair':return [spot(depot.position,'Collect the borrowed toolkit','parcel'),spot(desk,'Repair the display stand','toolkit',2)]
        if mode=='route':return [spot(depot.position,'Collect community notices','parcel')]+[
            spot(p,f'Post community notice {i+1}','notice') for i,p in enumerate(positions)]
        if mode=='lantern':
            lamps=region.lamps if region else mall.lamps[:4]
            return [spot((x,y+65),f'Check lamp connection {i+1}','lantern',1.5) for i,(x,y) in enumerate(lamps[:2])]
        if mode=='chalk':return [spot(p,f'Refresh direction {i+1}','chalk',1.2) for i,p in enumerate(positions)]
        raise ValueError('Unknown favor mode: '+mode)

    @property
    def needs_greetings(self):
        return bool(self.store and (self.store.request_level==2 or self.favor and self.favor.mode in ('greet','welcome')))

    @property
    def ready(self):
        if not self.store:
            return False
        if self.favor:
            if self.favor.mode in ('collect','sell'):return self.progress>=self.favor.amount
            if self.favor.mode in ('greet','welcome'):
                return len(self.greetings)>=self.favor.amount and all(s.completed for s in self.spots)
            return all(s.completed for s in self.spots)
        if self.store.request_level == 0:
            return self.parcel
        return all(s.completed for s in self.spots) and (self.store.request_level != 2 or len(self.greetings)>=3)

    @property
    def visible_spots(self):return [s for s in self.scene_spots if not s.completed]

    @property
    def scene_spots(self):
        if self.favor and self.favor.mode in ('repair','route') and not self.parcel:
            return [s for s in self.spots if s.kind=='parcel']
        return [s for s in self.spots if not s.completed or s.kind!='parcel']

    @property
    def objective(self):
        if not self.store:
            return ''
        owner = OWNERS[self.store.name]
        if self.ready:
            return f'Return to {owner} at {self.store.name} / E, then Enter.'
        if self.favor:
            mode=self.favor.mode
            if mode=='collect':return f'Collect litter here: {self.progress}/{self.favor.amount}.'
            if mode=='sell':return f'Sell trash at this section’s bins: {self.progress}/{self.favor.amount}.'
            if mode=='greet':return f'Ask different shoppers about Northgate: {len(self.greetings)}/{self.favor.amount}.'
            if mode=='welcome':return f'Welcome board: {"done" if self.spots[0].completed else "Hold E"} · greetings {len(self.greetings)}/{self.favor.amount}.'
            remaining=self.visible_spots
            return (remaining[0].label+'. J opens the map.') if remaining else 'Return to the owner.'
        if self.store.request_level == 0:
            return f'Collect supplies at {self.delivery_name}. J opens the map.'
        if self.store.request_level == 1:
            return 'Arrange the window display at the blue worktable. Press E.'
        return f'Welcome sign: {"done" if self.spots[0].completed else "Hold E"} / shoppers greeted {len(self.greetings)}/3.'

    def interact(self, spot):
        if spot not in self.visible_spots:
            return False
        if spot.duration or spot.kind == 'display':
            return False
        spot.completed = True
        if spot.kind=='parcel':self.parcel = True
        return True

    @property
    def display_items(self):
        return DISPLAY_ITEMS[self.store.name] if self.store and (self.store.request_level == 1 or self.favor and self.favor.mode=='display') else ()

    @property
    def display_plan(self):
        if not self.display_items:
            return ()
        # Different storefronts feature different shelf orders; stable across reopening.
        orders=((1,0,2),(2,1,0),(0,2,1))
        return orders[(list(OWNERS).index(self.store.name)+self.store.recurring_completed)%len(orders)]

    def arrange_display(self, arrangement):
        if not self.display_items or tuple(arrangement) != self.display_plan or self.ready:
            return False
        self.spots[0].completed = True
        return True

    def work(self, dt, player_position, held, stationary):
        finished = []
        for spot in self.visible_spots:
            if not spot.duration:
                continue
            if held and stationary and spot.position.distance_squared_to(player_position)<=72**2:
                spot.progress = min(spot.duration,spot.progress+dt)
                if spot.progress >= spot.duration:
                    spot.completed = True
                    finished.append(spot)
            else:
                spot.progress = 0
        return finished

    def greet(self, person):
        if self.needs_greetings and person.visible:
            self.greetings.add(person.identity)
            # Bound greetings to the active goal, including departed visitors.
            limit=self.favor.amount if self.favor else 3
            if len(self.greetings)>limit:
                self.greetings.remove(person.identity)

    def record_collection(self, count, position):
        if self.favor and self.favor.mode=='collect' and self.area.collidepoint(position):
            self.progress=min(self.favor.amount,self.progress+count)

    def record_sale(self, count, position):
        if self.favor and self.favor.mode=='sell' and self.area.collidepoint(position):
            self.progress=min(self.favor.amount,self.progress+count)

    def claim(self, store):
        if store is not self.store or not self.ready:
            return None
        _,_,improvement,bonus,reward = self.project
        if self.favor:store.recurring_completed += 1
        else:store.request_level += 1
        store.request_bonus += bonus
        store.request_wait = random.uniform(self.RECURRING_MIN,self.RECURRING_MAX) if store.request_level>=len(PROJECTS) else self.INTERVAL
        self.store = None
        self.spots = []
        self.parcel = False
        self.favor = None
        self.progress = 0
        self.greetings.clear()
        return improvement,bonus,reward
