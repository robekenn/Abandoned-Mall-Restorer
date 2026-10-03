"""A live, optional first-steps guide; it never grants items or blocks normal play."""
import pygame


class Tutorial:
    STEPS=(
        ('Take a small step','A note beside the keys says: “Begin where you are.” Move with WASD or arrows.'),
        ('Pick up one piece','Press E near litter. Your first bag holds one piece. Small work still counts.'),
        ('Make your first sale','Walk to a SELL bin and press E. The cash can help reopen Northgate.'),
        ('Give yourself room','Reopen Supplies ($10), then buy its 2-slot bag ($5). Keep collecting and selling.'),
        ('Find the next chapter','Press J for the map and owner countdowns. Their requests help bring neighbors back.'),
    )
    def __init__(self):self.active=False;self.step=0;self.journal_seen=False

    def start(self, game):
        self.active=True;self.step=0;self.origin=pygame.Vector2(game.player.rect.center)
        self.collected=game.total_collected;self.sold=game.total_sold;self.journal_seen=False

    def skip(self):self.active=False

    @property
    def goal(self):return f'First steps {self.step+1}/5 · '+self.STEPS[self.step][0],self.STEPS[self.step][1]

    def skip_rect(self, surface):return pygame.Rect(20+min(surface.get_width()-40,480)-81,97,67,22)

    def handle(self, event, game):
        if event.type==pygame.KEYDOWN and event.key==pygame.K_t:self.skip();return True
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.skip_rect(game.screen).collidepoint(event.pos):
            self.skip();return True
        return False

    def update(self, game):
        if not self.active:return
        done=(pygame.Vector2(game.player.rect.center).distance_to(self.origin)>=30,
              game.total_collected>self.collected,game.total_sold>self.sold,
              game.mall.north_stores[0].restored and game.upgrades.capacity_level>=1,self.journal_seen)[self.step]
        if done:
            self.step+=1
            if self.step==len(self.STEPS):self.active=False
