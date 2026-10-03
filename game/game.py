import pygame
from entities.player import Player
from entities.trash import Trash
from entities.trash_bin import TrashBin
from game.camera import Camera
from game.art import Art
from game.audio import Audio
from game.feedback import Feedback
from systems.litter import LitterSpawner
from systems.janitors import Janitors
from systems.shoppers import Shoppers, Shopper
from systems.requests import OwnerRequests, RequestSpot, OWNERS
from systems.upgrades import Upgrades
from systems.economy import money, rent_multiplier
from game.settings import TITLE, WINDOW_SIZE, FPS, INTERACTION_RADIUS
from mall.mall import Mall
from mall.section import RegionalGallery
from ui.hud import HUD
from ui.upgrade_shop import UpgradeShop
from ui.owner_menu import OwnerMenu
from ui.journal import Journal
from ui.display_menu import DisplayMenu
from ui.welcome import Welcome
from ui.speech import Speech
from ui.tutorial import Tutorial
from ui.developer import Developer
from ui.story_menu import StoryMenu
from systems.story import Story, StoryPoint
from systems.saves import SaveStore


class Game:
    def __init__(self, *, fullscreen=False, start_screen=False, developer=False, persistence=False, save_dir=None):
        pygame.display.init()
        pygame.font.init()
        self.fullscreen=fullscreen
        self.window_size=WINDOW_SIZE
        self.screen = pygame.display.set_mode((0,0) if fullscreen else WINDOW_SIZE,
                                              pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE)
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
        self.owner_menu = OwnerMenu()
        self.journal = Journal()
        self.display_menu = DisplayMenu()
        self.welcome = Welcome(start_screen)
        self.speech=Speech()
        self.tutorial=Tutorial()
        self.developer=Developer(developer)
        self.total_collected=self.total_sold=0
        self.owner_requests = OwnerRequests()
        self.shoppers = Shoppers()
        self.janitors = Janitors()
        self.story=Story();self.story.setup(self.mall)
        self.story_menu=StoryMenu()
        self.save_store=SaveStore(save_dir,developer,persistence)
        self.save_started=persistence and not start_screen
        self.welcome.has_save=self.save_store.available()
        self.cash = 0
        self.rent_timer = 0.0
        self.message = ''
        self.message_timer = 0.0
        self.running = True

    def target(self):
        origin = pygame.Vector2(self.player.rect.center)
        # Selling takes priority at a trash bin when the player is carrying a load.
        trash_bins = [d for d in self.mall.trash_bins if origin.distance_to(d.position) <= INTERACTION_RADIUS]
        if trash_bins and self.upgrades.held:
            return min(trash_bins,key=lambda d: origin.distance_squared_to(d.position))
        candidates = [t for t in self.mall.trash if not t.cleaned and origin.distance_to(t.position) <= self.upgrades.tool[1]]
        candidates += [s for s in self.mall.stores if origin.distance_to(s.position) <= INTERACTION_RADIUS]
        candidates += [r for r in self.mall.regions if not r.unlocked and r.ready(self.mall)
                       and origin.distance_to(r.position)<=INTERACTION_RADIUS]
        candidates += [p for p in self.shoppers.people if p.visible and origin.distance_to(p.position)<=64]
        candidates += [spot for spot in self.owner_requests.visible_spots if origin.distance_to(spot.position)<=72]
        candidates += [p for p in self.story.visible_points(self.mall) if origin.distance_to(p.position)<=72]
        candidates += trash_bins
        return min(candidates,key=lambda t: origin.distance_squared_to(t.position),default=None)

    def notify(self, message):
        self.message,self.message_timer = message,3.0

    def deny(self, message):
        self.notify(message)
        self.audio.play('blocked')
        return message

    def buy_upgrade(self, key):
        store = next((s for s in self.mall.stores if s.upgrade_shop==self.shop_menu.shop),None)
        if not self.shop_menu.open or store is None or not store.restored:
            return self.deny('Visit the reopened upgrade shop to buy upgrades.')
        self.cash,message,bought = self.upgrades.purchase(key,self.cash,self.shop_menu.shop)
        self.audio.play('milestone' if bought else 'blocked')
        if bought:self.save_checkpoint()
        return '' if bought else message

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
        self.total_sold += count
        self.owner_requests.record_sale(count,trash_bin.position)

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
                self.owner_requests.record_collection(1,trash.position)
                self.upgrades.held += 1
                collected += 1
                self.feedback.burst(trash.position,'+1 item')
        if not collected:
            return
        self.total_collected += collected
        self.player.use_tool(target.kind,target.position)
        self.audio.play('sweep' if target.kind == 'dirt' else 'pickup')
        if not first_sweep_was_done and self.mall.initial_cleanup_complete:
            self.notify('First sweep complete! Sell your load and grow the arcade.')
            self.audio.play('milestone')
        elif not east_sweep_was_done and self.mall.east.initial_cleanup_complete:
            self.notify('East gallery sweep complete! Reopen Vinyl & Company and keep growing.')
            self.audio.play('milestone')

    def interact(self):
        if self.shop_menu.open or self.owner_menu.open or self.journal.open or self.display_menu.open or self.welcome.open or self.developer.open or self.story_menu.open:
            return
        target = self.target()
        if isinstance(target,Trash):
            self.collect(target)
        elif isinstance(target,TrashBin):
            self.sell_trash(target)
        elif isinstance(target,StoryPoint):
            self.story.action(target,self)
        elif isinstance(target,Shopper):
            self.owner_requests.greet(target)
            self.speech.timer=0
            self.shoppers.greet(target,self.story)
            self.audio.play('pickup')
        elif isinstance(target,RequestSpot):
            if target.kind == 'display':
                self.display_menu.visit()
            elif self.owner_requests.interact(target):
                self.feedback.burst(target.position,'SUPPLIES')
                self.audio.play('pickup')
        elif isinstance(target,RegionalGallery):
            if not target.ready(self.mall):self.deny('Finish restoring the previous area before opening '+target.name+'.')
            elif self.cash<target.cost:self.deny(f'You need {money(target.cost-self.cash)} more to open {target.name}.')
            elif self.mall.unlock_section(target):
                self.cash -= target.cost
                self.feedback.burst(target.position,'AREA OPEN',restored=True)
                self.audio.play('milestone')
                self.notify(f'{target.name} is open. Begin with {target.stores[0].name}.')
                self.save_checkpoint()
        elif target is not None:
            if not target.available:
                self.deny(target.label)
            elif target.restored:
                if target.upgrade_shop:
                    self.open_upgrade_shop(target)
                else:
                    self.owner_menu.visit(target)
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
                    self.notify(f'{target.name} is open.' + (f' Next: {next_shop.name} (${next_shop.cost}).' if next_shop else ' All businesses reopened.')+f' E here to meet {OWNERS[target.name]}.')

                self.save_checkpoint()

        else:
            self.deny('Nothing within reach. Move closer to litter, a bin, a shop or the gallery gate.')

    def claim_request(self, store):
        result = self.owner_requests.claim(store)
        if result is None:
            self.deny('Finish the request and return to its owner first.')
            return False
        improvement,bonus,reward = result
        self.cash += reward
        self.feedback.burst(store.position,f'+{money(reward)}',restored=True)
        self.audio.play('milestone')
        rent=f' Our rent grows by {money(bonus)}.' if bonus else ''
        self.save_checkpoint()
        self.say_owner(store,f'Thank you. Here is {money(reward)} for your help.'+rent+' Northgate feels a little more like home.')
        return True

    def say_owner(self, store, text):
        for person in self.shoppers.people:person.speech_time=0
        self.speech.say(OWNERS[store.name],text,store.position)

    def open_upgrade_shop(self, store):
        self.shop_menu.shop = store.upgrade_shop
        self.shop_menu.open = True
        self.shop_menu.category = self.shop_menu.selection = 0
        self.shop_menu.notice = ''

    def save_checkpoint(self):
        return self.save_store.save(self) if self.save_started else False

    def continue_game(self):
        if self.save_store.load(self):
            self.welcome.continuing=True;self.welcome.start();return True
        self.welcome.status=self.save_store.status
        return False

    def toggle_fullscreen(self):
        self.fullscreen=not self.fullscreen
        self.screen=pygame.display.set_mode((0,0) if self.fullscreen else self.window_size,
                                            pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE)

    def frame_camera(self, viewport):
        area=next((a for a in self.mall.playable_areas if a.collidepoint(self.player.rect.center)),self.mall.opening_area)
        toward_bottom=max(0,min(1,(self.player.rect.centery-area.top-area.height*.45)/(area.height*.25)))
        framing=(70+max(0,(720-viewport[1])/2))*(1-toward_bottom)-38*toward_bottom
        self.camera.update((self.player.rect.centerx,self.player.rect.centery-framing),viewport)

    def update(self, dt, direction, interaction_held=False):
        viewport = self.screen.get_size()
        self.frame_camera(viewport)
        if self.welcome.open:
            self.welcome.update(dt)
            if not self.welcome.open:
                self.save_started=self.save_store.enabled
                if self.welcome.tutorial_enabled and not self.welcome.continuing:self.tutorial.start(self)
                if not self.welcome.continuing:self.save_checkpoint()
            return
        if self.shop_menu.open or self.owner_menu.open or self.journal.open or self.display_menu.open or self.developer.open or self.story_menu.open:
            return
        self.player.move(direction,dt,self.mall.obstacles,self.upgrades.speed_multiplier)
        self.frame_camera(viewport)
        self.message_timer = max(0,self.message_timer-dt)
        self.speech.update(dt)
        self.tutorial.update(self)
        self.feedback.update(dt)
        self.story.update(dt,self.mall)
        self.litter_spawner.update(dt,self.mall,self.player.rect.center,self.owner_requests)
        self.janitors.update(dt,self)
        ready = self.owner_requests.update(dt,self.mall)
        if ready and not self.owner_requests.store:
            self.notify(f'{OWNERS[ready[0].name]} has a new request. Visit {ready[0].name}.')
        self.shoppers.update(dt,self.mall,self.upgrades,self.owner_requests.store)
        completed = self.owner_requests.work(dt,self.player.rect.center,interaction_held,not any(direction))
        for spot in self.owner_requests.visible_spots:
            if spot.progress:
                self.player.use_tool('setup',spot.position+pygame.Vector2(48,-16))
        for spot in completed:
            self.player.use_tool('setup',spot.position+pygame.Vector2(48,-16))
            self.feedback.burst(spot.position,'DONE',restored=True)
            self.audio.play('pickup')
        opened = [s for s in self.mall.stores if s.restored and s.rent > 0]
        if opened or self.upgrades.fixture_rent:
            self.rent_timer += dt
            while self.rent_timer >= 5:
                multiplier = self.rent_multiplier
                self.cash += self.rent_income
                if multiplier == 1.5:
                    self.audio.play('bonus_rent')
                if multiplier:
                    self.feedback.burst(self.player.rect.center,f'+{money(self.rent_income)} rent',restored=True)
                self.rent_timer -= 5
        self.save_store.elapsed+=dt
        if self.save_started and self.save_store.elapsed>=30:self.save_checkpoint()

    @property
    def rent_multiplier(self):
        return rent_multiplier(self.mall.cleanliness)

    @property
    def rent_income(self):
        return (sum(s.rent for s in self.mall.stores if s.restored)+self.upgrades.fixture_rent)*self.rent_multiplier

    def draw(self):
        target = self.target()
        self.mall.draw(self.screen,self.camera,self.hud.font,self.art,target,self.upgrades)
        self.story.draw(self)
        for spot in self.owner_requests.scene_spots:
            spot.draw(self.screen,self.camera,self.art,self.hud.small,target is spot)
        # Tall furniture and people share depth, so walking behind a prop looks natural.
        layers=[(depth,'furniture',(name,center,size)) for depth,name,center,size in self.mall.furniture(self.upgrades)]
        layers += [(p.position.y,'shopper',p) for p in self.shoppers.people if p.visible]
        layers += [(p.position.y,'janitor',p) for p in self.janitors.people.values()]
        layers.append((self.player.rect.centery,'player',self.player))
        for _,kind,item in sorted(layers,key=lambda entry:entry[0]):
            if kind == 'furniture':
                name,center,size=item
                self.art.draw(self.screen,name,self.camera.point(center),size)
            elif kind=='janitor':
                item.draw(self)
            elif kind == 'shopper':
                item.draw(self.screen,self.camera,self.art,self.hud.small,target is item)
            else:
                item.draw(self.screen,self.camera,self.art)
        if self.welcome.open:
            if self.welcome.leaving:
                hud_layer=pygame.Surface(self.screen.get_size(),pygame.SRCALPHA)
                self.hud.draw(self,target,hud_layer)
                fade=self.welcome.fade
                hud_layer.set_alpha(round(255*fade*fade*(3-2*fade)))
                self.screen.blit(hud_layer,(0,0))
            self.welcome.draw(self)
        else:
            self.feedback.draw(self.screen,self.camera,self.hud.font)
            self.hud.draw(self,target)
            self.speech.draw(self)
            if self.developer.enabled:
                badge=self.hud.small.render('DEV · F3',True,(230,194,124))
                self.screen.blit(badge,(self.screen.get_width()-badge.get_width()-20,84))
            if self.story_menu.open:
                self.story_menu.draw(self)
            elif self.developer.open:
                self.developer.draw(self)
            elif self.shop_menu.open:
                self.shop_menu.draw(self)
            elif self.owner_menu.open:
                self.owner_menu.draw(self)
            elif self.journal.open:
                self.journal.draw(self)
            elif self.display_menu.open:
                self.display_menu.draw(self)
        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                dt = min(self.clock.tick(FPS)/1000,0.05)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                        self.window_size=(max(800,event.w),max(600,event.h))
                        self.screen = pygame.display.set_mode(self.window_size,pygame.RESIZABLE)
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                        muted = self.audio.toggle()
                        message = 'Music and effects muted.' if muted else 'Music and effects on.'
                        self.notify(message)
                        if self.shop_menu.open:
                            self.shop_menu.notice = message
                    elif self.welcome.open:
                        self.welcome.handle(event,self)
                    elif event.type==pygame.KEYDOWN and event.key==pygame.K_F5:
                        self.save_checkpoint()
                    elif self.story_menu.open:
                        self.story_menu.handle(event,self)
                    elif self.developer.enabled and event.type==pygame.KEYDOWN and event.key==pygame.K_F3:
                        if not (self.shop_menu.open or self.owner_menu.open or self.journal.open or self.display_menu.open):
                            self.developer.open=not self.developer.open
                    elif self.developer.open:
                        self.developer.handle(event,self)
                    elif self.display_menu.open:
                        self.display_menu.handle(event,self)
                    elif self.shop_menu.open:
                        self.shop_menu.handle(event,self)
                    elif self.owner_menu.open:
                        self.owner_menu.handle(event,self)
                    elif self.journal.open:
                        self.journal.handle(event,self)
                    elif self.tutorial.active and self.tutorial.handle(event,self):
                        pass
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_h:
                            self.tutorial.start(self)
                        elif event.key == pygame.K_j:
                            self.tutorial.journal_seen=True
                            self.journal.open = True
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_e:
                            self.interact()
                keys = pygame.key.get_pressed()
                direction = (int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                             int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]))
                if not pygame.key.get_focused():
                    direction = (0,0)
                self.update(dt,direction,keys[pygame.K_e] and pygame.key.get_focused())
                self.draw()
        finally:
            self.save_checkpoint()
            pygame.quit()
