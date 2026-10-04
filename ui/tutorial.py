"""Skippable character-led explanations, alternating with real practice."""
import pygame
from ui import theme


class Tutorial:
    STEPS=(
        ('Take a small step','I remember these halls full of neighbors. I do not have to fix everything today. First, let me get my bearings.','Move with WASD or the arrow keys.'),
        ('Pick up one piece','There is a little litter nearby. One piece is enough to begin. My bag only holds one for now.','Walk close to litter and press E or click it.'),
        ('Make your first sale','That is a start. The recycling money can help bring the shops back. Look for a bin marked SELL.','Walk to a SELL bin and press E.'),
        ('Give yourself room','Supplies used to lend everyone a hand. I can reopen it for $10, then buy a two-slot bag for $5. I can collect and sell a few more pieces to earn that.','Reopen Supplies, buy its 2-slot bag, then close the shop menu.'),
        ('Find the next chapter','I can take this at my own pace. The journal has the map, stories and optional requests. Owners can wait; there are no deadlines.','Press J to look around the journal, then close it to finish the guide.'),
    )
    def __init__(self):
        self.active=False;self.step=0;self.journal_seen=False;self.explaining=False

    @property
    def paused(self):return self.active and self.explaining

    def start(self, game):
        self.active=True;self.step=0;self.explaining=True
        self.origin=pygame.Vector2(game.player.rect.center)
        self.collected=game.total_collected;self.sold=game.total_sold;self.journal_seen=False

    def skip(self):self.active=False;self.explaining=False

    @property
    def goal(self):return f'First steps {self.step+1}/5 · '+self.STEPS[self.step][0],self.STEPS[self.step][2]

    def geometry(self, surface):
        panel=pygame.Rect(0,0,min(surface.get_width()-48,650),370);panel.center=surface.get_rect().center
        return panel,pygame.Rect(panel.x+24,panel.bottom-66,panel.width-174,42),pygame.Rect(panel.right-130,panel.bottom-66,106,42)

    def skip_rect(self, surface):
        if self.paused:return self.geometry(surface)[2]
        return pygame.Rect(20+min(surface.get_width()-40,480)-81,97,67,22)

    def handle(self, event, game):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_t:self.skip();game.save_checkpoint();return True
            if self.paused:
                if event.key in (pygame.K_RETURN,pygame.K_SPACE):
                    self.explaining=False;game.save_checkpoint()
                elif event.key==pygame.K_ESCAPE:game.pause.show()
                return True
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.skip_rect(game.screen).collidepoint(event.pos):self.skip();game.save_checkpoint();return True
            if self.paused and self.geometry(game.screen)[1].collidepoint(event.pos):
                self.explaining=False;game.save_checkpoint();return True
        return self.paused

    def update(self, game):
        if not self.active or self.explaining:return
        done=(pygame.Vector2(game.player.rect.center).distance_to(self.origin)>=30,
              game.total_collected>self.collected,game.total_sold>self.sold,
              game.mall.north_stores[0].restored and game.upgrades.capacity_level>=1,self.journal_seen)[self.step]
        if done:
            self.step+=1
            if self.step==len(self.STEPS):self.skip()
            else:self.explaining=True
            game.save_checkpoint()

    def draw(self, game):
        theme.dim(game.screen);panel,proceed,skip=self.geometry(game.screen);theme.frame(game.screen,panel)
        game.art.draw(game.screen,'player_down_0',(panel.x+55,panel.y+68),(48,72))
        title,story,task=self.STEPS[self.step]
        game.screen.blit(game.hud.small.render(f'Your thoughts · {self.step+1}/5 · World paused',True,theme.GOLD),(panel.x+95,panel.y+26))
        game.screen.blit(game.hud.title.render(title,True,theme.TEXT),(panel.x+95,panel.y+55))
        y=panel.y+115
        for line in theme.wrap(game.hud.font,story,panel.width-48):
            game.screen.blit(game.hud.font.render(line,True,theme.TEXT),(panel.x+24,y));y+=25
        y+=16
        for line in theme.wrap(game.hud.small,task,panel.width-48):
            game.screen.blit(game.hud.small.render(line,True,theme.ACCENT),(panel.x+24,y));y+=20
        for rect,label in ((proceed,'Enter / Space · Let me try'),(skip,'T · Skip')):
            theme.frame(game.screen,rect,theme.CARD)
            game.screen.blit(game.hud.small.render(label,True,theme.ACCENT),(rect.x+12,rect.y+12))
