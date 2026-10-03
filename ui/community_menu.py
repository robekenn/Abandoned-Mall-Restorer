"""A short, unhurried matching conversation at a community table."""
import pygame
from ui import theme


class CommunityMenu:
    def __init__(self):self.open=False;self.selection=0

    def geometry(self, surface):
        panel=pygame.Rect(0,0,min(surface.get_width()-64,700),490);panel.center=surface.get_rect().center
        rows=[pygame.Rect(panel.x+26,panel.y+228+i*48,panel.width-52,38) for i in range(3)]
        return panel,rows

    def action(self, game, index):
        if game.life.choose(game,index) and not game.life.active:self.open=False
        self.selection=0

    def handle(self, event, game):
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,pygame.K_e):self.open=False
            elif event.key in (pygame.K_UP,pygame.K_DOWN):self.selection=(self.selection+(-1 if event.key==pygame.K_UP else 1))%(3 if game.life.round<3 else 1)
            elif event.key in (pygame.K_RETURN,pygame.K_SPACE):self.action(game,self.selection)
            elif pygame.K_1<=event.key<=pygame.K_3 and (game.life.round<3 or event.key==pygame.K_1):self.action(game,event.key-pygame.K_1)
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for i,row in enumerate(self.geometry(game.screen)[1]):
                if (game.life.round<3 or i==0) and row.collidepoint(event.pos):self.action(game,i)

    def draw(self, game):
        life=game.life
        if not life.event:self.open=False;return
        theme.dim(game.screen);panel,rows=self.geometry(game.screen);theme.frame(game.screen,panel)
        game.screen.blit(game.hud.title.render(life.event.title,True,theme.TEXT),(panel.x+26,panel.y+25))
        game.screen.blit(game.hud.small.render(f'Little connections · {life.round}/3 · No deadline',True,theme.GOLD),(panel.x+26,panel.y+67))
        if life.round<3:
            name,clue,_=life.guest(life.round);description=name+': '+clue;choices=life.event.choices
        else:description='Everyone found something to take home. Northgate feels a little more like a neighborhood.';choices=('Thank the neighbors and collect your reward','','')
        for i,line in enumerate(theme.wrap(game.hud.font,description,panel.width-52)):
            game.screen.blit(game.hud.font.render(line,True,theme.TEXT),(panel.x+26,panel.y+115+i*26))
        for i,(choice,row) in enumerate(zip(choices,rows)):
            if not choice:continue
            theme.frame(game.screen,row,theme.CARD)
            if i==self.selection:pygame.draw.rect(game.screen,theme.ACCENT,row,1,border_radius=8)
            game.screen.blit(game.hud.font.render((str(i+1)+'  ' if life.round<3 else '')+choice,True,theme.ACCENT),(row.x+12,row.y+9))
        for i,line in enumerate(theme.wrap(game.hud.small,life.notice,panel.width-52)[:3]):
            game.screen.blit(game.hud.small.render(line,True,theme.MUTED),(panel.x+26,panel.y+389+i*19))
        game.screen.blit(game.hud.small.render('1 / 2 / 3 · Enter / click · Esc / E: return to the mall',True,theme.MUTED),(panel.x+26,panel.bottom-27))
