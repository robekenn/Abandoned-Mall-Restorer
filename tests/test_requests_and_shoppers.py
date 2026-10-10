import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from systems.shoppers import Shopper, Walkways


class LivingMallTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def open_pages(self):
        g = self.game
        for t in g.mall.trash:
            g.mall.clean_trash(t)
        for s in g.mall.stores[:2]:
            s.restored = True
        g.mall.refresh_businesses()
        return g.mall.stores[1]

    def accept(self, store):
        g = self.game
        store.request_wait = 0
        g.player.rect.center = store.position
        g.interact()
        self.assertTrue(g.owner_menu.open)
        g.owner_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN),g)
        self.assertFalse(g.owner_menu.open)
        self.assertIs(g.owner_requests.store,store)

    def claim(self, store):
        g = self.game
        g.player.rect.center = store.position
        g.interact()
        self.assertTrue(g.owner_menu.open)
        g.owner_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN),g)
        self.assertFalse(g.owner_menu.open)

    def test_delivery_uses_separate_satchel_and_claim_is_exactly_once(self):
        g = self.game; store = self.open_pages()
        self.accept(store)
        spot = g.owner_requests.spots[0]
        self.assertTrue(all(not w.collidepoint(spot.position) for w in g.mall.obstacles))
        g.upgrades.held = g.upgrades.capacity
        g.player.rect.center = spot.position
        g.interact()
        self.assertTrue(g.owner_requests.parcel)
        self.assertTrue(g.owner_requests.ready)
        self.assertEqual(g.upgrades.held,g.upgrades.capacity)
        self.assertEqual(g.cash,0)
        self.claim(store)
        self.assertEqual(g.cash,50)
        self.assertEqual(store.rent,store.base_rent+0.5)
        self.assertEqual(store.request_level,1)
        self.assertIsNone(g.owner_requests.store)
        g.claim_request(store)
        self.assertEqual(g.cash,50)
        self.assertEqual(store.request_level,1)

    def test_display_puzzle_requires_the_shelf_plan_then_unlocks_next_improvement(self):
        g = self.game; store = self.open_pages()
        store.request_level = 1; store.request_bonus = .5
        self.accept(store)
        spot = g.owner_requests.spots[0]
        g.player.rect.center = spot.position
        g.update(5,(0,0),True)
        self.assertFalse(spot.completed)  # Holding E cannot bypass the arrangement.
        g.interact()
        self.assertTrue(g.display_menu.open)
        for index in (0,1,2):g.display_menu.choose(index,g)
        self.assertFalse(g.owner_requests.ready)
        self.assertEqual(g.display_menu.arrangement,[])
        for index in g.owner_requests.display_plan:g.display_menu.choose(index,g)
        self.assertFalse(g.display_menu.open)
        self.assertTrue(g.owner_requests.ready)
        cash = g.cash
        self.claim(store)
        self.assertEqual(g.cash,cash+100)
        self.assertEqual(store.request_bonus,1.5)
        self.assertEqual(g.upgrades.decor,set())

    def test_welcome_project_needs_work_and_three_distinct_shoppers(self):
        g = self.game; store = self.open_pages()
        store.request_level = 2; store.request_bonus = 1.5
        self.accept(store)
        g.shoppers.update(0,g.mall,g.upgrades)
        visitor = g.shoppers.people[0]
        for _ in range(6):
            g.owner_requests.greet(visitor)
        self.assertEqual(len(g.owner_requests.greetings),1)
        self.assertFalse(g.owner_requests.ready)
        for identity in (100,101):
            extra = Shopper(identity,(160,1000),store,g.shoppers.walkways)
            g.shoppers.people.append(extra)
            g.player.rect.center = extra.position
            with patch.object(g,'target',return_value=extra):
                g.interact()
        self.assertEqual(len(g.owner_requests.greetings),3)
        self.assertFalse(g.owner_requests.ready)
        spot = g.owner_requests.spots[0]
        g.player.rect.center = spot.position
        g.update(2,(0,0),True)
        self.assertTrue(g.owner_requests.ready)
        cash = g.cash
        self.claim(store)
        self.assertEqual(g.cash,cash+200)
        self.assertEqual(store.request_bonus,3.5)
        self.assertEqual(store.request_level,3)
        self.assertFalse(g.owner_requests.eligible(store))
        self.assertFalse(g.owner_requests.accept(store,g.mall))
        with patch.object(g.litter_spawner,'update'):
            g.mall.dirty_tiles.clear()
            g.rent_timer = 0;g.cash=0
            g.update(5,(0,0))
            self.assertEqual(g.cash,(store.base_rent+3.5)*1.5)

    def test_only_one_request_no_shop_requests_and_no_early_rewards(self):
        g = self.game; pages = self.open_pages(); retro = g.mall.stores[2]
        self.assertFalse(g.owner_requests.accept(g.mall.stores[0],g.mall))
        self.assertFalse(g.owner_requests.accept(retro,g.mall))
        self.accept(pages)
        retro.restored = True
        self.assertFalse(g.owner_requests.accept(retro,g.mall))
        self.assertFalse(g.claim_request(pages))
        self.assertEqual((g.cash,pages.request_level,pages.request_bonus),(0,0,0))
        g.owner_menu.visit(retro)
        g.owner_menu.action(g)
        self.assertIs(g.owner_requests.store,pages)
        g.update(120,(0,0))
        self.assertIs(g.owner_requests.store,pages)  # no expiry

    def test_owner_menu_pauses_all_systems_and_renders_at_minimum_size(self):
        g = self.game; store = self.open_pages()
        g.screen = pygame.display.set_mode((800,600))
        g.owner_menu.visit(store)
        before = (g.cash,g.player.rect.center,g.litter_spawner.elapsed,g.shoppers.elapsed)
        g.update(100,(1,0),True)
        self.assertEqual((g.cash,g.player.rect.center,g.litter_spawner.elapsed,g.shoppers.elapsed),before)
        for level in range(4):
            store.request_level = level
            g.draw()
        store.request_level=0
        g.owner_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE),g)
        self.assertFalse(g.owner_menu.open)
        self.assertTrue(g.running)
        self.accept(store)
        g.draw()
        g.owner_menu.visit(store);g.draw()
        button = g.owner_menu.geometry(g.screen)[1]
        g.owner_menu.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=button.center),g)
        self.assertFalse(g.owner_menu.open)

    def test_east_requests_and_waypoints_are_reachable_after_unlock(self):
        g = self.game
        self.open_pages()
        for store in g.mall.stores:store.restored = True
        g.mall.unlock_east()
        for t in g.mall.east.trash:g.mall.clean_trash(t)
        for store in g.mall.east.stores:store.restored=True
        g.mall.refresh_businesses()
        store = g.mall.east.stores[1]
        g.shoppers.walkways.refresh(g.mall)
        for level in range(3):
            store.request_level=level
            store.request_wait=0
            self.assertTrue(g.owner_requests.accept(store,g.mall))
            for spot in g.owner_requests.spots:
                self.assertTrue(g.mall.east.area.collidepoint(spot.position))
                self.assertTrue(all(not w.collidepoint(spot.position) for w in g.mall.obstacles))
                path = g.shoppers.walkways.route(store.position,spot.position)
                self.assertTrue(path)
            g.owner_requests.store=None
        self.assertFalse(g.owner_requests.eligible(g.mall.east.stores[0]))

    def test_shoppers_wait_for_open_shops_use_clear_routes_and_stay_bounded(self):
        g = self.game
        g.shoppers.update(100,g.mall,g.upgrades)
        self.assertEqual(g.shoppers.people,[])
        self.open_pages()
        g.shoppers.update(0,g.mall,g.upgrades)
        self.assertEqual(len(g.shoppers.people),1)
        person = g.shoppers.people[0]
        self.assertIn(person.store,g.mall.stores[:2])
        self.assertTrue(person.path)
        for _ in range(600):
            g.shoppers.update(.1,g.mall,g.upgrades)
            self.assertLessEqual(len(g.shoppers.people),12)
            for visitor in g.shoppers.people:
                self.assertTrue(g.mall.opening_area.collidepoint(visitor.position))
                footprint=pygame.Rect(visitor.position.x-9,visitor.position.y-11,18,22)
                for wall in g.mall.obstacles:
                    if wall.colliderect(footprint):
                        self.assertIn(visitor.state,('entering','inside','exiting'))
                        self.assertLess(abs(visitor.position.x-visitor.store.rect.centerx),12)
                        self.assertGreaterEqual(visitor.position.y,visitor.store.rect.bottom-28)
                        self.assertTrue(wall == visitor.store.rect or wall == g.mall.back_wall)
        self.assertGreater(g.shoppers.next_identity,1)
        self.assertTrue(any(p.state!='arriving' for p in g.shoppers.people))

    def test_walkways_refresh_and_allow_east_routes_only_after_unlock(self):
        g=self.game;paths=Walkways();paths.refresh(g.mall)
        self.assertTrue(all(g.mall.opening_area.collidepoint(n) for n in paths.nodes))
        self.open_pages()
        for store in g.mall.stores:store.restored=True
        g.mall.unlock_east();paths.refresh(g.mall)
        route=paths.route((160,1000),g.mall.east.stores[0].position)
        self.assertTrue(route)
        self.assertTrue(any(g.mall.east.area.collidepoint(p) for p in route))
        walls=[w.inflate(20,24) for w in g.mall.obstacles]
        for a,b in zip(route,route[1:]):
            self.assertFalse(any(w.clipline(a,b) for w in walls))

    def test_visitors_use_purchased_amenities_and_do_not_modify_player_or_rent(self):
        g=self.game;store=self.open_pages()
        self.assertEqual(g.shoppers.amenities(g.mall,g.upgrades),[])
        g.upgrades.decor.update(('bench_0','fountain'))
        self.assertEqual(len(g.shoppers.amenities(g.mall,g.upgrades)),2)
        g.shoppers.update(0,g.mall,g.upgrades,store)
        person=g.shoppers.people[0]
        self.assertIs(person.store,store)
        person.position=pygame.Vector2(g.shoppers.walkways.nearest(store.position));person.path=[]
        person.state='exiting';person.wait=0
        person.update(0,g.shoppers,g.mall,g.upgrades)
        self.assertEqual(person.state,'strolling')
        self.assertTrue(person.path)
        cash,rent=g.cash,g.rent_income
        with patch.object(g,'target',return_value=person):g.interact()
        self.assertEqual((g.cash,g.rent_income),(cash,rent))
        self.assertEqual(g.upgrades.held,0)
        self.assertTrue(person.greeted)
        self.assertTrue(person.speech)
        self.assertGreater(person.speech_time,0)
        self.assertEqual(g.message_timer,0)
        for variant in range(4):
            for facing in ('down','up','left','right'):
                for frame in range(4):
                    self.assertEqual(g.art.sprites[f'shopper_{variant}_{facing}_{frame}'].get_size(),(16,24))
