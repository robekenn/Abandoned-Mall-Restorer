"""Bounded visitors with obstacle-aware routes through unlocked galleries."""
from collections import deque
import random
import pygame


class Walkways:
    def __init__(self):
        self.signature = None
        self.nodes = set()
        self.edges = {}

    def refresh(self, mall):
        signature = mall.east.unlocked
        if self.signature == signature:
            return
        self.signature = signature
        self.nodes = {p for p in mall.floor_tiles if not any(
            w.colliderect(pygame.Rect(p[0]-10,p[1]-12,20,24)) for w in mall.obstacles)}
        walls = [w.inflate(20,24) for w in mall.obstacles]
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
            return []
        path = []; node = end
        while node != start:
            path.append(pygame.Vector2(node)); node = previous[node]
        return list(reversed(path))


class Shopper:
    def __init__(self, identity, origin, store, walkways):
        self.identity = identity
        self.name = ('Alex','Bea','Sam','Nico','June','Lee','Robin','Kit')[identity%8]
        self.variant = identity%4
        self.position = pygame.Vector2(walkways.nearest(origin))
        self.entrance = self.position.copy()
        self.store = store
        self.path = walkways.route(self.position,store.position)
        self.state = 'arriving'
        self.wait = 0.0
        self.facing = 'down'
        self.frame = 0
        self.animation_time = 0.0
        self.done = False
        self.greeted = False

    @property
    def label(self):
        return f'Say hello to {self.name} / visiting {self.store.name}'

    @property
    def visible(self):
        return self.state != 'inside' and not self.done

    def update(self, dt, manager, mall, upgrades):
        if self.state == 'inside':
            self.wait += dt
            self.frame = 0
            if self.wait >= 10+self.identity%3*2:
                self.path = [self.store.position.copy(),pygame.Vector2(manager.walkways.nearest(self.store.position))]
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
            self.path = [self.store.position.copy(),pygame.Vector2(self.store.rect.centerx,self.store.rect.bottom-28)]
            self.state = 'entering'
        elif self.state == 'entering':
            self.state,self.wait = 'inside',0
        elif self.state == 'exiting':
            amenities = manager.amenities(mall,upgrades)
            goal = manager.random.choice(amenities) if amenities else self.entrance
            self.path = manager.walkways.route(self.position,goal)
            self.state,self.wait = ('strolling' if amenities else 'leaving'),0
        elif self.state == 'strolling':
            self.state,self.wait = 'resting',0
        elif self.state == 'resting':
            self.wait += dt
            if self.wait >= 4:
                self.path = manager.walkways.route(self.position,self.entrance)
                self.state,self.wait = 'leaving',0
        elif self.state == 'leaving':
            self.done = True

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
        if mall.east.unlocked and 'fountain_east' in upgrades.decor:
            points.append((mall.east.fountain.centerx,mall.east.fountain.bottom+45))
        return points

    def update(self, dt, mall, upgrades, preferred_store=None):
        self.walkways.refresh(mall)
        opened = [s for s in mall.stores if s.restored]
        for person in self.people:
            person.update(dt,self,mall,upgrades)
        self.people = [p for p in self.people if not p.done]
        for store in mall.stores:
            store.door_open = any(p.store is store and p.state in ('entering','exiting') for p in self.people)
        desired = min(12,len(opened)+(2 if mall.cleanliness >= 0.5 else 0)+len(self.amenities(mall,upgrades))//2) if opened else 0
        self.elapsed += dt
        if self.elapsed >= 8 and len(self.people)<desired:
            self.elapsed = 0
            store = preferred_store if preferred_store in opened else self.random.choice(opened)
            origin = (1860,1000) if store in mall.east.stores else (160,1000)
            self.people.append(Shopper(self.next_identity,origin,store,self.walkways))
            self.next_identity += 1

    def greet(self, person):
        if person.greeted:
            return f'{person.name}: Good to see you again!'
        person.greeted = True
        return f'{person.name}: '+self.random.choice([
            'It feels good to see this place coming back.',
            'I used to come here when I was little.',
            'Thanks for looking after our mall.',
            'One little change makes a big difference.'])

    def draw(self, surface, camera, art, font, target):
        for person in sorted(self.people,key=lambda p:p.position.y):
            person.draw(surface,camera,art,font,target is person)
