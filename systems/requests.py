"""Three relaxed owner jobs per paying business, with permanent shop improvements."""
from dataclasses import dataclass
import pygame


OWNERS = {'Pages Bookshop':'Mara','Retro Replay':'Jules','Bean Street':'Iris','The Tailor':'Theo',
          'Vinyl & Company':'Remy','The Green Table':'Ada'}
SUPPLIES = {'Pages Bookshop':'new books','Retro Replay':'game cartridges',
            'Bean Street':'coffee cups','The Tailor':'fabric rolls',
            'Vinyl & Company':'records','The Green Table':'herb pots'}
DISPLAY_ITEMS = {
    'Pages Bookshop': ('New novel','Travel guide','Rare edition'),
    'Retro Replay': ('New release','Classic game','Collector set'),
    'Bean Street': ('House blend','Morning mug','Gift tin'),
    'The Tailor': ('Linen shirt','Everyday scarf','Evening coat'),
    'Vinyl & Company': ('New album','Old favorite','Limited pressing'),
    'The Green Table': ('Fresh basil','Kitchen mint','Herb basket'),
}
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

    def __init__(self):
        self.store = None
        self.spots = []
        self.parcel = False
        self.greetings = set()
        self.delivery_name = ''

    def eligible(self, store):
        return store.restored and not store.upgrade_shop and store.request_level < len(PROJECTS) and store.request_wait <= 0

    def update(self, dt, mall):
        newly_ready = []
        for store in mall.stores:
            if store.restored and not store.upgrade_shop and store.request_level < len(PROJECTS):
                before = store.request_wait
                store.request_wait = max(0,store.request_wait-dt)
                if before > 0 and store.request_wait == 0:
                    newly_ready.append(store)
        return newly_ready

    @property
    def project(self):
        return PROJECTS[self.store.request_level] if self.store else None

    def details(self, store):
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
        east = store in mall.east.stores
        if store.request_level == 0:
            depot = mall.east.delivery if east else mall.delivery
            self.delivery_name = depot.name
            self.spots = [RequestSpot(depot.position.copy(),f'Collect {SUPPLIES[store.name]}','parcel')]
        elif store.request_level == 1:
            self.spots = [RequestSpot(store.position+pygame.Vector2(90,80),'Arrange the window display','display')]
        else:
            self.spots = [RequestSpot(store.position+pygame.Vector2(90,80),'Set up welcome sign','sign',2)]
        return True

    @property
    def ready(self):
        if not self.store:
            return False
        if self.store.request_level == 0:
            return self.parcel
        return all(s.completed for s in self.spots) and (self.store.request_level != 2 or len(self.greetings)>=3)

    @property
    def visible_spots(self):
        return [s for s in self.spots if not s.completed]

    @property
    def objective(self):
        if not self.store:
            return ''
        owner = OWNERS[self.store.name]
        if self.ready:
            return f'Return to {owner} at {self.store.name} / E, then Enter.'
        if self.store.request_level == 0:
            return f'Collect supplies at {self.delivery_name}. J opens the map.'
        if self.store.request_level == 1:
            return 'Arrange the window display at the blue worktable. Press E.'
        return f'Welcome sign: {"done" if self.spots[0].completed else "Hold E"} / shoppers greeted {len(self.greetings)}/3.'

    def interact(self, spot):
        if spot not in self.visible_spots:
            return False
        if spot.duration or spot.kind != 'parcel':
            return False
        spot.completed = True
        self.parcel = True
        return True

    @property
    def display_items(self):
        return DISPLAY_ITEMS[self.store.name] if self.store and self.store.request_level == 1 else ()

    @property
    def display_plan(self):
        if not self.display_items:
            return ()
        # Different storefronts feature different shelf orders; stable across reopening.
        orders=((1,0,2),(2,1,0),(0,2,1))
        return orders[list(OWNERS).index(self.store.name)%len(orders)]

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
        if self.store and self.store.request_level == 2:
            self.greetings.add(person.identity)
            # Only three greetings are needed; bounded to avoid accumulating departed NPCs.
            if len(self.greetings)>3:
                self.greetings.remove(person.identity)

    def claim(self, store):
        if store is not self.store or not self.ready:
            return None
        _,_,improvement,bonus,reward = self.project
        store.request_level += 1
        store.request_bonus += bonus
        store.request_wait = self.INTERVAL
        self.store = None
        self.spots = []
        self.parcel = False
        self.greetings.clear()
        return improvement,bonus,reward
