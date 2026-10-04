"""Four-area progression, endlessly paced favors and optional first steps."""
import os
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import pygame
from game.game import Game
from systems.favors import FAVORS
from systems.requests import OWNERS
from systems.saves import snapshot, restore_state
from systems.upgrades import Upgrades
from systems.shoppers import Shopper


class ExpansionTests(unittest.TestCase):
    def setUp(self):self.game=Game()
    def tearDown(self):pygame.quit()

    def restore_current(self):
        g=self.game
        for t in g.mall.trash:g.mall.clean_trash(t)
        for store in g.mall.stores:store.restored=True
        g.mall.refresh_businesses()

    def open_all(self):
        self.restore_current()
        for region in self.game.mall.regions:
            self.assertTrue(self.game.mall.unlock_section(region))
            self.restore_current()

    def accept_favor(self, index, store=None):
        g=self.game;store=store or g.mall.stores[1]
        store.request_level=3;store.request_wait=0
        store.recurring_completed=(index-list(OWNERS).index(store.name))%len(FAVORS)
        self.assertTrue(g.owner_requests.accept(store,g.mall))
        self.assertIs(g.owner_requests.favor,FAVORS[index])
        return store

    def finish(self):
        requests=self.game.owner_requests
        if requests.favor.mode=='collect':requests.record_collection(requests.amount,requests.store.position)
        if requests.favor.mode=='sell':requests.record_sale(requests.favor.amount,requests.store.position)
        for identity in range(3):requests.greet(SimpleNamespace(identity=identity,visible=True))
        while requests.visible_spots:
            for spot in requests.visible_spots:
                if spot.kind=='display':
                    self.game.display_menu.visit()
                    for index in requests.display_plan:self.game.display_menu.choose(index,self.game)
                elif spot.duration:requests.work(spot.duration,spot.position,True,True)
                else:self.assertTrue(requests.interact(spot))
        self.assertTrue(requests.ready)

    def test_four_areas_unlock_once_in_order_and_have_ten_businesses_each(self):
        g=self.game;g.cash=100000
        self.assertFalse(g.mall.garden.ready(g.mall));self.assertFalse(g.mall.commons.ready(g.mall))
        for region in g.mall.regions:
            self.assertFalse(region.unlocked)
            self.restore_current()
            self.assertTrue(region.ready(g.mall))
            g.cash=region.cost-1
            with patch.object(g,'target',return_value=region):g.interact()
            self.assertFalse(region.unlocked)
            self.assertEqual(g.cash,region.cost-1)
            g.cash=region.cost
            with patch.object(g,'target',return_value=region):g.interact()
            self.assertTrue(region.unlocked);self.assertEqual(g.cash,0)
            self.assertFalse(g.mall.unlock_section(region))
            self.assertEqual(len(region.stores),10)
            dirty=set(region.floor_tiles)&g.mall.dirty_tiles
            self.assertEqual(len(dirty),len(region.floor_tiles))
            g.mall.respawn_trash(g.mall.north_trash[0]);g.mall.clean_trash(g.mall.north_trash[0])
            self.assertEqual(set(region.floor_tiles)&g.mall.dirty_tiles,dirty)
            self.assertTrue(region.stores[0].available)
            self.assertFalse(region.stores[1].available)
            for t in region.trash:g.mall.clean_trash(t)
            for store in region.stores:
                self.assertTrue(store.available)
                g.cash=store.cost;g.player.rect.center=store.position;g.interact()
                self.assertTrue(store.restored)
                self.assertEqual(g.cash,0)
                g.shop_menu.open=False;g.owner_menu.open=False
        self.assertEqual(len(g.mall.stores),40)
        self.assertEqual(len(g.mall.playable_areas),4)
        self.assertEqual(g.mall.cleanliness,1)
        self.assertEqual(g.mall.barriers,[])

    def test_later_gates_block_walking_until_opened(self):
        g=self.game
        g.player.rect.center=(160,1435);g.player.move((0,1),1,g.mall.obstacles)
        self.assertLessEqual(g.player.rect.bottom,1480)
        self.restore_current();g.mall.unlock_east();self.restore_current();g.mall.unlock_section(g.mall.garden)
        g.player.rect.center=(160,1435);g.player.move((0,1),1,g.mall.obstacles)
        self.assertGreater(g.player.rect.centery,1512)
        g.player.rect.center=(1715,2600);g.player.move((1,0),1,g.mall.obstacles)
        self.assertLessEqual(g.player.rect.right,1760)
        self.restore_current();g.mall.unlock_section(g.mall.commons)
        g.player.rect.center=(1715,2600);g.player.move((1,0),1,g.mall.obstacles)
        self.assertGreater(g.player.rect.centerx,1792)

    def test_all_four_floors_are_reachable_covered_and_recurring_litter_stays_bounded(self):
        self.open_all();g=self.game
        g.shoppers.walkways.refresh(g.mall)
        for region in g.mall.regions:
            for tile in region.floor_tiles:
                self.assertTrue(any(t.position.distance_to(tile)<115 for t in region.trash))
            for store in region.stores:
                path=g.shoppers.walkways.route((160,1000),store.position)
                self.assertTrue(path,store.name)
                for a,b in zip(path,path[1:]):
                    self.assertFalse(any(w.inflate(20,24).clipline(a,b) for w in g.mall.obstacles))
            self.assertTrue(g.shoppers.walkways.route((160,1000),region.delivery.position))
        count=len(g.mall.trash)
        for _ in range(180):g.litter_spawner.update(4,g.mall,(240,430))
        self.assertEqual(len(g.mall.trash),count)
        self.assertEqual(len(g.mall.recurring_pools),4)
        for pool in g.mall.recurring_pools:self.assertLessEqual(sum(not t.cleaned for t in pool),12)
        for t in g.mall.trash:g.mall.clean_trash(t)
        self.assertEqual(g.mall.cleanliness,1)

    def test_regional_equipment_requires_previous_shop_and_stops_at_each_cap(self):
        u=Upgrades();cash=1000000
        for shop in ('garden','commons'):
            for offer in u.offers('Gear',shop):
                self.assertFalse(u.purchase(offer.key,cash,shop)[2])
        for key,prices in (('capacity',u.CAPACITY_PRICES),('value',u.VALUE_PRICES),('tool',u.TOOL_PRICES)):
            for _ in prices:cash,_,bought=u.purchase(key,cash);self.assertTrue(bought)
        for key,prices in (('advanced_capacity',u.ADVANCED_CAPACITY_PRICES),('advanced_value',u.ADVANCED_VALUE_PRICES),('speed',u.SPEED_PRICES)):
            for _ in prices:cash,_,bought=u.purchase(key,cash,'east');self.assertTrue(bought)
        for shop in ('garden','commons'):
            for key,levels,prices,*_ in u.REGIONAL_TRACKS[shop]:
                for price in prices:
                    before=cash;cash,_,bought=u.purchase(key,cash,shop)
                    self.assertTrue(bought);self.assertEqual(cash,before-price)
                self.assertTrue(next(o for o in u.offers('Gear',shop) if o.key==key).owned)
                self.assertFalse(u.purchase(key,cash,shop)[2])
        self.assertEqual((u.capacity,u.unit_value,u.tool[1:],u.speed_multiplier),(80,360,(260,12),2.6))
        self.assertTrue(all(o.owned for shop in ('north','east','garden','commons') for o in u.offers('Gear',shop)))

    def test_all_fixture_keys_match_unlocked_layout_and_add_rent_once(self):
        self.open_all();g=self.game;g.cash=1000000;keys=[]
        for store in (s for s in g.mall.stores if s.upgrade_shop):
            g.open_upgrade_shop(store)
            for category in ('Furniture','Garden'):
                for offer in g.upgrades.offers(category,store.upgrade_shop):
                    keys.append(offer.key);g.buy_upgrade(offer.key)
                    before=(g.cash,g.upgrades.fixture_rent);g.buy_upgrade(offer.key)
                    self.assertEqual((g.cash,g.upgrades.fixture_rent),before)
        self.assertEqual(len(keys),72);self.assertEqual(len(set(keys)),72)
        self.assertEqual((len(g.mall.benches),len(g.mall.lamps),len(g.mall.plants)),(8,16,16))
        self.assertEqual(g.upgrades.fixture_rent,72)
        self.assertEqual(len(g.mall.furniture(g.upgrades)),12+len(g.mall.social_tables))
        g.shop_menu.open=False
        with patch.object(g.litter_spawner,'update'):
            before=g.cash;g.update(5,(0,0));self.assertEqual(g.cash-before,g.rent_income)

    def test_twelve_favors_repeat_twice_with_exact_rewards_and_waits(self):
        self.restore_current();g=self.game;store=g.mall.stores[1]
        store.request_level=3;store.request_bonus=3.5;store.request_wait=0
        self.assertEqual(len(FAVORS),12)
        seen=[]
        for _ in range(24):
            self.assertTrue(g.owner_requests.accept(store,g.mall))
            seen.append(g.owner_requests.favor.key)
            bonus=g.owner_requests.favor.bonus;reward=g.owner_requests.details(store)[4]
            self.finish();cash,rent=g.cash,store.rent
            self.assertTrue(g.claim_request(store))
            self.assertEqual(g.cash-cash,reward);self.assertEqual(store.rent-rent,bonus)
            self.assertEqual(store.request_level,3)
            self.assertFalse(g.claim_request(store));self.assertEqual(g.cash,cash+reward)
            self.assertFalse(g.owner_requests.accept(store,g.mall))
            g.owner_requests.update(179,g.mall);self.assertFalse(g.owner_requests.accept(store,g.mall))
            self.assertGreaterEqual(store.request_wait,1)
            self.assertLessEqual(store.request_wait,421)
            g.owner_requests.update(store.request_wait,g.mall)
        self.assertEqual(len(set(seen[:12])),12)
        self.assertEqual(seen[:12],seen[12:])
        self.assertEqual(store.recurring_completed,24)
        self.assertEqual(store.request_bonus,7.5)  # Four +$0.50 favors in each rotation.

    def test_favor_sites_and_delivery_stages_work_for_every_owner(self):
        self.open_all();g=self.game
        for store in (s for s in g.mall.stores if not s.upgrade_shop):
            for index,favor in enumerate(FAVORS):
                with self.subTest(store=store.name,favor=favor.key):
                    self.accept_favor(index,store)
                    for spot in g.owner_requests.spots:
                        self.assertTrue(g.mall.area_for_store(store).collidepoint(spot.position))
                        footprint=pygame.Rect(spot.position.x-13,spot.position.y-15,26,30)
                        self.assertFalse(any(w.colliderect(footprint) for w in g.mall.obstacles))
                    if favor.mode in ('repair','route'):
                        self.assertEqual(len(g.owner_requests.visible_spots),1)
                        hidden=g.owner_requests.spots[1]
                        self.assertFalse(g.owner_requests.interact(hidden))
                        g.owner_requests.work(100,hidden.position,True,True)
                        self.assertFalse(hidden.completed)
                    g.upgrades.held=g.upgrades.capacity
                    self.finish();held=g.upgrades.held
                    self.assertTrue(g.claim_request(store))
                    self.assertEqual(g.upgrades.held,held)

    def test_collection_counts_across_zones_and_sales_stay_local(self):
        self.open_all();g=self.game
        with patch('systems.requests.random.randint',return_value=5):self.accept_favor(2)
        foreign=g.mall.east.trash[0];g.mall.respawn_trash(foreign)
        g.player.rect.center=foreign.position;g.collect(foreign)
        self.assertEqual(g.owner_requests.progress,1)
        g.upgrades.capacity_level=5;g.upgrades.held=0
        for t in g.mall.north_trash[:5]:
            g.mall.respawn_trash(t);g.player.rect.center=t.position;g.collect(t)
        self.assertEqual(g.owner_requests.progress,5);self.assertTrue(g.owner_requests.ready)
        g.claim_request(g.mall.stores[1]);self.accept_favor(6)
        g.upgrades.held=8;g.sell_trash(g.mall.east.bins[0]);self.assertEqual(g.owner_requests.progress,0)
        g.upgrades.held=8;g.sell_trash(g.mall.trash_bins[0]);self.assertEqual(g.owner_requests.progress,8)
        self.assertTrue(g.owner_requests.ready)
        g.sell_trash(g.mall.trash_bins[0]);self.assertEqual(g.owner_requests.progress,8)

    def test_collection_goal_varies_once_per_acceptance_and_caps_progress(self):
        self.restore_current();g=self.game;r=g.owner_requests
        for goal in (3,10):
            with patch('systems.requests.random.randint',return_value=goal) as roll:
                store=self.accept_favor(2)
                self.assertEqual(r.amount,goal)
                for _ in range(3):
                    self.assertIn(f'Collect {goal} pieces anywhere',r.details(store)[1])
                    self.assertIn(f'0/{goal}',r.objective)
                self.assertEqual(roll.call_count,1)
                r.record_collection(goal-1,store.position)
                self.assertFalse(r.ready)
                r.record_collection(100,store.position)
                self.assertEqual(r.progress,goal);self.assertTrue(r.ready)
                self.assertTrue(g.claim_request(store))
                self.assertEqual(r.collection_goal,0)

    def test_collection_counts_in_every_open_court(self):
        self.open_all();g=self.game
        with patch('systems.requests.random.randint',return_value=10):self.accept_favor(2)
        for i,pool in enumerate([g.mall.north_trash]+[region.trash for region in g.mall.active_regions],1):
            trash=pool[0];g.mall.respawn_trash(trash)
            g.upgrades.held=0;g.player.rect.center=trash.position;g.collect(trash)
            self.assertEqual(g.owner_requests.progress,i)

    def test_collection_save_preserves_goal_and_supports_legacy_checkpoints(self):
        self.restore_current();g=self.game
        with patch('systems.requests.random.randint',return_value=10):self.accept_favor(2)
        g.owner_requests.record_collection(7,g.player.rect.center)
        data=snapshot(g)
        with patch('systems.requests.random.randint',side_effect=AssertionError('Save must not reroll')):
            restore_state(data,g);r=g.owner_requests
            self.assertEqual((r.amount,r.progress,r.ready),(10,7,False))
        for bad in (0,2,11,True,5.5):
            data['request']['collection_goal']=bad
            with self.assertRaises(ValueError):restore_state(data,g)
        del data['request']['collection_goal'];data['request']['progress']=5
        restore_state(data,g);r=g.owner_requests
        self.assertEqual((r.amount,r.progress,r.ready),(5,5,True))

    def test_janitors_reserve_remaining_collection_litter_across_courts(self):
        self.open_all();g=self.game
        with patch('systems.requests.random.randint',return_value=3):self.accept_favor(2)
        g.owner_requests.record_collection(2,g.player.rect.center)
        for trash in g.mall.east.trash[:2]:g.mall.respawn_trash(trash)
        closest=g.mall.east.trash[0];g.player.rect.center=closest.position
        g.cash=1000000;self.assertTrue(g.janitors.purchase('east','hire',g)[0])
        j=g.janitors.people['east']
        with patch.object(j,'choose_work',wraps=j.choose_work) as choose:
            j.update(0,g.mall.east.trash,g)
            self.assertEqual(choose.call_args.args[2],[closest])
        self.assertIsNot(j.target,closest)
        self.assertEqual(g.owner_requests.progress,2)
        g.owner_requests.record_collection(1,closest.position)
        j.target=None;j.path=[]
        with patch.object(j,'choose_work',wraps=j.choose_work) as choose:
            j.update(0,g.mall.east.trash,g)
            self.assertEqual(choose.call_args.args[2],[])

    def test_favors_pause_in_menus_and_do_not_expire(self):
        self.restore_current();g=self.game;store=self.accept_favor(8)
        before=store.request_wait
        g.journal.open=True;g.update(400,(1,0),True)
        self.assertEqual(store.request_wait,before)
        self.assertFalse(g.owner_requests.ready)
        g.journal.open=False;g.update(400,(0,0))
        self.assertIs(g.owner_requests.store,store)
        self.assertFalse(g.owner_requests.ready)

    def test_routine_actions_are_quiet_and_shopper_bubbles_pause_the_speaker(self):
        g=self.game;trash=g.mall.trash[0];g.player.rect.center=trash.position;g.interact()
        self.assertEqual(g.message_timer,0);self.assertTrue(g.feedback.popups)
        g.sell_trash(g.mall.trash_bins[0]);self.assertEqual(g.message_timer,0)
        self.restore_current();g.cash=100;g.open_upgrade_shop(g.mall.stores[0]);g.shop_menu.buy(g,'capacity')
        self.assertEqual(g.shop_menu.notice,'');g.shop_menu.open=False
        g.shoppers.update(0,g.mall,g.upgrades);p=g.shoppers.people[0]
        with patch.object(g,'target',return_value=p):g.interact()
        self.assertEqual(g.message_timer,0);self.assertTrue(p.speech)
        position=p.position.copy();g.shoppers.update(1,g.mall,g.upgrades)
        self.assertEqual(p.position,position)
        rect,lines,head=g.speech.geometry(g,p.speech,p.position)
        self.assertEqual(rect.midbottom,(round(head.x),round(head.y-10)))
        g.owner_menu.visit(g.mall.stores[1]);time=p.speech_time;g.update(100,(0,0))
        self.assertEqual(p.speech_time,time)
        g.owner_menu.open=False;g.shoppers.update(10,g.mall,g.upgrades);g.shoppers.update(.2,g.mall,g.upgrades)
        self.assertNotEqual(p.position,position)

    def test_tutorial_follows_real_actions_and_never_grants_money(self):
        g=self.game;g.tutorial.start(g)
        g.tutorial.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN),g)
        g.update(.15,(1,0));self.assertEqual(g.tutorial.step,1)
        g.tutorial.explaining=False
        g.player.rect.center=g.mall.trash[0].position;g.interact();g.update(0,(0,0))
        self.assertEqual(g.tutorial.step,2);self.assertEqual(g.cash,0);g.tutorial.explaining=False
        g.sell_trash(g.mall.trash_bins[0]);g.update(0,(0,0));self.assertEqual(g.tutorial.step,3)
        self.assertEqual(g.cash,1);g.tutorial.explaining=False
        g.cash=15;g.player.rect.center=g.mall.stores[0].position;g.interact();g.buy_upgrade('capacity')
        g.shop_menu.open=False;g.update(0,(0,0));self.assertEqual(g.tutorial.step,4)
        g.tutorial.explaining=False;g.tutorial.journal_seen=True;g.update(0,(0,0));self.assertFalse(g.tutorial.active)
        self.assertEqual(g.cash,0)
        g.tutorial.start(g);g.tutorial.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_t),g)
        self.assertFalse(g.tutorial.active)

    def test_opening_can_disable_guide_and_live_skip_can_be_clicked(self):
        g=Game(start_screen=True)
        rect=g.welcome.tutorial_rect(g.screen)
        g.welcome.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center),g)
        self.assertFalse(g.welcome.tutorial_enabled)
        g.welcome.start();g.update(1,(0,0));self.assertFalse(g.tutorial.active)
        g.tutorial.start(g)
        g.tutorial.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=g.tutorial.skip_rect(g.screen).center),g)
        self.assertFalse(g.tutorial.active)

    def test_all_new_menus_and_journal_pages_fit_minimum_size(self):
        self.open_all();g=self.game;g.screen=pygame.display.set_mode((800,600))
        g.tutorial.start(g);g.draw();g.tutorial.skip()
        for region in g.mall.regions:
            g.player.rect.center=region.stores[0].position;g.update(0,(0,0));g.open_upgrade_shop(region.stores[0])
            for category in range(3):g.shop_menu.category=category;g.draw()
            g.shop_menu.open=False
        for page in range(3):g.journal.page=page;g.journal.open=True;g.draw()
        self.assertEqual(g.journal.page,2);g.journal.open=False
        store=g.mall.stores[1]
        for index in range(len(FAVORS)):
            self.accept_favor(index,store);g.owner_menu.visit(store);g.draw();g.owner_menu.open=False
            for spot in g.owner_requests.scene_spots:
                g.player.rect.center=spot.position;g.update(0,(0,0));g.draw()
            if g.owner_requests.display_items:g.display_menu.visit();g.draw();g.display_menu.open=False
            self.finish();g.claim_request(store)
