"""Visible food queues and continuous front-door trips between the two maps."""
import pygame
from systems.shoppers import Shopper, Shoppers


MENU={
    'Hearth Pizza':('a pizza slice','food_pizza'),
    'Mint & Noodles':('a noodle bowl','food_noodles'),
    'Orchard Juice':('an orchard juice','food_juice'),
    'Sunrise Bakery':('a fresh croissant','food_pastry'),
    'Copper Grill':('a grilled skewer','food_grill'),
    'Garden Bowls':('a garden salad','food_salad'),
    'Moonrise Desserts':('a berry sundae','food_dessert'),
}


class FoodCustomer(Shopper):
    def __init__(self,*args):
        super().__init__(*args)
        self.food=None;self.queue_ticket=None;self.service_time=0

    def update(self,dt,manager,mall,upgrades):
        if self.state=='to_courtyard':
            self.speech_time=max(0,self.speech_time-dt)
            if not self.speech_time:self.walk(dt,86)
            return
        if getattr(mall,'is_courtyard',False):
            if self.state in ('queuing','ordering'):
                self.speech_time=max(0,self.speech_time-dt)
                self.walk(dt,86);return
            if self.state=='returning_inside':return
            if self.state=='arriving':
                # Reserve the tail first, so newcomers never walk through the line.
                self.queue_ticket=manager.next_ticket;manager.next_ticket+=1
                self.state='queuing';self.wait=0;self.goal=None;self.path=[]
                return
            if self.state=='leaving':
                self.walk(dt,86)
                if not self.path and self.position.distance_to(self.entrance)<1:self.state='returning_inside'
                return
        super().update(dt,manager,mall,upgrades)

    def draw(self,surface,camera,art,font,selected):
        # A visible take-away dish replaces an ordinary shop's purchase bag.
        carrying=self.carrying;self.carrying=False
        super().draw(surface,camera,art,font,selected)
        self.carrying=carrying
        if self.visible and self.food:
            p=camera.point(self.display_position)
            art.draw(surface,self.food,(p.x+22,p.y-5),(32,32))


class FoodCourtVisitors(Shoppers):
    def __init__(self):
        super().__init__();self.next_ticket=0

    @staticmethod
    def queue_position(store,index):
        return store.position+pygame.Vector2(0,64*index*(1 if store.facing=='down' else -1))

    def update(self,dt,mall,upgrades,preferred_store=None):
        # All new customers are created at the indoor mall's front entrance.
        super().update(dt,mall,upgrades,preferred_store,spawn=False)
        for store in mall.stores:
            queue=sorted((p for p in self.people if p.store is store and p.state in ('queuing','ordering')),key=lambda p:p.queue_ticket)
            for index,person in enumerate(queue):
                goal=self.queue_position(store,index)
                if person.goal!=goal:
                    path=self.walkways.route(person.position,goal)
                    if path is None:continue
                    person.goal=goal;person.path=path
                if index or person.path or person.position.distance_to(goal)>1:continue
                if person.state!='ordering':
                    person.state='ordering';person.speech='Could I have '+MENU[store.name][0]+', please?';person.speech_time=4
                person.service_time+=dt
                if person.service_time>=max(3,7-1.25*upgrades.courtyard_service_level):
                    person.food=MENU[store.name][1];person.carrying=True
                    # Reuse the existing seating/departure stage, bypassing shop interiors.
                    person.visits=1;person.state='exiting';person.goal=None
                    person.speech='Thank you! This looks lovely.';person.speech_time=0


class CourtyardTravel:
    def __init__(self):self.elapsed=8

    def update(self,dt,game):
        courtyard=game.courtyard
        if not courtyard.unlocked:return
        indoor=game.shoppers;outdoor=courtyard.shoppers;world=courtyard.world
        indoor.walkways.refresh(game.mall);outdoor.walkways.refresh(world)
        door=courtyard.door(game.mall).position
        for person in list(indoor.people):
            if not isinstance(person,FoodCustomer) or person.state!='to_courtyard' or person.path:continue
            if person.position.distance_to(door)>1:continue
            path=outdoor.walkways.route(courtyard.return_door.position,person.store.position)
            if path is None:continue
            indoor.people.remove(person);outdoor.people.append(person)
            person.position=courtyard.return_door.position.copy();person.entrance=person.position.copy()
            person.path=path;person.state='arriving';person.goal=None
        for person in list(outdoor.people):
            if person.state!='returning_inside':continue
            path=indoor.walkways.route(door,game.mall.entrance)
            if path is None:continue
            outdoor.people.remove(person);indoor.people.append(person)
            person.position=door.copy();person.entrance=pygame.Vector2(game.mall.entrance)
            person.path=path;person.state='leaving';person.goal=None
        self.elapsed+=dt
        interval=3.5 if outdoor.traffic=='Busy hours' else 12 if outdoor.traffic=='Quiet hours' else 8
        if self.elapsed<interval:return
        self.elapsed=0
        outbound=[p for p in indoor.people if isinstance(p,FoodCustomer) and p.state=='to_courtyard']
        if len(outbound)+len(outdoor.people)>=outdoor.desired_population(world,game.upgrades):return
        if len(indoor.people)+len(outdoor.people)>=indoor.population_limit(game.mall)+outdoor.population_limit(world):return
        restaurants=[s for s in world.stores if s.restored and not s.upgrade_shop and
                     sum(p.store is s and p.state not in ('leaving','returning_inside') for p in outbound+outdoor.people)<6]
        if not restaurants:return
        path=indoor.walkways.route(game.mall.entrance,door)
        if path is None:return
        store=outdoor.random.choice(restaurants)
        identity=max(indoor.next_identity,outdoor.next_identity)
        person=FoodCustomer(identity,game.mall.entrance,store,indoor.walkways)
        indoor.next_identity=outdoor.next_identity=identity+1
        person.state='to_courtyard';person.path=path;indoor.people.append(person)
