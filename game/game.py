import pygame
from entities.player import Player
from entities.trash import Trash
from game.camera import Camera
from game.settings import TITLE, WINDOW_SIZE, FPS, INTERACTION_RADIUS
from mall.mall import Mall
from ui.hud import HUD


class Game:
    def __init__(self):
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.mall = Mall()
        self.player = Player((240, 380))
        self.camera = Camera(self.mall.size)
        self.hud = HUD()
        self.cash = 0
        self.rent_timer = 0.0
        self.message = "Welcome back to Northgate. Let's bring it to life."
        self.message_timer = 4.0
        self.running = True

    def target(self):
        candidates = [t for t in self.mall.trash if not t.cleaned]
        candidates += [s for s in self.mall.stores if s.available]
        origin = pygame.Vector2(self.player.rect.center)
        nearby = [t for t in candidates if origin.distance_to(t.position) <= INTERACTION_RADIUS]
        return min(nearby, key=lambda t: origin.distance_to(t.position), default=None)

    def notify(self, message):
        self.message, self.message_timer = message, 3.0

    def interact(self):
        target = self.target()
        if isinstance(target, Trash):
            target.cleaned = True
            self.cash += target.reward
            self.notify("Cleaned up! +$10")
        elif target is not None:
            if target.restored:
                self.notify("Pages Bookshop is open. Rent arrives every 5 seconds.")
            elif self.cash < target.cost:
                self.notify(f"You need ${target.cost-self.cash} more to reopen this shop.")
            else:
                self.cash -= target.cost
                target.restored = True
                self.rent_timer = 0.0
                self.notify("Pages Bookshop is open! +$5 rent every 5 seconds.")

    def update(self, dt, direction):
        self.player.move(direction, dt, self.mall.obstacles)
        self.camera.update(self.player.rect.center, self.screen.get_size())
        self.message_timer = max(0, self.message_timer-dt)
        if self.mall.stores[0].restored:
            self.rent_timer += dt
            while self.rent_timer >= 5:
                self.cash += 5
                self.rent_timer -= 5

    def draw(self):
        target = self.target()
        self.mall.draw(self.screen, self.camera, self.hud.font, target)
        self.player.draw(self.screen, self.camera)
        self.hud.draw(self.screen, self.cash, sum(t.cleaned for t in self.mall.trash),
                      len(self.mall.trash), target, self.message if self.message_timer else "",
                      self.mall.stores[0].restored)
        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                dt = min(self.clock.tick(FPS)/1000, 0.05)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_e:
                            self.interact()
                    elif event.type == pygame.VIDEORESIZE:
                        self.screen = pygame.display.set_mode((max(800,event.w), max(600,event.h)), pygame.RESIZABLE)
                keys = pygame.key.get_pressed()
                direction = (int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                             int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]))
                if not pygame.key.get_focused():
                    direction = (0, 0)
                self.update(dt, direction)
                self.draw()
        finally:
            pygame.quit()
