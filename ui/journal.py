"""Optional detail view: the map, income, equipment and owner readiness."""
import pygame
from systems.economy import money
from systems.requests import OWNERS
from ui import theme


class Journal:
    def __init__(self):self.open=False;self.page=0

    def geometry(self, surface):
        panel=pygame.Rect(0,0,min(surface.get_width()-40,900),min(surface.get_height()-56,640))
        panel.center=surface.get_rect().center
        close=pygame.Rect(panel.right-78,panel.y+20,58,28)
        return panel,close

    def page_buttons(self, surface):
        panel,_=self.geometry(surface)
        return [pygame.Rect(panel.right-110+i*44,panel.y+298,36,27) for i in range(2)]

    def handle(self,event,game):
        if event.type==pygame.KEYDOWN and event.key in (pygame.K_j,pygame.K_ESCAPE,pygame.K_e):self.open=False
        elif event.type==pygame.KEYDOWN and event.key in (pygame.K_LEFT,pygame.K_RIGHT):
            self.page=max(0,self.page+(-1 if event.key==pygame.K_LEFT else 1))
        elif event.type==pygame.MOUSEWHEEL:self.page=max(0,self.page-event.y)
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.geometry(game.screen)[1].collidepoint(event.pos):self.open=False
            for i,rect in enumerate(self.page_buttons(game.screen)):
                if rect.collidepoint(event.pos):self.page=max(0,self.page+(-1 if i==0 else 1))

    def draw(self,game):
        surface=game.screen;theme.dim(surface);panel,close=self.geometry(surface);theme.frame(surface,panel)
        surface.blit(game.hud.title.render('Mall journal',True,theme.TEXT),(panel.x+22,panel.y+22))
        theme.frame(surface,close,theme.CARD,False);text=game.hud.small.render('Close',True,theme.MUTED);surface.blit(text,text.get_rect(center=close.center))
        stats=[('Rent per 5 seconds',money(game.rent_income)),('Cleanliness bonus',f'{game.rent_multiplier:g}×'),
               ('Trash value',money(game.upgrades.unit_value)+' / item'),('Walking speed',f'{game.upgrades.speed_multiplier:g}×'),
               ('Visitors',str(len(game.shoppers.people))),('Fixture income',money(game.upgrades.fixture_rent)+' base')]
        half=(panel.width-66)//2
        for i,(label,value) in enumerate(stats):
            y=panel.y+92+i*27
            surface.blit(game.hud.small.render(label,True,theme.MUTED),(panel.x+22,y))
            text=game.hud.font.render(value,True,theme.TEXT);surface.blit(text,text.get_rect(topright=(panel.x+22+half,y-2)))
        map_rect=pygame.Rect(panel.x+44+half,panel.y+86,half,176)
        game.hud.directory(surface,game.mall,game.player.rect.center,game.owner_requests,game.shoppers.people,map_rect)
        surface.blit(game.hud.small.render('White: you   Blue: request   Gold: deliveries',True,theme.MUTED),(map_rect.x,map_rect.bottom+10))
        y=panel.y+304
        owners=[s for s in game.mall.stores if not s.upgrade_shop]
        pages=max(1,(len(owners)+5)//6);self.page=min(self.page,pages-1)
        surface.blit(game.hud.font.render(f'Store owners · {self.page+1}/{pages}',True,theme.ACCENT),(panel.x+22,y))
        for label,rect in zip(('<','>'),self.page_buttons(surface)):
            theme.frame(surface,rect,theme.CARD);text=game.hud.font.render(label,True,theme.ACCENT);surface.blit(text,text.get_rect(center=rect.center))
        for i,store in enumerate(owners[self.page*6:self.page*6+6]):
            r=pygame.Rect(panel.x+22,y+35+i*27,panel.width-44,24)
            if i%2==0:theme.frame(surface,r,theme.CARD,False)
            if not store.restored:status='Store closed'
            elif game.owner_requests.store is store:status='Your active request'
            elif store.request_wait>0:status='Next idea in '+theme.clock(store.request_wait)
            else:status='New favor ready' if store.request_level==3 else 'New request ready'
            surface.blit(game.hud.small.render(f'{OWNERS[store.name]} · {store.name}',True,theme.TEXT),(r.x+8,r.y+5))
            text=game.hud.small.render(status,True,theme.ACCENT if status in ('New request ready','New favor ready') else theme.MUTED)
            surface.blit(text,text.get_rect(topright=(r.right-8,r.y+5)))
        surface.blit(game.hud.small.render('J / Esc: return     Arrows / scroll: more owners',True,theme.MUTED),(panel.x+22,panel.bottom-27))
