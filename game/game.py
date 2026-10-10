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
from systems.courtyard_visitors import CourtyardTravel
from systems.requests import OwnerRequests, RequestSpot, OWNERS
from systems.upgrades import Upgrades
from systems.economy import money, rent_multiplier
from game.settings import TITLE, WINDOW_SIZE, FPS, INTERACTION_RADIUS
from mall.mall import Mall
from mall.courtyard import Courtyard, SceneDoor
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
from systems.save_slots import SaveSlots
from game.storage import save_directory
from game.preferences import Preferences, HintFont
from ui.settings_menu import SettingsMenu
from systems.mall_life import MallLife, EventSpot, EventTask
from ui.pause import PauseMenu
from ui.community_menu import CommunityMenu
from ui.cooking_menu import CookingMenu


class Game:
    def __init__(self, *, fullscreen=False, start_screen=False, developer=False, persistence=False, save_dir=None):
        self.preferences=Preferences(save_dir or save_directory(),persistence,fullscreen)
        self.settings_menu=SettingsMenu()
        fullscreen=self.preferences.fullscreen
        pygame.display.init()
        pygame.font.init()
        self.fullscreen=fullscreen
        self.window_size=WINDOW_SIZE
        self.screen = pygame.display.set_mode((0,0) if fullscreen else WINDOW_SIZE,
                                              pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        self.hud.font=HintFont(self.hud.font,self.preferences)
        self.hud.small=HintFont(self.hud.small,self.preferences)
        self.art = Art()
        from game.patio_art import install
        install(self.art)
        self.audio = Audio()
        self.audio.set_volumes(self.preferences.music,self.preferences.effects)
        self.pause=PauseMenu()
        self.save_slots=SaveSlots(save_dir,developer,persistence)
        self.save_store=self.save_slots.store()
        self.save_started=persistence and not start_screen
        self.welcome=Welcome(start_screen)
        self.welcome.tutorial_enabled=self.preferences.guide
        self.reset_playthrough(developer)
        self.welcome.refresh(self)
        self.running = True

    def reset_playthrough(self, developer=False):
        """Create fresh session objects while retaining display, art, audio and settings."""
        self.mall=Mall();self.player=Player((240,430));self.camera=Camera(self.mall.size)
        self.courtyard=Courtyard();self.visitor_travel=CourtyardTravel();self.scene='mall'
        self.main_position=None;self.main_camera=self.camera
        self.feedback=Feedback();self.litter_spawner=LitterSpawner();self.upgrades=Upgrades()
        self.shop_menu=UpgradeShop();self.owner_menu=OwnerMenu();self.cooking_menu=CookingMenu()
        self.journal=Journal();self.display_menu=DisplayMenu();self.speech=Speech();self.tutorial=Tutorial()
        self.developer=Developer(developer);self.owner_requests=OwnerRequests();self.shoppers=Shoppers()
        self.janitors=Janitors();self.story=Story();self.story.setup(self.mall);self.story_menu=StoryMenu()
        self.life=MallLife();self.community_menu=CommunityMenu();self.skip_exit_save=False
        self.total_collected=self.total_sold=0;self.cash=0;self.rent_timer=0;self.play_seconds=0
        self.message='';self.message_timer=0;self.request_notice='';self.request_notice_timer=0

    def start_new_game(self, name='My Northgate'):
        if not self.welcome.open or self.welcome.leaving:return False
        try:store=self.save_slots.allocate(name)
        except (OSError,ValueError):
            self.welcome.status='Could not create the save. Check that your save folder is accessible.';return False
        self.reset_playthrough(self.developer.enabled)
        if store.enabled and not store.save(self):
            self.save_started=False;self.welcome.status='Could not create the save. Your other malls are safe. Please try again.'
            return False
        self.save_store=store;self.save_started=store.enabled
        self.welcome.continuing=False;self.welcome.start()
        return True

    def return_to_main_menu(self, *, save=True):
        if save and self.save_started and not self.save_checkpoint():return False
        for menu in self.modal_menus:menu.open=False
        self.speech.timer=0;self.feedback.popups.clear();self.feedback.particles.clear()
        self.save_started=False
        self.welcome=Welcome(True);self.welcome.tutorial_enabled=self.preferences.guide
        self.welcome.refresh(self,selected=self.save_store.slot)
        return True

    def delete_save(self, identifier):
        if not self.welcome.open or self.welcome.leaving or self.save_started:return False
        result=self.save_slots.delete(identifier)
        self.welcome.status=self.save_slots.status
        self.welcome.refresh(self)
        return result

    def target(self):
        if self.scene=='courtyard':return self.courtyard.target(self)
        origin = pygame.Vector2(self.player.rect.center)
        door=self.courtyard.door(self.mall)
        if not self.courtyard.unlocked and self.mall.commons.unlocked and origin.distance_to(door.position)<=110:
            door.title='Open Courtyard passage ($50,000)' if self.courtyard.ready(self.mall) else 'Courtyard needs the Commons sweep and six reopened businesses'
            return door
        # Selling takes priority at a trash bin when the player is carrying a load.
        trash_bins = [d for d in self.mall.trash_bins if origin.distance_to(d.position) <= INTERACTION_RADIUS]
        if trash_bins and self.upgrades.held:
            return min(trash_bins,key=lambda d: origin.distance_squared_to(d.position))
        story_targets=[p for p in self.story.visible_points(self.mall)+self.story.visible_neighbors(self.mall)
                       if p.memory>=0 and origin.distance_to(p.position)<=(64 if p.source=='neighbor' else 32)]
        if story_targets:return min(story_targets,key=lambda p:origin.distance_squared_to(p.position))
        event_tasks=[t for t in self.life.visible_tasks if origin.distance_to(t.position)<=32]
        if event_tasks:return min(event_tasks,key=lambda t:origin.distance_squared_to(t.position))
        candidates = [t for t in self.mall.trash if not t.cleaned and origin.distance_to(t.position) <= self.upgrades.tool[1]]
        candidates += [s for s in self.mall.stores if origin.distance_to(s.position) <= INTERACTION_RADIUS]
        candidates += [r for r in self.mall.regions if not r.unlocked and r.ready(self.mall)
                       and origin.distance_to(r.position)<=INTERACTION_RADIUS]
        shoppers=[p for p in self.shoppers.people if p.visible and origin.distance_to(p.position)<=64]
        candidates += [spot for spot in self.owner_requests.visible_spots if origin.distance_to(spot.position)<=72]
        candidates += [p for p in self.story.visible_neighbors(self.mall) if origin.distance_to(p.position)<=64]
        candidates += [p for p in self.story.visible_points(self.mall) if origin.distance_to(p.position)<=72]
        if self.life.spot and origin.distance_to(self.life.spot.position)<=72:candidates.append(self.life.spot)
        candidates += [t for t in self.life.visible_tasks if origin.distance_to(t.position)<=64]
        candidates += trash_bins
        if not candidates:candidates=shoppers
        # Old checkpoints can contain a gathering at a story board's exact node.
        # Give the active gathering the tie so it remains possible to join it.
        return min(candidates,key=lambda t:(origin.distance_squared_to(t.position),0 if t is self.life.spot else 1),default=None)

    def notify(self, message):
        self.message,self.message_timer = message,3.0

    @property
    def modal_menus(self):
        """Register new menus here so input and simulation pause consistently."""
        return (self.pause, self.settings_menu, self.shop_menu, self.owner_menu,
                self.journal, self.display_menu, self.developer, self.story_menu,
                self.community_menu, self.cooking_menu)

    @property
    def world_paused(self):
        return self.welcome.open or self.tutorial.paused or any(menu.open for menu in self.modal_menus)

    def deny(self, message):
        self.notify(message)
        self.audio.play('blocked')
        return message

    def buy_upgrade(self, key):
        stores=self.courtyard.world.stores if self.scene=='courtyard' else self.mall.stores
        store = next((s for s in stores if s.upgrade_shop==self.shop_menu.shop),None)
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

    def pickup_at(self, screen_position):
        if self.world_paused:
            return
        if self.scene=='courtyard':self.courtyard.pickup_at(self,screen_position);return
        viewport=pygame.Rect(0,190 if self.tutorial.active else 170,self.screen.get_width(),self.screen.get_height()-(248 if self.tutorial.active else 228))
        if not viewport.collidepoint(screen_position):return
        point=pygame.Vector2(screen_position)+self.camera.offset
        candidates=[t for t in self.mall.trash if not t.cleaned and t.position.distance_squared_to(point)<=24**2]
        if not candidates:return
        target=min(candidates,key=lambda t:t.position.distance_squared_to(point))
        if target.position.distance_squared_to(self.player.rect.center)>self.upgrades.tool[1]**2:
            self.deny('Move closer to collect this litter.');return
        self.collect(target)

    def collect(self, target):
        if self.upgrades.held >= self.upgrades.capacity:
            self.deny('Bag full. Sell your load at a SELL trash bin.')
            return
        if target.cleaned:
            return
        origin = pygame.Vector2(self.player.rect.center)
        reach,batch = self.upgrades.tool[1:]
        nearby = sorted((t for t in self.mall.trash if not t.cleaned and origin.distance_to(t.position) <= reach),
                        key=lambda t:(t is not target,origin.distance_squared_to(t.position)))
        east_sweep_was_done = self.mall.east.initial_cleanup_complete
        first_sweep_was_done = self.mall.initial_cleanup_complete
        collected = 0
        for trash in nearby[:min(batch,self.upgrades.capacity-self.upgrades.held)]:
            if self.mall.clean_trash(trash):
                self.owner_requests.record_collection(1,trash.position)
                self.upgrades.held += 1
                collected += 1
                self.feedback.burst(trash.position,'+1 item',kind=trash.kind)
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
        if self.world_paused:
            return
        if self.scene=='courtyard':self.courtyard.interact(self);return
        target = self.target()
        if isinstance(target,SceneDoor):
            self.enter_courtyard()
        elif isinstance(target,Trash):
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
        elif isinstance(target,EventSpot):
            self.community_menu.open=True;self.community_menu.selection=0
        elif isinstance(target,EventTask):
            self.life.touch(self,target)
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
        self.life.show_owner(store)
        self.speech.say(OWNERS[store.name],text,self.life.owner_position(store))

    def open_upgrade_shop(self, store):
        self.shop_menu.shop = store.upgrade_shop
        self.shop_menu.open = True
        self.shop_menu.category = self.shop_menu.selection = 0
        self.shop_menu.notice = ''

    def enter_courtyard(self,*,save=True,position=None):
        if self.scene=='courtyard':return False
        if not self.courtyard.ready(self.mall):
            self.deny('Finish the Commons sweep and reopen six businesses to unlock the Courtyard.');return False
        if not self.courtyard.unlocked:
            if self.cash<self.courtyard.COST:self.deny(f'The courtyard passage needs {money(self.courtyard.COST)} to restore.');return False
            self.cash-=self.courtyard.COST;self.courtyard.unlocked=True
        self.courtyard.ensure_world();self.courtyard.open_passage(self.mall);self.main_position=pygame.Vector2(self.player.rect.center)
        self.scene='courtyard';self.camera=self.courtyard.camera;self.player.rect.center=position or self.courtyard.world.entrance
        self.feedback.popups.clear();self.feedback.particles.clear();self.speech.timer=0;self.frame_camera(self.screen.get_size())
        if save:self.save_checkpoint()
        return True

    def update_courtyard_visitors(self,dt):
        if self.courtyard.unlocked:
            self.courtyard.kitchen_requests.update(dt,self)
            self.courtyard.shoppers.update(dt,self.courtyard.world,self.upgrades)
            self.visitor_travel.update(dt,self)

    def update_shared_worlds(self, dt):
        """Both scenes keep visitors, litter and hired cleaners active."""
        self.shoppers.update(dt, self.mall, self.upgrades, self.owner_requests.store)
        self.update_courtyard_visitors(dt)
        self.update_litter(dt)
        self.update_janitors(dt)

    def update_income_and_autosave(self, dt):
        """Keep the same rent phase and save cadence when crossing scenes."""
        has_income = (any(s.restored and s.rent > 0 for s in self.mall.stores)
                      or self.upgrades.fixture_rent or self.courtyard.unlocked)
        if has_income:
            self.rent_timer += dt
            while self.rent_timer >= 5:
                income = self.rent_income
                self.cash += income
                self.rent_timer -= 5
                if income:
                    self.feedback.burst(self.player.rect.center, f'+{money(income)} rent', restored=True)
                    world = self.courtyard.world if self.scene == 'courtyard' else self.mall
                    if rent_multiplier(world.cleanliness) == 1.5:
                        self.audio.play('bonus_rent')
        self.save_store.elapsed += dt
        if self.save_started and self.save_store.elapsed >= 30:
            self.save_checkpoint()

    def update_janitors(self,dt):
        self.janitors.update(dt,self)
        if self.courtyard.unlocked:
            self.courtyard.janitors.update(dt,self,self.courtyard.world)

    def update_litter(self,dt):
        position=self.player.rect.center if self.scene=='mall' else None
        self.litter_spawner.update(dt,self.mall,position,self.owner_requests,traffic=self.shoppers.traffic)
        if self.courtyard.unlocked:
            position=self.player.rect.center if self.scene=='courtyard' else None
            self.courtyard.spawner.update(dt,self.courtyard.world,position,traffic=self.courtyard.shoppers.traffic)

    @property
    def cleanliness(self):
        worlds=[self.mall]
        if self.courtyard.unlocked:worlds.append(self.courtyard.world)
        tiles=sum(len(world.floor_tiles) for world in worlds)
        dirty=sum(len(world.dirty_tiles) for world in worlds)
        return 1-dirty/tiles if tiles else 1

    def leave_courtyard(self):
        if self.scene!='courtyard':return
        self.scene='mall';self.camera=self.main_camera
        self.player.rect.center=self.courtyard.door(self.mall).position
        self.main_position=None;self.feedback.popups.clear();self.feedback.particles.clear();self.speech.timer=0
        self.frame_camera(self.screen.get_size());self.save_checkpoint()

    def save_checkpoint(self):
        return self.save_store.save(self) if self.save_started else False

    def continue_game(self, identifier=None):
        if not self.welcome.open or self.welcome.leaving:return False
        store=self.save_slots.store(identifier)
        record=next((r for r in self.welcome.saves if r.identifier==identifier),None)
        if record:store.name=record.name
        if store.load(self):
            self.save_store=store
            for menu in self.modal_menus:menu.open=False
            self.speech.timer=0;self.feedback.popups.clear();self.feedback.particles.clear()
            self.message_timer=self.request_notice_timer=0;self.skip_exit_save=False
            self.welcome.continuing=True;self.welcome.start();return True
        self.welcome.status=store.status
        return False

    def toggle_fullscreen(self):
        self.fullscreen=not self.fullscreen
        self.preferences.fullscreen=self.fullscreen;self.preferences.save()
        self.screen=pygame.display.set_mode((0,0) if self.fullscreen else self.window_size,
                                            pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE)

    def frame_camera(self, viewport):
        if self.scene=='courtyard':
            bias=-50+120*max(0,min(1,(self.player.rect.centery-850)/180))
            self.courtyard.camera.update((self.player.rect.centerx,self.player.rect.centery+bias),viewport);return
        # Blend framing within each vertical row, including the corridor between
        # them. Choosing a new court must not jump the camera by a hundred pixels.
        y=self.player.rect.centery
        north=self.mall.opening_area; south=self.mall.garden.area
        def bias(area):
            fraction=max(0,min(1,(y-area.top-area.height*.45)/(area.height*.25)))
            return (70+max(0,(720-viewport[1])/2))*(1-fraction)-38*fraction
        if y<=north.bottom-192:framing=bias(north)
        elif y>=south.top+192:framing=bias(south)
        else:
            blend=(y-(north.bottom-192))/(south.top+192-(north.bottom-192))
            blend=blend*blend*(3-2*blend)
            framing=-38+(108+max(0,(720-viewport[1])/2))*blend
        self.camera.update((self.player.rect.centerx,y-framing),viewport)

    def update(self, dt, direction, interaction_held=False):
        viewport = self.screen.get_size()
        self.frame_camera(viewport)
        if self.settings_menu.open or self.pause.open:return
        if self.welcome.open:
            self.welcome.update(dt)
            if not self.welcome.open:
                self.save_started=self.save_store.enabled
                if self.welcome.tutorial_enabled and not self.welcome.continuing:self.tutorial.start(self)
                if not self.welcome.continuing:self.save_checkpoint()
            return
        if any(menu.open for menu in self.modal_menus if menu is not self.cooking_menu):
            return
        if self.tutorial.paused:return
        if self.cooking_menu.open:self.cooking_menu.update(dt,self);return
        self.play_seconds+=dt
        if self.scene=='courtyard':self.courtyard.update(self,dt,direction);return
        self.player.move(direction,dt,self.mall.obstacles,self.upgrades.speed_multiplier)
        if self.courtyard.crossing(self,direction):return
        self.frame_camera(viewport)
        self.message_timer = max(0,self.message_timer-dt)
        self.request_notice_timer=max(0,self.request_notice_timer-dt)
        self.speech.update(dt)
        self.tutorial.update(self)
        if self.tutorial.paused:return
        self.feedback.update(dt)
        self.story.update(dt,self.mall)
        self.life.update(dt,self)
        ready = self.owner_requests.update(dt,self.mall)
        if ready and not self.owner_requests.store:
            self.request_notice=(ready[0].name+' has a favor' if len(ready)==1 else f'{len(ready)} owners have new favors')
            self.request_notice_timer=8
        self.update_shared_worlds(dt)
        self.life.work(dt,self,interaction_held,not any(direction))
        completed = self.owner_requests.work(dt,self.player.rect.center,interaction_held,not any(direction))
        for spot in self.owner_requests.visible_spots:
            if spot.progress:
                self.player.use_tool('setup',spot.position+pygame.Vector2(48,-16))
        for spot in completed:
            self.player.use_tool('setup',spot.position+pygame.Vector2(48,-16))
            self.feedback.burst(spot.position,'DONE',restored=True)
            self.audio.play('pickup')
        self.update_income_and_autosave(dt)

    @property
    def rent_multiplier(self):
        return rent_multiplier(self.mall.cleanliness)

    @property
    def rent_income(self):
        fixtures=sum(not k.startswith('courtyard_') for k in self.upgrades.decor)
        return (sum(s.rent for s in self.mall.stores if s.restored)+fixtures)*self.rent_multiplier+self.courtyard.income(self.upgrades)

    def draw(self):
        if self.welcome.open and not self.welcome.leaving:
            self.welcome.draw(self)
            if self.settings_menu.open:self.settings_menu.draw(self)
            elif self.pause.open:self.pause.draw(self)
            pygame.display.flip();return
        if self.scene=='courtyard':self.courtyard.draw(self);return
        target = self.target()
        self.mall.draw(self.screen,self.camera,self.hud.font,self.art,target,self.upgrades)
        self.story.draw(self)
        self.life.draw(self)
        if self.mall.commons.unlocked:
            self.courtyard.draw_passage(self,self.courtyard.door(self.mall))
        if self.owner_requests.store:
            p=self.camera.point(self.owner_requests.store.position)
            pygame.draw.circle(self.screen,(111,211,233),p,26,3)
            label=self.hud.small.render('YOUR REQUEST',True,(111,211,233))
            self.screen.blit(label,label.get_rect(midtop=(p.x,p.y+29)))
        for spot in self.owner_requests.scene_spots:
            spot.draw(self.screen,self.camera,self.art,self.hud.small,target is spot)
        for task in self.life.tasks:task.draw(self.screen,self.camera,self.art,self.hud.small,target is task)
        # Tall furniture and people share depth, so walking behind a prop looks natural.
        layers=[(depth,'furniture',(name,center,size)) for depth,name,center,size in self.mall.furniture(self.upgrades)]
        if self.life.spot:
            p=self.life.spot.position
            layers.append((p.y-10,'furniture',('community_table_'+str(self.life.event_index(self.life.active)),(p.x,p.y-40),(96,72))))
        layers += [(p.position.y,'neighbor',p) for p in self.story.visible_neighbors(self.mall)]
        layers += [(p.display_position.y,'shopper',p) for p in self.shoppers.people if p.visible]
        layers += [(p.position.y,'janitor',p) for p in self.janitors.people.values()]
        if self.life.owner and self.life.owner_time:layers.append((self.life.owner_position(self.life.owner).y,'owner',self.life.owner))
        layers.append((self.player.rect.centery,'player',self.player))
        for _,kind,item in sorted(layers,key=lambda entry:entry[0]):
            if kind == 'furniture':
                name,center,size=item
                self.art.draw(self.screen,name,self.camera.point(center),size)
            elif kind=='owner':
                self.life.draw_owner(self)
            elif kind=='neighbor':
                self.story.draw_neighbor(self,item)
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
            if self.tutorial.paused:
                self.tutorial.draw(self)
            elif self.community_menu.open:
                self.community_menu.draw(self)
            elif self.story_menu.open:
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
        if self.settings_menu.open:self.settings_menu.draw(self)
        elif self.pause.open:self.pause.draw(self)
        pygame.display.flip()

    def handle_event(self, event):
        if event.type==pygame.QUIT:self.settings_menu.open=False
        if self.settings_menu.open and event.type!=pygame.QUIT:
            self.settings_menu.handle(event,self);return
        if self.welcome.open and self.welcome.editing and not self.pause.open:
            if event.type in (pygame.KEYDOWN,pygame.TEXTINPUT):self.welcome.handle(event,self);return
        if self.welcome.open and not self.pause.open and event.type==pygame.KEYDOWN and event.key in (pygame.K_RETURN,pygame.K_SPACE,pygame.K_n,pygame.K_d,pygame.K_UP,pygame.K_DOWN,pygame.K_PAGEUP,pygame.K_PAGEDOWN):
            self.welcome.handle(event,self);return
        if event.type==pygame.KEYDOWN and event.key==pygame.K_F2:
            self.settings_menu.open=True;return
        event=self.preferences.normalize(event)
        if event.type==pygame.QUIT:
            if not self.pause.open or not self.pause.confirm:self.pause.show(True)
        elif event.type==pygame.VIDEORESIZE and not self.fullscreen:
            self.window_size=(max(800,event.w),max(600,event.h))
            self.screen=pygame.display.set_mode(self.window_size,pygame.RESIZABLE)
        elif event.type==pygame.KEYDOWN and event.key==pygame.K_F11:self.toggle_fullscreen()
        elif event.type==pygame.KEYDOWN and event.key==pygame.K_m:
            muted=self.audio.toggle();self.notify('Music and effects muted.' if muted else 'Music and effects on.')
            if self.shop_menu.open:self.shop_menu.notice=self.message
        elif self.pause.open:self.pause.handle(event,self)
        elif self.welcome.open:
            self.welcome.handle(event,self)
            if self.preferences.guide!=self.welcome.tutorial_enabled:
                self.preferences.guide=self.welcome.tutorial_enabled;self.preferences.save()
        elif event.type==pygame.KEYDOWN and event.key==pygame.K_F5:self.save_checkpoint()
        elif self.cooking_menu.open:self.cooking_menu.handle(event,self)
        elif self.community_menu.open:self.community_menu.handle(event,self)
        elif self.story_menu.open:self.story_menu.handle(event,self)
        elif self.tutorial.paused:
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:self.pause.show()
            else:self.tutorial.handle(event,self)
        elif self.scene=='courtyard' and event.type==pygame.KEYDOWN and event.key==pygame.K_F3:pass
        elif self.developer.enabled and event.type==pygame.KEYDOWN and event.key==pygame.K_F3:
            if not (self.shop_menu.open or self.owner_menu.open or self.journal.open or self.display_menu.open):self.developer.open=not self.developer.open
        elif self.developer.open:self.developer.handle(event,self)
        elif self.display_menu.open:self.display_menu.handle(event,self)
        elif self.shop_menu.open:self.shop_menu.handle(event,self)
        elif self.owner_menu.open:self.owner_menu.handle(event,self)
        elif self.journal.open:
            if self.scene=='courtyard':self.courtyard.journal_handle(event,self)
            else:self.journal.handle(event,self)
        elif self.tutorial.active and self.tutorial.handle(event,self):pass
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:self.pickup_at(event.pos)
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_h:
                if self.scene=='mall':self.tutorial.start(self)
                else:self.journal.tab=0;self.journal.open=True
            elif event.key==pygame.K_j:self.tutorial.journal_seen=True;self.journal.open=True
            elif event.key==pygame.K_ESCAPE:self.pause.show()
            elif event.key==pygame.K_e:self.interact()

    def run(self):
        try:
            while self.running:
                dt=min(self.clock.tick(FPS)/1000,0.05)
                for event in pygame.event.get():self.handle_event(event)
                if not self.running:break
                keys=pygame.key.get_pressed()
                direction=self.preferences.direction(keys)
                if not pygame.key.get_focused():direction=(0,0)
                self.update(dt,direction,keys[self.preferences.keys['interact']] and pygame.key.get_focused())
                self.draw()
        finally:
            if not self.skip_exit_save:self.save_checkpoint()
            pygame.quit()
