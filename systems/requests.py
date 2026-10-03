"""Three relaxed owner jobs per paying business, with permanent shop improvements."""
from dataclasses import dataclass
import pygame


OWNERS = {'Pages Bookshop':'Mara','Retro Replay':'Jules','Bean Street':'Iris','The Tailor':'Theo',
          'Vinyl & Company':'Remy','The Green Table':'Ada'}
SUPPLIES = {'Pages Bookshop':'new books','Retro Replay':'game cartridges',
            'Bean Street':'coffee cups','The Tailor':'fabric rolls',
            'Vinyl & Company':'records','The Green Table':'herb pots'}
PROJECTS = (
    ('A fresh start','Bring our display supplies from the delivery crate by the bins.',
     'Welcoming display',0.5,50),
    ('Room to grow','Water two community seedling trays. Hold E at each tray, then come back.',
     'Community corner',1,100),
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
    def __init__(self):
        self.store = None
        self.spots = []
        self.parcel = False
        self.greetings = set()

    def eligible(self, store):
        return store.restored and not store.upgrade_shop and store.request_level < len(PROJECTS)

    @property
    def project(self):
        return PROJECTS[self.store.request_level] if self.store else None

    def details(self, store):
        title,description,improvement,bonus,reward = PROJECTS[store.request_level]
        if store.request_level == 0:
            description = f'Our {SUPPLIES[store.name]} arrived. Bring them from the blue delivery crate by the bins so we can welcome our first customers.'
        return title,description,improvement,bonus,reward

    def accept(self, store, mall):
        if self.store or store not in mall.stores or not self.eligible(store):
            return False
        self.store = store
        self.parcel = False
        self.greetings.clear()
        east = store in mall.east.stores
        bins = mall.east.bins if east else mall.trash_bins[:2]
        if store.request_level == 0:
            depot = min(bins,key=lambda b:b.position.distance_squared_to(store.position))
            self.spots = [RequestSpot(depot.position+pygame.Vector2(0,90),f'Collect {SUPPLIES[store.name]}','parcel')]
        elif store.request_level == 1:
            # Temporary seedling trays do not grant purchased planter upgrades.
            positions = [(1900,880),(3160,880)] if east else [(480,880),(1220,880)]
            self.spots = [RequestSpot(pygame.Vector2(p),f'Water seedling tray {i+1}','seedlings',1.5)
                          for i,p in enumerate(positions)]
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
            return 'Pick up display supplies at the blue crate marker by the bins.'
        if self.store.request_level == 1:
            return f'Hold E to water seedling trays: {sum(s.completed for s in self.spots)}/2.'
        return f'Welcome sign: {"done" if self.spots[0].completed else "Hold E"} / shoppers greeted {len(self.greetings)}/3.'

    def interact(self, spot):
        if spot not in self.visible_spots:
            return False
        if spot.duration:
            return False
        spot.completed = True
        self.parcel = True
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
        self.store = None
        self.spots = []
        self.parcel = False
        self.greetings.clear()
        return improvement,bonus,reward
