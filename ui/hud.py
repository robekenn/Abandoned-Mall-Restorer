"""Three essential counters, one objective and a contextual action."""
import pygame
from entities.trash import Trash
from entities.trash_bin import TrashBin
from systems.economy import money, cleanliness_label
from systems.requests import OWNERS, RequestSpot
from systems.shoppers import Shopper
from mall.store import Store
from ui import theme


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None,25)
        self.title = pygame.font.Font(None,34)
        self.small = pygame.font.Font(None,20)

    def wrap(self, text, width):
        return theme.wrap(self.font,text,width)

    def goal(self, game):
        mall=game.mall;requests=game.owner_requests
        if requests.store:
            return f'{OWNERS[requests.store.name]}: {requests.project[0]}',requests.objective
        if game.upgrades.held == game.upgrades.capacity:
            return 'Bag full','Sell your trash at a mall bin.'
        if not mall.stores[0].restored:
            return 'A small beginning','Reopen Supplies for $10.'
        if not mall.initial_cleanup_complete:
            return 'First sweep',f'Clean the north arcade. {sum(not t.cleaned for t in mall.north_trash)} patches left.'
        if not mall.east.unlocked and mall.next_store is None:
            return 'A new chapter','Open the east gallery for $1,500.'
        if mall.east.unlocked and mall.east.stores[0].restored and not mall.east.initial_cleanup_complete:
            return 'East gallery',f'Finish its first sweep. {sum(not t.cleaned for t in mall.east.trash)} patches left.'
        if mall.next_store:
            return 'Next opening',f'{mall.next_store.name} · {money(mall.next_store.cost)}'
        return 'A welcoming mall','Visit owners when their next idea is ready.'

    def prompt(self, game, target):
        if isinstance(target,Trash):
            return 'E','Collect litter' if game.upgrades.held<game.upgrades.capacity else 'Bag full. Find a bin.'
        if isinstance(target,TrashBin):return 'E','Sell carried trash'
        if isinstance(target,Shopper):return 'E',f'Say hello to {target.name}'
        if isinstance(target,RequestSpot):return ('Hold E' if target.duration else 'E'),target.title
        if isinstance(target,Store):
            if not target.restored:return 'E',f'Reopen {target.name}' if target.available else 'This store is still closed'
            return 'E',('Enter Workshop' if target.upgrade_shop=='east' else 'Enter Supplies') if target.upgrade_shop else f'Talk to {OWNERS[target.name]}'
        if target:return 'E','Open east gallery · $1,500'
        return 'Move','WASD or arrow keys'

    def directory(self, surface, mall, player, requests=None, people=(), bounds=None):
        if bounds is None:
            bounds=pygame.Rect(surface.get_width()-340,120,300,180)
        sx,sy=bounds.width/mall.size[0],bounds.height/mall.size[1]
        theme.frame(surface,bounds,theme.BG)
        for area in mall.playable_areas:
            r=pygame.Rect(bounds.x+area.x*sx,bounds.y+area.y*sy,area.width*sx,area.height*sy)
            pygame.draw.rect(surface,(69,94,84),r)
        for gate in mall.gates:
            r=pygame.Rect(bounds.x+gate.x*sx,bounds.y+gate.y*sy,max(2,gate.width*sx),max(2,gate.height*sy))
            pygame.draw.rect(surface,theme.GOLD,r)
        for store in mall.stores+mall.distant_stores:
            r=pygame.Rect(bounds.x+store.rect.x*sx,bounds.y+store.rect.y*sy,store.rect.width*sx,store.rect.height*sy)
            pygame.draw.rect(surface,theme.GOLD if store.restored else (43,57,58),r)
        for bin in mall.trash_bins:
            p=(round(bounds.x+bin.position.x*sx),round(bounds.y+bin.position.y*sy))
            pygame.draw.rect(surface,theme.ACCENT,(p[0]-2,p[1]-2,4,4))
        if requests and requests.store:
            destinations=[requests.store.position] if requests.ready else [s.position for s in requests.visible_spots]
            if not destinations and requests.store.request_level==2:
                destinations=[p.position for p in people if p.visible and p.identity not in requests.greetings]
            for p in destinations:
                pygame.draw.circle(surface,(111,211,233),(round(bounds.x+p.x*sx),round(bounds.y+p.y*sy)),4)
        pygame.draw.circle(surface,theme.TEXT,(round(bounds.x+player[0]*sx),round(bounds.y+player[1]*sy)),3)

    def draw(self, game, target):
        surface=game.screen;width,height=surface.get_size();mall=game.mall
        pygame.draw.rect(surface,theme.BG,(0,0,width,76))
        surface.blit(self.title.render('NORTHGATE',True,theme.TEXT),(22,13))
        region='East gallery' if mall.east.unlocked and mall.east.area.collidepoint(game.player.rect.center) else 'North arcade'
        surface.blit(self.small.render(region,True,theme.MUTED),(23,47))
        values=[('CLEAN',cleanliness_label(mall.cleanliness)),('CASH',money(game.cash)),('BAG',f'{game.upgrades.held} / {game.upgrades.capacity}')]
        for i,(label,value) in enumerate(values):
            r=pygame.Rect(width-450+i*145,10,133,56);theme.frame(surface,r,theme.PANEL,False)
            surface.blit(self.small.render(label,True,theme.MUTED),(r.x+12,r.y+8))
            color=theme.GOLD if label=='BAG' and game.upgrades.held==game.upgrades.capacity else theme.TEXT
            text=self.font.render(value,True,color);surface.blit(text,(r.x+12,r.y+27))
        title,objective=self.goal(game)
        card=pygame.Rect(20,88,min(width-40,480),72);theme.frame(surface,card)
        surface.blit(self.small.render(title,True,theme.ACCENT),(card.x+14,card.y+12))
        for i,line in enumerate(theme.wrap(self.font,objective,card.width-28)[:2]):
            surface.blit(self.font.render(line,True,theme.TEXT),(card.x+14,card.y+34+i*21))
        pygame.draw.rect(surface,theme.BG,(0,height-58,width,58))
        key,action=self.prompt(game,target)
        key_width=58 if key=='Hold E' else 44
        r=pygame.Rect(20,height-43,key_width,28);theme.frame(surface,r,theme.CARD,False)
        label=self.small.render(key,True,theme.GOLD);surface.blit(label,label.get_rect(center=r.center))
        available=width-key_width-330
        for i,line in enumerate(theme.wrap(self.small,action,available)[:2]):
            surface.blit(self.small.render(line,True,theme.TEXT),(r.right+12,height-41+i*17))
        controls=self.small.render('J Journal   M Sound   Esc Exit',True,theme.MUTED)
        surface.blit(controls,controls.get_rect(midright=(width-20,height-29)))
        if game.message_timer:
            lines=theme.wrap(self.small,game.message,min(540,width-68))[:2]
            box=pygame.Rect(0,0,min(568,width-40),20+len(lines)*18)
            box.midbottom=(width//2,height-70);theme.frame(surface,box)
            for i,line in enumerate(lines):surface.blit(self.small.render(line,True,theme.TEXT),(box.x+14,box.y+10+i*18))
