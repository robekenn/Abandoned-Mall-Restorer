import pygame
from entities.player import Player
from entities.trash import Trash
from entities.trash_bin import TrashBin
from game.camera import Camera
from game.art import Art
from game.audio import Audio
from game.feedback import Feedback
from systems.litter import LitterSpawner
from systems.upgrades import Upgrades
from systems.economy import money, rent_multiplier
from game.settings import TITLE, WINDOW_SIZE, FPS, INTERACTION_RADIUS
from mall.mall import Mall
from mall.section import EastGallery
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
        self.message = 'Collect litter, sell it at a trash bin, then reopen Northgate Supplies.'
        self.message_timer = 6.0
        self.running = True

    def target(self):
        origin = pygame.Vector2(self.player.rect.center)
        # Selling takes priority at a trash bin when the player is carrying a load.
        trash_bins = [d for d in self.mall.trash_bins if origin.distance_to(d.position) <= INTERACTION_RADIUS]
        if trash_bins and self.upgrades.held:
            return min(trash_bins,key=lambda d: origin.distance_squared_to(d.position))
        candidates = [t for t in self.mall.trash if not t.cleaned and origin.distance_to(t.position) <= self.upgrades.tool[1]]
        candidates += [s for s in self.mall.stores if origin.distance_to(s.position) <= INTERACTION_RADIUS]
        if (not self.mall.east.unlocked and self.mall.east.ready(self.mall)
                and origin.distance_to(self.mall.east.position) <= INTERACTION_RADIUS):
            candidates.append(self.mall.east)
        candidates += trash_bins
        return min(candidates,key=lambda t: origin.distance_squared_to(t.position),default=None)

    def notify(self, message):
        self.message,self.message_timer = message,3.0

    def deny(self, message):
        self.notify(message)
        self.audio.play('blocked')
        return message

    def buy_upgrade(self, key):
        store = self.mall.stores[0] if self.shop_menu.shop == 'north' else self.mall.east.stores[0]
        if not self.shop_menu.open or not store.restored or (self.shop_menu.shop == 'east' and not self.mall.east.unlocked):
            return self.deny('Visit the reopened upgrade shop to buy upgrades.')
        self.cash,message,bought = self.upgrades.purchase(key,self.cash,self.shop_menu.shop)
        self.audio.play('milestone' if bought else 'blocked')
        return message

    def sell_trash(self, trash_bin):
        if not self.upgrades.held:
            self.deny('Your bag is empty. Collect some litter first.')
            return
        count = self.upgrades.held
        payout = count*self.upgrades.unit_value
        self.cash += payout
        self.upgrades.held = 0
        self.feedback.burst(trash_bin.position,f'+${payout}',restored=True)
        self.audio.play('pickup')
        self.notify(f'Sold {count} items for ${payout}. Bag emptied.')

    def collect(self, target):
        if self.upgrades.held >= self.upgrades.capacity:
            self.deny('Bag full. Sell your load at a SELL trash bin.')
            return
        if target.cleaned:
            return
        origin = pygame.Vector2(self.player.rect.center)
        reach,batch = self.upgrades.tool[1:]
        nearby = sorted((t for t in self.mall.trash if not t.cleaned and origin.distance_to(t.position) <= reach),
                        key=lambda t: origin.distance_squared_to(t.position))
        east_sweep_was_done = self.mall.east.initial_cleanup_complete
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
        elif not east_sweep_was_done and self.mall.east.initial_cleanup_complete:
            self.notify('East gallery sweep complete! Reopen Vinyl & Company and keep growing.')
            self.audio.play('milestone')
        else:
            self.notify(f'Collected {collected}. Bag {self.upgrades.held}/{self.upgrades.capacity} / sell at a trash bin.')

    def interact(self):
        if self.shop_menu.open:
            return
        target = self.target()
        if isinstance(target,Trash):
            self.collect(target)
        elif isinstance(target,TrashBin):
            self.sell_trash(target)
        elif isinstance(target,EastGallery):
            if not target.ready(self.mall):
                self.deny('Reopen all five north arcade businesses before opening the east gallery.')
            elif self.cash < target.cost:
                self.deny(f'You need {money(target.cost-self.cash)} more to open the east gallery.')
            elif self.mall.unlock_east():
                self.cash -= target.cost
                self.feedback.burst(target.position,'EAST GALLERY OPEN',restored=True)
                self.audio.play('milestone')
                self.notify('East gallery open! Reopen Eastgate Workshop for $2,000.')
        elif target is not None:
            if not target.available:
                self.deny(target.label)
            elif target.restored:
                if target.upgrade_shop:
                    self.open_upgrade_shop(target)
                else:
                    self.notify(f'{target.name}: +{money(target.rent*self.rent_multiplier)} / 5s '
                                f'({self.rent_multiplier:g}x rent at current cleanliness).')
            elif self.cash < target.cost:
                self.deny(f'You need {money(target.cost-self.cash)} more to reopen {target.name}.')
            else:
                self.cash -= target.cost
                target.restored = True
                self.mall.refresh_businesses()
                self.feedback.burst(target.position,'OPEN',restored=True)
                self.audio.play('milestone')
                if target.upgrade_shop:
                    self.open_upgrade_shop(target)
                    self.notify(f'{target.name} is open. Choose your upgrades.')
                else:
                    next_shop = self.mall.next_store
                    self.notify(f'{target.name} is open.' + (f' Next: {next_shop.name} (${next_shop.cost}).' if next_shop else ' All businesses reopened.'))

        else:
            self.deny('Nothing within reach. Move closer to litter, a bin, a shop or the gallery gate.')

    def open_upgrade_shop(self, store):
        self.shop_menu.shop = store.upgrade_shop
        self.shop_menu.open = True
        self.shop_menu.category = self.shop_menu.selection = 0
        self.shop_menu.notice = ('Bags beyond 20 slots and faster walking.' if store.upgrade_shop == 'east'
                                 else 'Gear and fixtures / each fixture adds $1 base rent per 5s.')

    def update(self, dt, direction):
        viewport = self.screen.get_size()
        framing = 70+max(0,(720-viewport[1])/2)
        self.camera.update((self.player.rect.centerx,self.player.rect.centery-framing),viewport)
        if self.shop_menu.open:
            return
        self.player.move(direction,dt,self.mall.obstacles,self.upgrades.speed_multiplier)
        self.camera.update((self.player.rect.centerx,self.player.rect.centery-framing),viewport)
        self.message_timer = max(0,self.message_timer-dt)
        self.feedback.update(dt)
        self.litter_spawner.update(dt,self.mall,self.player.rect.center)
        opened = [s for s in self.mall.stores if s.restored and s.rent > 0]
        if opened or self.upgrades.fixture_rent:
            self.rent_timer += dt
            while self.rent_timer >= 5:
                multiplier = self.rent_multiplier
                self.cash += self.rent_income
                if multiplier == 1.5:
                    self.audio.play('bonus_rent')
                if self.upgrades.fixture_rent and multiplier:
                    self.feedback.burst(self.player.rect.center,
                                        f'+{money(self.upgrades.fixture_rent*multiplier)} fixtures',restored=True)
                self.rent_timer -= 5
                for store in opened:
                    if multiplier:
                        self.feedback.burst(store.position,f'+{money(store.rent*multiplier)} rent',restored=True)

    @property
    def rent_multiplier(self):
        return rent_multiplier(self.mall.cleanliness)

    @property
    def rent_income(self):
        return (sum(s.rent for s in self.mall.stores if s.restored)+self.upgrades.fixture_rent)*self.rent_multiplier

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
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                        muted = self.audio.toggle()
                        message = 'Music and effects muted.' if muted else 'Music and effects on.'
                        self.notify(message)
                        if self.shop_menu.open:
                            self.shop_menu.notice = message
                    elif self.shop_menu.open:
                        self.shop_menu.handle(event,self)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_e:
                            self.interact()
                keys = pygame.key.get_pressed()
                direction = (int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                             int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]))
                if not pygame.key.get_focused():
                    direction = (0,0)
                self.update(dt,direction)
                self.draw()
        finally:
            pygame.quit()
