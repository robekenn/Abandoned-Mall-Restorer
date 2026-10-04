"""A food court on its own map; indoor geometry never enters its renderer."""
from dataclasses import dataclass
import pygame
from mall.mall import Mall
from mall.section import floor_tiles, covered_positions
from mall.store import Store
from mall.social import SocialTable
from entities.trash import Trash
from entities.trash_bin import TrashBin
from systems.courtyard_visitors import FoodCourtVisitors
from systems.janitors import Janitors
from systems.litter import LitterSpawner
from systems.economy import money, rent_multiplier
from game.camera import Camera
from ui import theme


@dataclass(eq=False)
class SceneDoor:
    position: pygame.Vector2
    title: str
    anchor: pygame.Vector2 | None = None

    @property
    def label(self):return self.title


class CourtyardWorld(Mall):
    def __init__(self):
        self.size=(2000,1440);self.opening_area=pygame.Rect(40,40,1920,1360)
        self.regions=[];self.entrance=pygame.Vector2(199,775)
        self.distant_stores=[];self.is_courtyard=True
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
        self.boundary_walls=[r.copy() for r in self.obstacles[:6]]
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
    def barriers(self):return []

    @property
    def deliveries(self):return []

    @property
    def recurring_pools(self):return [self.trash] if self.initial_cleanup_complete and self.stores[0].restored else []

    def area_name(self,position):return 'Northgate Courtyard'


class Courtyard:
    COST=50000

    def __init__(self):
        self.unlocked=False;self.world=None;self.shoppers=FoodCourtVisitors();self.janitors=Janitors();self.spawner=LitterSpawner(cap=12)
        self.camera=Camera((2000,1440));self.return_door=SceneDoor(pygame.Vector2(135,775),'Return to Community Commons',pygame.Vector2(56,775))

    def ensure_world(self):
        if self.world is None:
            self.world=CourtyardWorld();self.world.return_door=self.return_door
            self.open_wall(self.world,0,775)
        return self.world

    @staticmethod
    def open_wall(world,x,y):
        wall=next((r for r in world.obstacles if r.x==x and r.width==40 and r.height==world.size[1]),None)
        if wall:
            world.obstacles.remove(wall)
            world.obstacles += [pygame.Rect(x,0,40,y-88),pygame.Rect(x,y+88,40,world.size[1]-y-88)]

    def open_passage(self,mall):
        self.open_wall(mall,mall.size[0]-40,self.door(mall).position.y)

    def crossing(self,game,direction):
        if game.scene=='courtyard':
            if direction[0]<0 and game.player.rect.centerx<=64 and abs(game.player.rect.centery-775)<=68:
                game.leave_courtyard();return True
        elif game.mall.commons.unlocked:
            if direction[0]>0 and game.player.rect.centerx>=game.mall.size[0]-64 and abs(game.player.rect.centery-self.door(game.mall).position.y)<=68:
                if self.unlocked:return game.enter_courtyard()
                message='Press E at the Courtyard sign to open the passage for '+money(self.COST)+'.' if self.ready(game.mall) else 'Finish the Commons sweep and reopen six businesses to open the Courtyard.'
                if game.message!=message or game.message_timer<=0:game.deny(message)
        return False

    @staticmethod
    def door(mall):
        y=mall.commons.area.top+700
        return SceneDoor(pygame.Vector2(mall.commons.area.right-100,y),'Enter the Courtyard food court',pygame.Vector2(mall.commons.area.right-16,y))

    @staticmethod
    def ready(mall):
        return mall.commons.unlocked and mall.commons.initial_cleanup_complete and sum(s.restored for s in mall.commons.stores)>=6

    def target(self,game):
        world=self.ensure_world();origin=pygame.Vector2(game.player.rect.center)
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
        game.deny('Move closer to litter, a restaurant or recycling. Walk through the wall opening to return inside.')

    def income(self,upgrades):
        if not self.unlocked:return 0
        base=sum(s.rent for s in self.world.stores if s.restored)
        fixtures=sum(key.startswith('courtyard_') for key in upgrades.decor)
        return (base*(1+.15*upgrades.courtyard_service_level)+fixtures)*rent_multiplier(self.world.cleanliness)

    def update(self,game,dt,direction):
        world=self.ensure_world();world.comfort=game.upgrades.courtyard_comfort_level
        game.player.move(direction,dt,world.obstacles,game.upgrades.speed_multiplier)
        if self.crossing(game,direction):return
        game.frame_camera(game.screen.get_size())
        game.feedback.update(dt);game.speech.update(dt);game.message_timer=max(0,game.message_timer-dt)
        self.spawner.update(dt,world,game.player.rect.center)
        game.shoppers.update(dt,game.mall,game.upgrades,game.owner_requests.store)
        game.update_courtyard_visitors(dt)
        self.janitors.update(dt,game,world)
        game.rent_timer+=dt
        while game.rent_timer>=5:
            income=game.rent_income;game.cash+=income;game.rent_timer-=5
            if income:game.feedback.burst(game.player.rect.center,f'+{money(income)} rent',restored=True)
            if rent_multiplier(world.cleanliness)==1.5:game.audio.play('bonus_rent')
        game.save_store.elapsed+=dt
        if game.save_started and game.save_store.elapsed>=30:game.save_checkpoint()

    def journal_handle(self,event,game):
        game.journal.handle(event,game)

    @staticmethod
    def draw_passage(game,door):
        surface=game.screen;camera=game.camera
        # Expose the continuous floor through a generous 176px wall opening.
        wall_x=game.mall.size[0]-40 if game.scene=='mall' else 0
        y=round(door.position.y)
        gap=camera.rect((wall_x,y-88,40,176))
        pygame.draw.rect(surface,(165,157,125),gap)
        for row in range(y-88,y+88,16):
            pygame.draw.line(surface,(120,128,106),camera.point((wall_x,row)),camera.point((wall_x+40,row)))
        for edge in (y-96,y+88):
            pygame.draw.rect(surface,(116,128,111),camera.rect((wall_x-8,edge,56,8)))
        # An unobtrusive inlay leads into the opening, with no glass or door frame.
        left=wall_x-96 if game.scene=='mall' else wall_x+40
        pygame.draw.rect(surface,(165,157,125),camera.rect((left,y-3,96,6)))
        # A wooden plaque hangs from a bracket fixed to the actual boundary wall.
        left=wall_x-194 if game.scene=='mall' else wall_x+40
        plaque=pygame.Rect(left,y-188,194,72)
        beam=pygame.Rect(left-4,y-210,202,6)
        pygame.draw.rect(surface,(113,82,50),camera.rect(beam))
        pygame.draw.rect(surface,(194,159,99),camera.rect(beam),1)
        for x in (plaque.left+20,plaque.right-20):
            pygame.draw.line(surface,(177,166,130),camera.point((x,y-204)),camera.point((x,plaque.top)),2)
        pygame.draw.rect(surface,(67,59,43),camera.rect(plaque.move(3,3)))
        pygame.draw.rect(surface,(119,84,48),camera.rect(plaque))
        pygame.draw.rect(surface,(207,171,103),camera.rect(plaque),3)
        pygame.draw.rect(surface,(151,111,62),camera.rect(plaque.inflate(-10,-10)),1)
        title='COURTYARD' if game.scene=='mall' else 'COMMUNITY COMMONS'
        lines=[title]
        if game.scene=='mall' and not game.courtyard.unlocked:
            lines += ['OPEN · '+money(game.courtyard.COST),'E to open' if game.courtyard.ready(game.mall) else 'Commons sweep + 6 shops']
            # Rubble blocks the unrestored passage; it is cleared by the paid unlock.
            for dx,dy,w,h in ((2,42,22,13),(15,25,23,17),(1,9,25,15)):
                block=camera.rect((wall_x+dx,y+dy,w,h))
                pygame.draw.rect(surface,(102,106,91),block);pygame.draw.rect(surface,(150,145,118),block,2)
        else:lines += ['Walk through to enter' if game.scene=='mall' else 'Walk through to return']
        for i,line in enumerate(lines):
            label=game.hud.small.render(line,True,(248,230,184))
            if label.get_width()>plaque.width-16:
                label=pygame.transform.smoothscale(label,(plaque.width-16,label.get_height()))
            surface.blit(label,label.get_rect(center=camera.point((plaque.centerx,plaque.top+16+i*20))))

    def draw(self,game):
        world=self.ensure_world();surface=game.screen;camera=self.camera;art=game.art;target=self.target(game)
        surface.fill((41,58,57));view=surface.get_rect().move(round(camera.offset.x),round(camera.offset.y))
        # Warm pavers, a continuous entrance walk and bounded brick dining courts.
        for x in range(max(40,(view.left-40)//64*64+40),min(1960,view.right+64),64):
            for y in range(max(40,(view.top-40)//64*64+40),min(1400,view.bottom+64),64):
                clean=world.tile_restored((x+31,y+31))
                path=744<=y<808 or 808<=x<872 or 1192<=x<1256
                color=((176,170,143) if path else (155,153,126)) if clean else ((112,122,105) if path else (96,109,93))
                rect=camera.rect((x,y,64,64));pygame.draw.rect(surface,color,rect)
                pygame.draw.rect(surface,(137,141,117) if clean else (83,98,85),rect,1)
                pygame.draw.line(surface,(190,182,150) if clean else (123,132,109),rect.topleft,rect.topright)
                if not clean and (x//64+y//64)%7==0:
                    pygame.draw.line(surface,(76,95,77),(rect.x+10,rect.y+12),(rect.x+18,rect.y+23),2)
        for table in world.social_tables:
            pad=camera.rect((table.position.x-120,table.position.y-48,240,144))
            pygame.draw.rect(surface,(126,107,84),pad)
            for row in range(6):
                for col in range(8):
                    brick=pygame.Rect(pad.x+col*32-(16 if row%2 else 0)+2,pad.y+row*24+2,29,21).clip(pad)
                    pygame.draw.rect(surface,(154,128,96) if (row+col)%3 else (167,140,104),brick)
            pygame.draw.rect(surface,(197,170,122),pad,3)
        for wall in world.boundary_walls:
            pygame.draw.rect(surface,(47,67,59),camera.rect(wall))
            pygame.draw.rect(surface,(99,117,85),camera.rect(wall),3)
        # A consistent sill ties the kitchens together without covering any route.
        for y in (320,1108):
            pygame.draw.rect(surface,(128,120,88),camera.rect((320,y,1560,8)))
            pygame.draw.rect(surface,(195,172,119),camera.rect((320,y,1560,2)))
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
                badge=game.hud.small.render('SERVICE & PATIO UPGRADES',True,theme.GOLD)
                plaque=badge.get_rect(center=camera.point((store.rect.centerx,store.rect.top+140))).inflate(20,12)
                theme.frame(surface,plaque,theme.PANEL,False);surface.blit(badge,badge.get_rect(center=plaque.center))
            if store.available:
                point=camera.point(store.position);pygame.draw.circle(surface,theme.ACCENT if store.restored else theme.GOLD,point,12,2)
                if target is store:pygame.draw.circle(surface,theme.TEXT,point,21,2)
        for b in world.trash_bins:b.draw(surface,camera,art,game.hud.small,target is b)
        for trash in world.trash:
            if view.inflate(64,64).collidepoint(trash.position):trash.draw(surface,camera,art,target is trash)
        self.draw_passage(game,self.return_door)
        layers=[(t.position.y,'table',t) for t in world.social_tables]
        layers += [(p.display_position.y,'person',p) for p in self.shoppers.people if p.visible]
        layers += [(j.position.y,'janitor',j) for j in self.janitors.people.values()]
        layers.append((game.player.rect.centery,'player',game.player))
        for _,kind,item in sorted(layers,key=lambda v:v[0]):
            if kind=='table':
                i=world.social_tables.index(item);art.draw(surface,'courtyard_table' if f'courtyard_table_{i}' in game.upgrades.decor else 'courtyard_table_broken',camera.point(item.position),(160,112))
            elif kind=='janitor':item.draw(game)
            elif kind=='person':item.draw(surface,camera,art,game.hud.small,target is item)
            else:item.draw(surface,camera,art)
        for i,p in enumerate(((700,280),(1100,280),(1100,1160),(1500,1160))):
            if f'courtyard_herb_{i}' in game.upgrades.decor:art.draw(surface,'herb_planter',camera.point(p),(48,64))
        for i,p in enumerate(((583,480),(1031,480),(1415,480),(1750,850))):
            if f'courtyard_light_{i}' in game.upgrades.decor:art.draw(surface,'patio_lights',camera.point(p),(128,72))
        game.feedback.draw(surface,camera,game.hud.font)
        game.hud.draw(game,target)
        game.speech.draw_bubble(game,game.speech.name,game.speech.text,game.speech.position) if game.speech.timer else None
        for p in self.shoppers.people:
            if p.visible and p.speech_time:game.speech.draw_bubble(game,p.name,p.speech,p.display_position)
        if game.journal.open:game.journal.draw(game)
        if game.shop_menu.open:game.shop_menu.draw(game)
        if game.settings_menu.open:game.settings_menu.draw(game)
        elif game.pause.open:game.pause.draw(game)
        pygame.display.flip()

    def snapshot(self,game):
        if not self.unlocked:return {'unlocked':False}
        from systems.saves import snapshot_worker
        janitor=self.janitors.people.get('courtyard')
        return {'unlocked':True,'scene':game.scene=='courtyard',
                'janitor':snapshot_worker(janitor,self.world) if janitor else None,
                'position':list(game.player.rect.center) if game.scene=='courtyard' else None,
                'stores':[s.restored for s in self.world.stores],
                'trash':[[t.cleaned,t.ever_cleaned,getattr(t,'revision',0)] for t in self.world.trash],
                'dirty':[list(p) for p in sorted(self.world.dirty_tiles)],
                'litter_timer':self.spawner.elapsed,'litter_turn':self.spawner.turn,
                'traffic_clock':self.shoppers.traffic_elapsed,'identity':self.shoppers.next_identity}
