"""A food court on its own map; indoor geometry never enters its renderer."""
from dataclasses import dataclass
import pygame
from mall.mall import Mall
from mall.section import floor_tiles, covered_positions
from mall.store import Store
from mall.social import SocialTable
from entities.trash import Trash
from entities.trash_bin import TrashBin
from systems.shoppers import Shoppers
from systems.litter import LitterSpawner
from systems.economy import money, rent_multiplier
from game.camera import Camera
from ui import theme


@dataclass(eq=False)
class SceneDoor:
    position: pygame.Vector2
    title: str

    @property
    def label(self):return self.title


class CourtyardWorld(Mall):
    def __init__(self):
        self.size=(2000,1440);self.opening_area=pygame.Rect(40,40,1920,1360)
        self.regions=[];self.entrance=pygame.Vector2(199,775)
        self.stores=[]
        specs=[('Courtyard Provisions',30000,0),('Hearth Pizza',45000,250),('Mint & Noodles',60000,330),
               ('Orchard Juice',75000,420),('Sunrise Bakery',90000,510),('Copper Grill',110000,620),
               ('Garden Bowls',135000,750),('Moonrise Desserts',160000,900)]
        for i,(name,cost,rent) in enumerate(specs):
            store=Store((320+(i%4)*400,100 if i<4 else 1120,360,220),name,i==0,cost,rent,'cafe','down' if i<4 else 'up')
            store.section_key='courtyard';self.stores.append(store)
        self.stores[0].upgrade_shop='courtyard';self.north_stores=self.stores
        self.obstacles=[pygame.Rect(0,0,2000,40),pygame.Rect(0,1400,2000,40),
                        pygame.Rect(0,0,40,1440),pygame.Rect(1960,0,40,1440),pygame.Rect(40,40,1920,280),pygame.Rect(40,1120,1920,280)]+[s.rect for s in self.stores]
        self.trash_bins=[TrashBin((260,600),'Courtyard compost station'),TrashBin((1830,1000),'Courtyard recycling station')]
        self.obstacles += [b.rect for b in self.trash_bins]
        self.floor_tiles=floor_tiles(self.opening_area,self.obstacles)
        self.north_floor_tiles=list(self.floor_tiles);self.dirty_tiles=set(self.floor_tiles)
        self._initial_cleanup_complete=False
        positions=covered_positions(self.opening_area,self.floor_tiles,self.obstacles,self.stores,self.trash_bins,entrance_buffer=64)
        self.trash=[Trash(p,'dirt' if i%4==0 else 'trash') for i,p in enumerate(positions)];self.north_trash=self.trash
        self.initial_litter_count=len(self.trash);self.social_tables=[]
        for goal in ((600,650),(1000,650),(1400,650),(600,900),(1000,900),(1400,900)):
            for p in sorted(self.floor_tiles,key=lambda p:pygame.Vector2(p).distance_squared_to(goal)):
                seats=(pygame.Vector2(p[0]-64,p[1]),pygame.Vector2(p[0]+64,p[1]))
                table=SocialTable(pygame.Vector2(p[0],p[1]-30),seats,'courtyard')
                if not self.opening_area.contains(table.footprint.inflate(180,160)):continue
                if any(w.colliderect(table.footprint.inflate(40,40)) for w in self.obstacles):continue
                if any(table.footprint.inflate(24,24).collidepoint(t.position) for t in self.trash):continue
                if any(tuple(seat) not in self.floor_tiles or any(w.colliderect(pygame.Rect(seat.x-12,seat.y-14,24,28)) for w in self.obstacles+[table.footprint]) for seat in seats):continue
                if any(table.position.distance_to(t.position)<160 for t in self.social_tables):continue
                self.social_tables.append(table);self.obstacles.append(table.footprint);break
        self.benches=[];self.fountain=pygame.Rect(1000,480,32,32);self.comfort=0

    @property
    def recurring_pools(self):return [self.trash] if self.initial_cleanup_complete and self.stores[0].restored else []

    def area_name(self,position):return 'Northgate Courtyard'


class Courtyard:
    COST=50000

    def __init__(self):
        self.unlocked=False;self.world=None;self.shoppers=Shoppers();self.spawner=LitterSpawner(cap=12)
        self.camera=Camera((2000,1440));self.return_door=SceneDoor(pygame.Vector2(120,775),'Return to Community Commons')

    def ensure_world(self):
        if self.world is None:self.world=CourtyardWorld()
        return self.world

    @staticmethod
    def door(mall):return SceneDoor(pygame.Vector2(mall.commons.area.left+96,mall.commons.area.top+610),'Enter the Courtyard food court')

    @staticmethod
    def ready(mall):
        return mall.commons.unlocked and mall.commons.initial_cleanup_complete and sum(s.restored for s in mall.commons.stores)>=6

    def target(self,game):
        world=self.ensure_world();origin=pygame.Vector2(game.player.rect.center)
        if origin.distance_to(self.return_door.position)<=72:return self.return_door
        candidates=[b for b in world.trash_bins if origin.distance_to(b.position)<=72]
        if candidates and game.upgrades.held:return min(candidates,key=lambda b:origin.distance_squared_to(b.position))
        candidates += [t for t in world.trash if not t.cleaned and origin.distance_to(t.position)<=game.upgrades.tool[1]]
        candidates += [s for s in world.stores if origin.distance_to(s.position)<=72]
        if not candidates:candidates=[p for p in self.shoppers.people if p.visible and origin.distance_to(p.position)<=64]
        return min(candidates,key=lambda p:origin.distance_squared_to(p.position),default=None)

    def collect(self,game,target):
        if game.upgrades.held>=game.upgrades.capacity:game.deny('Bag full. Use a courtyard recycling station.');return
        reach,batch=game.upgrades.tool[1:];origin=pygame.Vector2(game.player.rect.center)
        pool=sorted((t for t in self.world.trash if not t.cleaned and origin.distance_to(t.position)<=reach),key=lambda t:(t is not target,origin.distance_squared_to(t.position)))
        count=0;first_sweep=self.world.initial_cleanup_complete
        for trash in pool[:min(batch,game.upgrades.capacity-game.upgrades.held)]:
            if self.world.clean_trash(trash):
                count+=1;game.upgrades.held+=1;game.owner_requests.record_collection(1,trash.position)
                game.feedback.burst(trash.position,'+1 item',kind=trash.kind)
        if count:
            game.total_collected+=count;game.player.use_tool(target.kind,target.position);game.audio.play('pickup')
            if not first_sweep and self.world.initial_cleanup_complete:game.notify('Courtyard first sweep complete. Reopen the restaurants in order.')

    def pickup_at(self,game,pos):
        if not pygame.Rect(0,170,game.screen.get_width(),game.screen.get_height()-228).collidepoint(pos):return
        point=pygame.Vector2(pos)+self.camera.offset
        targets=[t for t in self.world.trash if not t.cleaned and t.position.distance_to(point)<=24]
        if not targets:return
        target=min(targets,key=lambda t:t.position.distance_squared_to(point))
        if target.position.distance_to(game.player.rect.center)>game.upgrades.tool[1]:game.deny('Move closer to collect this litter.');return
        self.collect(game,target)

    def interact(self,game):
        target=self.target(game)
        if isinstance(target,SceneDoor):game.leave_courtyard();return
        if isinstance(target,Trash):self.collect(game,target);return
        if isinstance(target,TrashBin):
            if not game.upgrades.held:game.deny('Your bag is empty.');return
            payout=game.upgrades.held*game.upgrades.unit_value*(1+.25*game.upgrades.courtyard_compost_level)
            game.total_sold+=game.upgrades.held;game.upgrades.held=0;game.cash+=payout
            game.feedback.burst(target.position,f'+{money(payout)}',restored=True);game.audio.play('pickup');return
        if isinstance(target,Store):
            if not target.available:game.deny(target.label);return
            if target.restored:
                if target.upgrade_shop:game.open_upgrade_shop(target)
                else:game.speech.say(target.name,'The kitchen is open. Restore our seating and improve service at Provisions to welcome more neighbors.',target.position)
                return
            if game.cash<target.cost:game.deny(f'You need {money(target.cost-game.cash)} more to reopen {target.name}.');return
            game.cash-=target.cost;target.restored=True;self.world.refresh_businesses()
            game.audio.play('milestone');game.feedback.burst(target.position,'KITCHEN OPEN',restored=True)
            if target.upgrade_shop:game.open_upgrade_shop(target)
            game.save_checkpoint();return
        if target in self.shoppers.people:self.shoppers.greet(target);game.audio.play('pickup');return
        game.deny('Move closer to litter, a restaurant, recycling or the return doors.')

    def income(self,upgrades):
        if not self.unlocked:return 0
        base=sum(s.rent for s in self.world.stores if s.restored)
        fixtures=sum(key.startswith('courtyard_') for key in upgrades.decor)
        return (base*(1+.15*upgrades.courtyard_service_level)+fixtures)*rent_multiplier(self.world.cleanliness)

    def update(self,game,dt,direction):
        world=self.ensure_world();world.comfort=game.upgrades.courtyard_comfort_level
        game.player.move(direction,dt,world.obstacles,game.upgrades.speed_multiplier)
        self.camera.update((game.player.rect.centerx,game.player.rect.centery-50),game.screen.get_size())
        game.feedback.update(dt);game.speech.update(dt);game.message_timer=max(0,game.message_timer-dt)
        self.spawner.update(dt,world,game.player.rect.center)
        self.shoppers.update(dt,world,game.upgrades)
        game.rent_timer+=dt
        while game.rent_timer>=5:game.cash+=game.rent_income;game.rent_timer-=5
        game.save_store.elapsed+=dt
        if game.save_started and game.save_store.elapsed>=30:game.save_checkpoint()

    def journal_handle(self,event,game):
        if event.type==pygame.KEYDOWN and event.key in (pygame.K_j,pygame.K_e,pygame.K_ESCAPE):game.journal.open=False
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if game.journal.geometry(game.screen)[1].collidepoint(event.pos):game.journal.open=False

    def draw(self,game):
        world=self.ensure_world();surface=game.screen;camera=self.camera;art=game.art;target=self.target(game)
        surface.fill((41,58,57));view=surface.get_rect().move(round(camera.offset.x),round(camera.offset.y))
        for x in range(max(40,(view.left-40)//64*64+40),min(1960,view.right+64),64):
            for y in range(max(40,(view.top-40)//64*64+40),min(1400,view.bottom+64),64):
                color=(154,143,111) if world.tile_restored((x+31,y+31)) else (99,106,88)
                rect=camera.rect((x,y,63,63));pygame.draw.rect(surface,color,rect)
                pygame.draw.rect(surface,(116,116,93),rect,1)
                if (x//64+y//64)%7==0:pygame.draw.line(surface,(83,100,78),(rect.x+8,rect.y+8),(rect.x+16,rect.y+19),2)
        for wall in world.obstacles[:6]:pygame.draw.rect(surface,(65,85,70),camera.rect(wall))
        # Brick dining pads and planted edges distinguish the outdoor patio.
        for table in world.social_tables:
            pad=camera.rect((table.position.x-80,table.position.y-30,160,112))
            pygame.draw.rect(surface,(141,112,85),pad,border_radius=12);pygame.draw.rect(surface,(185,155,113),pad,2,border_radius=12)
        for position in ((80,450),(1920,450),(80,1040),(1920,1040)):
            art.draw(surface,'patio_tree',camera.point(position),(96,144))
        for i,store in enumerate(world.stores):
            if not view.inflate(100,100).colliderect(store.rect):continue
            name='food_stall_'+str(i)+'_'+('open' if store.restored else 'closed')+('_up' if store.facing=='up' else '')
            art.draw(surface,name,camera.point(store.rect.center),(360,240))
            label=game.hud.small.render(store.name.upper(),True,theme.TEXT)
            rect=label.get_rect(center=camera.point((store.rect.centerx,store.rect.top+100 if store.facing=='down' else store.rect.bottom-100))).inflate(16,10)
            pygame.draw.rect(surface,(39,53,48),rect,border_radius=3);surface.blit(label,label.get_rect(center=rect.center))
            if store.upgrade_shop:
                badge=game.hud.small.render('PROVISIONS · SERVICE UPGRADES',True,theme.ACCENT)
                surface.blit(badge,badge.get_rect(center=camera.point((store.rect.centerx,store.rect.top+130))))
            if store.available:
                point=camera.point(store.position);pygame.draw.circle(surface,theme.ACCENT if store.restored else theme.GOLD,point,12,2)
                if target is store:pygame.draw.circle(surface,theme.TEXT,point,21,2)
        for b in world.trash_bins:b.draw(surface,camera,art,game.hud.small,target is b)
        for trash in world.trash:
            if view.inflate(64,64).collidepoint(trash.position):trash.draw(surface,camera,art,target is trash)
        door=camera.point(self.return_door.position);art.draw(surface,'courtyard_doors',door,(96,128))
        label=game.hud.small.render('RETURN TO COMMONS',True,theme.TEXT);surface.blit(label,label.get_rect(midtop=(door.x,door.y+70)))
        layers=[(t.position.y,'table',t) for t in world.social_tables]
        layers += [(p.display_position.y,'person',p) for p in self.shoppers.people if p.visible]
        layers.append((game.player.rect.centery,'player',game.player))
        for _,kind,item in sorted(layers,key=lambda v:v[0]):
            if kind=='table':
                i=world.social_tables.index(item);art.draw(surface,'courtyard_table' if f'courtyard_table_{i}' in game.upgrades.decor else 'social_table',camera.point(item.position),(112,96))
            elif kind=='person':item.draw(surface,camera,art,game.hud.small,target is item)
            else:item.draw(surface,camera,art)
        for i,p in enumerate(((100,470),(1870,470),(100,1080),(1870,1080))):
            if f'courtyard_herb_{i}' in game.upgrades.decor:art.draw(surface,'herb_planter',camera.point(p),(72,96))
        for i,p in enumerate(((600,480),(1000,480),(1400,480),(1750,850))):
            if f'courtyard_light_{i}' in game.upgrades.decor:art.draw(surface,'patio_lights',camera.point(p),(128,72))
        game.feedback.draw(surface,camera,game.hud.font)
        header=pygame.Rect(0,0,surface.get_width(),170);pygame.draw.rect(surface,theme.PANEL,header)
        surface.blit(game.hud.title.render('Northgate Courtyard',True,theme.TEXT),(20,18))
        surface.blit(game.hud.font.render(f'{money(game.cash)} · Bag {game.upgrades.held}/{game.upgrades.capacity} · Clean {world.cleanliness:.0%}',True,theme.GOLD),(20,55))
        opened=sum(s.restored for s in world.stores[1:]);next_store=world.next_store
        goal=f'First sweep: {world.active_litter_count} pieces left' if not world.initial_cleanup_complete else f'Next kitchen: {next_store.name} · {money(next_store.cost)}' if next_store else 'All seven kitchens open. Welcome the neighborhood!'
        surface.blit(game.hud.font.render(goal,True,theme.ACCENT),(20,89))
        surface.blit(game.hud.small.render(f'{opened}/7 restaurants · {self.shoppers.traffic} · J: courtyard map · F2: settings',True,theme.MUTED),(20,126))
        footer=pygame.Rect(0,surface.get_height()-58,surface.get_width(),58);pygame.draw.rect(surface,theme.PANEL,footer)
        prompt=target.label if target is not None else 'Explore the patio; E: interact · Left-click: collect nearby litter'
        if isinstance(target,Store):prompt=('Visit Provisions for service upgrades' if target.upgrade_shop else 'Kitchen open · Chat with the cooks') if target.restored else f'Reopen {target.name} · {money(target.cost)}' if target.available else 'Finish the sweep and reopen the previous kitchen'
        surface.blit(game.hud.small.render(game.message if game.message_timer else 'E: '+prompt,True,theme.GOLD),(20,footer.y+18))
        game.speech.draw_bubble(game,game.speech.name,game.speech.text,game.speech.position) if game.speech.timer else None
        for p in self.shoppers.people:
            if p.visible and p.speech_time:game.speech.draw_bubble(game,p.name,p.speech,p.display_position)
        if game.journal.open:self.draw_journal(game)
        if game.shop_menu.open:game.shop_menu.draw(game)
        if game.settings_menu.open:game.settings_menu.draw(game)
        elif game.pause.open:game.pause.draw(game)
        pygame.display.flip()

    def snapshot(self,game):
        if not self.unlocked:return {'unlocked':False}
        return {'unlocked':True,'scene':game.scene=='courtyard',
                'position':list(game.player.rect.center) if game.scene=='courtyard' else None,
                'stores':[s.restored for s in self.world.stores],
                'trash':[[t.cleaned,t.ever_cleaned,getattr(t,'revision',0)] for t in self.world.trash],
                'dirty':[list(p) for p in sorted(self.world.dirty_tiles)],
                'litter_timer':self.spawner.elapsed,'litter_turn':self.spawner.turn,
                'traffic_clock':self.shoppers.traffic_elapsed,'identity':self.shoppers.next_identity}

    def draw_journal(self,game):
        theme.dim(game.screen);panel,close=game.journal.geometry(game.screen);theme.frame(game.screen,panel)
        game.screen.blit(game.hud.title.render('Courtyard food court',True,theme.TEXT),(panel.x+22,panel.y+20))
        theme.frame(game.screen,close);game.screen.blit(game.hud.small.render('Close',True,theme.ACCENT),(close.x+9,close.y+6))
        maprect=pygame.Rect(panel.x+24,panel.y+72,panel.width-48,220);pygame.draw.rect(game.screen,(63,83,70),maprect)
        def point(pos):return (maprect.x+pos[0]/2000*maprect.width,maprect.y+pos[1]/1440*maprect.height)
        for s in self.world.stores:
            r=pygame.Rect(point(s.rect.topleft),(s.rect.width/2000*maprect.width,s.rect.height/1440*maprect.height))
            pygame.draw.rect(game.screen,theme.ACCENT if s.restored else theme.MUTED,r)
        for t in self.world.social_tables:pygame.draw.circle(game.screen,theme.GOLD,point(t.position),3)
        pygame.draw.circle(game.screen,theme.TEXT,point(game.player.rect.center),5)
        pygame.draw.circle(game.screen,theme.GOLD,point(self.return_door.position),5)
        lines=['Return doors: west patio edge. Shared cash, bag and equipment travel with you.',
               'Reopen Provisions, finish the courtyard sweep, then reopen the seven kitchens.',
               'Service training adds 15% restaurant income per tier. Comfort adds seating time and visitor space.',
               'Composting adds 25% recycling payouts per tier, at courtyard stations only.',
               'Furniture restores picnic tables; Garden installs herb pots and evening lights.',
               'The indoor mall pauses while you are outside. Both maps earn rent during active play.']
        y=maprect.bottom+18
        for line in lines:
            for wrapped in theme.wrap(game.hud.small,line,panel.width-48):
                game.screen.blit(game.hud.small.render(wrapped,True,theme.ACCENT),(panel.x+24,y));y+=20
