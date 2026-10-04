"""Real kitchen input, safe payouts, pause behavior and compatible checkpoints."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy');os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import copy
import random
import unittest
from unittest.mock import patch
import pygame
from systems.cooking import CookingRound, RECIPES, KitchenRequests
from systems.saves import snapshot, restore_state
from tests import test_feature_expansion as helpers


class RecipeTests(unittest.TestCase):
    def test_every_recipe_can_finish_and_wrong_actions_do_not_skip_steps(self):
        for name,recipe in RECIPES.items():
            with self.subTest(name=name):
                r=CookingRound(name,random.Random(17))
                for step in range(recipe.steps):
                    wrong=(r.order[step]+1)%len(recipe.choices or ('Left','Right','Up','Down')) if r.order else 0
                    if step==0:self.assertFalse(r.action(wrong));self.assertEqual(r.step,step)
                    if r.order:self.assertTrue(r.action(r.order[step]))
                    else:
                        r.update(r.target*r.sweep_seconds);self.assertTrue(r.action())
                self.assertTrue(r.complete);self.assertEqual(r.mistakes,1)
                self.assertFalse(r.action());self.assertEqual(r.step,recipe.steps)
                elapsed=r.elapsed;r.update(20);self.assertEqual(r.elapsed,elapsed)

    def test_timing_band_can_be_hit_on_both_directions_and_order_variants_exist(self):
        for name in ('Orchard Juice','Copper Grill'):
            r=CookingRound(name,random.Random(3));r.update((2-r.target)*r.sweep_seconds)
            self.assertTrue(r.action());self.assertEqual(r.mistakes,0)
        for name in RECIPES:
            variants={tuple(CookingRound(name,random.Random(i)).order) if RECIPES[name].mode not in ('pour','grill') else tuple(CookingRound(name,random.Random(i)).targets) for i in range(10)}
            self.assertGreater(len(variants),1,name)


class CookingTests(unittest.TestCase):
    def setUp(self):
        self.helper=helpers.FeatureTests();self.helper.setUp();self.world=self.helper.enter();self.g=self.helper.g
        for t in self.world.trash:self.world.clean_trash(t)
        for store in self.world.stores:store.restored=True
        self.world.refresh_businesses()
        self.g.courtyard.kitchen_requests.pending='Hearth Pizza';self.g.courtyard.kitchen_requests.wait=0
    def tearDown(self):self.helper.tearDown()

    def key(self,key,**extra):self.g.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key,**extra))
    def click(self,point):self.g.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=point))

    def open(self,store):
        g=self.g;g.courtyard.kitchen_requests.pending=store.name;g.courtyard.kitchen_requests.wait=0;g.player.rect.center=store.position;g.frame_camera(g.screen.get_size());g.interact()
        self.assertTrue(g.cooking_menu.open);return g.cooking_menu

    def finish(self,menu,mouse=False):
        self.key(pygame.K_RETURN)
        while not menu.round.complete:
            r=menu.round
            index=r.order[r.step] if r.order else 0
            if not r.order:self.g.update(r.target*r.sweep_seconds,(1,0))
            if mouse:self.click(menu.choice_rects(self.g.screen)[index].center)
            else:self.key(pygame.K_1+index if r.recipe.mode=='ingredients' else (pygame.K_LEFT,pygame.K_RIGHT,pygame.K_UP,pygame.K_DOWN)[index] if r.order else pygame.K_SPACE)

    def test_all_restaurants_have_real_input_and_single_payout_then_replay(self):
        g=self.g
        for i,store in enumerate(self.world.stores[1:]):
            menu=self.open(store);cash=g.cash
            self.finish(menu,mouse=i%2==0)
            self.assertEqual(g.cash-cash,round(store.base_rent*.25))
            self.assertEqual(g.courtyard.cooking[store.name],{'served':1,'best':100,'tips':menu.tip,'failed':0})
            paid=g.cash;self.assertEqual(menu.round.finish(g,store),0);self.assertEqual(g.cash,paid)
            self.key(pygame.K_RETURN);self.assertFalse(menu.open)
            g.interact();self.assertFalse(menu.open)
            self.assertFalse(menu.open);self.assertEqual(g.cash,paid)

    def test_click_counter_opens_kitchen_and_distant_click_does_not(self):
        g=self.g;store=self.world.stores[1]
        g.player.rect.center=self.world.entrance;g.frame_camera(g.screen.get_size())
        g.courtyard.pickup_at(g,g.camera.point(store.position));self.assertFalse(g.cooking_menu.open)
        g.player.rect.center=store.position;g.frame_camera(g.screen.get_size())
        self.click(g.camera.point(store.rect.center));self.assertTrue(g.cooking_menu.open)
        self.key(pygame.K_ESCAPE)
        g.interact();self.assertTrue(g.cooking_menu.open)
        self.assertEqual(g.hud.prompt(g,store),('E / click','Help cook at Hearth Pizza'))

    def test_cancel_and_key_repeat_do_not_pay_or_advance_and_provisions_stays_shop(self):
        g=self.g;menu=self.open(self.world.stores[1]);cash=g.cash
        self.key(pygame.K_RETURN);correct=menu.round.order[0]
        self.key(pygame.K_1+correct,repeat=True);self.assertEqual(menu.round.step,0)
        g.interact();self.assertEqual(menu.round.step,0)
        self.key(pygame.K_ESCAPE);self.assertEqual(g.cash,cash-round(self.world.stores[1].base_rent*.1));self.assertEqual(g.courtyard.cooking['Hearth Pizza']['failed'],1)
        store=self.world.stores[0];g.player.rect.center=store.position;g.interact()
        self.assertTrue(g.shop_menu.open);self.assertFalse(menu.open)
        g.shop_menu.open=False;self.assertFalse(menu.visit(store,g))
        self.world.stores[1].restored=False;self.assertFalse(menu.visit(self.world.stores[1],g))

    def test_cooking_pauses_world_but_timer_runs_and_overlays_pause_cooking(self):
        g=self.g;menu=self.open(self.world.stores[3]);self.key(pygame.K_RETURN)
        before=snapshot(g);position=g.player.rect.center
        g.update(.5,(1,0),True)
        self.assertEqual(menu.round.elapsed,.5);self.assertEqual(g.player.rect.center,position)
        self.assertEqual(snapshot(g),before)
        for overlay in (g.settings_menu,g.pause):
            overlay.open=True;g.update(2,(1,0));overlay.open=False
            self.assertEqual(menu.round.elapsed,.5)
        self.key(pygame.K_j);self.assertFalse(g.journal.open)
        self.key(pygame.K_ESCAPE);g.update(.1,(0,0));self.assertGreater(g.rent_timer,before['rent_timer'])

    def test_completed_stats_survive_continue_and_old_saves_and_invalid_save_is_atomic(self):
        g=self.g;menu=self.open(self.world.stores[1]);self.finish(menu)
        data=snapshot(g);restore_state(data,g)
        self.assertEqual(snapshot(g),data);self.assertFalse(g.cooking_menu.open)
        for value in (-1,True,101):
            bad=copy.deepcopy(data);bad['courtyard']['cooking']['Hearth Pizza']['best']=value
            with self.assertRaises(ValueError):restore_state(bad,g)
            self.assertEqual(snapshot(g),data)
        bad=copy.deepcopy(data);bad['courtyard']['cooking']['Imaginary kitchen']={'served':1,'best':100,'tips':10}
        with self.assertRaises(ValueError):restore_state(bad,g)
        self.assertEqual(snapshot(g),data)
        old=copy.deepcopy(data);del old['courtyard']['cooking'];restore_state(old,g)
        self.assertFalse(g.courtyard.cooking);self.assertEqual(g.cash,data['cash'])

    def test_all_kitchens_render_intro_play_result_and_fit_small_window(self):
        g=self.g;g.screen=pygame.display.set_mode((800,600))
        for store in self.world.stores[1:]:
            menu=self.open(store);g.draw()
            panel,body,button,close=menu.geometry(g.screen)
            self.assertTrue(g.screen.get_rect().contains(panel))
            self.assertTrue(all(panel.contains(r) for r in [body,button,close]+menu.choice_rects(g.screen)))
            self.key(pygame.K_RETURN);g.draw()
            while not menu.round.complete:
                r=menu.round
                if not r.order:g.update(r.target*r.sweep_seconds,(0,0))
                menu.act(r.order[r.step] if r.order else 0,g);g.draw()
            self.key(pygame.K_ESCAPE)

    def test_request_gate_shared_cooldown_and_background_updates_without_swarm(self):
        g=self.g;q=g.courtyard.kitchen_requests;q.pending=None;q.wait=1
        store=self.world.stores[1];g.player.rect.center=store.position;g.interact()
        self.assertFalse(g.cooking_menu.open)
        g.leave_courtyard();g.update(.5,(0,0));self.assertAlmostEqual(q.wait,.5)
        g.journal.open=True;g.update(100,(0,0));g.journal.open=False;self.assertAlmostEqual(q.wait,.5)
        g.update(.5,(0,0));self.assertIn(q.pending,RECIPES)
        name=q.pending;g.update(100,(0,0));self.assertEqual(q.pending,name)
        self.assertTrue(q.accept(name));self.assertIsNone(q.pending);self.assertGreaterEqual(q.wait,180);self.assertLessEqual(q.wait,600)
        self.assertFalse(q.accept(name));q.wait=0;q.update(0,g);self.assertNotEqual(q.pending,name)

    def test_three_mistakes_forfeit_deposit_once_and_block_immediate_retry(self):
        g=self.g;store=self.world.stores[1];menu=self.open(store);cash=g.cash
        self.key(pygame.K_RETURN);fee=menu.round.deposit
        for _ in range(3):menu.act((menu.round.order[0]+1)%5,g)
        self.assertTrue(menu.round.failed);self.assertEqual(g.cash,cash-fee)
        self.assertEqual(g.courtyard.cooking[store.name]['failed'],1)
        g.update(1,(0,0));menu.act(0,g);self.assertEqual(g.cash,cash-fee)
        self.assertEqual(g.courtyard.cooking[store.name]['failed'],1)
        self.key(pygame.K_RETURN);g.interact();self.assertFalse(menu.open)
        self.assertIsNone(g.courtyard.kitchen_requests.pending)

    def test_progressive_ingredient_timeout_and_timing_bands_are_capped(self):
        g=self.g;store=self.world.stores[1]
        g.courtyard.cooking[store.name]={'served':15,'best':100,'tips':0,'failed':0}
        menu=self.open(store);self.assertEqual(menu.round.level,5);self.assertEqual(menu.round.remaining,4.5)
        cash=g.cash;self.key(pygame.K_RETURN);g.update(4.5,(0,0));self.assertTrue(menu.round.failed)
        self.assertEqual(g.cash,cash-menu.round.deposit);g.draw()
        novice=CookingRound('Orchard Juice');expert=CookingRound('Orchard Juice',served=15)
        capped=CookingRound('Orchard Juice',served=1000)
        self.assertLess(expert.band,novice.band);self.assertLess(expert.sweep_seconds,novice.sweep_seconds)
        self.assertEqual(capped.band,expert.band);self.assertEqual(capped.sweep_seconds,expert.sweep_seconds)
        for r in (novice,expert):r.elapsed=(r.target+.075)*r.sweep_seconds
        self.assertTrue(novice.action());self.assertFalse(expert.action())

    def test_wrong_ingredient_costs_time_and_tip_but_success_refunds_deposit(self):
        g=self.g;store=self.world.stores[1];menu=self.open(store);cash=g.cash
        self.key(pygame.K_RETURN);menu.act((menu.round.order[0]+1)%5,g)
        self.assertEqual(menu.round.remaining,10);self.assertEqual(menu.round.score,80)
        for _ in range(3):menu.act(menu.round.order[menu.round.step],g)
        tip=round(store.base_rent*.25*.8);self.assertEqual(g.cash,cash+tip)
        g.update(.5,(0,0));self.assertEqual(menu.tip,tip)
        g.draw()

    def test_intro_cancel_and_insufficient_deposit_keep_request_and_accepted_save_cannot_retry(self):
        g=self.g;store=self.world.stores[1];menu=self.open(store);g.cash=0
        self.key(pygame.K_RETURN);self.assertFalse(menu.started);self.assertIn('deposit',menu.round.notice)
        self.assertEqual(g.courtyard.kitchen_requests.pending,store.name);g.draw()
        self.key(pygame.K_ESCAPE);self.assertEqual(g.courtyard.kitchen_requests.pending,store.name)
        g.cash=100;menu=self.open(store);self.key(pygame.K_RETURN);data=snapshot(g)
        restore_state(data,g);self.assertEqual(g.cash,75);self.assertIsNone(g.courtyard.kitchen_requests.pending)
        self.assertEqual(snapshot(g),data);g.interact();self.assertFalse(g.cooking_menu.open)
        bad=copy.deepcopy(data);bad['courtyard']['kitchen_requests']['wait']=-1
        with self.assertRaises(ValueError):restore_state(bad,g)
        self.assertEqual(snapshot(g),data)
        old=copy.deepcopy(data);del old['courtyard']['kitchen_requests'];restore_state(old,g)
        self.assertGreaterEqual(g.courtyard.kitchen_requests.wait,180)
