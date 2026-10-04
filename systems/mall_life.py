"""Optional gatherings and evolving conversations, independent of restoration gates."""
from dataclasses import dataclass
import pygame
import random
from systems.requests import RequestSpot


@dataclass(frozen=True)
class Gathering:
    title: str
    invitation: str
    choices: tuple
    guests: tuple


GATHERINGS=(
    Gathering('The neighborhood book swap','Mara saved a table for stories with another chapter left in them.',
              ('An illustrated adventure','A garden handbook','A familiar mystery'),
              (('Lena','My little nephew wants pictures and a grand adventure.',0),
               ('Ash','I finally have a windowsill. I want to learn how to grow something.',1),
               ('Tess','Granddad and I used to solve fictional crimes together.',2))),
    Gathering('A taste of Northgate','Iris is sharing the recipes that once made these halls smell like home.',
              ('Warm cinnamon toast','A pot of mint tea','Fresh berry cake'),
              (('June','Something warm and spiced reminds me of our Sunday breakfasts.',0),
               ('Robin','I would love something herbal to drink while we catch up.',1),
               ('Nico','My sister used to pick berries for her birthday dessert.',2))),
    Gathering('A little plant sale','Fern says a borrowed pot and a little sunlight can begin a garden.',
              ('Kitchen basil','A flowering pot','A shady fern'),
              (('Mo','I want something I can snip for our evening pasta.',0),
               ('Bea','My sunny doorstep needs a splash of color.',1),
               ('Lee','My apartment is shady. Could a leafy plant be happy there?',2))),
    Gathering('The evening makers market','Em and Remy brought a few handmade things to share after work.',
              ('A patchwork scarf','A small paper lantern','A favorite old record'),
              (('Kit','I get cold walking home. Something soft would be lovely.',0),
               ('Sam','My daughter wants a little glowing light for our window.',1),
               ('Alex','I want to hear the songs we danced to here years ago.',2))),
)

OWNER_STORIES={
    'Mara':('I kept the bookshop key on my ring even when the gate was locked. It was a small kind of hope.',
            'A child asked whether the reading corner was coming back. I pulled our old cushions out that evening.',
            'Now the regulars leave books for one another. This shop has become a conversation again.'),
    'Jules':('I used to spend my pocket money here. Opening it myself still feels a little unreal.',
             'Someone brought back a game with their old score written inside. We are keeping that label.',
             'We have started teaching the younger kids our old games. They usually beat us.'),
    'Iris':('My mother measured every recipe in the same chipped mug. I found it in the back cupboard.',
            'The smell of toast brought an old neighbor through the door. She remembered that mug too.',
            'There is always an extra chair now. I think Mum would approve.'),
    'Theo':('People used to bring their best coats here before every winter lantern walk.',
            'A neighbor asked me to mend a coat rather than replace it. There is a story in every seam.',
            'The offcuts are becoming scarves for the community table. Nothing good needs to be wasted.'),
    'Remy':('I kept the last record played here. The sleeve still has a Northgate price sticker.',
             'An old customer recognized the song through the door. We listened to the whole side together.',
             'Neighbors take turns picking the evening record. The soundtrack belongs to all of us now.'),
    'Fern':('These seed tins belonged to my father. He said gardens begin with someone making room.',
            'We traded cuttings with the cafe. Their windowsill is greener than mine now.',
            'People bring empty pots and leave with something living. That feels like Northgate to me.'),
    'Wren':('I first learned to read sitting on the floor of this mall. The letters seemed enormous.',
            'A parent asked for the book I loved then. I had kept a copy all these years.',
            'We have a reading circle again. Some of the listeners were here the first time.'),
    'Em':('My aunt taught me to sew at a table just like this one. I still hear her telling me to slow down.',
          'We are saving little squares from the first orders. Each one remembers a neighbor.',
          'One day those squares will become a quilt for the mall. A place made from little pieces.'),
}


@dataclass(eq=False)
class EventSpot:
    position: pygame.Vector2
    title: str

    @property
    def label(self):return 'Join '+self.title


@dataclass(eq=False)
class EventTask(RequestSpot):
    @property
    def label(self):return ('Hold E: ' if self.duration else 'E: ')+self.title

    def draw(self, surface, camera, art, font, selected):
        point=camera.point(self.position)
        names=('Plant kitchen herbs','Plant sunny flowers','Plant shade-loving leaves','Find donated paper','Find spare ribbon','Find wooden frames')
        sprite='event_item_'+str(names.index(self.title)) if self.title in names else 'request_'+self.kind
        art.draw(surface,sprite,(point.x,point.y-16),(48,48))
        if not self.completed:
            pygame.draw.circle(surface,(130,196,180),point,12,2)
        if selected:pygame.draw.circle(surface,(230,194,124),point,20,2)
        if self.duration and self.progress and not self.completed:
            bar=pygame.Rect(point.x-24,point.y-48,48,5)
            pygame.draw.rect(surface,(38,56,57),bar)
            pygame.draw.rect(surface,(130,196,180),(bar.x,bar.y,round(48*self.progress/self.duration),5))


class MallLife:
    COOLDOWN=300.0

    def __init__(self):
        self.completed={key:0 for key in ('north','east','garden','commons')}
        self.cooldowns={key:0.0 for key in self.completed}
        self.owner_chats={}
        self.active=None
        self.spot=None
        self.round=0
        self.participants=[]
        self.notice=''
        self.elapsed=0.0
        self.owner=None
        self.owner_time=0.0
        self.tasks=[];self.activity='match'

    @staticmethod
    def local_cleanliness(mall, area):
        tiles=[p for p in mall.floor_tiles if area.collidepoint(p)]
        return 1-sum(p in mall.dirty_tiles for p in tiles)/len(tiles) if tiles else 0

    def court(self, game, key):return next(c for c in game.janitors.courts(game.mall) if c[0]==key)

    def available(self, game, key):
        court=self.court(game,key)
        return court[5] and sum(s.restored and not s.upgrade_shop for s in court[3])>=2 and self.local_cleanliness(game.mall,court[2])>=.5

    def event_index(self, key):return (list(self.completed).index(key)+self.completed[key])%len(GATHERINGS)

    def gathering(self, key):return GATHERINGS[self.event_index(key)]

    @property
    def event(self):return self.gathering(self.active) if self.active else None

    def start(self, game, key):
        if self.active or self.cooldowns[key]>0 or not self.available(game,key):return False
        court=self.court(game,key);game.shoppers.walkways.refresh(game.mall)
        index=self.event_index(key)
        # Four distinct neighborhoods within each court, with repeat-visit variation.
        goals=((court[2].left+260,court[2].top+580),
               (court[2].right-270,court[2].top+560),
               (court[2].left+280,court[2].bottom-450),
               (court[2].right-280,court[2].bottom-460))
        goal=pygame.Vector2(goals[index])+pygame.Vector2(random.uniform(-80,80),random.uniform(-64,64))
        nodes=sorted(game.shoppers.walkways.nodes,key=lambda p:(pygame.Vector2(p).distance_squared_to(goal),p))
        point=next((p for p in nodes if court[2].contains(pygame.Rect(p[0]-90,p[1]-100,180,180))
                    and not any(w.colliderect(pygame.Rect(p[0]-90,p[1]-82,180,162)) for w in game.mall.obstacles)
                    and not game.player.rect.colliderect(pygame.Rect(p[0]-90,p[1]-82,180,162))
                    and not any(pygame.Rect(person.position.x-10,person.position.y-12,20,24).colliderect(pygame.Rect(p[0]-90,p[1]-82,180,162))
                                for person in list(game.shoppers.people)+list(game.janitors.people.values()))
                    and game.shoppers.walkways.route(game.mall.entrance,p) is not None),None)
        if point is None:return False
        self.active=key;self.spot=EventSpot(pygame.Vector2(point),self.event.title);self.round=0;self.elapsed=30;self.participants=[]
        self.activity=('match','recipe','plant','hunt')[index]
        self.tasks=[]
        if self.activity in ('plant','hunt'):
            desired=[(court[2].left+180,court[2].top+440),
                     (court[2].right-180,court[2].top+600),
                     (court[2].centerx,court[2].bottom-380)]
            for i,goal in enumerate(desired):
                safe=[p for p in nodes if court[2].contains(pygame.Rect(p[0]-24,p[1]-32,48,64))
                      and pygame.Vector2(p).distance_squared_to(point)>140**2
                      and all(pygame.Vector2(p).distance_squared_to(t.position)>100**2 for t in self.tasks)
                      and not any(w.colliderect(pygame.Rect(p[0]-24,p[1]-32,48,64)) for w in game.mall.obstacles)
                      ]
                if not safe:
                    self.active=None;self.spot=None;self.tasks=[];return False
                nearest=sorted(safe,key=lambda p:pygame.Vector2(p).distance_squared_to(goal))[:24]
                reachable=[p for p in nearest if game.shoppers.walkways.route(point,p) is not None]
                if not reachable:
                    self.active=None;self.spot=None;self.tasks=[];return False
                pos=pygame.Vector2(random.choice(reachable[:8]))
                title=('Plant kitchen herbs','Plant sunny flowers','Plant shade-loving leaves')[i] if self.activity=='plant' else ('Find donated paper','Find spare ribbon','Find wooden frames')[i]
                self.tasks.append(EventTask(pos,title,'plant' if self.activity=='plant' else 'toolkit',2 if self.activity=='plant' else 0))
        self.notice={'match':'Listen to each reader and choose a book for them.',
                     'recipe':'Prepare the cafe tasting in order: brew tea, toast bread, then plate cake.',
                     'plant':'Visit three green markers and hold E to plant a community trail.',
                     'hunt':'Explore three green markers for donated materials, then return to the makers table.'}[self.activity]
        self.sync_spots(game.mall);self.update(0,game)
        game.audio.play('milestone');game.save_checkpoint();return True

    def sync_spots(self, mall):
        # Story spots are maintained by Story.update; events add their own channel.
        obstacle=pygame.Rect(self.spot.position.x-39,self.spot.position.y-49,78,39) if self.spot else None
        previous=getattr(mall,'event_obstacle',None)
        if obstacle!=previous:
            if previous is not None:mall.obstacles.remove(previous)
            if obstacle is not None:mall.obstacles.append(obstacle)
            mall.event_obstacle=obstacle
        if not self.spot and getattr(mall,'suspended_tables',[]):
            for table in mall.suspended_tables:mall.social_tables.append(table);mall.obstacles.append(table.footprint)
            mall.suspended_tables=[]
        mall.event_spots=[tuple(self.spot.position+pygame.Vector2(dx,68)) for dx in (-64,0,64)] if self.spot else []
        mall.event_task_markers=[tuple(t.position) for t in self.visible_tasks]

    def guest(self, index):
        name,clue,answer=self.event.guests[index]
        return (self.participants[index] if index<len(self.participants) else name),clue,answer

    @property
    def visible_tasks(self):return [t for t in self.tasks if not t.completed]

    def touch(self, game, task):
        if task not in self.visible_tasks or task.duration:return False
        task.completed=True;self.round=sum(t.completed for t in self.tasks)
        game.feedback.burst(task.position,'Material found',restored=True)
        game.audio.play('pickup');game.save_checkpoint();return True

    def work(self, dt, game, held, stationary):
        for task in self.visible_tasks:
            if not task.duration:continue
            if held and stationary and task.position.distance_squared_to(game.player.rect.center)<=64**2:
                task.progress=min(task.duration,task.progress+dt)
                game.player.use_tool('setup',task.position)
                if task.progress>=task.duration:
                    task.completed=True;self.round=sum(t.completed for t in self.tasks)
                    game.feedback.burst(task.position,'Planted',restored=True)
                    game.audio.play('pickup');game.save_checkpoint()
            else:task.progress=0

    def menu_content(self):
        if self.round>=3:
            endings=('Books have new readers. The swap shelf will keep their stories moving.',
                     'Tea, toast and cake are ready. The cafe tasting can begin.',
                     'The herb, flower and shade beds make a living trail through the court.',
                     'Donated scraps are ready for the makers. Nothing good needs to be wasted.')
            return endings[self.event_index(self.active)],('Thank the neighbors and collect your reward','','')
        if self.activity=='recipe':
            return ('First, brew a warm drink.','Next, prepare the warm cinnamon toast.','Finally, plate the berry dessert.')[self.round],('Brew mint tea','Toast cinnamon bread','Plate berry cake')
        if self.activity in ('plant','hunt'):
            instruction='Visit the three green markers and hold E to plant the beds.' if self.activity=='plant' else 'Explore the three green markers and press E to collect donated materials.'
            return instruction+f' Finished: {self.round}/3. J opens the map.',()
        name,clue,_=self.guest(self.round)
        return name+': '+clue,self.event.choices

    def choose(self, game, choice):
        if not self.active:return False
        if self.round>=3:
            if choice!=0:return False
            reward=(200,500,1000,1800)[list(self.completed).index(self.active)]
            key=self.active;game.cash+=reward;self.completed[key]+=1;self.cooldowns[key]=self.COOLDOWN
            game.feedback.burst(self.spot.position,f'+${reward} · Neighbors together',restored=True)
            game.audio.play('milestone');self.active=None;self.spot=None;self.round=0;self.notice='';self.participants=[];self.tasks=[];self.activity='match'
            for person in game.shoppers.people:person.event_clue=''
            self.sync_spots(game.mall);game.save_checkpoint();return True
        if self.activity in ('plant','hunt'):return False
        name,_,answer=self.guest(self.round)
        if self.activity=='recipe':name='Iris';answer=self.round
        if choice!=answer:
            self.notice=f'{name}: A kind thought, but listen to what I am looking for. You can try again.'
            game.audio.play('blocked');return False
        self.round+=1;self.notice=f'{name}: That is just what I was hoping for. Thank you for making room for us.'
        game.feedback.burst(self.spot.position,'A little connection',restored=True)
        game.audio.play('pickup');game.save_checkpoint();return True

    def update(self, dt, game):
        for key in self.cooldowns:
            self.cooldowns[key]=max(0,self.cooldowns[key]-dt)
        self.owner_time=max(0,self.owner_time-dt)
        self.sync_spots(game.mall)
        if not self.spot:return
        self.elapsed+=dt
        if self.elapsed>=30:
            self.elapsed=0
            people=game.shoppers.gather(self.court(game,self.active)[2],game.mall.event_spots,game.mall) or []
            if not self.participants:self.participants=[p.name for p in people]
            for i,person in enumerate(people):person.event_clue=self.event.guests[i][1]

    def chat(self, game, store):
        from systems.requests import OWNERS, SUPPLIES
        owner=OWNERS[store.name];stage=min(2,store.request_level)
        count=self.owner_chats.get(store.name,0);self.owner_chats[store.name]=count+1
        personal=OWNER_STORIES.get(owner,(
            f'I kept a box of {SUPPLIES[store.name]} when Northgate closed. I could not quite give up on this place.',
            f'Someone recognized our {SUPPLIES[store.name]} through the window. We talked until closing time.',
            'The shop feels like ours again. Every familiar face brings back a little more of the neighborhood.'))
        area=game.mall.area_for_store(store)
        reactions=('A clean hall makes people feel welcome before they even reach our door.' if self.local_cleanliness(game.mall,area)>=.5 else
                   'It is a little untidy out there today. We will get it back together, one small thing at a time.',
                   'I have started putting a spare chair by the door. You never know who might need a moment.',
                   'When you pass another owner, tell them I said hello. We are neighbors before we are shops.')
        text=personal[stage] if count%2==0 else reactions[(count//2)%len(reactions)]
        game.say_owner(store,text);game.save_checkpoint();return text

    def show_owner(self, store):
        self.owner=store;self.owner_time=10

    def owner_position(self, store):return store.position+pygame.Vector2(42,0)

    def draw(self, game):
        if self.spot:
            point=game.camera.point(self.spot.position)
            pygame.draw.circle(game.screen,(230,194,124),point,10,2)
            if game.target() is self.spot:pygame.draw.circle(game.screen,(130,196,180),point,20,2)

    def draw_owner(self, game):
        if self.owner and self.owner_time:
            point=game.camera.point(self.owner_position(self.owner));variant=sum(map(ord,self.owner.name))%4
            game.art.draw(game.screen,f'owner_{variant}_down_0',(point.x,point.y-12),(48,72))
