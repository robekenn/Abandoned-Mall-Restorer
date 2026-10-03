"""Bounded visitors with obstacle-aware routes through unlocked galleries."""
from collections import deque
import random
import pygame
from game.lore import SHOPPER_LINES


class Walkways:
    def __init__(self):
        self.signature = None
        self.nodes = set()
        self.edges = {}
        self.walls=[]

    def refresh(self, mall):
        signature = tuple(r.unlocked for r in mall.regions)
        if self.signature == signature:
            return
        self.signature = signature
        self.nodes = {p for p in mall.floor_tiles if not any(
            w.colliderect(pygame.Rect(p[0]-10,p[1]-12,20,24)) for w in mall.obstacles)}
        walls = [w.inflate(20,24) for w in mall.obstacles]
        self.walls=walls
        self.edges = {p:[q for q in ((p[0]+64,p[1]),(p[0]-64,p[1]),(p[0],p[1]+64),(p[0],p[1]-64))
                         if q in self.nodes and not any(w.clipline(p,q) for w in walls)] for p in self.nodes}

    def nearest(self, point):
        return min(self.nodes,key=lambda p:pygame.Vector2(p).distance_squared_to(point))

    def route(self, origin, destination):
        start,end = self.nearest(origin),self.nearest(destination)
        # Use a regular BFS with parents; it also detects sealed/disconnected paths.
        queue = deque([start]); previous = {start:None}
        while queue and end not in previous:
            node = queue.popleft()
            for neighbor in self.edges[node]:
                if neighbor not in previous:
                    previous[neighbor] = node
                    queue.append(neighbor)
        if end not in previous:
            return None
        path = []; node = end
        while node != start:
            path.append(pygame.Vector2(node)); node = previous[node]
        path=[pygame.Vector2(start)]+list(reversed(path))+[pygame.Vector2(destination)]
        if any(w.clipline(origin,start) or w.clipline(end,destination) for w in self.walls):return None
        return path


class Shopper:
    def __init__(self, identity, origin, store, walkways):
        self.identity = identity
        self.name = ('Alex','Bea','Sam','Nico','June','Lee','Robin','Kit')[identity%8]
        self.variant = identity%4
        self.position = pygame.Vector2(origin)
        self.entrance = self.position.copy()
        self.store = store
        self.path = walkways.route(self.position,store.position) or []
        self.state = 'arriving'
        self.wait = 0.0
        self.facing = 'down'
        self.frame = 0
        self.animation_time = 0.0
        self.done = False
        self.greeted = False
        self.speech = ''
        self.speech_time = 0

    @property
    def label(self):
        return f'Say hello to {self.name} / visiting {self.store.name}'

    @property
    def visible(self):
        return self.state != 'inside' and not self.done

    def update(self, dt, manager, mall, upgrades):
        if self.speech_time and self.visible:
            self.speech_time=max(0,self.speech_time-dt)
            self.frame=0
            return
        if self.state == 'inside':
            self.wait += dt
            self.frame = 0
            if self.wait >= 10+self.identity%3*2:
                self.path = [self.store.position.copy()]
                self.state,self.wait = 'exiting',0
            return
        moving = False
        budget = 86*dt
        while self.path and budget > 0:
            delta = self.path[0]-self.position
            distance = delta.length()
            if distance < 0.01:
                self.path.pop(0); continue
            self.facing = ('right' if delta.x > 0 else 'left') if abs(delta.x)>abs(delta.y) else ('down' if delta.y>0 else 'up')
            step = min(distance,budget)
            self.position += delta*(step/distance)
            budget -= step; moving = True
            if step == distance:
                self.path.pop(0)
        self.animation_time = self.animation_time+dt if moving else 0
        self.frame = int(self.animation_time/0.18)%4 if moving else 0
        if self.path:
            return
        if self.state == 'arriving':
            if self.position.distance_to(self.store.position)>1:
                self.path=manager.walkways.route(self.position,self.store.position) or []
                return
            self.path = [self.store.position.copy(),pygame.Vector2(self.store.rect.centerx,self.store.rect.bottom-28 if self.store.facing=='down' else self.store.rect.top+28)]
            self.state = 'entering'
        elif self.state == 'entering':
            self.state,self.wait = 'inside',0
        elif self.state == 'exiting':
            amenities = manager.amenities(mall,upgrades)
            goals=list(amenities);manager.random.shuffle(goals)
            goal=next((p for p in goals if manager.walkways.route(self.position,p) is not None),self.entrance)
            path=manager.walkways.route(self.position,goal)
            if path is None:return
            self.path=path
            self.state,self.wait = ('leaving' if pygame.Vector2(goal)==self.entrance else 'strolling'),0
        elif self.state == 'strolling':
            self.state,self.wait = 'resting',0
        elif self.state == 'resting':
            self.wait += dt
            community=getattr(mall,'community_spots',())
            linger=12 if any(self.position.distance_to(p)<32 for p in community) else 4
            if self.wait >= linger:
                path=manager.walkways.route(self.position,self.entrance)
                if path is None:return
                self.path=path
                self.state,self.wait = 'leaving',0
        elif self.state == 'leaving':
            # An exhausted/failed route never counts as leaving in mid-concourse.
            if self.position.distance_to(self.entrance)<1:self.done = True
            else:self.path=manager.walkways.route(self.position,self.entrance) or []

    def draw(self, surface, camera, art, font, selected):
        if not self.visible:
            return
        point = camera.point(self.position)
        art.draw(surface,f'shopper_{self.variant}_{self.facing}_{self.frame}',(point.x,point.y-12),(48,72))
        if selected:
            pygame.draw.ellipse(surface,(175,210,186),(point.x-14,point.y+8,28,10),2)
            label = font.render(self.name,True,(218,225,191))
            surface.blit(label,label.get_rect(center=(point.x,point.y-54)))


class Shoppers:
    def __init__(self):
        self.people = []
        self.walkways = Walkways()
        self.random = random.Random(97)
        self.elapsed = 8.0
        self.next_identity = 0

    def amenities(self, mall, upgrades):
        points = [(b.centerx,b.bottom+40) for i,b in enumerate(mall.benches) if f'bench_{i}' in upgrades.decor]
        if 'fountain' in upgrades.decor:
            points.append((mall.fountain.centerx,mall.fountain.bottom+45))
        for region in mall.active_regions:
            if f'fountain_{region.key}' in upgrades.decor:
                points.append((region.fountain.centerx,region.fountain.bottom+45))
        points.extend(getattr(mall,'community_spots',()))
        return points

    def gather(self, area, goals, mall):
        """Invite a few real visitors along safe routes, respecting the population cap."""
        self.walkways.refresh(mall)
        stores=[s for s in mall.stores if s.restored and area.collidepoint(s.position)]
        if not stores:return
        neighbors=[p for p in self.people if p.visible and area.collidepoint(p.position)
                   and p.state not in ('entering','exiting')][:3]
        limit=12+4*max(0,len(mall.active_regions)-1)
        while len(neighbors)<3 and len(self.people)<limit:
            store=stores[len(neighbors)%len(stores)]
            if self.walkways.route(mall.entrance,store.position) is None:break
            person=Shopper(self.next_identity,mall.entrance,store,self.walkways)
            self.next_identity+=1;self.people.append(person);neighbors.append(person)
        for person,goal in zip(neighbors,goals):
            path=self.walkways.route(person.position,goal)
            if path is not None:person.path=path;person.state='strolling';person.wait=0

    def update(self, dt, mall, upgrades, preferred_store=None):
        self.walkways.refresh(mall)
        opened = [s for s in mall.stores if s.restored]
        for person in self.people:
            person.update(dt,self,mall,upgrades)
        self.people = [p for p in self.people if not p.done]
        for store in mall.stores:
            store.door_open = any(p.store is store and p.state in ('entering','exiting') for p in self.people)
        limit=12+4*max(0,len(mall.active_regions)-1)
        desired = min(limit,len(opened)+(2 if mall.cleanliness >= 0.5 else 0)+len(self.amenities(mall,upgrades))//2) if opened else 0
        self.elapsed += dt
        if self.elapsed >= 8 and len(self.people)<desired:
            self.elapsed = 0
            store = preferred_store if preferred_store in opened else self.random.choice(opened)
            if self.walkways.route(mall.entrance,store.position) is None:return
            self.people.append(Shopper(self.next_identity,mall.entrance,store,self.walkways))
            self.next_identity += 1

    def greet(self, person, story=None):
        for other in self.people:other.speech_time=0
        person.speech='Good to see you again. These halls feel more like home.' if person.greeted else self.random.choice(SHOPPER_LINES)
        if story and not person.greeted:
            if story.festival:person.speech='My little one made a lantern. Thank you for giving us somewhere to bring it.'
            elif any(story.completed):person.speech=self.random.choice(('I came for the shops. I stayed because someone made room at the table.',
                'Mara saved a chair for me at the reading circle. I had forgotten how that feels.',
                'Someone has started folding lanterns again. They are all different, just like before.',
                'I brought a neighbor today. Next time, maybe we will bring two.'))
        person.greeted=True
        person.speech_time=max(5,min(10,len(person.speech)/14))
        return f'{person.name}: '+person.speech

    def draw(self, surface, camera, art, font, target):
        for person in sorted(self.people,key=lambda p:p.position.y):
            person.draw(surface,camera,art,font,target is person)
