"""Connected visitor trips, visible restaurant service and courtyard maintenance."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import copy
import unittest
from unittest.mock import patch
import pygame
from tests import test_feature_expansion as feature_helpers
from systems.courtyard_visitors import FoodCustomer, MENU
from systems.saves import snapshot, restore_state


class CourtyardServiceTests(unittest.TestCase):
    def setUp(self):
        self.helper=feature_helpers.FeatureTests();self.helper.setUp();self.world=self.helper.enter();self.g=self.helper.g
    def tearDown(self):self.helper.tearDown()

    def reopen(self,count=8):
        for t in self.world.trash:self.world.clean_trash(t)
        for s in self.world.stores[:count]:s.restored=True
        self.world.refresh_businesses()

    def customer(self,identity,store):
        manager=self.g.courtyard.shoppers;manager.walkways.refresh(self.world)
        p=FoodCustomer(identity,store.position,store,manager.walkways)
        p.entrance=self.g.courtyard.return_door.position.copy();p.path=[]
        manager.people.append(p);return p

    def test_visitors_walk_from_front_to_patio_and_return_with_same_identity_and_food(self):
        self.reopen(2);g=self.g;main=g.shoppers;patio=g.courtyard.shoppers
        main.elapsed=-10000;g.visitor_travel.update(0,g)
        self.assertEqual(len(main.people),1);self.assertFalse(patio.people)
        p=main.people[0];self.assertIsInstance(p,FoodCustomer)
        self.assertEqual(p.position,g.mall.entrance);self.assertEqual(p.state,'to_courtyard')
        identity,name=p.identity,p.name;seen_outside=seen_return=False
        g.visitor_travel.elapsed=-10000
        for _ in range(400):
            main.update(1,g.mall,g.upgrades,spawn=False)
            patio.update(1,self.world,g.upgrades);g.visitor_travel.update(0,g)
            if p in patio.people:
                seen_outside=True;self.assertNotEqual(p.state,'inside')
            if seen_outside and p in main.people:
                seen_return=True;self.assertEqual((p.identity,p.name),(identity,name))
                self.assertEqual(p.food,MENU[p.store.name][1]);self.assertEqual(p.state,'leaving')
            if p.done:break
        self.assertTrue(seen_outside);self.assertTrue(seen_return);self.assertTrue(p.done)
        self.assertLess(p.position.distance_to(g.mall.entrance),1)

    def test_outdoor_manager_never_spawns_customers_directly(self):
        self.reopen();self.g.courtyard.shoppers.update(90,self.world,self.g.upgrades)
        self.assertFalse(self.g.courtyard.shoppers.people)
        self.g.visitor_travel.update(90,self.g)
        self.assertTrue(self.g.shoppers.people);self.assertFalse(self.g.courtyard.shoppers.people)

    def test_queue_order_and_service_are_visible_and_fifo(self):
        self.reopen(2);manager=self.g.courtyard.shoppers;store=self.world.stores[1]
        people=[self.customer(i,store) for i in range(3)]
        manager.update(0,self.world,self.g.upgrades)
        self.assertEqual([p.queue_ticket for p in people],[0,1,2])
        for _ in range(5):manager.update(.5,self.world,self.g.upgrades)
        self.assertEqual(people[0].state,'ordering');self.assertGreater(people[0].service_time,0)
        self.assertTrue(all(p.service_time==0 and p.state=='queuing' and p.visible for p in people[1:]))
        self.assertGreater(people[2].position.y,people[1].position.y)
        for _ in range(20):
            manager.update(.5,self.world,self.g.upgrades)
            if people[0].food:break
        self.assertEqual(people[0].food,'food_pizza');self.assertIsNone(people[1].food)
        self.assertTrue(all(p.visible and p.state not in ('inside','entering') for p in people))

    def test_new_arrival_routes_to_tail_without_crossing_the_counter(self):
        self.reopen(2);manager=self.g.courtyard.shoppers;store=self.world.stores[1]
        self.customer(1,store);self.customer(2,store);manager.update(0,self.world,self.g.upgrades)
        newcomer=FoodCustomer(3,self.world.entrance,store,manager.walkways)
        manager.people.append(newcomer);manager.update(0,self.world,self.g.upgrades)
        tail=manager.queue_position(store,2)
        self.assertEqual(newcomer.state,'queuing');self.assertEqual(newcomer.path[-1],tail)
        self.assertNotIn(store.position,newcomer.path)

    def test_every_restaurant_serves_its_own_dish_and_all_six_queue_slots_are_reachable(self):
        self.reopen();manager=self.g.courtyard.shoppers;manager.walkways.refresh(self.world)
        for i,store in enumerate(self.world.stores[1:]):
            manager.people=[];p=self.customer(i,store)
            for index in range(6):
                goal=manager.queue_position(store,index)
                self.assertIsNotNone(manager.walkways.route(self.world.entrance,goal),(store.name,index))
            for _ in range(25):
                manager.update(.5,self.world,self.g.upgrades)
                self.assertNotIn(p.state,('inside','entering'))
                if p.food:break
            self.assertEqual(p.food,MENU[store.name][1])

    def test_journal_hires_upgrades_and_pauses_the_local_janitor(self):
        g=self.g;g.journal.open=True
        g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_2))
        self.assertEqual(g.journal.staff_courts(g)[0][0],'courtyard')
        g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
        j=g.courtyard.janitors.people['courtyard'];self.assertFalse(g.janitors.people)
        g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_c))
        g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_w))
        self.assertEqual((j.clean_level,j.walk_level),(1,1));before=j.position.copy()
        g.update(10,(0,0));self.assertEqual(j.position,before)
        g.draw();g.journal.open=False
        g.update(1,(0,0));self.assertNotEqual(j.position,before)

    def test_courtyard_janitor_resumes_partial_work_and_corrupt_save_is_atomic(self):
        g=self.g;manager=g.courtyard.janitors
        self.assertTrue(manager.purchase('courtyard','hire',g,self.world)[0])
        j=manager.people['courtyard'];trash=self.world.trash[0]
        j.position=trash.position.copy();j.target=trash;j.target_revision=getattr(trash,'revision',0);j.path=[]
        manager.update(2,g,self.world);self.assertEqual(j.progress,2)
        data=snapshot(g);restore_state(data,g);self.assertEqual(snapshot(g),data)
        j=g.courtyard.janitors.people['courtyard'];self.assertEqual(j.progress,2)
        g.courtyard.janitors.update(3,g,g.courtyard.world)
        self.assertTrue(j.target is None);self.assertEqual(j.cleaned,1);self.assertEqual(j.earnings,.75*g.upgrades.unit_value)
        before=snapshot(g);bad=copy.deepcopy(before);bad['courtyard']['janitor']['walk']=99
        with self.assertRaises(ValueError):restore_state(bad,g)
        self.assertEqual(snapshot(g),before)

    def test_outside_rent_uses_the_same_character_popup(self):
        self.reopen();g=self.g;g.feedback.popups.clear();g.rent_timer=0
        g.update(5,(0,0))
        self.assertTrue(any(p.text.endswith(' rent') for p in g.feedback.popups))

    def test_indoor_benches_are_broken_until_purchased_and_patio_seating_is_distinct(self):
        g=self.g;g.leave_courtyard();g.open_upgrade_shop(g.mall.stores[0])
        self.assertTrue(all(name=='bench_dirty' for _,name,_,_ in g.mall.furniture(g.upgrades) if name.startswith('bench_')))
        self.assertEqual(g.buy_upgrade('bench_0'),'')
        names=[name for _,name,_,_ in g.mall.furniture(g.upgrades) if name.startswith('bench_')]
        self.assertEqual(names[:2],['bench_clean','bench_dirty'])
        self.assertNotEqual(pygame.image.tobytes(g.art.sprites['bench_dirty'],'RGBA'),pygame.image.tobytes(g.art.sprites['bench_clean'],'RGBA'))
        self.assertNotEqual(pygame.image.tobytes(g.art.sprites['courtyard_table_broken'],'RGBA'),pygame.image.tobytes(g.art.sprites['courtyard_table'],'RGBA'))

    def test_menus_pause_both_worlds_and_transfers(self):
        self.reopen();g=self.g;g.update(1,(0,0));clock=(g.shoppers.traffic_elapsed,g.courtyard.shoppers.traffic_elapsed,g.visitor_travel.elapsed)
        for menu in (g.pause,g.journal,g.shop_menu,g.settings_menu):
            menu.open=True;g.update(30,(0,0));menu.open=False
            self.assertEqual(clock,(g.shoppers.traffic_elapsed,g.courtyard.shoppers.traffic_elapsed,g.visitor_travel.elapsed))
