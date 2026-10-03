"""One readable conversation anchored to its speaker, above the world HUD."""
import pygame
from ui import theme


class Speech:
    def __init__(self):
        self.name='';self.text='';self.position=pygame.Vector2();self.timer=0

    def say(self, name, text, position):
        self.name,self.text,self.position=name,text,pygame.Vector2(position)
        self.timer=max(5,min(10,len(text)/14))

    def update(self, dt):self.timer=max(0,self.timer-dt)

    @staticmethod
    def geometry(game, text, position):
        width=min(330,game.screen.get_width()-40)
        lines=theme.wrap(game.hud.small,text,width-28)
        rect=pygame.Rect(0,0,width,43+len(lines)*19)
        head=game.camera.point(position)+pygame.Vector2(0,-62)
        rect.midbottom=(round(head.x),round(head.y-10))
        top=194 if game.tutorial.active else 170
        rect.clamp_ip(pygame.Rect(12,top,game.screen.get_width()-24,game.screen.get_height()-top-70))
        return rect,lines,head

    def draw_bubble(self, game, name, text, position):
        if not game.screen.get_rect().collidepoint(game.camera.point(position)):return
        rect,lines,head=self.geometry(game,text,position)
        theme.frame(game.screen,rect,theme.PANEL)
        # Short pointer stays attached to the box even when it is clamped near a screen edge.
        x=max(rect.left+18,min(rect.right-18,head.x))
        pygame.draw.polygon(game.screen,theme.PANEL,[(x-7,rect.bottom-1),(x+7,rect.bottom-1),(x,rect.bottom+8)])
        game.screen.blit(game.hud.small.render(name,True,theme.ACCENT),(rect.x+14,rect.y+12))
        for i,line in enumerate(lines):
            game.screen.blit(game.hud.small.render(line,True,theme.TEXT),(rect.x+14,rect.y+32+i*19))

    def draw(self, game):
        if self.timer:self.draw_bubble(game,self.name,self.text,self.position)
        else:
            for person in game.shoppers.people:
                if person.visible and person.speech_time:
                    self.draw_bubble(game,person.name,person.speech,person.display_position)
                    break
