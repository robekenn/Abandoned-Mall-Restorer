"""Both maps stay litter-active, with bounded rates matching their own traffic."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from systems.saves import snapshot,restore_state
from systems.litter import LitterSpawner
from tests import test_feature_expansion as helpers


class BackgroundLitterTests(unittest.TestCase):
    def setUp(self):
        self.helper=helpers.FeatureTests();self.helper.setUp();self.world=self.helper.enter();self.g=self.helper.g
        for t in self.world.trash:self.world.clean_trash(t)
        self.world.stores[0].restored=True;self.world.refresh_businesses()
        self.g.courtyard.kitchen_requests.wait=600
    def tearDown(self):self.helper.tearDown()

    def test_both_maps_spawn_from_either_scene_and_overall_cleanliness_changes(self):
        g=self.g;before=g.cleanliness
        g.update(4,(0,0))
        self.assertEqual((g.mall.active_litter_count,self.world.active_litter_count),(1,1))
        self.assertLess(g.cleanliness,before)
        g.leave_courtyard();g.update(4,(0,0))
        self.assertEqual((g.mall.active_litter_count,self.world.active_litter_count),(2,2))
        self.assertEqual([sum(not t.cleaned for t in pool) for pool in g.mall.recurring_pools],[1,1,0,0])

    def test_every_traffic_interval_spawns_on_both_maps(self):
        g=self.g
        for traffic,seconds in (('Busy hours',2),('Steady hours',4),('Quiet hours',8)):
            for world in (g.mall,self.world):
                for t in world.trash:world.clean_trash(t)
                spawner=LitterSpawner()
                spawner.update(seconds-.1,world,None,traffic=traffic)
                self.assertEqual(world.active_litter_count,0)
                spawner.update(.11,world,None,traffic=traffic)
                self.assertEqual(world.active_litter_count,1)

    def test_indoor_and_courtyard_traffic_are_independent(self):
        g=self.g;g.shoppers.traffic_elapsed=200;g.courtyard.shoppers.traffic_elapsed=100
        for _ in range(4):g.update(2,(0,0))
        self.assertEqual(g.mall.active_litter_count,4);self.assertEqual(self.world.active_litter_count,1)
        self.assertEqual(g.shoppers.traffic,'Busy hours');self.assertEqual(g.courtyard.shoppers.traffic,'Quiet hours')

    def test_busy_litter_preserves_local_caps_and_fair_rotation(self):
        g=self.g;g.shoppers.traffic_elapsed=g.courtyard.shoppers.traffic_elapsed=200
        for _ in range(70):g.update_litter(2)
        self.assertEqual([sum(not t.cleaned for t in pool) for pool in g.mall.recurring_pools],[12]*4)
        self.assertEqual(self.world.active_litter_count,12)

    def test_menus_cooking_and_tutorial_pause_both_spawners(self):
        g=self.g
        for modal in (g.pause,g.settings_menu,g.journal,g.shop_menu,g.owner_menu,g.display_menu,g.developer,g.story_menu,g.community_menu,g.welcome):
            modal.open=True;g.update(4,(0,0));modal.open=False
        with patch.object(type(g.tutorial),'paused',new_callable=lambda:property(lambda _:True)):g.update(4,(0,0))
        g.courtyard.kitchen_requests.pending=self.world.stores[1].name;g.courtyard.kitchen_requests.wait=0
        self.world.stores[1].restored=True
        self.assertTrue(g.cooking_menu.visit(self.world.stores[1],g));g.update(4,(0,0))
        self.assertEqual((g.mall.active_litter_count,self.world.active_litter_count),(0,0))
        self.assertEqual((g.litter_spawner.elapsed,g.courtyard.spawner.elapsed),(0,0))

    def test_rate_change_and_continue_keep_fractional_spawn_progress(self):
        g=self.g
        for spawner,world in ((g.litter_spawner,g.mall),(g.courtyard.spawner,self.world)):
            spawner.update(6,world,None,traffic='Quiet hours')
            self.assertEqual(spawner.elapsed,3)
        data=snapshot(g);restore_state(data,g);self.assertEqual(snapshot(g),data)
        for spawner,world in ((g.litter_spawner,g.mall),(g.courtyard.spawner,g.courtyard.world)):
            spawner.update(.49,world,None,traffic='Busy hours');self.assertEqual(world.active_litter_count,0)
            spawner.update(.02,world,None,traffic='Busy hours');self.assertEqual(world.active_litter_count,1)
            self.assertLess(spawner.elapsed,4)

    def test_unopened_courtyard_and_unfinished_sweep_do_not_spawn(self):
        g=Game();g.update(8,(0,0));self.assertIsNone(g.courtyard.world)
        self.assertEqual(g.mall.active_litter_count,g.mall.initial_litter_count)
        spawner=LitterSpawner();spawner.update(100,g.mall,None,traffic='Busy hours')
        self.assertEqual(spawner.elapsed,0)

    def test_only_active_map_excludes_player_position_from_spawn_choices(self):
        g=self.g
        with patch.object(g.litter_spawner,'update') as indoor,patch.object(g.courtyard.spawner,'update') as outdoor:
            g.update_litter(1)
            self.assertIsNone(indoor.call_args.args[2]);self.assertEqual(outdoor.call_args.args[2],g.player.rect.center)
            g.leave_courtyard();g.update_litter(1)
            self.assertEqual(indoor.call_args.args[2],g.player.rect.center);self.assertIsNone(outdoor.call_args.args[2])
