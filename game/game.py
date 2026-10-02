import pygame
from entities.player import Player
from entities.trash import Trash
from entities.dumpster import Dumpster
from game.camera import Camera
from game.art import Art
from game.audio import Audio
from game.feedback import Feedback
from systems.litter import LitterSpawner
from systems.upgrades import Upgrades
from game.settings import TITLE, WINDOW_SIZE, FPS, INTERACTION_RADIUS
from mall.mall import Mall
from ui.hud import HUD
from ui.upgrade_shop import UpgradeShop


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
        self.upgrades = Upgrades()
        self.shop_menu = UpgradeShop()
        self.cash = 0
        self.rent_timer = 0.0
        self.message = 'Collect litter, sell it at a dumpster, then reopen Northgate Supplies.'
        self.message_timer = 6.0
        self.running = True

    def target(self):
        origin = pygame.Vector2(self.player.rect.center)
        # Selling takes priority at a dumpster when the player is carrying a load.
        dumpsters = [d for d in self.mall.dumpsters if origin.distance_to(d.position) <= INTERACTION_RADIUS]
        if dumpsters and self.upgrades.held:
            return min(dumpsters,key=lambda d: origin.distance_squared_to(d.position))
        candidates = [t for t in self.mall.trash if not t.cleaned and origin.distance_to(t.position) <= self.upgrades.tool[1]]
        candidates += [s for s in self.mall.stores if s.available and origin.distance_to(s.position) <= INTERACTION_RADIUS]
        candidates += dumpsters
        return min(candidates,key=lambda t: origin.distance_squared_to(t.position),default=None)

    def notify(self, message):
        self.message,self.message_timer = message,3.0

    def buy_upgrade(self, key):
        if not self.shop_menu.open or not self.mall.stores[0].restored:
            return 'Visit the reopened Northgate Supplies shop to buy upgrades.'
        self.cash,message,bought = self.upgrades.purchase(key,self.cash)
        if bought:
            self.audio.play('milestone')
        return message

    def sell_trash(self, dumpster):
        if not self.upgrades.held:
            self.notify('Your bag is empty. Collect some litter first.')
            return
        count = self.upgrades.held
        payout = count*self.upgrades.unit_value
        self.cash += payout
        self.upgrades.held = 0
        self.feedback.burst(dumpster.position,f'+${payout}',restored=True)
        self.audio.play('pickup')
        self.notify(f'Sold {count} items for ${payout}. Bag emptied.')

    def collect(self, target):
        if self.upgrades.held >= self.upgrades.capacity:
            self.notify('Bag full. Sell your load at a SELL dumpster.')
            return
        if target.cleaned:
            return
        origin = pygame.Vector2(self.player.rect.center)
        reach,batch = self.upgrades.tool[1:]
        nearby = sorted((t for t in self.mall.trash if not t.cleaned and origin.distance_to(t.position) <= reach),
                        key=lambda t: origin.distance_squared_to(t.position))
        first_sweep_was_done = self.mall.initial_cleanup_complete
        collected = 0
        for trash in nearby[:min(batch,self.upgrades.capacity-self.upgrades.held)]:
            if self.mall.clean_trash(trash):
                self.upgrades.held += 1
                collected += 1
                self.feedback.burst(trash.position,'+1 item')
        if not collected:
            return
        self.player.use_tool(target.kind,target.position)
        self.audio.play('sweep' if target.kind == 'dirt' else 'pickup')
        if not first_sweep_was_done and self.mall.initial_cleanup_complete:
            self.notify('First sweep complete! Sell your load and grow the arcade.')
            self.audio.play('milestone')
        else:
            self.notify(f'Collected {collected}. Bag {self.upgrades.held}/{self.upgrades.capacity} / sell at a dumpster.')

    def interact(self):
        if self.shop_menu.open:
            return
        target = self.target()
        if isinstance(target,Trash):
            self.collect(target)
        elif isinstance(target,Dumpster):
            self.sell_trash(target)
        elif target is not None:
            if target.restored:
                if target is self.mall.stores[0]:
                    self.shop_menu.open = True
                else:
                    self.notify(f'{target.name}: +${target.rent} rent every 5 seconds.')
            elif self.cash < target.cost:
                self.notify(f'You need ${target.cost-self.cash} more to reopen {target.name}.')
            else:
                self.cash -= target.cost
                target.restored = True
                self.mall.refresh_businesses()
                self.feedback.burst(target.position,'OPEN',restored=True)
                self.audio.play('milestone')
                if target is self.mall.stores[0]:
                    self.shop_menu.open = True
                    self.notify('Northgate Supplies is open. Choose your first upgrades.')
                else:
                    next_shop = self.mall.next_store
                    self.notify(f'{target.name} is open.' + (f' Next: {next_shop.name} (${next_shop.cost}).' if next_shop else ' All businesses reopened.'))

    def update(self, dt, direction):
        viewport = self.screen.get_size()
        framing = 70+max(0,(720-viewport[1])/2)
        self.camera.update((self.player.rect.centerx,self.player.rect.centery-framing),viewport)
        if self.shop_menu.open:
            return
        self.player.move(direction,dt,self.mall.obstacles)
        self.camera.update((self.player.rect.centerx,self.player.rect.centery-framing),viewport)
        self.message_timer = max(0,self.message_timer-dt)
        self.feedback.update(dt)
        self.litter_spawner.update(dt,self.mall,self.player.rect.center)
        opened = [s for s in self.mall.stores if s.restored and s.rent > 0]
        if opened:
            self.rent_timer += dt
            while self.rent_timer >= 5:
                self.cash += sum(s.rent for s in opened)
                self.rent_timer -= 5
                for store in opened:
                    self.feedback.burst(store.position,f'+${store.rent} rent',restored=True)

    def draw(self):
        target = self.target()
        self.mall.draw(self.screen,self.camera,self.hud.font,self.art,target,self.upgrades)
        self.player.draw(self.screen,self.camera,self.art)
        self.feedback.draw(self.screen,self.camera,self.hud.font)
        self.hud.draw(self,target)
        if self.shop_menu.open:
            self.shop_menu.draw(self)
        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                dt = min(self.clock.tick(FPS)/1000,0.05)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.VIDEORESIZE:
                        self.screen = pygame.display.set_mode((max(800,event.w),max(600,event.h)),pygame.RESIZABLE)
                    elif self.shop_menu.open:
                        self.shop_menu.handle(event,self)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_e:
                            self.interact()
                        elif event.key == pygame.K_m:
                            muted = self.audio.toggle()
                            self.notify('Sound muted.' if muted else 'Sound on.')
                keys = pygame.key.get_pressed()
                direction = (int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                             int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]))
                if not pygame.key.get_focused():
                    direction = (0,0)
                self.update(dt,direction)
                self.draw()
        finally:
            pygame.quit()
