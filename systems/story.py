"""Four neighborhood chapters; memories and care make a festival possible."""
from dataclasses import dataclass
import pygame
import random

READING_TABLE = 'table_0'
READING_CHAIRS = ('table_0_seat_0', 'table_0_seat_1')
READING_FIXTURES = (READING_TABLE, *READING_CHAIRS)


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
        'Marty? You always chose the lantern with the crooked handle. I kept it with our reading-circle books. '
        'I thought we should put everything back exactly as it was. Then a child asked if she could bring her own story. '
        'Help me reopen Pages and restore the first table and its two chairs by the west seats. Our three keepsakes will help us begin.',
        ('A faded photograph shows young Marty holding a crooked lantern. A note from Mara reads: “You said it was the best one because it was yours.”',
         'An old drawing shows the west reading table with mismatched chairs. Someone has penciled in another place: “For whoever comes next.”',
         'A folded program invites neighbors to bring a favorite story. In the margin: “Leave time for someone we have not met yet.”'),
        'Look at our reading table, Marty. I left a place for the new story that child wants to bring. '
        'The old chairs never matched, did they? Somehow I forgot that. '
        'Remy kept a recording of the last lantern walk. When you reach East, ask him what else he can hear on it.',1000,'Reading circle'),
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
        self.layout=3
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
            goals=((area.left+340,area.top+680),(area.right-330,area.top+520),
                   (area.left+300,area.bottom-480),(area.right-360,area.bottom-450))
            goal=goals[i] if self.layout>=2 else (area.left+488,area.top+760)
            goal=(area.left+145 if i%2==0 else area.right-145,area.top+610)
            board=min(safe,key=lambda p:pygame.Vector2(p).distance_squared_to(goal))
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
        return [p for p in self.points if p.source=='neighbor' and p.chapter<=len(mall.active_regions) and self.started[p.chapter] and not self.memories[p.chapter][p.memory]]

    def clue(self, chapter, memory):
        return next(p.clue for p in self.points if p.chapter==chapter and p.memory==memory)

    @staticmethod
    def lantern_positions(store):
        y=store.rect.top+110 if store.facing=='down' else store.rect.top+24
        return [(store.rect.left+dx,y) for dx in (40,100,store.rect.width-100,store.rect.width-40)]

    def requirements(self, game, i):
        if i == 0:
            if self.completed[0]:
                # Older chapters could finish with other fixtures. Keep that achievement.
                return [("Mara's reading circle gathered", 1, 1)]
            pages = next(store for store in game.mall.north_stores if store.name == 'Pages Bookshop')
            decor = game.upgrades.decor
            return [('Reopen Pages Bookshop', int(pages.restored), 1),
                    ('Finish the North arcade first sweep', int(game.mall.initial_cleanup_complete), 1),
                    ('Recover the reading-circle keepsakes', sum(self.memories[0]), 3),
                    ('Restore North table 1 at Supplies', int(READING_TABLE in decor), 1),
                    ('Restore its left and right chairs', sum(key in decor for key in READING_CHAIRS), 2)]
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

    def mara_chat(self, game):
        """Mara follows the authored project without changing ordinary owner requests."""
        if self.completed[0]:
            return 'Someone left a book for next week, Marty. I was so busy remembering our old readers that I nearly forgot to invite the new ones. Remy will be glad to hear the chairs are filling up.'
        if not self.started[0]:
            return 'Marty, I kept your crooked lantern with the reading-circle books. There is a note on the gold community board by the west wall. Read it when you have a moment; I have a small idea.'
        for index, (_, count, goal) in enumerate(self.requirements(game, 0)):
            if count >= goal:
                continue
            return (
                'The first reading can wait until Pages is open. Finish the North arcade sweep, then reopen the bookshop. I still have the books ready.',
                'A clear floor will give our readers room to arrive. Finish the first sweep of the North arcade; the circle can wait for you.',
                'Our photograph, drawing and program are still out there. Look for the gold keepsake marks and ask the neighbor holding one. Your Story journal has the clues.',
                'Let us use North table 1, by the west seats. Supplies can restore its tabletop from the Furniture page. We can make room for a new story there.',
                'The tabletop is ready. Supplies sells its left and right chairs separately. Two places to sit will be enough for our first reading.',
            )[index]
        return 'The books and places are ready, Marty. Read the gold community board once more and we can invite our first readers. I think I am ready to hear a new story too.'

    def gathering_goals(self, mall, i):
        """North's first reading uses the existing west table without moving furniture."""
        if i == 0:
            table = next(table for table in mall.social_tables if table.fixture_key == READING_TABLE)
            # Gather on clear approach tiles; ordinary diners can still reserve the chairs.
            return [seat + pygame.Vector2(0, 64) for seat in table.seats] + [table.position + pygame.Vector2(0, 112)]
        board = next(point.position for point in self.points if point.chapter == i and point.memory < 0)
        return [board + pygame.Vector2(dx, dy) for dx, dy in ((-64, 64), (64, 64), (0, 128))]

    def action(self, point, game):
        i=point.chapter
        if point.source=='neighbor':
            if point not in self.visible_neighbors(game.mall):return False
            if not self.memories[i][point.memory]:
                self.memories[i][point.memory]=True
                item=(('photograph','fountain drawing','festival program'),('record sleeve','cassette','old ticket'),
                      ('flower pattern','spool of thread','lantern sketch'),('guest book','table plan','invitation'))[i][point.memory]
                text=f'I found this {item} lying around while I was walking here. I thought {CHAPTERS[i].speaker} might know its story. Here, take it back to the community board.'
                game.shoppers.depart(point.name,point.variant,point.position,game.mall)
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
        else:text=self.mara_chat(game) if i==0 else CHAPTERS[i].opening;action=None
        game.story_menu.visit(i,text,action);return True

    def invite(self, game, i):
        self.update(0,game.mall)
        area=game.janitors.courts(game.mall)[i][2]
        goals=self.gathering_goals(game.mall,i)
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
        if i == 0:
            instructions = (
                'Reopen Pages Bookshop after the North arcade first sweep.',
                'Finish the first North arcade sweep to welcome the readers.',
                'Find the three gold keepsakes. J → Story has the clues.',
                'Supplies → Furniture: restore North table 1 by the west seats.',
                'Supplies → Furniture: restore table 1\'s left and right chairs.',
            )
            for instruction, (_, count, goal) in zip(instructions, self.requirements(game, 0)):
                if count < goal:
                    return CHAPTERS[0].title, instruction
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
        mall.community_spots=[tuple(goal) for i,done in enumerate(self.completed) if done
                              and (self.celebrations[i]>0 or self.elapsed%150<30) for goal in self.gathering_goals(mall,i)]

    def draw(self, game):
        for point in self.visible_points(game.mall):
            pixel=game.camera.point(point.position)
            if point.memory<0:
                game.art.draw(game.screen,'chapter_board_'+str(point.chapter) if self.completed[point.chapter] else 'community_board',(pixel.x,pixel.y-16),(72,72))
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
                    # Short strings sit directly on the two front coping panels.
                    # The central doorway stays clear; lamps overlap the facade.
                    for left,right in ((24,114),(store.rect.width-114,store.rect.width-24)):
                        start=game.camera.point((store.rect.left+left,store.rect.top+6))
                        end=game.camera.point((store.rect.left+right,store.rect.top+6))
                        pygame.draw.line(game.screen,(133,100,72),start,end,3)
                else:
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
        if i == 0:
            for store in court[3][:2]:store.restored=True
            game.upgrades.decor.update(READING_FIXTURES)
            game.mall.refresh_businesses()
            self.started[0]=True;self.memories[0]=[True]*3
            game.player.rect.center=next(p.position for p in self.points if p.chapter==0 and p.memory<0)
            return True
        for s in court[3][:6]:s.restored=True
        owner=next(s for s in court[3] if not s.upgrade_shop and s is not game.owner_requests.store)
        owner.request_level=max(2,owner.request_level);owner.request_bonus=max(1.5,owner.request_bonus)
        fixtures=[o.key for category in ('Furniture','Garden') for o in game.upgrades.offers(category,court[0])]
        game.upgrades.decor.update(fixtures[:3]);game.mall.refresh_businesses()
        self.started[i]=True;self.memories[i]=[True]*3
        game.player.rect.center=next(p.position for p in self.points if p.chapter==i and p.memory<0)
        return True
