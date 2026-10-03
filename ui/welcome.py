"""A quiet introduction that dissolves into the existing mall scene."""
import pygame
from ui import theme


class Welcome:
    FADE_SECONDS=.9
    STORY=(
        'Northgate used to be the heart of this neighborhood. Now its shops are shuttered, '
        'its fountain is silent, and most people have stopped coming.',
        'You have been handed the keys and one last chance to bring it back.',
        'Start with one piece of litter. Reopen one shop. Small acts of care can give '
        'a whole community somewhere to belong again.',
    )

    def __init__(self, open=True):
        self.open=open
        self.elapsed=0.0
        self.leaving=False
        self.fade=0.0
        self.heading=pygame.font.Font(None,58)

    def geometry(self, surface):
        panel=pygame.Rect(0,0,min(surface.get_width()-64,680),min(surface.get_height()-64,510))
        panel.center=surface.get_rect().center
        start=pygame.Rect(panel.x+30,panel.bottom-103,panel.width-156,46)
        quit=pygame.Rect(start.right+12,start.y,84,46)
        return panel,start,quit

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
            if event.key in (pygame.K_RETURN,pygame.K_SPACE):self.start()
            elif event.key==pygame.K_ESCAPE:game.running=False
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            _,start,quit=self.geometry(game.screen)
            if start.collidepoint(event.pos):self.start()
            elif quit.collidepoint(event.pos):game.running=False

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
        hover=start.collidepoint(pygame.mouse.get_pos())
        theme.frame(overlay,start,(53,88,79) if hover else theme.CARD)
        text=game.hud.font.render('Start restoring',True,theme.ACCENT)
        overlay.blit(text,text.get_rect(center=start.center))
        theme.frame(overlay,quit,theme.PANEL)
        text=game.hud.small.render('Quit',True,theme.MUTED)
        overlay.blit(text,text.get_rect(center=quit.center))
        sound='Sound off' if game.audio.muted else 'Sound on'
        caption=f'Enter: start     F11: fullscreen / window     M: {sound}'
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
