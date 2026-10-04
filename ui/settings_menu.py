"""Mouse-first audio, display and control preferences."""
import pygame
from game.preferences import DEFAULT_KEYS
from ui import theme


class SettingsMenu:
    def __init__(self):self.open=False;self.tab=0;self.page=0;self.capture=None;self.notice='';self.drag=None

    def geometry(self,screen):
        panel=pygame.Rect(0,0,min(screen.get_width()-48,700),520);panel.center=screen.get_rect().center
        tabs=[pygame.Rect(panel.x+24+i*(panel.width-48)//2,panel.y+65,(panel.width-48)//2-8,32) for i in range(2)]
        rows=[pygame.Rect(panel.x+24,panel.y+113+i*45,panel.width-48,36) for i in range(7)]
        close=pygame.Rect(panel.right-120,panel.bottom-48,96,30)
        return panel,tabs,rows,close

    def actions(self):return list(DEFAULT_KEYS)[self.page*6:self.page*6+6]

    def apply(self,game):
        game.audio.set_volumes(game.preferences.music,game.preferences.effects)
        game.welcome.tutorial_enabled=game.preferences.guide
        game.preferences.save();self.notice=game.preferences.status

    def handle(self,event,game):
        p=game.preferences
        if event.type==pygame.MOUSEBUTTONUP:self.drag=None;return
        if event.type==pygame.MOUSEMOTION and self.drag is not None and event.buttons[0]:
            rect=self.geometry(game.screen)[2][self.drag]
            value=max(0,min(1,(event.pos[0]-rect.x-240)/(rect.width-260)))
            setattr(p,('music','effects')[self.drag],round(value,2));self.apply(game);return
        if self.capture and event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:self.capture=None;return
            action=self.capture;self.notice=p.bind(action,event.key)
            if p.keys[action]==event.key:self.capture=None
            return
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,pygame.K_F2):self.open=False
            elif event.key==pygame.K_TAB:self.tab=1-self.tab
            elif event.key in (pygame.K_LEFT,pygame.K_RIGHT) and self.tab==1:self.page=1-self.page
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            _,tabs,rows,close=self.geometry(game.screen)
            if close.collidepoint(event.pos):self.open=False;return
            for i,rect in enumerate(tabs):
                if rect.collidepoint(event.pos):self.tab=i;return
            for i,rect in enumerate(rows):
                if not rect.collidepoint(event.pos):continue
                if self.tab==1:
                    if i<6:self.capture=self.actions()[i];self.notice='Press a new key · Esc cancels'
                    else:self.page=1-self.page
                elif i<2:
                    self.drag=i
                    value=max(0,min(1,(event.pos[0]-rect.x-240)/(rect.width-260)))
                    setattr(p,('music','effects')[i],round(value,2));self.apply(game)
                elif i==2:game.toggle_fullscreen()
                elif i==3:p.guide=not p.guide;self.apply(game)
                elif i==4:p.notifications=not p.notifications;self.apply(game)
                elif i==5:
                    p.music=p.effects=1;p.guide=p.notifications=True;p.keys=DEFAULT_KEYS.copy();self.apply(game)
                return

    def draw(self,game):
        theme.dim(game.screen);panel,tabs,rows,close=self.geometry(game.screen);theme.frame(game.screen,panel)
        # Settings uses literal key names, so the captured name is never translated twice.
        font=pygame.font.Font(None,24);small=pygame.font.Font(None,20)
        game.screen.blit(game.hud.title.render('Settings',True,theme.TEXT),(panel.x+24,panel.y+20))
        for i,label in enumerate(('Sound & display','Controls')):
            theme.frame(game.screen,tabs[i],theme.CARD)
            game.screen.blit(font.render(label,True,theme.ACCENT if i==self.tab else theme.MUTED),(tabs[i].x+12,tabs[i].y+7))
        p=game.preferences
        if self.tab==0:
            labels=[f'Music  {p.music:.0%}',f'Effects  {p.effects:.0%}','Fullscreen: '+('On' if game.fullscreen else 'Off'),
                    'Guide for new games: '+('On' if p.guide else 'Off'),'Owner favor reminders: '+('On' if p.notifications else 'Off'),'Restore default controls & sound']
        else:labels=[a.title()+'   '+p.label(a) for a in self.actions()]+[f'Page {self.page+1}/2 · click for next page']
        for i,label in enumerate(labels):
            rect=rows[i];theme.frame(game.screen,rect,theme.CARD)
            game.screen.blit(font.render(label,True,theme.GOLD if self.tab==1 and i<len(self.actions()) and self.capture==self.actions()[i] else theme.TEXT),(rect.x+12,rect.y+8))
            if self.tab==0 and i<2:
                bar=pygame.Rect(rect.x+240,rect.y+15,rect.width-260,6)
                pygame.draw.rect(game.screen,theme.BORDER,bar)
                pygame.draw.circle(game.screen,theme.ACCENT,(bar.x+round(bar.width*(p.music if i==0 else p.effects)),bar.centery),7)
        theme.frame(game.screen,close,theme.CARD)
        game.screen.blit(small.render('Close · Esc',True,theme.ACCENT),(close.x+10,close.y+7))
        for i,line in enumerate(theme.wrap(small,self.notice or 'Click a setting. Menu navigation keys stay available.',panel.width-150)[:2]):
            game.screen.blit(small.render(line,True,theme.MUTED),(panel.x+24,panel.bottom-52+i*18))
