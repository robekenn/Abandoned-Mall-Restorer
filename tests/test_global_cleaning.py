"""Offscreen staff work and one floor-weighted cleanliness figure across maps."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from tests import test_feature_expansion as helpers
from systems.saves import snapshot, restore_state
from systems.economy import cleanliness_label


class GlobalCleaningTests(unittest.TestCase):
    def setUp(self):
        self.helper=helpers.FeatureTests();self.helper.setUp()
        self.world=self.helper.enter();self.g=self.helper.g
        self.g.player.rect.center=self.world.entrance
        self.g.cash=10000000
        for key,_,_,_,_,_,_ in self.g.janitors.courts(self.g.mall):
            self.assertTrue(self.g.janitors.purchase(key,'hire',self.g)[0])
        self.assertTrue(self.g.courtyard.janitors.purchase('courtyard','hire',self.g,self.world)[0])

    def tearDown(self):self.helper.tearDown()

    def prepare_work(self):
        g=self.g
        jobs=[]
        for world,manager in ((g.mall,g.janitors),(self.world,g.courtyard.janitors)):
            for trash in world.trash:world.clean_trash(trash)
            for key,_,_,_,pool,_,_ in manager.courts(world):
                worker=manager.people[key]
                trash=next(t for t in pool if tuple(t.position) in worker.paths.nodes)
                world.respawn_trash(trash)
                worker.position=trash.position.copy();worker.target=trash
                worker.target_revision=getattr(trash,'revision',0);worker.path=[];worker.progress=4
                jobs.append((worker,trash))
        return jobs

    def test_all_five_workers_finish_once_from_either_map_and_only_local_popups_show(self):
        g=self.g
        for scene in ('courtyard','mall'):
            with self.subTest(scene=scene):
                if scene=='mall':g.leave_courtyard()
                jobs=self.prepare_work();cash=g.cash;before=g.cleanliness
                g.feedback.popups.clear();g.rent_timer=0
                g.update(1,(0,0))
                self.assertTrue(all(t.cleaned for _,t in jobs))
                self.assertTrue(all(j.progress==0 and j.target is None for j,_ in jobs))
                self.assertEqual(g.cash-cash,5*.75*g.upgrades.unit_value)
                self.assertEqual([j.cleaned for j,_ in jobs],[1 if scene=='courtyard' else 2]*5)
                self.assertGreater(g.cleanliness,before)
                self.assertEqual(len(g.feedback.popups),1 if scene=='courtyard' else 4)

    def test_clean_hud_is_weighted_by_floor_tiles_and_identical_on_both_maps(self):
        g=self.g
        g.mall.dirty_tiles=set(g.mall.floor_tiles);self.world.dirty_tiles.clear()
        expected=len(self.world.floor_tiles)/(len(g.mall.floor_tiles)+len(self.world.floor_tiles))
        self.assertAlmostEqual(g.cleanliness,expected)
        self.assertNotAlmostEqual(g.cleanliness,.5)
        for scene in ('courtyard','mall'):
            if scene=='mall':g.leave_courtyard()
            with patch('ui.hud.cleanliness_label',wraps=cleanliness_label) as label:
                g.hud.draw(g,None)
                label.assert_called_once_with(g.cleanliness)
            self.assertAlmostEqual(g.cleanliness,expected)

    def test_locked_courtyard_does_not_count_or_get_created(self):
        g=Game()
        self.assertIsNone(g.courtyard.world)
        self.assertEqual(g.cleanliness,g.mall.cleanliness)
        g.update_janitors(1)
        self.assertIsNone(g.courtyard.world)

    def test_pause_menus_and_tutorial_freeze_both_crews(self):
        g=self.g;jobs=self.prepare_work()
        for scene in ('courtyard','mall'):
            if scene=='mall':g.leave_courtyard()
            for modal in (g.pause,g.settings_menu,g.journal,g.shop_menu,g.owner_menu,g.display_menu,g.developer,g.story_menu,g.community_menu,g.welcome):
                modal.open=True;g.update(1,(0,0));modal.open=False
                self.assertTrue(all(j.progress==4 and not t.cleaned for j,t in jobs))
            with patch.object(type(g.tutorial),'paused',new_callable=lambda:property(lambda _:True)):
                g.update(1,(0,0))
            self.assertTrue(all(j.progress==4 and not t.cleaned for j,t in jobs))

    def test_continue_restores_partial_work_then_background_completions(self):
        g=self.g;self.prepare_work();data=snapshot(g)
        restore_state(data,g)
        self.assertEqual(snapshot(g),data)
        g.update(1,(0,0))
        self.assertTrue(all(j.cleaned==1 for j in g.janitors.people.values()))
        self.assertEqual(g.courtyard.janitors.people['courtyard'].cleaned,1)
        completed=snapshot(g);restore_state(completed,g)
        self.assertEqual(snapshot(g),completed)
