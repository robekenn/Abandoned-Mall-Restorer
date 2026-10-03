"""Four neighborhood chapters; memories and care make a festival possible."""
from dataclasses import dataclass
import pygame
import random


@dataclass(frozen=True)
class Chapter:
    key: str
    title: str
    speaker: str
    opening: str
    memories: tuple
    ending: str
    reward: int
    gathering: str


CHAPTERS=(
    Chapter('north','First lights','Mara',
        'You used to fold paper lanterns here after school. Yours always leaned a little. '
        'When the shutters came down, we kept a box of them. The mall did not need a hero. '
        'It needed someone to begin. Help us remember why we gathered here.',
        ('A faded photograph shows you beneath a lantern taller than your head. On its back: “First lights, together.”',
         'An old drawing shows the fountain surrounded by chairs. Nobody drew the shops. They drew the people.',
         'A folded program lists a reading circle, hot tea and a lantern walk. There was never an admission price.'),
        'Look at the chairs filling up. You have not rebuilt the whole mall, but you have given us a place to begin again. '
        'Remy kept a recording of the last lantern walk. Ask him in the east court.',1000,'Reading circle'),
    Chapter('east','The sound of returning','Remy',
        'I saved the last festival tape. At first I thought the important part was the music. '
        'Listen closer: cups on tables, children laughing, someone calling a friend’s name. '
        'That is the sound we are trying to bring back.',
        ('A record sleeve has a handwritten dedication: “For the ones who stay to stack the chairs.”',
         'A cassette label reads “Northgate, winter evening.” Between songs, a crowd sings a little out of tune.',
         'An old concert ticket has no price. It says: “Bring a story. Bring a neighbor.”'),
        'There is music between the shutters again. Fern still remembers how we made the lanterns. '
        'She says the garden court can grow something in winter after all.',5000,'Record afternoon'),
    Chapter('garden','Things made by hand','Fern',
        'We used to make lanterns from scraps: paper, thread, a little patience. Every one looked different. '
        'That was the point. You cannot order a neighborhood from a catalog. '
        'You make room for people to leave a little of themselves here.',
        ('A pressed flower rests inside a lantern pattern. Its note says: “Winter is not the end of growing.”',
         'A spool of bright thread has been shared and rewound so often that its label is unreadable.',
         'A sketch shows a lantern patched with three colors. Beneath it: “Mended is still beautiful.”'),
        'The tables are busy and the lanterns are ready. Take them to the Commons. '
        'Wren has been waiting for a reason to put the long table out again.',12000,'Lantern workshop'),
    Chapter('commons','A place for everyone','Wren',
        'The last year we held the walk, we ran out of chairs. People brought some from home. '
        'We kept adding places until everyone fit. Northgate was never finished. '
        'It was a promise to keep making room. Will you help us keep it?',
        ('A guest book holds names in many hands. Someone has added: “I did not know anyone when I arrived.”',
         'A table plan has been erased and extended past the edge of the page. There is room for one more.',
         'The final invitation is blank where the date should be. It was waiting for the neighborhood to choose a day.'),
        'The invitation can have a date again. There is no perfect moment when all the work is done. '
        'There is this evening, these neighbors, and the light we can share. Let us begin the lantern walk.',30000,'Neighborhood supper'),
)


@dataclass(eq=False)
class StoryPoint:
    chapter: int
    position: pygame.Vector2
    memory: int = -1
    source: str = 'ground'
    name: str = ''
    variant: int = 0
    clue: str = ''

    @property
    def label(self):
        if self.memory<0:return 'Read the community board'
        if self.source=='neighbor':return 'Talk to '+self.name
        return 'Recover a Northgate keepsake'


class Story:
    def __init__(self):
        self.seed=random.SystemRandom().randrange(2**31)
        self.started=[False]*4;self.memories=[[False]*3 for _ in range(4)];self.completed=[False]*4
        self.festival=False;self.elapsed=0.;self.celebrations=[0.]*4;self.points=[]

    @property
    def current(self):return next((i for i,done in enumerate(self.completed) if not done),4)

    def setup(self, mall):
        self.points=[];rng=random.Random(self.seed)
        areas=[mall.opening_area]+[r.area for r in mall.regions]
        for i,area in enumerate(areas):
            floor=mall.north_floor_tiles if i==0 else mall.regions[i-1].floor_tiles
            stores=mall.north_stores if i==0 else mall.regions[i-1].stores
            safe=[p for p in floor if area.contains(pygame.Rect(p[0]-16,p[1]-16,32,32)) and
                  not any(w.colliderect(pygame.Rect(p[0]-16,p[1]-16,32,32)) for w in mall.obstacles)]
            board=min(safe,key=lambda p:pygame.Vector2(p).distance_squared_to((area.left+488,area.top+760)))
            self.points.append(StoryPoint(i,pygame.Vector2(board),-1,'board'))
            keeper=rng.randrange(3);ground=0;chosen=[board]
            for memory in range(3):
                neighbor=memory==keeper
                if neighbor:
                    goal=(area.left+300,area.top+800);name=('Lena','Ash','Tess','Mo')[i]
                    clue='Ask '+name+' near the west seating area.'
                else:
                    goal=(area.left+110,area.top+410) if ground==0 else (area.right-120,area.bottom-380)
                    clue='Look in the quiet northwest corner.' if ground==0 else 'Look along the far southeast storefront edge.'
                    ground+=1;name=''
                candidates=[p for p in safe if p not in chosen and
                            all(store.position.distance_squared_to(p)>85**2 for store in stores) and
                            (neighbor or pygame.Vector2(p).distance_squared_to(board)>300**2)]
                nearest=sorted(candidates,key=lambda p:pygame.Vector2(p).distance_squared_to(goal))[:6 if neighbor else 12]
                point=rng.choice(nearest);chosen.append(point)
                self.points.append(StoryPoint(i,pygame.Vector2(point),memory,'neighbor' if neighbor else 'ground',name,i,clue))
        self.update(0,mall)

    def visible_points(self, mall):
        unlocked=1+len(mall.active_regions)
        return [p for p in self.points if p.source!='neighbor' and p.chapter<unlocked and (p.memory<0 or
                p.chapter==self.current and self.started[p.chapter] and not self.memories[p.chapter][p.memory])]

    def visible_neighbors(self, mall):
        return [p for p in self.points if p.source=='neighbor' and p.chapter<=len(mall.active_regions) and self.started[p.chapter]]

    def clue(self, chapter, memory):
        return next(p.clue for p in self.points if p.chapter==chapter and p.memory==memory)

    @staticmethod
    def lantern_positions(store):
        y=store.rect.top+110 if store.facing=='down' else store.rect.top-64
        return [(store.rect.left+dx,y) for dx in (40,100,store.rect.width-100,store.rect.width-40)]

    def requirements(self, game, i):
        court=game.janitors.courts(game.mall)[i]
        stores=court[3];key=court[0]
        fixture_keys={o.key for category in ('Furniture','Garden') for o in game.upgrades.offers(category,key)}
        first_sweep=game.mall.initial_cleanup_complete if i==0 else game.mall.regions[i-1].initial_cleanup_complete
        return [('Recover the three keepsakes',sum(self.memories[i]),3),
                ('Complete the first sweep',int(first_sweep),1),
                ('Reopen six businesses',sum(s.restored for s in stores),6),
                ('Help owners with two requests',sum(s.request_level+s.recurring_completed for s in stores if not s.upgrade_shop),2),
                ('Restore three local fixtures',len(fixture_keys&game.upgrades.decor),3)]

    def ready(self, game, i):
        return i==self.current and self.started[i] and all(n>=goal for _,n,goal in self.requirements(game,i))

    def action(self, point, game):
        i=point.chapter
        if point.source=='neighbor':
            if point not in self.visible_neighbors(game.mall):return False
            if not self.memories[i][point.memory]:
                self.memories[i][point.memory]=True
                item=(('photograph','fountain drawing','festival program'),('record sleeve','cassette','old ticket'),
                      ('flower pattern','spool of thread','lantern sketch'),('guest book','table plan','invitation'))[i][point.memory]
                text=f'I found this {item} lying around while I was walking here. I thought {CHAPTERS[i].speaker} might know its story. Here, take it back to the community board.'
                game.feedback.burst(point.position,'KEEPSAKE',restored=True)
                game.save_checkpoint()
            else:text='I am glad that little keepsake found its way home. Come say hello whenever you pass.'
            game.speech.say(point.name,text,point.position);game.audio.play('pickup');return True
        if point.memory>=0:
            if point not in self.visible_points(game.mall):return False
            self.memories[i][point.memory]=True
            game.story_menu.visit(i,CHAPTERS[i].memories[point.memory],None)
            game.audio.play('pickup');game.save_checkpoint();return True
        if i<self.current:
            text=CHAPTERS[i].ending
            action='festival' if i==3 and self.current==4 else 'gather'
        elif i>self.current:
            text='First, finish '+CHAPTERS[self.current].title+'. Every court has something to give the next.';action=None
        elif not self.started[i]:text=CHAPTERS[i].opening;action='begin'
        elif self.ready(game,i):text=CHAPTERS[i].ending;action='claim'
        else:text=CHAPTERS[i].opening;action=None
        game.story_menu.visit(i,text,action);return True

    def invite(self, game, i):
        self.update(0,game.mall)
        area=game.janitors.courts(game.mall)[i][2]
        # Gather around the board, rather than sending neighbors to distant finds.
        board=next(p.position for p in self.points if p.chapter==i and p.memory<0)
        goals=[board+pygame.Vector2(dx,dy) for dx,dy in ((-64,64),(64,64),(0,128))]
        game.shoppers.gather(area,goals,game.mall)

    def confirm(self, game, i, action):
        if action=='begin' and i==self.current:self.started[i]=True;return True
        if action=='claim' and self.ready(game,i):
            self.completed[i]=True;self.celebrations[i]=45
            game.cash+=CHAPTERS[i].reward
            board=next(p for p in self.points if p.chapter==i and p.memory<0)
            game.feedback.burst(board.position,f'+${CHAPTERS[i].reward}',restored=True)
            self.invite(game,i);game.audio.play('milestone');return True
        if action=='festival' and self.current==4:
            self.festival=True;self.celebrations=[60.]*4
            for chapter in range(4):self.invite(game,chapter)
            game.audio.play('milestone')
            game.story_menu.visit(3,'You remember looking up at the lanterns as a child. Tonight someone else is looking up. '
                                  'You made this possible one small act at a time. Northgate will still need care tomorrow. '
                                  'For tonight, there is light enough for everyone.',None)
            return True
        if action=='gather' and self.completed[i]:self.celebrations[i]=30;self.invite(game,i);return True
        return False

    def hud_goal(self, game):
        i=self.current
        if i==4:
            return ('The lantern walk','Read the Commons community board to light the first lantern.') if not self.festival else None
        if i>len(game.mall.active_regions):return None
        if not self.started[i]:return CHAPTERS[i].title,'Read the gold community board. J → Story shows where to begin.'
        if self.ready(game,i):return CHAPTERS[i].title,'Return to the community board and gather the neighbors.'
        requirements=self.requirements(game,i)
        for index in (0,3,4):
            label,count,goal=requirements[index]
            if count<goal and (index==0 or requirements[2][1]>=6):return CHAPTERS[i].title,label+f' · {count}/{goal}. J → Story.'
        return None

    def update(self, dt, mall):
        self.elapsed+=dt
        self.celebrations=[max(0,t-dt) for t in self.celebrations]
        # Neighbors meet regularly after a chapter, without generating free income.
        mall.story_markers=[tuple(p.position) for p in self.visible_points(mall) if p.memory<0]
        mall.community_spots=[tuple(p.position+pygame.Vector2(dx,dy)) for p in self.points if p.memory<0 and self.completed[p.chapter]
                              and (self.celebrations[p.chapter]>0 or self.elapsed%150<30) for dx,dy in ((-64,64),(64,64),(0,128))]

    def draw(self, game):
        for point in self.visible_points(game.mall):
            pixel=game.camera.point(point.position)
            if point.memory<0:
                game.art.draw(game.screen,'community_board',(pixel.x,pixel.y-16),(72,72))
                if point.chapter==self.current:pygame.draw.circle(game.screen,(230,194,124),pixel,16,2)
            else:
                game.art.draw(game.screen,'story_'+CHAPTERS[point.chapter].key,(pixel.x,pixel.y-8),(48,48))
                if point.position.distance_squared_to(game.player.rect.center)<180**2:
                    pygame.draw.rect(game.screen,(230,194,124),(pixel.x+15,pixel.y-14,3,3))
        for i,done in enumerate(self.completed):
            if not done:continue
            board=next(p for p in self.points if p.chapter==i and p.memory<0)
            stores=game.mall.north_stores if i==0 else game.mall.regions[i-1].stores
            for store in stores:
                if not store.restored:continue
                lanterns=[game.camera.point(p) for p in self.lantern_positions(store)]
                north=store.facing=='up'
                if north:
                    # Front-corner uprights lift the string above the low roof.
                    # The lamps hang from it, matching the upper row's fixtures.
                    for x in (store.rect.left+18,store.rect.right-18):
                        base=game.camera.point((x,store.rect.top+12))
                        tip=game.camera.point((x,store.rect.top-88))
                        pygame.draw.line(game.screen,(41,56,59),base,tip,4)
                        pygame.draw.line(game.screen,(133,110,76),base,tip,2)
                pygame.draw.line(game.screen,(133,110,76),(lanterns[0].x-22,lanterns[0].y-24),
                                 (lanterns[-1].x+22,lanterns[-1].y-24),2)
                for n,p in enumerate(lanterns):
                    name='festival_lantern_north_' if north else 'festival_lantern_'
                    game.art.draw(game.screen,name+str((int(self.elapsed*2)+n)%2),p,(48,48))
            if self.celebrations[i]>0:
                for n in range(15):
                    p=game.camera.point(board.position+pygame.Vector2((n*31)%210-105,(n*17+self.elapsed*24)%100-70))
                    pygame.draw.rect(game.screen,((223,180,94),(130,196,180),(228,216,164))[n%3],(p.x,p.y,3,4))

    def draw_neighbor(self, game, point):
        pixel=game.camera.point(point.position)
        game.art.draw(game.screen,f'shopper_{point.variant}_down_0',(pixel.x,pixel.y-12),(48,72))
        if not self.memories[point.chapter][point.memory]:
            game.art.draw(game.screen,'story_'+CHAPTERS[point.chapter].key,(pixel.x+20,pixel.y-4),(24,24))

    def prepare(self, game):
        """Opt-in developer shortcut prepares the next chapter for its real claim."""
        if not game.developer.enabled or self.current==4:return False
        i=self.current
        while i>len(game.mall.active_regions):
            game.developer.act('next',game)
        court=game.janitors.courts(game.mall)[i]
        for t in court[4]:game.mall.clean_trash(t)
        for s in court[3][:6]:s.restored=True
        owner=next(s for s in court[3] if not s.upgrade_shop and s is not game.owner_requests.store)
        owner.request_level=max(2,owner.request_level);owner.request_bonus=max(1.5,owner.request_bonus)
        fixtures=[o.key for category in ('Furniture','Garden') for o in game.upgrades.offers(category,court[0])]
        game.upgrades.decor.update(fixtures[:3]);game.mall.refresh_businesses()
        self.started[i]=True;self.memories[i]=[True]*3
        game.player.rect.center=next(p.position for p in self.points if p.chapter==i and p.memory<0)
        return True
