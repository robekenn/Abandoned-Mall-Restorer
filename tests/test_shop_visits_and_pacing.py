"""Regression checks for real visits, timed requests and focused menus."""
import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from systems.upgrades import Upgrades
from systems.shoppers import Shopper


class ShopVisitsAndPacingTests(unittest.TestCase):
    def setUp(self):
        self.game=Game()

    def tearDown(self):
        pygame.quit()

    def open_stores(self):
        g=self.game
        for t in g.mall.trash:g.mall.clean_trash(t)
        for store in g.mall.stores:store.restored=True
        g.mall.refresh_businesses()
        return g.mall.stores[1],g.mall.stores[2]

    def test_first_request_waits_three_minutes_of_open_store_play(self):
        g=self.game;store=g.mall.stores[1]
        g.owner_requests.update(300,g.mall)
        self.assertEqual(store.request_wait,180)
        self.open_stores()
        self.assertFalse(g.owner_requests.accept(store,g.mall))
        g.owner_requests.update(179,g.mall)
        self.assertFalse(g.owner_requests.accept(store,g.mall))
        self.assertEqual(g.owner_requests.update(1,g.mall)[0],store)
        self.assertTrue(g.owner_requests.accept(store,g.mall))
        self.assertEqual(g.owner_requests.update(1,g.mall),[])

    def test_claim_resets_only_its_timer_and_favors_follow_three_projects(self):
        g=self.game;store,other=self.open_stores()
        g.owner_requests.update(180,g.mall)
        self.assertTrue(g.owner_requests.accept(store,g.mall))
        g.owner_requests.interact(g.owner_requests.spots[0])
        self.assertTrue(g.claim_request(store))
        self.assertEqual(store.request_wait,180)
        self.assertTrue(g.owner_requests.eligible(other))
        self.assertFalse(g.owner_requests.accept(store,g.mall))
        g.owner_requests.update(179,g.mall)
        self.assertFalse(g.owner_requests.accept(store,g.mall))
        g.owner_requests.update(1,g.mall)
        self.assertTrue(g.owner_requests.accept(store,g.mall))
        g.owner_requests.store=None
        store.request_level=3
        g.owner_requests.update(999,g.mall)
        self.assertTrue(g.owner_requests.accept(store,g.mall))
        self.assertIsNotNone(g.owner_requests.favor)
        self.assertEqual(store.request_level,3)

    def test_waiting_owner_cannot_be_skipped_with_repeated_actions(self):
        g=self.game;store,_=self.open_stores()
        for _ in range(4):
            g.owner_menu.visit(store)
            g.update(300,(0,0))
            g.owner_menu.action(g)
        self.assertEqual(store.request_wait,180)
        self.assertIsNone(g.owner_requests.store)
        self.assertEqual(store.request_level,0)

    def test_journal_pauses_timers_and_esc_returns_to_game(self):
        g=self.game;store,_=self.open_stores();g.journal.open=True
        before=(g.cash,g.player.rect.center,g.shoppers.elapsed,g.litter_spawner.elapsed,store.request_wait)
        g.update(200,(1,0),True);g.interact();g.draw()
        self.assertEqual(before,(g.cash,g.player.rect.center,g.shoppers.elapsed,g.litter_spawner.elapsed,store.request_wait))
        g.journal.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE),g)
        self.assertFalse(g.journal.open)
        self.assertTrue(g.running)
        g.update(1,(0,0))
        self.assertEqual(store.request_wait,179)

    def test_j_key_opens_and_closes_journal_in_event_loop(self):
        g=self.game
        batches=[[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_j)],
                 [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE)],
                 [pygame.event.Event(pygame.QUIT)],
                 [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_DOWN),pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN)]]
        states=[]
        with patch('pygame.event.get',side_effect=batches),patch.object(g,'draw',side_effect=lambda:states.append(g.journal.open)):
            g.run()
        self.assertEqual(states,[True,False,False])

    def test_shopper_walks_in_hides_visits_and_walks_back_out(self):
        g=self.game;store,_=self.open_stores()
        g.shoppers.walkways.refresh(g.mall)
        person=Shopper(0,store.position,store,g.shoppers.walkways)
        g.shoppers.people=[person]
        seen=set()
        for _ in range(350):
            g.shoppers.update(.1,g.mall,g.upgrades)
            seen.add(person.state)
            if person.state=='inside':
                self.assertFalse(person.visible)
                g.player.rect.center=person.position
                self.assertIsNot(g.target(),person)
                with patch.object(g.art,'draw') as draw:
                    person.draw(g.screen,g.camera,g.art,g.hud.small,True)
                    draw.assert_not_called()
            if person.state in ('entering','exiting'):
                self.assertTrue(store.door_open)
            if person.done:break
        self.assertTrue({'entering','inside','exiting','leaving'}<=seen)
        self.assertTrue(person.done)
        self.assertLess(person.position.distance_to(person.entrance),1)

    def test_all_north_and_east_doors_have_safe_visits(self):
        g=self.game;self.open_stores();g.mall.unlock_east()
        for store in g.mall.east.stores:store.restored=True
        g.shoppers.walkways.refresh(g.mall)
        for identity,store in enumerate(g.mall.stores):
            with self.subTest(store=store.name):
                person=Shopper(identity,store.position,store,g.shoppers.walkways)
                g.shoppers.people=[person];g.shoppers.elapsed=-1000
                seen=set()
                for _ in range(250):
                    g.shoppers.update(.1,g.mall,g.upgrades)
                    seen.add(person.state)
                    footprint=pygame.Rect(person.position.x-9,person.position.y-11,18,22)
                    for wall in g.mall.obstacles:
                        if wall.colliderect(footprint):
                            self.assertIn(person.state,('entering','inside','exiting'))
                            self.assertLess(abs(person.position.x-store.rect.centerx),12)
                            if store.facing=='down':self.assertGreaterEqual(person.position.y,store.rect.bottom-28)
                            else:self.assertLessEqual(person.position.y,store.rect.top+28)
                            self.assertTrue(wall in (store.rect,g.mall.back_wall,g.mall.east.back_wall,g.mall.front_wall,g.mall.east.front_wall))
                    if person.done:break
                self.assertTrue({'entering','inside','exiting','leaving'}<=seen)
                self.assertTrue(person.done)
                self.assertFalse(store.door_open)

    def test_workshop_value_contracts_require_supplies_and_stop_at_eighty(self):
        u=Upgrades();cash=10000
        unchanged=u.purchase('advanced_value',cash,'east')
        self.assertEqual(unchanged[0],cash);self.assertFalse(unchanged[2])
        self.assertIsNone(next((o for o in u.offers('Gear') if o.key=='advanced_value'),None))
        u.value_level=len(u.VALUE_PRICES)
        for value,price in zip((45,60,80),(900,1800,3200)):
            previous=cash
            self.assertFalse(u.purchase('advanced_value',price-1,'east')[2])
            cash,_,bought=u.purchase('advanced_value',cash,'east')
            self.assertTrue(bought)
            self.assertEqual(cash,previous-price)
            self.assertEqual(u.unit_value,value)
        self.assertTrue(u.offers('Gear')[1].owned)
        self.assertTrue(u.offers('Gear','east')[0].owned)
        self.assertFalse(u.purchase('advanced_value',cash,'east')[2])

    def test_sale_uses_workshop_value_and_preserves_bag_upgrades(self):
        g=self.game;g.upgrades.value_level=5;g.upgrades.advanced_value_level=2
        g.upgrades.capacity_level=5;g.upgrades.advanced_capacity_level=4
        g.upgrades.held=40
        g.sell_trash(g.mall.trash_bins[0])
        self.assertEqual((g.cash,g.upgrades.held,g.upgrades.capacity),(2400,0,40))

    def test_all_panels_fit_minimum_window_and_every_shop_tab(self):
        g=self.game;store,_=self.open_stores()
        g.mall.unlock_east()
        g.screen=pygame.display.set_mode((800,600))
        for shop in ('north','east'):
            g.shop_menu.shop=shop;g.shop_menu.open=True
            for category in range(3):
                g.shop_menu.category=category;g.shop_menu.selection=0
                panel,_=g.shop_menu.geometry(g.screen)
                for _,row in g.shop_menu.rows(g):
                    self.assertTrue(panel.contains(row))
                    self.assertLessEqual(row.bottom,panel.bottom-100)
                g.draw()
        g.shop_menu.open=False
        for level,wait in ((0,180),(0,0),(1,179),(3,0)):
            store.request_level=level;store.request_wait=wait
            g.owner_menu.visit(store);g.draw()
        g.owner_menu.open=False;g.journal.open=True
        g.draw()
        panel,close=g.journal.geometry(g.screen)
        self.assertTrue(g.screen.get_rect().contains(panel))
        self.assertTrue(panel.contains(close))
