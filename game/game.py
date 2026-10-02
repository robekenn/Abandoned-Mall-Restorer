import pygame
from entities.player import Player
from entities.trash import Trash
from game.camera import Camera
from game.art import Art
from game.audio import Audio
from game.feedback import Feedback
from systems.litter import LitterSpawner
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
        self.player = Player((240, 430))
        self.camera = Camera(self.mall.size)
        self.hud = HUD()
        self.art = Art()
        self.audio = Audio()
        self.feedback = Feedback()
        self.litter_spawner = LitterSpawner()
        self.decor = 0
        self.cash = 0
        self.rent_timer = 0.0
        self.message = 'A whole mall ahead. Start with the dust at your feet.'
        self.message_timer = 6.0
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
            first_sweep_was_done = self.mall.initial_cleanup_complete
            if not self.mall.clean_trash(target):
                return
            self.cash += target.reward
            self.player.use_tool(target.kind, target.position)
            self.feedback.burst(target.position, '+$10')
            self.audio.play('sweep' if target.kind == 'dirt' else 'pickup')
            count = self.mall.cleaned_count
            milestones = {1: 'One small patch. A real beginning.',
                          5: 'A place to sit again. Greenery unlocked / Tab.',
                          10: 'Ten small steps. You can reopen Pages now.'}
            if not first_sweep_was_done and self.mall.initial_cleanup_complete:
                self.notify('The first sweep is finished. Water returns; the next shop can follow Pages.')
                self.audio.play('milestone')
            elif not first_sweep_was_done and count in milestones:
                self.notify(milestones[count])
                self.audio.play('milestone')
            else:
                self.notify(f'{self.mall.active_litter_count} cleanup tasks left. Every patch helps.')
        elif target is not None:
            if target.restored:
                self.notify(f'{target.name} is open. +${target.rent} rent every 5 seconds.')
            elif self.cash < target.cost:
                self.notify(f"You need ${target.cost-self.cash} more to reopen this shop.")
            else:
                self.cash -= target.cost
                target.restored = True
                self.mall.refresh_businesses()
                self.feedback.burst(target.position, 'OPEN', restored=True)
                self.audio.play('milestone')
                next_shop = self.mall.next_store
                if next_shop and next_shop.available:
                    self.notify(f'{target.name} is open. Next: {next_shop.name} (${next_shop.cost}).')
                elif next_shop:
                    self.notify(f'{target.name} is open. Finish the first sweep to unlock {next_shop.name}.')
                else:
                    self.notify('All four shops are open. Keep the arcade welcoming.')

    def change_decor(self):
        if self.mall.cleaned_count < 5:
            self.notify("Clean 5 spots to unlock scenery choices.")
            return
        choices = 3 if self.mall.cleaned_count >= 10 else 2
        self.decor = (self.decor + 1) % choices
        self.notify(["Scenery: original mall", "Scenery: greenery and warm lamps", "Scenery: welcoming mosaic courtyard"][self.decor])

    def update(self, dt, direction):
        self.player.move(direction, dt, self.mall.obstacles)
        viewport = self.screen.get_size()
        # Preserve the opening's storefront framing in shorter windows.
        framing = 70 + max(0, (720 - viewport[1]) / 2)
        self.camera.update((self.player.rect.centerx, self.player.rect.centery-framing), viewport)
        self.message_timer = max(0, self.message_timer-dt)
        self.feedback.update(dt)
        self.litter_spawner.update(dt, self.mall, self.player.rect.center)
        opened = [s for s in self.mall.stores if s.restored]
        if opened:
            self.rent_timer += dt
            while self.rent_timer >= 5:
                self.cash += sum(s.rent for s in opened)
                self.rent_timer -= 5
                for store in opened:
                    self.feedback.burst(store.position, f'+${store.rent} rent', restored=True)

    def draw(self):
        target = self.target()
        self.mall.draw(self.screen, self.camera, self.hud.font, self.art, target, self.decor)
        self.player.draw(self.screen, self.camera, self.art)
        self.feedback.draw(self.screen, self.camera, self.hud.font)
        self.hud.draw(self.screen, self.cash, sum(t.cleaned for t in self.mall.trash),
                      len(self.mall.trash), target, self.message if self.message_timer else "",
                      self.mall.stores[0].restored, self.mall.cleaned_count, self.decor,
                      self.mall, self.player.rect.center, self.audio.muted)
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
                        elif event.key == pygame.K_TAB:
                            self.change_decor()
                        elif event.key == pygame.K_m:
                            muted = self.audio.toggle()
                            self.notify('Sound muted.' if muted else 'Sound on.')
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
