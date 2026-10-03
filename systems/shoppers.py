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
        signature = (tuple(r.unlocked for r in mall.regions),tuple(tuple(w) for w in mall.obstacles))
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

    def join(self, point):
        if not self.nodes:return None
        closest=self.nearest(point)
        if not any(w.clipline(point,closest) for w in self.walls):return closest
        candidates=sorted(self.nodes,key=lambda p:pygame.Vector2(p).distance_squared_to(point))[:12]
        return next((p for p in candidates if not any(w.clipline(point,p) for w in self.walls)),None)

    def route(self, origin, destination):
        start,end = self.join(origin),self.join(destination)
        if start is None or end is None:return None
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
        self.visits=0;self.carrying=False;self.activity='';self.rest_seconds=4;self.seat=None;self.friend_name='';self.goal=None;self.event_clue=''

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
                self.carrying=True
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
            self.visits+=1
            if self.visits==1 and self.identity%3==1 and mall.cleanliness>=.75:
                neighbors=sorted((s for s in mall.stores if s.restored and s is not self.store
                                  and mall.area_for_store(self.store).collidepoint(s.position)),
                                 key=lambda s:self.position.distance_squared_to(s.position))
                for store in neighbors:
                    path=manager.walkways.route(self.position,store.position)
                    if path is not None:
                        self.store=store;self.path=path;self.state='arriving';return
            goals=manager.amenities(mall,upgrades)
            manager.random.shuffle(goals)
            # Visitors enjoy amenities in their own court, keeping trips manageable.
            local=[p for p in goals if mall.area_for_store(self.store).collidepoint(p)]
            goal=next((p for p in local if manager.walkways.route(self.position,p) is not None),self.entrance)
            friend=next((p for p in manager.people if p is not self and p.state=='resting' and p.activity in ('fountain','gathering') and mall.area_for_store(self.store).collidepoint(p.position)),None) if self.identity%4==2 else None
            if friend is not None:
                meeting=manager.walkways.nearest(friend.position+pygame.Vector2(64,0))
                if manager.walkways.route(self.position,meeting) is not None:goal=meeting;self.friend_name=friend.name
                else:friend=None
            path=manager.walkways.route(self.position,goal)
            if path is None:return
            self.path=path;self.goal=pygame.Vector2(goal);self.activity='meeting' if friend is not None else manager.activity(goal,mall,upgrades)
            self.seat=next((b for b in mall.benches if pygame.Vector2(goal).distance_to((b.centerx,b.bottom+40))<1),None) if self.activity=='bench' else None
            self.rest_seconds=(8 if self.activity=='bench' else 12 if self.activity=='fountain' else 20 if self.activity in ('gathering','meeting') else 4)
            self.rest_seconds*=1.5 if mall.cleanliness>=.75 and self.identity%3==1 else 1
            self.state,self.wait = ('leaving' if pygame.Vector2(goal)==self.entrance else 'strolling'),0
        elif self.state == 'strolling':
            if self.goal is not None and self.position.distance_to(self.goal)>1:
                self.path=manager.walkways.route(self.position,self.goal) or [];return
            if self.activity!='meeting':self.activity=manager.activity(self.position,mall,upgrades)
            if self.activity=='gathering':self.rest_seconds=max(self.rest_seconds,20)
            self.state,self.wait = 'resting',0
        elif self.state == 'resting':
            self.wait += dt
            if self.wait >= self.rest_seconds:
                path=manager.walkways.route(self.position,self.entrance)
                if path is None:return
                self.path=path;self.activity=''
                self.state,self.wait = 'leaving',0
        elif self.state == 'leaving':
            # An exhausted/failed route never counts as leaving in mid-concourse.
            if self.position.distance_to(self.entrance)<1:self.done = True
            else:self.path=manager.walkways.route(self.position,self.entrance) or []

    @property
    def display_position(self):
        return pygame.Vector2(self.seat.centerx,self.seat.centery+22) if self.state=='resting' and self.activity=='bench' and self.seat else self.position

    def draw(self, surface, camera, art, font, selected):
        if not self.visible:
            return
        point = camera.point(self.display_position)
        pose='sit' if self.state=='resting' and self.activity=='bench' else str(self.frame)
        art.draw(surface,f'shopper_{self.variant}_{self.facing}_{pose}',(point.x,point.y-12),(48,72))
        if self.carrying:
            side=-21 if self.facing=='left' else 21
            art.draw(surface,'purchase_bag',(point.x+side,point.y+4),(24,24))
        if self.state=='resting' and self.activity in ('fountain','gathering'):
            art.draw(surface,'visitor_'+('cup' if self.activity=='fountain' else 'book'),(point.x+18,point.y-9),(18,18))
        if selected:
            pygame.draw.ellipse(surface,(175,210,186),(point.x-14,point.y+8,28,10),2)
            label = font.render(self.name,True,(218,225,191))
            surface.blit(label,label.get_rect(center=(point.x,point.y-54)))


class Shoppers:
    def __init__(self):
        self.people = []
        self.walkways = Walkways()
        self.path_signature=None
        self.random = random.Random(97)
        self.elapsed = 8.0
        self.next_identity = 0

    def amenities(self, mall, upgrades):
        points = [(b.centerx,b.bottom+40) for i,b in enumerate(mall.benches) if f'bench_{i}' in upgrades.decor and not any(p.activity=='bench' and p.state in ('strolling','resting') and pygame.Vector2(p.goal if p.state=='strolling' and p.goal is not None else p.position).distance_to((b.centerx,b.bottom+40))<1 for p in self.people)]
        if 'fountain' in upgrades.decor:
            points.append((mall.fountain.centerx,mall.fountain.bottom+45))
        for region in mall.active_regions:
            if f'fountain_{region.key}' in upgrades.decor:
                points.append((region.fountain.centerx,region.fountain.bottom+45))
        points.extend(getattr(mall,'community_spots',()))
        points.extend(getattr(mall,'event_spots',()))
        return points

    def activity(self, goal, mall, upgrades):
        point=pygame.Vector2(goal)
        if any(point.distance_to(p)<32 for p in list(getattr(mall,'community_spots',()))+list(getattr(mall,'event_spots',()))):return 'gathering'
        if any(point.distance_to((b.centerx,b.bottom+40))<32 for i,b in enumerate(mall.benches) if f'bench_{i}' in upgrades.decor):return 'bench'
        return 'fountain' if any(point.distance_to(p)<32 for p in self.amenities(mall,upgrades)) else ''

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
            if path is not None:person.path=path;person.goal=pygame.Vector2(goal);person.state='strolling';person.wait=0;person.activity='gathering';person.rest_seconds=20
        return neighbors

    def update(self, dt, mall, upgrades, preferred_store=None):
        self.walkways.refresh(mall)
        if self.path_signature!=self.walkways.signature:
            self.path_signature=self.walkways.signature
            for person in self.people:
                if person.path and person.state not in ('inside','entering','exiting'):
                    person.path=self.walkways.route(person.position,person.path[-1]) or []
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
        if person.state=='resting':
            person.speech={'bench':'I meant to leave, but this is a lovely place to sit and catch up.',
                           'fountain':'Listen to the water. I remember that sound from when I was small.',
                           'gathering':'Someone saved a place for me at the table. I brought something to share.',
                           'meeting':f'I bumped into {person.friend_name}. We used to meet here after school. It is good to have our spot back.'}.get(person.activity,person.speech)
        elif person.carrying and person.greeted:person.speech='I found a little something to take home. It is nice to shop close to my neighbors again.'
        if person.event_clue:person.speech=person.event_clue
        person.greeted=True
        person.speech_time=max(5,min(10,len(person.speech)/14))
        return f'{person.name}: '+person.speech

    def draw(self, surface, camera, art, font, target):
        for person in sorted(self.people,key=lambda p:p.position.y):
            person.draw(surface,camera,art,font,target is person)
