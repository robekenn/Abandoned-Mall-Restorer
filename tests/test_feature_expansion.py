"""Social groups, seating, traffic, world transitions and persistent food-court progress."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import copy
import tempfile
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from mall.courtyard import SceneDoor
from systems.shoppers import Shopper, Walkways
from systems.saves import snapshot,restore_state,SaveStore


class FeatureTests(unittest.TestCase):
    def setUp(self):self.g=Game()
    def tearDown(self):pygame.quit()

    def open_all(self):
        g=self.g
        for region in g.mall.regions:
            for t in g.mall.trash:g.mall.clean_trash(t)
            for s in g.mall.stores:s.restored=True
            g.mall.refresh_businesses();self.assertTrue(g.mall.unlock_section(region))
        for t in g.mall.trash:g.mall.clean_trash(t)
        for s in g.mall.stores:s.restored=True
        g.mall.refresh_businesses()

    def enter(self):
        self.open_all();g=self.g;g.cash=2000000
        g.player.rect.center=g.courtyard.door(g.mall).position
        self.assertTrue(g.enter_courtyard());return g.courtyard.world

    def test_arrivals_include_cohesive_families_and_teen_groups(self):
        g=self.g;m=g.shoppers;m.mall=g.mall;m.walkways.refresh(g.mall)
        store=g.mall.stores[1];store.restored=True
        for _ in range(3):m.spawn_party(g.mall,store,10)
        self.assertEqual([p.age for p in m.people],['adult','adult','adult','child','teen','teen'])
        for follower in (p for p in m.people if p.leader):
            self.assertEqual(follower.group_id,follower.leader.group_id)
            follower.leader.position=pygame.Vector2(455,455);follower.position=pygame.Vector2(391,455)
            before=follower.position.copy();follower.update(.1,m,g.mall,g.upgrades)
            self.assertLessEqual(follower.position.distance_to(before),14.5)
            self.assertFalse(any(w.colliderect(pygame.Rect(follower.position.x-9,follower.position.y-11,18,22)) for w in g.mall.obstacles))
            follower.leader.state='inside';self.assertFalse(follower.visible)
            follower.leader.done=True;follower.update(.1,m,g.mall,g.upgrades);self.assertTrue(follower.done)

    def test_child_and_teen_art_covers_walk_and_seated_poses(self):
        g=self.g;m=g.shoppers;m.walkways.refresh(g.mall)
        person=Shopper(1,(455,455),g.mall.stores[1],m.walkways)
        for age in ('child','teen'):
            person.age=age
            for facing in ('up','down','left','right'):
                person.facing=facing
                for frame in range(4):person.frame=frame;person.draw(g.screen,g.camera,g.art,g.hud.small,True)
                person.state='resting';person.activity='table';person.path=[]
                person.draw(g.screen,g.camera,g.art,g.hud.small,True)
                person.state='arriving';person.activity=''

    def test_teens_change_between_walking_and_running_without_teleporting(self):
        g=self.g;m=g.shoppers;m.mall=g.mall;m.walkways.refresh(g.mall)
        p=Shopper(9,(455,455),g.mall.stores[1],m.walkways);p.age='teen'
        for clock,speed in ((0,104),(12,128)):
            p.position=pygame.Vector2(455,455);p.path=[pygame.Vector2(583,455)];m.traffic_elapsed=clock
            p.update(.1,m,g.mall,g.upgrades);self.assertAlmostEqual(p.position.x-455,speed*.1)

    def test_busy_and_quiet_periods_change_population_and_pause_in_menus(self):
        self.open_all();g=self.g;m=g.shoppers
        m.traffic_elapsed=200;busy=m.desired_population(g.mall,g.upgrades)
        m.traffic_elapsed=400;quiet=m.desired_population(g.mall,g.upgrades)
        self.assertGreater(busy,quiet);self.assertLessEqual(busy,36)
        clock=m.traffic_elapsed;g.pause.show();g.update(100,(0,0));self.assertEqual(m.traffic_elapsed,clock)
        g.pause.open=False;data=snapshot(g);restore_state(data,g);self.assertEqual(g.shoppers.traffic_elapsed,clock)

    def test_tables_have_reachable_unique_seats_and_visitors_chat(self):
        self.open_all();g=self.g;m=g.shoppers;m.walkways.refresh(g.mall);m.mall=g.mall
        g.upgrades.decor.update(key for t in g.mall.social_tables for key in (t.fixture_key,*t.seat_keys));m.upgrades=g.upgrades
        self.assertEqual(len(g.mall.social_tables),8)
        for table in g.mall.social_tables:
            for seat in table.seats:self.assertIsNotNone(m.walkways.route(g.mall.entrance,seat))
        store=g.mall.stores[1];people=[Shopper(i,store.position,store,m.walkways) for i in (1,2)];m.people=people
        for p in people:
            p.state='exiting';p.visits=1;p.path=[];p.update(0,m,g.mall,g.upgrades)
            self.assertEqual(p.activity,'table');p.position=p.goal.copy();p.path=[];p.update(0,m,g.mall,g.upgrades)
        self.assertIs(people[0].table,people[1].table)
        self.assertNotEqual(people[0].table_seat,people[1].table_seat)
        self.assertTrue(all(p.speech_time for p in people))

    def test_keepsake_giver_departs_once_and_stays_gone_after_continue(self):
        g=self.g;g.mall.stores[0].restored=True;g.story.started[0]=True
        point=g.story.visible_neighbors(g.mall)[0]
        self.assertTrue(g.story.action(point,g));self.assertNotIn(point,g.story.visible_neighbors(g.mall))
        person=next(p for p in g.shoppers.people if p.name==point.name)
        self.assertEqual(person.state,'leaving');self.assertIsNotNone(person.path)
        self.assertFalse(g.story.action(point,g));restore_state(snapshot(g),g)
        self.assertFalse(g.story.visible_neighbors(g.mall))

    def test_boards_stay_on_room_edges_and_indoor_connections_remain_open(self):
        self.open_all();g=self.g;areas=g.mall.playable_areas
        for point in (p for p in g.story.points if p.memory<0):
            area=areas[point.chapter]
            self.assertLess(min(point.position.x-area.left,area.right-point.position.x),210)
            self.assertFalse(any(w.collidepoint(point.position) for w in g.mall.obstacles))
        self.assertFalse(hasattr(g.mall,'service_caps'))
        for point in ((1776,200),(1776,1350),(1100,1496),(1776,1650),(1776,2850)):
            self.assertFalse(any(w.collidepoint(point) for w in g.mall.obstacles))
        paths=Walkways();paths.refresh(g.mall)
        for s in g.mall.stores:self.assertIsNotNone(paths.route(g.mall.entrance,s.position))

    def test_courtyard_requires_commons_cleanup_shops_and_one_entry_payment(self):
        g=self.g;g.cash=2000000;self.assertFalse(g.enter_courtyard());self.assertIsNone(g.courtyard.world)
        self.open_all();g.player.rect.center=g.courtyard.door(g.mall).position
        g.cash=49999;self.assertIsInstance(g.target(),SceneDoor);g.interact();self.assertEqual(g.scene,'mall')
        g.cash=50000;g.interact();self.assertEqual((g.scene,g.cash),('courtyard',0))
        self.assertFalse(g.enter_courtyard());g.leave_courtyard()
        g.welcome.open=False;g.player.rect.center=(3530,g.courtyard.door(g.mall).position.y)
        g.update(.05,(1,0));self.assertEqual((g.scene,g.cash),('courtyard',0))
        self.assertEqual(g.mall.size,(3600,3040));self.assertEqual(g.courtyard.world.size,(2000,1440))

    def test_restaurant_progression_and_every_patio_route_are_reachable(self):
        world=self.enter();g=self.g;m=g.courtyard.shoppers;m.walkways.refresh(world)
        for s in world.stores:self.assertIsNotNone(m.walkways.route(world.entrance,s.position))
        for t in world.trash:self.assertIsNotNone(m.walkways.route(world.entrance,t.position))
        for table in world.social_tables:
            for seat in table.seats:self.assertIsNotNone(m.walkways.route(world.entrance,seat))
        self.assertEqual(len(world.social_tables),6)
        g.player.rect.center=world.stores[1].position;before=g.cash;g.interact();self.assertEqual(g.cash,before)
        g.player.rect.center=world.stores[0].position;g.interact();self.assertTrue(g.shop_menu.open);g.shop_menu.open=False
        self.assertFalse(world.stores[1].available)
        for t in world.trash:world.clean_trash(t)
        self.assertEqual(world.cleanliness,1)
        for s in world.stores[1:]:
            self.assertTrue(s.available);g.player.rect.center=s.position;before=g.cash;g.interact()
            self.assertTrue(s.restored);self.assertEqual(g.cash,before-s.cost)
        self.assertIsNone(world.next_store)

    def test_courtyard_service_comfort_and_compost_have_effects_without_speed(self):
        world=self.enter();g=self.g
        for t in world.trash:world.clean_trash(t)
        for s in world.stores:s.restored=True
        g.open_upgrade_shop(world.stores[0]);before=g.rent_income;speed=g.upgrades.speed_multiplier
        for key in ('courtyard_service','courtyard_comfort','courtyard_compost'):self.assertEqual(g.buy_upgrade(key),'')
        self.assertGreater(g.rent_income,before);self.assertEqual(g.upgrades.speed_multiplier,speed)
        self.assertFalse(any('speed' in o.key for o in g.upgrades.offers('Gear','courtyard')))
        g.shop_menu.open=False;g.player.rect.center=world.trash_bins[0].position;g.upgrades.held=4;before=g.cash
        g.interact();self.assertEqual(g.cash-before,5*g.upgrades.unit_value);self.assertEqual(g.upgrades.held,0)
        g.courtyard.update(g,0,(0,0));self.assertEqual(world.comfort,1)
        for _ in range(2):g.upgrades.purchase('courtyard_service',g.cash,'courtyard')
        self.assertFalse(g.upgrades.purchase('courtyard_service',g.cash,'courtyard')[2])

    def test_courtyard_mouse_pickup_updates_bag_and_indoor_collection_favor(self):
        world=self.enter();g=self.g;store=g.mall.stores[1]
        from systems.requests import OWNERS
        store.request_level=3;store.request_wait=0;store.recurring_completed=(2-list(OWNERS).index(store.name))%12
        g.owner_requests.accept(store,g.mall)
        trash=next(t for t in world.trash if 450<t.position.y<950);g.player.rect.center=trash.position;g.frame_camera(g.screen.get_size())
        pos=tuple(round(v) for v in g.camera.point(trash.position))
        g.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos))
        self.assertTrue(trash.cleaned);self.assertEqual((g.upgrades.held,g.owner_requests.progress),(1,1))

    def test_only_active_world_renders_visitors_travel_and_menus_pause_courtyard(self):
        self.enter();g=self.g
        with patch.object(g.mall,'draw',side_effect=AssertionError('Indoor map must not render')):g.draw()
        clock=g.shoppers.traffic_elapsed
        g.update(1,(0,0));self.assertEqual(g.shoppers.traffic_elapsed,clock+1)
        for menu in (g.pause,g.settings_menu,g.shop_menu,g.journal):
            menu.open=True;before=(g.cash,g.player.rect.center,g.courtyard.spawner.elapsed,g.courtyard.shoppers.traffic_elapsed)
            g.update(40,(1,0));self.assertEqual(before,(g.cash,g.player.rect.center,g.courtyard.spawner.elapsed,g.courtyard.shoppers.traffic_elapsed));menu.open=False
        g.journal.open=True;g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE));self.assertFalse(g.journal.open)

    def test_both_worlds_roundtrip_and_legacy_saves_migrate(self):
        world=self.enter();g=self.g;world.stores[0].restored=True
        g.upgrades.purchase('courtyard_service',g.cash,'courtyard')
        g.upgrades.decor.add('courtyard_table_0');world.clean_trash(world.trash[0]);g.courtyard.shoppers.traffic_elapsed=201
        with tempfile.TemporaryDirectory() as directory:
            g.save_store=SaveStore(directory,enabled=True);self.assertTrue(g.save_store.save(g))
            data=snapshot(g);restore_state(data,g);self.assertEqual(snapshot(g),data)
            self.assertEqual(g.scene,'courtyard');g.draw();g.leave_courtyard();g.draw()
        legacy=snapshot(Game());del legacy['courtyard'];del legacy['traffic_clock']
        for key in list(legacy['upgrades']):
            if key.startswith('courtyard_'):del legacy['upgrades'][key]
        restore_state(legacy,g);self.assertEqual(g.scene,'mall');self.assertFalse(g.courtyard.unlocked)
        self.assertIsNone(g.courtyard.world)

    def test_old_seating_overlap_migrates_janitors_and_active_events(self):
        g=self.g
        for trash in g.mall.trash:g.mall.clean_trash(trash)
        for store in g.mall.stores:store.restored=True
        g.cash=100000;g.janitors.purchase('north','hire',g)
        tables=list(g.mall.social_tables)
        g.janitors.people['north'].position=tables[1].position+pygame.Vector2(0,30)
        for table in tables:g.mall.obstacles.remove(table.footprint)
        g.mall.social_tables=[]
        from systems.mall_life import EventSpot
        g.life.active='north';g.life.spot=EventSpot(tables[0].position+pygame.Vector2(0,30),g.life.event.title);g.life.sync_spots(g.mall)
        old_position=g.janitors.people['north'].position.copy();data=snapshot(g)
        restore_state(data,g)
        self.assertNotEqual(g.janitors.people['north'].position,old_position)
        self.assertEqual(len(g.mall.suspended_tables),1)
        restore_state(snapshot(g),g)
        g.life.active=None;g.life.spot=None;g.life.sync_spots(g.mall)
        self.assertEqual(len(g.mall.social_tables),2)

    def test_corrupt_courtyard_save_does_not_mutate_live_game(self):
        self.enter();g=self.g;before=snapshot(g);bad=copy.deepcopy(before);bad['courtyard']['stores'][2]=True
        with self.assertRaises(ValueError):restore_state(bad,g)
        self.assertEqual(snapshot(g),before)
        bad=copy.deepcopy(before);bad['upgrades']['courtyard_service_level']=99
        with self.assertRaises(ValueError):restore_state(bad,g)
        self.assertEqual(snapshot(g),before)

    def test_wall_doors_are_reachable_and_return_to_the_new_threshold(self):
        world=self.enter();g=self.g;paths=Walkways();paths.refresh(g.mall)
        door=g.courtyard.door(g.mall)
        self.assertGreater(door.anchor.x+56,g.mall.commons.area.right)
        self.assertLess(door.position.x,g.mall.commons.area.right)
        self.assertIsNotNone(paths.route(g.mall.entrance,door.position))
        paths.refresh(world)
        self.assertLess(g.courtyard.return_door.anchor.x-56,world.opening_area.left)
        self.assertIsNotNone(paths.route(world.entrance,g.courtyard.return_door.position))
        g.main_position=pygame.Vector2(1888,2122)  # Previous preview's floating door.
        g.welcome.open=False;g.player.rect.center=(70,775);g.update(.05,(-1,0))
        self.assertEqual(g.player.rect.center,tuple(door.position));self.assertNotIsInstance(g.target(),SceneDoor)

    def test_shared_outdoor_hud_journal_tabs_and_cook_prompt(self):
        world=self.enter();g=self.g
        for t in world.trash:world.clean_trash(t)
        for store in world.stores:store.restored=True
        g.player.rect.center=world.stores[1].position
        g.courtyard.kitchen_requests.waits['Hearth Pizza']=0
        self.assertEqual(g.hud.prompt(g,g.target()),('E / click','Help cook at Hearth Pizza'))
        with patch.object(g.hud,'draw',wraps=g.hud.draw) as hud:
            g.draw();hud.assert_called_once()
        g.journal.open=True
        for key,tab in ((pygame.K_1,0),(pygame.K_2,1),(pygame.K_3,2),(pygame.K_4,3)):
            g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key))
            self.assertEqual(g.journal.tab,tab);g.draw()
        with patch.object(g.life,'start') as start:
            g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN));start.assert_not_called()
        self.assertIn('Return',g.journal.notice)

    def test_courtyard_menus_and_art_render_at_minimum_resolution(self):
        world=self.enter();g=self.g;g.screen=pygame.display.set_mode((800,600))
        for state in (False,True):
            for s in world.stores:s.restored=state
            for s in world.stores:g.player.rect.center=s.position;g.frame_camera(g.screen.get_size());g.draw()
        g.open_upgrade_shop(world.stores[0])
        for category in range(3):g.shop_menu.category=category;g.shop_menu.selection=0;g.draw()
        g.shop_menu.open=False;g.journal.open=True;g.draw();g.journal.open=False
        g.pause.show();g.draw();g.pause.open=False;g.settings_menu.open=True;g.draw()
