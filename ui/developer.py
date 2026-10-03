"""Explicitly enabled playtest shortcuts; F3 never affects a normal game."""
import pygame
from ui import theme
from systems.economy import money


class Developer:
    ACTIONS=(('cash_10000','Add $10,000'),('cash_100000','Add $100,000'),
             ('cash_1000000','Add $1,000,000'),('clean','Clean this court'),('next','Jump to next court'))

    def __init__(self, enabled=False):
        self.enabled=enabled;self.open=False;self.selection=0;self.notice=''

    def geometry(self, surface):
        panel=pygame.Rect(0,0,min(580,surface.get_width()-64),440)
        panel.center=surface.get_rect().center
        rows=[pygame.Rect(panel.x+24,panel.y+118+i*48,panel.width-48,38) for i in range(len(self.ACTIONS))]
        return panel,rows

    def act(self, action, game):
        if not self.enabled:return False
        if action.startswith('cash_') and action in dict(self.ACTIONS):
            amount=int(action.split('_')[1]);game.cash+=amount;self.notice=money(amount)+' added.'
        elif action=='clean':
            court=next((c for c in game.janitors.courts(game.mall) if c[5] and c[2].collidepoint(game.player.rect.center)),None)
            if court is None:self.notice='Step into a court before cleaning it.';return False
            for trash in court[4]:game.mall.clean_trash(trash)
            self.notice=court[1]+' cleaned.'
        elif action=='next':
            region=next((r for r in game.mall.regions if not r.unlocked),None)
            if region is None:self.notice='All four courts are already open.';return False
            previous=game.janitors.courts(game.mall)[game.mall.regions.index(region)]
            for trash in previous[4]:game.mall.clean_trash(trash)
            for store in previous[3]:store.restored=True
            game.mall.refresh_businesses()
            if not game.mall.unlock_section(region):return False
            game.player.rect.center=region.stores[0].position
            game.tutorial.skip()
            game.frame_camera(game.screen.get_size())
            self.notice=region.name+' opened for playtesting.'
        else:return False
        return True

    def handle(self, event, game):
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,pygame.K_e):self.open=False
            elif event.key in (pygame.K_UP,pygame.K_DOWN):self.selection=(self.selection+(-1 if event.key==pygame.K_UP else 1))%len(self.ACTIONS)
            elif event.key in (pygame.K_RETURN,pygame.K_SPACE):self.act(self.ACTIONS[self.selection][0],game)
            elif pygame.K_1<=event.key<=pygame.K_5:self.act(self.ACTIONS[event.key-pygame.K_1][0],game)
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for i,row in enumerate(self.geometry(game.screen)[1]):
                if row.collidepoint(event.pos):self.selection=i;self.act(self.ACTIONS[i][0],game)

    def draw(self, game):
        theme.dim(game.screen);panel,rows=self.geometry(game.screen);theme.frame(game.screen,panel)
        game.screen.blit(game.hud.title.render('Developer playtest',True,theme.TEXT),(panel.x+24,panel.y+22))
        game.screen.blit(game.hud.small.render('Shortcuts for exploring and testing Northgate.',True,theme.MUTED),(panel.x+24,panel.y+66))
        game.screen.blit(game.hud.small.render('Cash: '+money(game.cash),True,theme.GOLD),(panel.x+24,panel.y+88))
        for i,((_,label),row) in enumerate(zip(self.ACTIONS,rows)):
            theme.frame(game.screen,row,theme.CARD)
            if i==self.selection:pygame.draw.rect(game.screen,theme.ACCENT,row,1,border_radius=6)
            game.screen.blit(game.hud.font.render(f'{i+1}  {label}',True,theme.TEXT),(row.x+14,row.y+9))
        game.screen.blit(game.hud.small.render(self.notice,True,theme.ACCENT),(panel.x+24,panel.bottom-61))
        game.screen.blit(game.hud.small.render('1–5 / click: apply   Up/Down: select   F3 / Esc: close',True,theme.MUTED),(panel.x+24,panel.bottom-29))
