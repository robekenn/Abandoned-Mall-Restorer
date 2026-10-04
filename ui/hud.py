"""Three essential counters, one objective and a contextual action."""
import pygame
from entities.trash import Trash
from entities.trash_bin import TrashBin
from systems.economy import money, cleanliness_label
from systems.requests import OWNERS, RequestSpot
from systems.shoppers import Shopper
from mall.store import Store
from systems.story import StoryPoint, CHAPTERS
from ui import theme
from systems.mall_life import EventSpot
from mall.courtyard import SceneDoor, Courtyard


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None,25)
        self.title = pygame.font.Font(None,34)
        self.small = pygame.font.Font(None,20)

    def wrap(self, text, width):
        return theme.wrap(self.font,text,width)

    def goal(self, game):
        if game.scene=='courtyard':
            world=game.courtyard.world
            if game.upgrades.held==game.upgrades.capacity:return 'Bag full','Sell your trash at a courtyard station.'
            if not world.stores[0].restored:return 'Courtyard Provisions','Reopen Provisions · '+money(world.stores[0].cost)
            if not world.initial_cleanup_complete:return 'First courtyard sweep',f'Clean the patio. {world.active_litter_count} patches left.'
            if world.next_store:return 'Next kitchen',world.next_store.name+' · '+money(world.next_store.cost)
            return 'A table for everyone','All seven kitchens open. Visit Provisions for service and garden upgrades.'
        mall=game.mall;requests=game.owner_requests
        if game.tutorial.active:return game.tutorial.goal
        if requests.store:
            return requests.store.name+' · '+OWNERS[requests.store.name],requests.objective
        if game.life.spot and game.mall.area_for_store(game.life.court(game,game.life.active)[3][0]).collidepoint(game.player.rect.center):
            return game.life.event.title,(game.life.visible_tasks[0].label if game.life.visible_tasks else 'Visit the community table')+' · '+str(game.life.round)+'/3'
        if game.upgrades.held == game.upgrades.capacity:
            return 'Bag full','Sell your trash at a mall bin.'
        if not mall.stores[0].restored:
            return 'A small beginning','Reopen Supplies for $10.'
        if game.upgrades.capacity_level==0:
            return 'Room to carry more','Visit Supplies for bag, trash-value and tool upgrades.'
        if not mall.initial_cleanup_complete:
            return 'First sweep',f'Clean the north arcade. {sum(not t.cleaned for t in mall.north_trash)} patches left.'
        for region in mall.active_regions:
            if region.stores[0].restored and not region.initial_cleanup_complete:
                return region.name,f'Finish its first sweep. {sum(not t.cleaned for t in region.trash)} patches left.'
        story_goal=game.story.hud_goal(game)
        if story_goal:return story_goal
        ready=next((r for r in mall.regions if not r.unlocked and r.ready(mall)),None)
        if ready:return 'A new chapter',f'Open {ready.name} · {money(ready.cost)}'
        if mall.next_store:
            return 'Next opening',f'{mall.next_store.name} · {money(mall.next_store.cost)}'
        if game.story.current<4:
            chapter=game.story.current
            if game.story.ready(game,chapter):return CHAPTERS[chapter].title,'Return to the community board to gather the neighbors.'
            return 'The lantern walk','J → Story: help each court bring the festival back.'
        return 'A place for everyone','Visit the Commons board to begin another lantern walk.'

    def prompt(self, game, target):
        if isinstance(target,SceneDoor):return 'E',target.title
        if isinstance(target,EventSpot):return 'E','Join '+target.title
        if isinstance(target,StoryPoint):return 'E',target.label
        if isinstance(target,Trash):
            return 'E / click','Collect litter' if game.upgrades.held<game.upgrades.capacity else 'Bag full. Find a bin.'
        if isinstance(target,TrashBin):return 'E','Sell carried trash'
        if isinstance(target,Shopper):return 'E',f'Say hello to {target.name}'
        if isinstance(target,RequestSpot):return ('Hold E' if target.duration else 'E'),target.title
        if isinstance(target,Store):
            if not target.restored:return 'E',f'Reopen {target.name}' if target.available else 'This store is still closed'
            return 'E',('Enter '+target.name) if target.upgrade_shop else f'Talk to {OWNERS[target.name]}' if target.name in OWNERS else 'Chat with the cooks'
        if target:return 'E',f'Open {target.name} · {money(target.cost)}'
        return 'Move','WASD or arrow keys'

    def directory(self, surface, mall, player, requests=None, people=(), bounds=None):
        if bounds is None:
            bounds=pygame.Rect(surface.get_width()-340,120,300,180)
        sx,sy=bounds.width/mall.size[0],bounds.height/mall.size[1]
        theme.frame(surface,bounds,theme.BG)
        for area in mall.playable_areas:
            r=pygame.Rect(bounds.x+area.x*sx,bounds.y+area.y*sy,area.width*sx,area.height*sy)
            pygame.draw.rect(surface,(69,94,84),r)
        for gate in mall.barriers:
            r=pygame.Rect(bounds.x+gate.x*sx,bounds.y+gate.y*sy,max(2,gate.width*sx),max(2,gate.height*sy))
            pygame.draw.rect(surface,theme.GOLD,r)
        for store in mall.stores+mall.distant_stores:
            r=pygame.Rect(bounds.x+store.rect.x*sx,bounds.y+store.rect.y*sy,store.rect.width*sx,store.rect.height*sy)
            pygame.draw.rect(surface,theme.ACCENT if store.upgrade_shop else theme.GOLD if store.restored else (43,57,58),r)
        for bin in mall.trash_bins:
            p=(round(bounds.x+bin.position.x*sx),round(bounds.y+bin.position.y*sy))
            pygame.draw.rect(surface,theme.ACCENT,(p[0]-2,p[1]-2,4,4))
        deliveries=mall.deliveries
        for depot in deliveries:
            p=(round(bounds.x+depot.position.x*sx),round(bounds.y+depot.position.y*sy))
            pygame.draw.rect(surface,theme.GOLD,(p[0]-3,p[1]-3,6,6),1)
        for point in getattr(mall,'event_spots',()):
            pygame.draw.circle(surface,theme.GOLD,(round(bounds.x+point[0]*sx),round(bounds.y+point[1]*sy)),4)
        for point in getattr(mall,'event_task_markers',()):
            pygame.draw.circle(surface,theme.ACCENT,(round(bounds.x+point[0]*sx),round(bounds.y+point[1]*sy)),4)
        for point in getattr(mall,'story_markers',()):
            pygame.draw.circle(surface,theme.GOLD,(round(bounds.x+point[0]*sx),round(bounds.y+point[1]*sy)),3)
        if getattr(mall,'commons',None) and mall.commons.unlocked:
            door=Courtyard.door(mall).position
            point=(round(bounds.x+door.x*sx),round(bounds.y+door.y*sy))
            pygame.draw.rect(surface,theme.ACCENT,(point[0]-3,point[1]-4,6,8),1)
            label=self.small.render('PATIO',True,theme.ACCENT)
            x=point[0]+6 if point[0]+6+label.get_width()<bounds.right else point[0]-label.get_width()-6
            surface.blit(label,(x,point[1]-7))
        if hasattr(mall,'return_door'):
            point=(round(bounds.x+mall.return_door.position.x*sx),round(bounds.y+mall.return_door.position.y*sy))
            pygame.draw.rect(surface,theme.ACCENT,(point[0]-3,point[1]-4,6,8),1)
        if requests and requests.store:
            pygame.draw.circle(surface,(111,211,233),(round(bounds.x+requests.store.position.x*sx),round(bounds.y+requests.store.position.y*sy)),7,2)
            destinations=[requests.store.position] if requests.ready else [s.position for s in requests.visible_spots]
            if not destinations and requests.needs_greetings:
                destinations=[p.position for p in people if p.visible and p.identity not in requests.greetings]
            for p in destinations:
                pygame.draw.circle(surface,(111,211,233),(round(bounds.x+p.x*sx),round(bounds.y+p.y*sy)),4)
        pygame.draw.circle(surface,theme.TEXT,(round(bounds.x+player[0]*sx),round(bounds.y+player[1]*sy)),3)

    def draw(self, game, target, surface=None):
        surface=game.screen if surface is None else surface;width,height=surface.get_size();outside=game.scene=='courtyard';mall=game.courtyard.world if outside else game.mall
        pygame.draw.rect(surface,theme.BG,(0,0,width,76))
        surface.blit(self.title.render('NORTHGATE',True,theme.TEXT),(22,13))
        region=mall.area_name(game.player.rect.center)
        surface.blit(self.small.render(region+" · "+(game.courtyard.shoppers if outside else game.shoppers).traffic,True,theme.MUTED),(23,47))
        values=[('CLEAN',cleanliness_label(game.cleanliness)),('CASH',money(game.cash)),('BAG',f'{game.upgrades.held} / {game.upgrades.capacity}')]
        for i,(label,value) in enumerate(values):
            r=pygame.Rect(width-450+i*145,10,133,56);theme.frame(surface,r,theme.PANEL,False)
            surface.blit(self.small.render(label,True,theme.MUTED),(r.x+12,r.y+8))
            color=theme.GOLD if label=='BAG' and game.upgrades.held==game.upgrades.capacity else theme.TEXT
            text=self.font.render(value,True,color);surface.blit(text,(r.x+12,r.y+27))
        title,objective=self.goal(game)
        reminder=not outside and game.preferences.notifications and not game.owner_requests.store and any(game.owner_requests.eligible(s) for s in mall.stores)
        card=pygame.Rect(20,88,min(width-350 if reminder else width-40,480),94 if game.tutorial.active else 72);theme.frame(surface,card)
        surface.blit(self.small.render(title,True,theme.ACCENT),(card.x+14,card.y+12))
        for i,line in enumerate(theme.wrap(self.font,objective,card.width-28)[:3 if game.tutorial.active else 2]):
            surface.blit(self.font.render(line,True,theme.TEXT),(card.x+14,card.y+34+i*21))
        if game.tutorial.active:
            skip=game.tutorial.skip_rect(surface);theme.frame(surface,skip,theme.CARD,False)
            label=self.small.render('T Skip',True,theme.MUTED);surface.blit(label,label.get_rect(center=skip.center))
        pygame.draw.rect(surface,theme.BG,(0,height-58,width,58))
        key,action=self.prompt(game,target)
        key_width=max(44,self.small.size(key)[0]+20)
        r=pygame.Rect(20,height-43,key_width,28);theme.frame(surface,r,theme.CARD,False)
        label=self.small.render(key,True,theme.GOLD);surface.blit(label,label.get_rect(center=r.center))
        controls=self.small.render('J Journal   H Help   F2 Settings   Esc Pause',True,theme.MUTED)
        available=max(100,width-key_width-controls.get_width()-64)
        for i,line in enumerate(theme.wrap(self.small,action,available)[:2]):
            surface.blit(self.small.render(line,True,theme.TEXT),(r.right+12,height-41+i*17))
        surface.blit(controls,controls.get_rect(midright=(width-20,height-29)))
        available_requests=0 if outside else sum(game.owner_requests.eligible(s) for s in mall.stores)
        if available_requests and game.preferences.notifications and not game.owner_requests.store:
            text=(game.request_notice if game.request_notice_timer else f'{available_requests} owner favors available')+' · J: owners'
            box=pygame.Rect(width-310,88,290,52);theme.frame(surface,box)
            for i,line in enumerate(theme.wrap(self.small,text,box.width-24)[:2]):
                surface.blit(self.small.render(line,True,theme.GOLD),(box.x+12,box.y+9+i*18))
        if game.message_timer:
            lines=theme.wrap(self.small,game.message,min(540,width-68))[:2]
            box=pygame.Rect(0,0,min(568,width-40),20+len(lines)*18)
            box.midbottom=(width//2,height-70);theme.frame(surface,box)
            for i,line in enumerate(lines):surface.blit(self.small.render(line,True,theme.TEXT),(box.x+14,box.y+10+i*18))
