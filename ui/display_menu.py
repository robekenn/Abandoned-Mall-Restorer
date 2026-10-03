"""A short shop-specific shelf arrangement, with mouse and keyboard choices."""
import pygame
from ui import theme


class DisplayMenu:
    def __init__(self):
        self.open=False
        self.arrangement=[]
        self.notice=''

    def visit(self):
        self.open=True
        self.arrangement=[]
        self.notice=''

    def geometry(self, surface):
        panel=pygame.Rect(0,0,min(surface.get_width()-48,760),min(surface.get_height()-72,470))
        panel.center=surface.get_rect().center
        width=(panel.width-56)//3
        choices=[pygame.Rect(panel.x+20+i*(width+8),panel.y+286,width,54) for i in range(3)]
        return panel,choices

    def choose(self, index, game):
        requests=game.owner_requests
        if not requests.display_items or requests.ready:
            self.open=False
            return
        if index in self.arrangement:
            self.notice='Each item has one place. Backspace undoes your last choice.'
            return
        self.arrangement.append(index)
        self.notice=''
        game.audio.play('pickup')
        if len(self.arrangement)==3:
            if requests.arrange_display(self.arrangement):
                self.open=False
                game.player.use_tool('setup',requests.spots[0].position+pygame.Vector2(48,-16))
                game.feedback.burst(requests.spots[0].position,'DISPLAY READY',restored=True)
                game.audio.play('milestone')
                game.notify(requests.objective)
            else:
                self.arrangement=[]
                self.notice='Let’s try again. Follow the shelf plan from left to right.'
                game.audio.play('blocked')

    def handle(self, event, game):
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,pygame.K_e):self.open=False
            elif event.key in (pygame.K_1,pygame.K_2,pygame.K_3):self.choose(event.key-pygame.K_1,game)
            elif event.key==pygame.K_BACKSPACE and self.arrangement:
                self.arrangement.pop();self.notice=''
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for i,rect in enumerate(self.geometry(game.screen)[1]):
                if rect.collidepoint(event.pos):self.choose(i,game);break

    def draw(self, game):
        theme.dim(game.screen)
        panel,choices=self.geometry(game.screen)
        theme.frame(game.screen,panel)
        items=game.owner_requests.display_items
        if not items:return
        game.screen.blit(game.hud.title.render('A window worth stopping for',True,theme.TEXT),(panel.x+20,panel.y+20))
        game.screen.blit(game.hud.small.render('Match the shelf plan, from left to right.',True,theme.MUTED),(panel.x+20,panel.y+62))
        game.screen.blit(game.hud.small.render('OWNER’S SHELF PLAN',True,theme.ACCENT),(panel.x+20,panel.y+110))
        width=choices[0].width
        for slot,index in enumerate(game.owner_requests.display_plan):
            r=pygame.Rect(choices[slot].x,panel.y+140,width,46)
            theme.frame(game.screen,r,theme.CARD,False)
            text=game.hud.font.render(items[index],True,theme.TEXT)
            game.screen.blit(text,text.get_rect(center=r.center))
            placement=pygame.Rect(r.x,panel.y+216,width,44)
            theme.frame(game.screen,placement,theme.CARD if slot==len(self.arrangement) else theme.PANEL)
            name=items[self.arrangement[slot]] if slot<len(self.arrangement) else f'Place item {slot+1}'
            text=game.hud.small.render(name,True,theme.GOLD if slot<len(self.arrangement) else theme.MUTED)
            game.screen.blit(text,text.get_rect(center=placement.center))
        for i,r in enumerate(choices):
            theme.frame(game.screen,r,theme.CARD)
            text=game.hud.font.render(f'{i+1}  {items[i]}',True,theme.MUTED if i in self.arrangement else theme.ACCENT)
            game.screen.blit(text,text.get_rect(center=r.center))
        for i,line in enumerate(theme.wrap(game.hud.small,self.notice,panel.width-40)):
            game.screen.blit(game.hud.small.render(line,True,theme.GOLD),(panel.x+20,panel.y+366+i*18))
        game.screen.blit(game.hud.small.render('1–3 / click: place an item     Backspace: undo     Esc: return',True,theme.MUTED),(panel.x+20,panel.bottom-26))
