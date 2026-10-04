"""A quiet introduction that dissolves into the existing mall scene."""
import pygame
from ui import theme


class Welcome:
    FADE_SECONDS=.9
    STORY=(
        'Northgate was the heart of this neighborhood. Now its shops are shuttered and its fountain is silent.',
        'You remember its winter lantern walks from childhood. Now you have the keys.',
        'One piece of litter. One reopened shop. Small acts of care can give a community somewhere to belong again.',
    )

    def __init__(self, open=True):
        self.open=open
        self.tutorial_enabled=True
        self.has_save=False;self.continuing=False;self.confirm_new=False;self.status=''
        self.elapsed=0.0
        self.leaving=False
        self.fade=0.0
        self.heading=pygame.font.Font(None,58)

    def geometry(self, surface):
        panel=pygame.Rect(0,0,min(surface.get_width()-64,680),min(surface.get_height()-64,510))
        panel.center=surface.get_rect().center
        start=pygame.Rect(panel.x+30,panel.bottom-103,panel.width-156,46)
        quit=pygame.Rect(start.right+12,start.y,84,46)
        if self.has_save:start.width=(start.width-12)//2
        return panel,start,quit

    def new_rect(self, surface):
        _,start,_=self.geometry(surface)
        return pygame.Rect(start.right+12,start.y,start.width,46)

    def choose_new(self):
        if self.has_save and not self.confirm_new:
            self.confirm_new=True;self.status='Start fresh? Choose New game again to replace this save.'
        else:self.start()

    def tutorial_rect(self, surface):
        panel,_,_=self.geometry(surface)
        return pygame.Rect(panel.x+30,panel.bottom-142,panel.width-60,25)

    def start(self):
        if not self.leaving:
            self.leaving=True
            self.fade=0.0

    def update(self, dt):
        self.elapsed+=dt
        if self.leaving:
            self.fade=min(1,self.fade+dt/self.FADE_SECONDS)
            if self.fade>=1:self.open=False

    def handle(self, event, game):
        if self.leaving:return
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN,pygame.K_SPACE):
                if self.has_save:game.continue_game()
                else:self.start()
            elif event.key==pygame.K_n:self.choose_new()
            elif event.key==pygame.K_ESCAPE:game.pause.show(True)
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            _,start,quit=self.geometry(game.screen)
            if self.tutorial_rect(game.screen).collidepoint(event.pos):self.tutorial_enabled=not self.tutorial_enabled
            elif self.has_save and self.new_rect(game.screen).collidepoint(event.pos):self.choose_new()
            elif start.collidepoint(event.pos):
                if self.has_save:game.continue_game()
                else:self.start()
            elif quit.collidepoint(event.pos):game.pause.show(True)

    def draw(self, game):
        overlay=pygame.Surface(game.screen.get_size(),pygame.SRCALPHA)
        overlay.fill((8,16,20,165))
        panel,start,quit=self.geometry(overlay)
        theme.frame(overlay,panel)
        overlay.blit(game.hud.small.render('A SMALL BEGINNING',True,theme.ACCENT),(panel.x+30,panel.y+27))
        overlay.blit(self.heading.render('Northgate Mall',True,theme.TEXT),(panel.x+28,panel.y+58))
        overlay.blit(game.hud.font.render('A place worth coming back to.',True,theme.GOLD),(panel.x+30,panel.y+111))
        y=panel.y+162
        for paragraph in self.STORY:
            for line in theme.wrap(game.hud.font,paragraph,panel.width-60):
                overlay.blit(game.hud.font.render(line,True,theme.TEXT),(panel.x+30,y));y+=24
            y+=14
        option='First steps guide: '+('On' if self.tutorial_enabled else 'Off')+'  ·  click to change'
        overlay.blit(game.hud.small.render(option,True,theme.ACCENT),self.tutorial_rect(overlay).topleft)
        hover=start.collidepoint(pygame.mouse.get_pos())
        theme.frame(overlay,start,(53,88,79) if hover else theme.CARD)
        text=game.hud.font.render('Continue' if self.has_save else 'Start restoring',True,theme.ACCENT)
        overlay.blit(text,text.get_rect(center=start.center))
        if self.has_save:
            new=self.new_rect(overlay);theme.frame(overlay,new,theme.CARD)
            text=game.hud.font.render('Confirm new game' if self.confirm_new else 'New game',True,theme.MUTED)
            overlay.blit(text,text.get_rect(center=new.center))
        if self.status:
            for i,line in enumerate(theme.wrap(game.hud.small,self.status,panel.width-60)):
                overlay.blit(game.hud.small.render(line,True,theme.GOLD),(panel.x+30,panel.bottom-180+i*18))
        theme.frame(overlay,quit,theme.PANEL)
        text=game.hud.small.render('Quit',True,theme.MUTED)
        overlay.blit(text,text.get_rect(center=quit.center))
        sound='Sound off' if game.audio.muted else 'Sound on'
        caption=f'Enter: {"continue" if self.has_save else "start"}     N: new game     F2: settings     M: {sound}'
        overlay.blit(game.hud.small.render(caption,True,theme.MUTED),(panel.x+30,panel.bottom-37))
        # Smoothstep keeps the opening and the handoff from snapping between screens.
        alpha=1-min(1,self.fade)
        alpha=alpha*alpha*(3-2*alpha)
        overlay.set_alpha(round(255*alpha))
        game.screen.blit(overlay,(0,0))
        if self.elapsed<.65 and not self.leaving:
            shade=pygame.Surface(game.screen.get_size())
            shade.fill(theme.BG);shade.set_alpha(round(255*(1-self.elapsed/.65)))
            game.screen.blit(shade,(0,0))
