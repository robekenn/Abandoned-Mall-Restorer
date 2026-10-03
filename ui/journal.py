"""Optional detail view: the map, income, equipment and owner readiness."""
import pygame
from systems.economy import money
from systems.requests import OWNERS
from ui import theme


class Journal:
    def __init__(self):self.open=False;self.page=0;self.tab=0;self.court=0;self.notice=''

    def geometry(self, surface):
        panel=pygame.Rect(0,0,min(surface.get_width()-40,900),min(surface.get_height()-56,640))
        panel.center=surface.get_rect().center
        close=pygame.Rect(panel.right-78,panel.y+20,58,28)
        return panel,close

    def page_buttons(self, surface):
        panel,_=self.geometry(surface)
        return [pygame.Rect(panel.right-110+i*44,panel.y+298,36,27) for i in range(2)]

    def tabs(self, surface):
        panel,_=self.geometry(surface)
        return [pygame.Rect(panel.x+22+i*124,panel.y+59,114,25) for i in range(2)]

    def staff_rows(self, surface):
        panel,_=self.geometry(surface)
        return [pygame.Rect(panel.x+22,panel.y+98+i*94,panel.width-44,86) for i in range(4)]

    def staff_buttons(self, row):
        return {'hire':pygame.Rect(row.right-178,row.y+45,164,28),
                'clean':pygame.Rect(row.right-354,row.y+45,164,28),
                'walk':pygame.Rect(row.right-178,row.y+45,164,28)}

    def buy_staff(self, game, key, action):
        success,self.notice=game.janitors.purchase(key,action,game)
        game.audio.play('milestone' if success else 'blocked')

    def handle(self,event,game):
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_j,pygame.K_ESCAPE,pygame.K_e):self.open=False;return
            if event.key in (pygame.K_1,pygame.K_2,pygame.K_TAB):
                self.tab=(self.tab+1)%2 if event.key==pygame.K_TAB else event.key-pygame.K_1
                self.notice='';return
            if self.tab==1:
                if event.key in (pygame.K_UP,pygame.K_DOWN):self.court=(self.court+(-1 if event.key==pygame.K_UP else 1))%4
                action={pygame.K_RETURN:'hire',pygame.K_SPACE:'hire',pygame.K_c:'clean',pygame.K_w:'walk'}.get(event.key)
                if action:self.buy_staff(game,game.janitors.courts(game.mall)[self.court][0],action)
                return
            if event.key in (pygame.K_LEFT,pygame.K_RIGHT):self.page=max(0,self.page+(-1 if event.key==pygame.K_LEFT else 1))
        elif event.type==pygame.MOUSEWHEEL:
            if self.tab==0:self.page=max(0,self.page-event.y)
            else:self.court=(self.court-event.y)%4
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.geometry(game.screen)[1].collidepoint(event.pos):self.open=False;return
            for i,rect in enumerate(self.tabs(game.screen)):
                if rect.collidepoint(event.pos):self.tab=i;self.notice='';return
            if self.tab==1:
                for i,row in enumerate(self.staff_rows(game.screen)):
                    if row.collidepoint(event.pos):
                        self.court=i;key=game.janitors.courts(game.mall)[i][0]
                        actions=('clean','walk') if key in game.janitors.people else ('hire',)
                        for action in actions:
                            if self.staff_buttons(row)[action].collidepoint(event.pos):self.buy_staff(game,key,action)
                return
            for i,rect in enumerate(self.page_buttons(game.screen)):
                if rect.collidepoint(event.pos):self.page=max(0,self.page+(-1 if i==0 else 1))

    def draw_staff(self, game, panel):
        for i,((key,name,_,_,_,unlocked,_),row) in enumerate(zip(game.janitors.courts(game.mall),self.staff_rows(game.screen))):
            theme.frame(game.screen,row,theme.CARD)
            if i==self.court:pygame.draw.rect(game.screen,theme.ACCENT,row,1,border_radius=8)
            game.screen.blit(game.hud.font.render(name,True,theme.TEXT),(row.x+12,row.y+9))
            person=game.janitors.people.get(key)
            if person:
                detail=f'{person.clean_seconds}s pickup · {person.speed}px/s · {person.cleaned} cleaned · earned {money(person.earnings)}'
                actions=('clean','walk')
            else:
                detail='One local janitor · automatic sales at 75% of your trash value'
                actions=('hire',)
            game.screen.blit(game.hud.small.render(detail,True,theme.MUTED),(row.x+12,row.y+32))
            for action in actions:
                button=self.staff_buttons(row)[action]
                if action=='hire':label='Hire '+money(game.janitors.hire_cost(key,game.mall)) if unlocked else 'Court locked'
                else:
                    price=game.janitors.upgrade_price(key,action,game.mall)
                    values=person.CLEAN_SECONDS if action=='clean' else person.WALK_SPEEDS
                    level=getattr(person,action+'_level');value=values[min(3,level+1)]
                    label=('Clean '+str(value)+'s' if action=='clean' else 'Walk '+str(value))+' · '+(money(price) if price is not None else 'Max')
                theme.frame(game.screen,button,theme.PANEL,False)
                text=game.hud.small.render(label,True,theme.ACCENT if unlocked else theme.MUTED)
                game.screen.blit(text,text.get_rect(center=button.center))
        if self.notice:
            game.screen.blit(game.hud.small.render(self.notice,True,theme.GOLD),(panel.x+22,panel.bottom-49))
        caption='1/2: tabs   Up/Down: court   Enter: hire   C: clean upgrade   W: walk upgrade'
        game.screen.blit(game.hud.small.render(caption,True,theme.MUTED),(panel.x+22,panel.bottom-27))

    def draw(self,game):
        surface=game.screen;theme.dim(surface);panel,close=self.geometry(surface);theme.frame(surface,panel)
        surface.blit(game.hud.title.render('Mall journal',True,theme.TEXT),(panel.x+22,panel.y+22))
        theme.frame(surface,close,theme.CARD,False);text=game.hud.small.render('Close',True,theme.MUTED);surface.blit(text,text.get_rect(center=close.center))
        for i,(label,rect) in enumerate(zip(('Overview','Janitors'),self.tabs(surface))):
            theme.frame(surface,rect,theme.CARD,False)
            text=game.hud.small.render(label,True,theme.ACCENT if self.tab==i else theme.MUTED);surface.blit(text,text.get_rect(center=rect.center))
        if self.tab==1:self.draw_staff(game,panel);return
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
        surface.blit(game.hud.small.render('1/2: tabs   J / Esc: return   Arrows / scroll: owners',True,theme.MUTED),(panel.x+22,panel.bottom-27))
