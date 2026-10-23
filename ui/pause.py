"""Escape pauses; exiting always requires a deliberate confirmation."""
import pygame
from ui import theme


class PauseMenu:
    def __init__(self):
        self.open=False;self.confirm=False;self.selection=0;self.notice='';self.save_failed=False
        self.destination='exit'

    def show(self, confirm=False, destination='exit'):
        self.open=True;self.confirm=confirm;self.selection=0;self.notice='';self.save_failed=False
        self.destination=destination

    def geometry(self, surface):
        panel=pygame.Rect(0,0,min(surface.get_width()-64,560),min(surface.get_height()-64,520));panel.center=surface.get_rect().center
        rows=[pygame.Rect(panel.x+28,panel.y+151+i*54,panel.width-56,44) for i in range(5)]
        return panel,rows

    def labels(self, game):
        if not self.confirm:return ('Back to main menu' if game.welcome.open else 'Resume restoring',
                '' if game.welcome.open else 'Save progress', '' if game.welcome.open else 'Main menu','Settings','Exit game')
        if self.destination=='main':return ('Stay in Northgate','Save and return to main menu',
                'Return without saving' if self.save_failed else '', '', '')
        return ('Stay in Northgate','Save and exit' if game.save_started else 'Exit game',
                'Exit without saving' if self.save_failed else '', '', '')

    def activate(self, game, index):
        if not self.confirm:
            if index==0:self.open=False
            elif index==1:
                game.save_checkpoint();self.notice=game.save_store.status if game.save_started else 'This playtest session has no save file.'
            elif index==2 and not game.welcome.open:self.show(True,'main')
            elif index==3:game.settings_menu.open=True
            elif index==4:self.show(True)
        elif index==0:
            self.confirm=False;self.selection=0;self.save_failed=False;self.notice=''
        elif index==1:
            if self.destination=='main':
                if not game.return_to_main_menu():
                    self.save_failed=True;self.notice='Could not save. Stay and try again, or deliberately return without saving.'
                return
            if game.save_started and not game.save_checkpoint():
                self.save_failed=True;self.notice='Your progress could not be saved. Try again, or stay in the game.';return
            game.skip_exit_save=True;game.running=False
        elif index==2 and self.save_failed:
            if self.destination=='main':game.return_to_main_menu(save=False);return
            game.skip_exit_save=True;game.running=False

    def handle(self, event, game):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                if self.confirm:self.activate(game,0)
                else:self.open=False
            elif event.key in (pygame.K_UP,pygame.K_DOWN):
                choices=[i for i,label in enumerate(self.labels(game)) if label]
                current=choices.index(self.selection) if self.selection in choices else 0
                self.selection=choices[(current+(-1 if event.key==pygame.K_UP else 1))%len(choices)]
            elif event.key in (pygame.K_RETURN,pygame.K_SPACE):self.activate(game,self.selection)
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for i,row in enumerate(self.geometry(game.screen)[1]):
                if self.labels(game)[i] and row.collidepoint(event.pos):self.activate(game,i)

    def draw(self, game):
        theme.dim(game.screen);panel,rows=self.geometry(game.screen);theme.frame(game.screen,panel)
        title=('Return to the main menu?' if self.destination=='main' else 'Leave Northgate?') if self.confirm else 'A moment to breathe'
        description=('Save this mall, then choose another or start fresh.' if self.destination=='main' else 'Your little acts of care will be here when you return.') if self.confirm else 'The mall can wait. Take your time.'
        game.screen.blit(game.hud.title.render(title,True,theme.TEXT),(panel.x+28,panel.y+25))
        for i,line in enumerate(theme.wrap(game.hud.font,description,panel.width-56)):
            game.screen.blit(game.hud.font.render(line,True,theme.MUTED),(panel.x+28,panel.y+75+i*24))
        for i,(label,row) in enumerate(zip(self.labels(game),rows)):
            if not label:continue
            theme.frame(game.screen,row,theme.CARD)
            if i==self.selection:pygame.draw.rect(game.screen,theme.ACCENT,row,1,border_radius=9)
            text=game.hud.font.render(label,True,theme.TEXT);game.screen.blit(text,text.get_rect(center=row.center))
        for i,line in enumerate(theme.wrap(game.hud.small,self.notice,panel.width-56)[:2]):
            game.screen.blit(game.hud.small.render(line,True,theme.GOLD),(panel.x+28,panel.bottom-65+i*18))
        game.screen.blit(game.hud.small.render('Up / Down · Enter / click · Esc: return',True,theme.MUTED),(panel.x+28,panel.bottom-26))
