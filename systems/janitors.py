"""One paid cleaner per court, with local routes and discounted automatic sales."""
import pygame
from systems.shoppers import Walkways
from entities.player import draw_tool


class CourtPaths(Walkways):
    def __init__(self, area):
        super().__init__()
        self.area=area.copy()

    def refresh(self, mall):
        previous=self.signature
        super().refresh(mall)
        if previous==self.signature:return
        self.nodes={p for p in self.nodes if self.area.collidepoint(p)}
        self.edges={p:[q for q in self.edges[p] if q in self.nodes] for p in self.nodes}


class Janitor:
    WALK_SPEEDS=(48,64,80,96)
    CLEAN_SECONDS=(5,4,3,2)

    def __init__(self, key, area, origin, mall):
        self.key=key
        self.paths=CourtPaths(area);self.paths.refresh(mall)
        self.position=pygame.Vector2(self.paths.nearest(origin))
        self.walk_level=self.clean_level=0
        self.target=None;self.path=[];self.progress=0
        self.facing='down';self.frame=0;self.animation_time=0
        self.wander_index=0;self.idle_wait=0
        self.cleaned=0;self.earnings=0

    @property
    def speed(self):return self.WALK_SPEEDS[self.walk_level]

    @property
    def clean_seconds(self):return self.CLEAN_SECONDS[self.clean_level]

    def route_to(self, destination, mall):
        end=self.paths.nearest(destination)
        path=self.paths.route(self.position,end)
        start=self.paths.nearest(self.position)
        if path is None:return None
        # Both off-grid joins must fit the cleaner's footprint.
        joins=[(self.position,start),(end,destination)]
        if any(w.inflate(20,24).clipline(a,b) for a,b in joins for w in mall.obstacles):return None
        return [pygame.Vector2(start)]+path+[pygame.Vector2(destination)]

    def choose_work(self, pool, mall, protected=()):
        for trash in sorted((t for t in pool if not t.cleaned and t not in protected),key=lambda t:self.position.distance_squared_to(t.position)):
            path=self.route_to(trash.position,mall)
            if path is not None:
                self.target=trash;self.target_revision=getattr(trash,'revision',0);self.path=path;self.progress=0;return True
        return False

    def move(self, dt):
        budget=self.speed*dt;used=0
        while self.path and budget>0:
            delta=self.path[0]-self.position;distance=delta.length()
            if distance<.001:self.path.pop(0);continue
            self.facing=('right' if delta.x>0 else 'left') if abs(delta.x)>abs(delta.y) else ('down' if delta.y>0 else 'up')
            step=min(distance,budget);self.position+=delta*(step/distance)
            used+=step;budget-=step
            if step==distance:self.path.pop(0)
        self.animation_time=self.animation_time+dt if used else 0
        self.frame=int(self.animation_time/.2)%4 if used else 0
        return max(0,dt-used/self.speed)

    def update(self, dt, pool, game, world=None):
        world=game.mall if world is None else world
        before=self.paths.signature;self.paths.refresh(world)
        if before!=self.paths.signature and self.path:
            destination=self.target.position if self.target else self.path[-1]
            route=self.route_to(destination,world)
            self.path=route or []
            if route is None:self.target=None;self.progress=0
        requests=game.owner_requests
        visible=(world is game.mall and game.scene=='mall') or (world is game.courtyard.world and game.scene=='courtyard')
        player_position=game.player.rect.center if visible else (game.main_position if world is game.mall and game.main_position is not None else world.entrance)
        protected=[]
        if requests.favor and requests.favor.mode=='collect' and requests.progress<requests.amount:
            remaining=requests.amount-requests.progress
            protected=sorted((t for t in world.trash if not t.cleaned),key=lambda t:t.position.distance_squared_to(player_position))[:remaining]
        if self.target in protected:self.target=None;self.path=[];self.progress=0
        if self.target and (self.target.cleaned or getattr(self.target,'revision',0)!=self.target_revision):
            self.target=None;self.path=[];self.progress=0
        if self.target and self.path and not self.progress:
            closer=[t for t in pool if not t.cleaned and t not in protected and
                    self.position.distance_squared_to(t.position)<self.position.distance_squared_to(self.target.position)]
            def length(path):
                return sum(pygame.Vector2(a).distance_to(b) for a,b in zip([self.position]+path,path))
            remaining_distance=length(self.path)
            for trash in sorted(closer,key=lambda t:self.position.distance_squared_to(t.position)):
                route=self.route_to(trash.position,world)
                # A shortcut must shorten the walk, avoiding oscillation around obstacles.
                if route is not None and length(route)+64<remaining_distance:
                    self.target=trash;self.target_revision=getattr(trash,'revision',0)
                    self.path=route;self.progress=0;break
        if not self.target and self.choose_work(pool,world,protected):self.idle_wait=0
        if not self.target:
            if not self.path:
                self.idle_wait+=dt
                if self.idle_wait>=3:
                    nodes=sorted(self.paths.nodes)
                    self.wander_index=(self.wander_index+7)%len(nodes)
                    self.path=self.paths.route(self.position,nodes[self.wander_index]) or [];self.idle_wait=0
            self.move(dt);return
        remaining=self.move(dt)
        if self.path:return
        self.frame=0;self.progress+=remaining
        if self.progress+1e-9<self.clean_seconds:return
        if world.clean_trash(self.target):
            payout=game.upgrades.unit_value*.75
            game.cash+=payout;self.earnings+=payout;self.cleaned+=1
            if visible:game.feedback.burst(self.target.position,f'+${payout:g}',restored=True)
        self.target=None;self.progress=0;self.path=[]

    def draw(self, game):
        point=game.camera.point(self.position)
        cleaning=bool(self.progress and self.target and not self.target.cleaned and not self.path)
        frame=int(self.progress/.105)%4 if cleaning else self.frame
        pose=f'clean_{frame}' if cleaning else str(frame)
        game.art.draw(game.screen,f'janitor_{self.facing}_{pose}',(point.x,point.y-12),(48,72))
        if cleaning:
            draw_tool(game.screen,game.art,point,self.facing,frame,'broom' if self.target.kind=='dirt' else 'grabber')
        if self.progress:
            rect=pygame.Rect(point.x-23,point.y-65,46,5)
            pygame.draw.rect(game.screen,(41,56,59),rect)
            pygame.draw.rect(game.screen,(113,175,188),(rect.x,rect.y,round(rect.width*self.progress/self.clean_seconds),rect.height))


class Janitors:
    def __init__(self):self.people={}

    @staticmethod
    def courts(mall):
        if getattr(mall,'is_courtyard',False):
            return [('courtyard','Courtyard',mall.opening_area,mall.stores,mall.trash,True,mall.entrance)]
        return [('north','North arcade',mall.opening_area,mall.north_stores,mall.north_trash,True,mall.delivery.position)]+[
            (r.key,r.name,r.area,r.stores,r.trash,r.unlocked,r.delivery.position) for r in mall.regions]

    def hire_cost(self, key, mall):return 2*max(s.cost for s in next(c for c in self.courts(mall) if c[0]==key)[3])

    def upgrade_price(self, key, track, mall):
        person=self.people[key];level=getattr(person,track+'_level')
        return None if level==3 else self.hire_cost(key,mall)*(1,2,4)[level]//4

    def purchase(self, key, action, game, mall=None):
        mall=game.mall if mall is None else mall
        court=next((c for c in self.courts(mall) if c[0]==key),None)
        if court is None or not court[5]:return False,'Open this court before hiring.'
        if action=='hire':
            if key in self.people:return False,'This court already has its janitor.'
            price=self.hire_cost(key,mall)
        elif action in ('walk','clean') and key in self.people:
            price=self.upgrade_price(key,action,mall)
            if price is None:return False,'This upgrade is already at its maximum.'
        else:return False,'Hire this court’s janitor first.'
        if game.cash<price:return False,f'You need ${price-game.cash:g} more.'
        game.cash-=price
        if action=='hire':self.people[key]=Janitor(key,court[2],court[6],mall)
        else:
            person=self.people[key];setattr(person,action+'_level',getattr(person,action+'_level')+1)
        return True,''

    def update(self, dt, game, mall=None):
        mall=game.mall if mall is None else mall
        for key,_,_,_,pool,_,_ in self.courts(mall):
            if key in self.people:self.people[key].update(dt,pool,game,mall)
