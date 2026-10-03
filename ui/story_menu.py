"""Short, readable story encounters; the journal holds the detailed checklist."""
import pygame
from ui import theme
from systems.story import CHAPTERS


class StoryMenu:
    def __init__(self):self.open=False;self.chapter=0;self.text='';self.action=None

    def visit(self, chapter, text, action):self.open=True;self.chapter=chapter;self.text=text;self.action=action

    def geometry(self, surface):
        panel=pygame.Rect(0,0,min(720,surface.get_width()-48),420);panel.center=surface.get_rect().center
        button=pygame.Rect(panel.x+24,panel.bottom-82,panel.width-48,42)
        return panel,button

    def handle(self, event, game):
        _,button=self.geometry(game.screen)
        if event.type==pygame.KEYDOWN and event.key in (pygame.K_ESCAPE,pygame.K_e):self.open=False;return
        if (event.type==pygame.KEYDOWN and event.key in (pygame.K_RETURN,pygame.K_SPACE)) or (
                event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and button.collidepoint(event.pos)):
            action=self.action;self.open=False
            if action:game.story.confirm(game,self.chapter,action)
            game.save_checkpoint()

    def draw(self, game):
        theme.dim(game.screen);panel,button=self.geometry(game.screen);theme.frame(game.screen,panel)
        chapter=CHAPTERS[self.chapter]
        game.screen.blit(game.hud.small.render(chapter.speaker+' · NORTHGATE REMEMBERS',True,theme.GOLD),(panel.x+24,panel.y+24))
        game.screen.blit(game.hud.title.render(chapter.title,True,theme.TEXT),(panel.x+24,panel.y+55))
        for i,line in enumerate(theme.wrap(game.hud.font,self.text,panel.width-48)):
            game.screen.blit(game.hud.font.render(line,True,theme.TEXT),(panel.x+24,panel.y+107+i*26))
        caption='J → Story: chapter goals and recovered memories'
        game.screen.blit(game.hud.small.render(caption,True,theme.MUTED),(panel.x+24,panel.bottom-112))
        labels={'begin':'Remember Northgate','claim':'Bring the neighbors together','festival':'Begin the lantern walk','gather':'Invite the neighbors again'}
        theme.frame(game.screen,button,theme.CARD)
        text=game.hud.font.render(labels.get(self.action,'Back to the mall'),True,theme.ACCENT)
        game.screen.blit(text,text.get_rect(center=button.center))
        game.screen.blit(game.hud.small.render('Enter / click: continue   Esc / E: return',True,theme.MUTED),(panel.x+24,panel.bottom-26))
