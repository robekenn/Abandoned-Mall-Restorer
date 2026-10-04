"""Shared visitor entry, uninterrupted crossings and persistent discovery locations."""
import copy
import os
import tempfile
import unittest
from unittest.mock import patch
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
import pygame
from game.game import Game
from systems.shoppers import Shopper
from systems.saves import snapshot,restore_state


class CourtTransitionTests(unittest.TestCase):
    def setUp(self):self.game=Game(developer=True)
    def tearDown(self):pygame.quit()

    def open_all(self):
        g=self.game
        for region in g.mall.regions:
            for t in g.mall.trash:g.mall.clean_trash(t)
            for s in g.mall.stores:s.restored=True
            g.mall.refresh_businesses();self.assertTrue(g.mall.unlock_section(region))
        for s in g.mall.stores:s.restored=True
        g.shoppers.walkways.refresh(g.mall)

    def test_all_forty_stores_have_safe_routes_from_the_shared_visible_door(self):
        self.open_all();g=self.game;paths=g.shoppers.walkways
        self.assertTrue(g.mall.entrance_rect.collidepoint(g.mall.entrance))
        for store in g.mall.stores:
            with self.subTest(store=store.name):
                route=paths.route(g.mall.entrance,store.position)
                self.assertIsNotNone(route)
                self.assertEqual(route[-1],store.position)
                for a,b in zip([g.mall.entrance]+route,route):
                    self.assertFalse(any(w.clipline(a,b) for w in paths.walls))
                g.shoppers.people=[];g.shoppers.elapsed=8
                g.shoppers.update(0,g.mall,g.upgrades,store)
                self.assertEqual(g.shoppers.people[0].entrance,g.mall.entrance)
                self.assertEqual(g.shoppers.people[0].position,g.mall.entrance)

    def test_visitors_cross_courts_enter_real_doors_and_leave_only_at_main_entry(self):
        self.open_all();g=self.game;g.upgrades.decor.update(('bench_0','fountain'))
        for court in g.janitors.courts(g.mall):
            for store in (court[3][1],court[3][-1]):
                with self.subTest(store=store.name):
                    p=Shopper(0,g.mall.entrance,store,g.shoppers.walkways);states=set()
                    for _ in range(2500):
                        before=p.position.copy();p.update(.1,g.shoppers,g.mall,g.upgrades);states.add(p.state)
                        self.assertLessEqual(p.position.distance_to(before),8.601)
                        if p.state not in ('inside','entering','exiting'):
                            footprint=pygame.FRect(p.position.x-10,p.position.y-12,20,24)
                            self.assertFalse(any(w.colliderect(footprint) for w in g.mall.obstacles))
                        if p.done:break
                    self.assertTrue({'entering','inside','exiting','leaving'}<=states)
                    self.assertTrue(p.done);self.assertLess(p.position.distance_to(g.mall.entrance),1)

    def test_missing_route_does_not_hide_or_send_a_person_through_walls(self):
        self.open_all();g=self.game;store=g.mall.commons.stores[1]
        p=Shopper(0,g.mall.entrance,store,g.shoppers.walkways)
        p.position=pygame.Vector2(391,967);p.path=[]
        with patch.object(g.shoppers.walkways,'route',return_value=None):
            for state in ('arriving','leaving'):
                p.state=state;p.update(.1,g.shoppers,g.mall,g.upgrades)
                self.assertTrue(p.visible);self.assertFalse(p.done);self.assertEqual(p.state,state)
        nodes=g.shoppers.walkways.nodes
        with patch.object(g.shoppers.walkways,'edges',{p:[] for p in nodes}):
            self.assertIsNone(g.shoppers.walkways.route(g.mall.entrance,store.position))

    def test_walking_through_each_open_connection_keeps_visitors_alive(self):
        self.open_all();g=self.game;g.shoppers.elapsed=-1000
        person=Shopper(0,g.mall.entrance,g.mall.commons.stores[-1],g.shoppers.walkways);g.shoppers.people=[person]
        crossings=[((1710,1000),(1,0)),((160,1430),(0,1)),((1710,2500),(1,0)),((1860,1430),(0,1))]
        for origin,direction in crossings:
            g.player.rect.center=origin
            for _ in range(16):
                before=person.position.copy();g.update(.05,direction)
                self.assertIn(person,g.shoppers.people);self.assertTrue(person.visible)
                self.assertLessEqual(person.position.distance_to(before),4.301)
            expected=pygame.Vector2(origin)+pygame.Vector2(direction)*192
            self.assertLess(pygame.Vector2(g.player.rect.center).distance_to(expected),.1)

    def test_camera_crossings_are_continuous_and_vertical_tracking_never_reverses(self):
        self.open_all();g=self.game;g.screen=pygame.display.set_mode((800,600))
        for origin,direction in (((1725,1000),(1,0)),((160,1300),(0,1)),((1725,2500),(1,0))):
            offsets=[]
            for n in range(440 if direction[1] else 100):
                g.player.rect.center=pygame.Vector2(origin)+pygame.Vector2(direction)*n;g.frame_camera((800,600));offsets.append(g.camera.offset.copy())
            changes=[b-a for a,b in zip(offsets,offsets[1:])]
            self.assertTrue(all(d.length()<1.6 for d in changes))
            if direction[1]:self.assertTrue(all(d.y>=0 for d in changes))

    def test_keepsakes_are_scattered_varied_safe_and_retained_in_a_checkpoint(self):
        self.open_all();g=self.game;layouts=[]
        for seed in (9,22,713):
            g.story.seed=seed;g.story.setup(g.mall);layout=[]
            for i in range(4):
                board=next(p for p in g.story.points if p.chapter==i and p.memory<0)
                ground=[p for p in g.story.points if p.chapter==i and p.source=='ground']
                neighbors=[p for p in g.story.points if p.chapter==i and p.source=='neighbor']
                self.assertEqual((len(ground),len(neighbors)),(2,1))
                self.assertGreater(ground[0].position.distance_to(ground[1].position),700)
                self.assertTrue(all(p.position.distance_to(board.position)>300 for p in ground))
                for p in ground+neighbors:
                    self.assertIsNotNone(g.shoppers.walkways.route(g.mall.entrance,p.position))
                    self.assertFalse(any(w.colliderect(pygame.FRect(p.position.x-13,p.position.y-15,26,30)) for w in g.mall.obstacles))
                    layout.append((p.chapter,p.memory,tuple(p.position),p.source))
            layouts.append(layout)
        self.assertNotEqual(layouts[0],layouts[1])
        data=snapshot(g);restore_state(data,g)
        self.assertCountEqual([(p.chapter,p.memory,tuple(p.position),p.source) for p in g.story.points if p.memory>=0],layouts[-1])

    def test_discovery_layout_does_not_shift_after_unlocks_and_continue(self):
        g=self.game;g.story.seed=71;g.story.setup(g.mall)
        original=[(tuple(p.position),p.source) for p in g.story.points]
        self.open_all();restore_state(snapshot(g),g)
        self.assertEqual([(tuple(p.position),p.source) for p in g.story.points],original)

    def test_talking_to_a_keeper_with_full_bag_recovers_once_and_neighbor_leaves(self):
        g=self.game;g.story.confirm(g,0,'begin');g.upgrades.held=1
        keeper=g.story.visible_neighbors(g.mall)[0];g.player.rect.center=keeper.position
        self.assertIs(g.target(),keeper);g.interact()
        self.assertTrue(g.story.memories[0][keeper.memory]);self.assertEqual(g.upgrades.held,1)
        self.assertNotIn(keeper,g.story.visible_neighbors(g.mall));self.assertIn('found this',g.speech.text)
        cash=g.cash;self.assertFalse(g.story.action(keeper,g));self.assertEqual(g.cash,cash)
        self.assertFalse(g.story_menu.open)

    def test_old_checkpoints_migrate_discovery_without_losing_completed_memories(self):
        g=self.game;g.story.started[0]=True;g.story.memories[0][1]=True
        data=snapshot(g);del data['story']['seed'];restore_state(data,g)
        self.assertTrue(g.story.memories[0][1]);self.assertEqual(g.story.seed,0)
        # Subsequent restores use the stored seed and preserve placements.
        first=[tuple(p.position) for p in g.story.points];restore_state(snapshot(g),g)
        self.assertEqual(first,[tuple(p.position) for p in g.story.points])

    def test_lanterns_attach_to_both_storefront_facings_only_after_chapter_claim(self):
        g=self.game;g.story.prepare(g)
        with patch.object(g.art,'draw',wraps=g.art.draw) as draw:
            g.story.draw(g);self.assertFalse(any(c.args[1].startswith('festival_lantern') for c in draw.call_args_list))
        g.story.confirm(g,0,'claim')
        with patch.object(g.art,'draw',wraps=g.art.draw) as draw:
            g.story.draw(g)
        calls=[c for c in draw.call_args_list if c.args[1].startswith('festival_lantern')]
        stores=[s for s in g.mall.north_stores if s.restored]
        expected=[g.camera.point(p) for s in stores for p in g.story.lantern_positions(s)]
        self.assertEqual([c.args[2] for c in calls],expected)
        for store in stores:
            positions=g.story.lantern_positions(store)
            if store.facing=='up':
                self.assertTrue(all(store.rect.left<x<store.rect.right and y==store.rect.top+24 for x,y in positions))
            else:self.assertTrue(all(store.rect.collidepoint(p) for p in positions))
        north_calls=[c for c in calls if c.args[1].startswith('festival_lantern_north_')]
        self.assertEqual(len(north_calls),4*sum(s.facing=='up' for s in stores))
        self.assertTrue(all(c.args[3]==(48,48) for c in north_calls))
        # The angled rectangular lamp is drawn separately from the facade lamp.
        sprite=g.art.sprites['festival_lantern_north_0']
        self.assertEqual(sprite.get_size(),(8,8))
        original=pygame.transform.flip(g.art.sprites['festival_lantern_0'],False,True)
        self.assertNotEqual(pygame.image.tobytes(sprite,'RGBA'),pygame.image.tobytes(original,'RGBA'))

    def test_reaching_animation_expires_without_changing_collision_or_idle_scale(self):
        g=self.game;before=g.player.rect.copy();g.player.use_tool('dirt',(300,430))
        g.screen=pygame.display.set_mode((800,600))
        for _ in range(4):g.draw();g.player.move((0,0),.105,g.mall.obstacles)
        self.assertEqual(g.player.rect,before);self.assertAlmostEqual(g.player.action_time,0)
        g.draw();self.assertEqual(g.art.sprites['player_right_clean_0'].get_size(),(16,24))
