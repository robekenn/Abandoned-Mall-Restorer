"""Optional detail view: the map, income, equipment and owner readiness."""
import pygame
from systems.economy import money, rent_multiplier
from systems.requests import OWNERS
from systems.story import CHAPTERS
from ui import theme


class Journal:
    def __init__(self):self.open=False;self.page=0;self.tab=0;self.court=0;self.notice='';self.chapter=0;self.memories_view=False

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
        return [pygame.Rect(panel.x+22+i*124,panel.y+59,114,25) for i in range(4)]

    def staff_rows(self, surface):
        panel,_=self.geometry(surface)
        return [pygame.Rect(panel.x+22,panel.y+98+i*94,panel.width-44,86) for i in range(4)]

    def staff_buttons(self, row):
        return {'hire':pygame.Rect(row.right-178,row.y+45,164,28),
                'clean':pygame.Rect(row.right-354,row.y+45,164,28),
                'walk':pygame.Rect(row.right-178,row.y+45,164,28)}

    @staticmethod
    def staff_context(game):
        return (game.courtyard.janitors,game.courtyard.world) if game.scene=='courtyard' else (game.janitors,game.mall)

    def staff_courts(self,game):
        manager,world=self.staff_context(game)
        return manager.courts(world)

    def buy_staff(self, game, key, action):
        manager,world=self.staff_context(game)
        success,self.notice=manager.purchase(key,action,game,world)
        game.audio.play('milestone' if success else 'blocked')
        if success:game.save_checkpoint()

    def handle(self,event,game):
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_j,pygame.K_ESCAPE,pygame.K_e):self.open=False;return
            if event.key in (pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_TAB):
                self.tab=(self.tab+1)%4 if event.key==pygame.K_TAB else event.key-pygame.K_1
                if self.tab==2:self.chapter=min(3,game.story.current)
                self.notice='';return
            if self.tab==3:
                if event.key in (pygame.K_UP,pygame.K_DOWN):self.court=(self.court+(-1 if event.key==pygame.K_UP else 1))%4
                elif event.key in (pygame.K_RETURN,pygame.K_SPACE):self.start_event(game,self.court)
                return
            if self.tab==2:
                if event.key==pygame.K_r:self.memories_view=not self.memories_view
                if event.key in (pygame.K_LEFT,pygame.K_RIGHT):self.chapter=max(0,min(3,self.chapter+(-1 if event.key==pygame.K_LEFT else 1)))
                return
            if self.tab==1:
                if event.key in (pygame.K_UP,pygame.K_DOWN):self.court=(self.court+(-1 if event.key==pygame.K_UP else 1))%len(self.staff_courts(game))
                action={pygame.K_RETURN:'hire',pygame.K_SPACE:'hire',pygame.K_c:'clean',pygame.K_w:'walk'}.get(event.key)
                if action:self.buy_staff(game,self.staff_courts(game)[self.court%len(self.staff_courts(game))][0],action)
                return
            if event.key in (pygame.K_LEFT,pygame.K_RIGHT):self.page=max(0,self.page+(-1 if event.key==pygame.K_LEFT else 1))
        elif event.type==pygame.MOUSEWHEEL:
            if self.tab==0:self.page=max(0,self.page-event.y)
            elif self.tab==1:self.court=(self.court-event.y)%len(self.staff_courts(game))
            elif self.tab==2:self.chapter=max(0,min(3,self.chapter-event.y))
            else:self.court=(self.court-event.y)%4
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.geometry(game.screen)[1].collidepoint(event.pos):self.open=False;return
            for i,rect in enumerate(self.tabs(game.screen)):
                if rect.collidepoint(event.pos):
                    self.tab=i;self.notice=''
                    if i==2:self.chapter=min(3,game.story.current)
                    return
            if self.tab==3:
                for i,row in enumerate(self.life_rows(game.screen)):
                    if row.collidepoint(event.pos):self.court=i;self.start_event(game,i)
                return
            if self.tab==2:
                for i,rect in enumerate(self.page_buttons(game.screen)):
                    if rect.collidepoint(event.pos):self.chapter=max(0,min(3,self.chapter+(-1 if i==0 else 1)))
                return
            if self.tab==1:
                for i,row in enumerate(self.staff_rows(game.screen)[:len(self.staff_courts(game))]):
                    if row.collidepoint(event.pos):
                        self.court=i;key=self.staff_courts(game)[i][0]
                        actions=('clean','walk') if key in self.staff_context(game)[0].people else ('hire',)
                        for action in actions:
                            if self.staff_buttons(row)[action].collidepoint(event.pos):self.buy_staff(game,key,action)
                return
            for i,rect in enumerate(self.page_buttons(game.screen)):
                if rect.collidepoint(event.pos):self.page=max(0,self.page+(-1 if i==0 else 1))

    def life_rows(self, surface):
        panel,_=self.geometry(surface)
        return [pygame.Rect(panel.x+22,panel.y+98+i*86,panel.width-44,78) for i in range(4)]

    def start_event(self, game, index):
        if game.scene=='courtyard':
            self.notice='Return to the indoor mall to host a gathering.';return
        key=list(game.life.completed)[index]
        if game.life.start(game,key):
            self.open=False;game.notify(game.life.event.title+' · Follow the gold table on your journal map.')
        elif game.life.active:self.notice='A gathering is already underway. Visit its community table to join in.'
        elif game.life.cooldowns[key]>0:self.notice='Give the neighbors a little time to prepare for another gathering.'
        else:self.notice='Open two regular businesses and clean at least half of this court to host a gathering.'

    def draw_life(self, game, panel):
        for i,(court,row) in enumerate(zip(game.janitors.courts(game.mall),self.life_rows(game.screen))):
            key,name=court[:2];life=game.life;theme.frame(game.screen,row,theme.CARD)
            if i==self.court:pygame.draw.rect(game.screen,theme.ACCENT,row,1,border_radius=8)
            game.screen.blit(game.hud.font.render(name,True,theme.TEXT),(row.x+12,row.y+8))
            title=life.event.title if life.active==key else life.gathering(key).title
            game.screen.blit(game.hud.small.render(title,True,theme.GOLD),(row.x+12,row.y+33))
            if life.active==key:status=f'Underway · {life.round}/3 connections · Visit the community table'
            elif not court[5]:status='Open this court to bring its neighbors together'
            elif life.cooldowns[key]>0:status='Next gathering in '+theme.clock(life.cooldowns[key])+' of play'
            elif not life.available(game,key):status='Needs 2 regular shops and 50% local cleanliness'
            else:status='Enter / click to host · Completed '+str(life.completed[key])
            game.screen.blit(game.hud.small.render(status,True,theme.ACCENT),(row.x+12,row.y+55))
        for n,line in enumerate(theme.wrap(game.hud.small,self.notice or 'Optional gatherings have no deadline. Listen to each neighbor and find a little something they will love.',panel.width-44)[:3]):
            game.screen.blit(game.hud.small.render(line,True,theme.MUTED),(panel.x+22,panel.bottom-85+n*19))
        game.screen.blit(game.hud.small.render('1–4: tabs   Up/Down: court   Enter: host   J / Esc: return',True,theme.MUTED),(panel.x+22,panel.bottom-27))

    def draw_staff(self, game, panel):
        manager,world=self.staff_context(game)
        self.court%=len(manager.courts(world))
        for i,((key,name,_,_,_,unlocked,_),row) in enumerate(zip(manager.courts(world),self.staff_rows(game.screen))):
            theme.frame(game.screen,row,theme.CARD)
            if i==self.court:pygame.draw.rect(game.screen,theme.ACCENT,row,1,border_radius=8)
            game.screen.blit(game.hud.font.render(name,True,theme.TEXT),(row.x+12,row.y+9))
            person=manager.people.get(key)
            if person:
                detail=f'{person.clean_seconds}s pickup · {person.speed}px/s · {person.cleaned} cleaned · earned {money(person.earnings)}'
                actions=('clean','walk')
            else:
                detail='One local janitor · automatic sales at 75% of your trash value'
                actions=('hire',)
            game.screen.blit(game.hud.small.render(detail,True,theme.MUTED),(row.x+12,row.y+32))
            for action in actions:
                button=self.staff_buttons(row)[action]
                if action=='hire':label='Hire '+money(manager.hire_cost(key,world)) if unlocked else 'Court locked'
                else:
                    price=manager.upgrade_price(key,action,world)
                    values=person.CLEAN_SECONDS if action=='clean' else person.WALK_SPEEDS
                    level=getattr(person,action+'_level');value=values[min(3,level+1)]
                    label=('Clean '+str(value)+'s' if action=='clean' else 'Walk '+str(value))+' · '+(money(price) if price is not None else 'Max')
                theme.frame(game.screen,button,theme.PANEL,False)
                text=game.hud.small.render(label,True,theme.ACCENT if unlocked else theme.MUTED)
                game.screen.blit(text,text.get_rect(center=button.center))
        if self.notice:
            game.screen.blit(game.hud.small.render(self.notice,True,theme.GOLD),(panel.x+22,panel.bottom-49))
        caption='1–4: tabs   ↑/↓: court   Enter: hire   C: cleaning   W: walking'
        game.screen.blit(game.hud.small.render(caption,True,theme.MUTED),(panel.x+22,panel.bottom-27))

    def draw_story(self, game, panel):
        i=self.chapter;chapter=CHAPTERS[i]
        game.screen.blit(game.hud.title.render(chapter.title,True,theme.TEXT),(panel.x+22,panel.y+99))
        status=chapter.gathering if game.story.completed[i] else 'In progress' if game.story.started[i] else 'A chapter to discover'
        game.screen.blit(game.hud.small.render(f'{i+1}/4 · {chapter.speaker} · '+status,True,theme.GOLD),(panel.x+22,panel.y+133))
        description=chapter.ending if game.story.completed[i] else chapter.opening
        for n,line in enumerate(theme.wrap(game.hud.small,description,panel.width-44)):
            game.screen.blit(game.hud.small.render(line,True,theme.MUTED),(panel.x+22,panel.y+163+n*21))
        for label,rect in zip(('<','>'),self.page_buttons(game.screen)):
            theme.frame(game.screen,rect,theme.CARD);text=game.hud.font.render(label,True,theme.ACCENT);game.screen.blit(text,text.get_rect(center=rect.center))
        if self.memories_view:
            y=panel.y+329
            for n,text in enumerate(chapter.memories):
                text=text if game.story.memories[i][n] else game.story.clue(i,n)
                lines=theme.wrap(game.hud.small,text,panel.width-44)
                for line in lines:
                    game.screen.blit(game.hud.small.render(line,True,theme.TEXT),(panel.x+22,y));y+=19
                y+=10
        else:
            for n,(label,count,goal) in enumerate(game.story.requirements(game,i)):
                row=pygame.Rect(panel.x+22,panel.y+334+n*28,panel.width-44,25)
                theme.frame(game.screen,row,theme.CARD,False)
                game.screen.blit(game.hud.small.render(label,True,theme.TEXT),(row.x+10,row.y+5))
                text=game.hud.small.render('Done' if count>=goal else f'{count}/{goal}',True,theme.ACCENT)
                game.screen.blit(text,text.get_rect(topright=(row.right-10,row.y+5)))
        result='The lantern walk is here. Northgate still has stories to share.' if game.story.festival else 'Read the gold community board in each court to begin or finish.'
        game.screen.blit(game.hud.small.render(result,True,theme.GOLD),(panel.x+22,panel.bottom-53))
        game.screen.blit(game.hud.small.render('1–4: tabs   Left/Right: chapters   R: keepsakes   J / Esc: return',True,theme.MUTED),(panel.x+22,panel.bottom-27))

    def draw(self,game):
        surface=game.screen;theme.dim(surface);panel,close=self.geometry(surface);theme.frame(surface,panel)
        surface.blit(game.hud.title.render('Mall journal',True,theme.TEXT),(panel.x+22,panel.y+22))
        theme.frame(surface,close,theme.CARD,False);text=game.hud.small.render('Close',True,theme.MUTED);surface.blit(text,text.get_rect(center=close.center))
        for i,(label,rect) in enumerate(zip(('Overview','Janitors','Story','Mall life'),self.tabs(surface))):
            theme.frame(surface,rect,theme.CARD,False)
            text=game.hud.small.render(label,True,theme.ACCENT if self.tab==i else theme.MUTED);surface.blit(text,text.get_rect(center=rect.center))
        if self.tab==3:self.draw_life(game,panel);return
        if self.tab==1:self.draw_staff(game,panel);return
        if self.tab==2:self.draw_story(game,panel);return
        outside=game.scene=='courtyard';world=game.courtyard.world if outside else game.mall
        visitors=game.courtyard.shoppers if outside else game.shoppers
        stats=[('Rent per 5 seconds',money(game.rent_income)),('Cleanliness bonus',f'{rent_multiplier(world.cleanliness):g}×'),
               ('Trash value',money(game.upgrades.unit_value)+' / item'),('Walking speed',f'{game.upgrades.speed_multiplier:g}×'),
               ('Visitors',str(len(visitors.people))),('Fixture income',money(sum(k.startswith('courtyard_') for k in game.upgrades.decor) if outside else sum(not k.startswith('courtyard_') for k in game.upgrades.decor))+' base')]
        half=(panel.width-66)//2
        for i,(label,value) in enumerate(stats):
            y=panel.y+92+i*27
            surface.blit(game.hud.small.render(label,True,theme.MUTED),(panel.x+22,y))
            text=game.hud.font.render(value,True,theme.TEXT);surface.blit(text,text.get_rect(topright=(panel.x+22+half,y-2)))
        map_rect=pygame.Rect(panel.x+44+half,panel.y+86,half,176)
        game.hud.directory(surface,world,game.player.rect.center,None if outside else game.owner_requests,visitors.people,map_rect)
        surface.blit(game.hud.small.render('White: you   Blue: task   Gold: story / delivery',True,theme.MUTED),(map_rect.x,map_rect.bottom+10))
        y=panel.y+304
        owners=[s for s in world.stores if not s.upgrade_shop]
        pages=max(1,(len(owners)+5)//6);self.page=min(self.page,pages-1)
        surface.blit(game.hud.font.render(f'{"Restaurants" if outside else "Store owners"} · {self.page+1}/{pages}',True,theme.ACCENT),(panel.x+22,y))
        for label,rect in zip(('<','>'),self.page_buttons(surface)):
            theme.frame(surface,rect,theme.CARD);text=game.hud.font.render(label,True,theme.ACCENT);surface.blit(text,text.get_rect(center=rect.center))
        for i,store in enumerate(owners[self.page*6:self.page*6+6]):
            r=pygame.Rect(panel.x+22,y+35+i*24,panel.width-44,22)
            if i%2==0:theme.frame(surface,r,theme.CARD,False)
            if not store.restored:status='Store closed'
            elif outside:
                requests=game.courtyard.kitchen_requests
                if requests.ready(store.name):status='Needs cooking help'
                else:status='Next request in '+theme.clock(requests.waits[store.name])
            elif game.owner_requests.store is store:status='Your active request'
            elif store.request_wait>0:status='Next idea in '+theme.clock(store.request_wait)
            else:status='New favor ready' if store.request_level==3 else 'New request ready'
            surface.blit(game.hud.small.render(store.name if outside else f'{OWNERS[store.name]} · {store.name}',True,theme.TEXT),(r.x+8,r.y+5))
            text=game.hud.small.render(status,True,theme.ACCENT if status in ('New request ready','New favor ready','Needs cooking help') else theme.MUTED)
            surface.blit(text,text.get_rect(topright=(r.right-8,r.y+5)))
        saved=game.save_store.status if game.save_store.enabled else 'Playtest session'
        surface.blit(game.hud.small.render('Each kitchen has its own cooldown · Countdowns run during play' if outside else 'F5 save · '+saved,True,theme.MUTED),(panel.x+22,panel.bottom-53))
        surface.blit(game.hud.small.render('1–4: tabs   J / Esc: return   Arrows / scroll: owners',True,theme.MUTED),(panel.x+22,panel.bottom-27))
