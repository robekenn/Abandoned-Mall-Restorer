"""Every menu's Enter actions are reachable through actual left-click events."""

import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import unittest
import pygame
from game.game import Game
from tests import test_feature_expansion as helpers


class ClickConfirmationTests(unittest.TestCase):
    def setUp(self):
        self.g = Game(developer=True)
        self.g.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        pygame.quit()

    def click(self, rect):
        point = rect.center
        self.g.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=point))
        self.g.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=point))

    def action(self, position):
        self.g.player.rect.center = position
        self.g.frame_camera(self.g.screen.get_size())
        self.click(self.g.hud.button_rects(self.g.screen)['action'])

    def enter_courtyard(self):
        helper = helpers.FeatureTests()
        helper.g = self.g
        return helper.enter()

    def restore_north(self):
        g = self.g
        for trash in g.mall.north_trash:
            g.mall.clean_trash(trash)
        for store in g.mall.north_stores[:3]:
            store.restored = True
        g.mall.refresh_businesses()

    def test_tutorial_and_story_continue_with_clicks(self):
        g = self.g
        g.tutorial.start(g)
        self.assertTrue(g.world_paused)
        self.click(g.tutorial.geometry(g.screen)[1])
        self.assertFalse(g.tutorial.explaining)
        self.assertTrue(g.tutorial.active)
        g.tutorial.skip()
        self.action(g.story.points[0].position)
        self.assertTrue(g.story_menu.open)
        self.click(g.story_menu.geometry(g.screen)[1])
        self.assertFalse(g.story_menu.open)
        self.assertTrue(g.story.started[0])

    def test_owner_request_acceptance_and_reward_use_the_clickable_button(self):
        g = self.g
        self.restore_north()
        store = g.mall.stores[1]
        store.request_wait = 0
        self.action(store.position)
        self.assertTrue(g.owner_menu.open)
        self.click(g.owner_menu.geometry(g.screen)[1])
        self.assertFalse(g.owner_menu.open)
        self.assertIs(g.owner_requests.store, store)
        self.action(g.owner_requests.spots[0].position)
        self.assertTrue(g.owner_requests.ready)
        self.action(store.position)
        self.click(g.owner_menu.geometry(g.screen)[1])
        self.assertEqual(store.request_level, 1)
        self.assertEqual(g.cash, 50)
        self.assertIsNone(g.owner_requests.store)

    def test_gathering_host_choices_and_final_reward_are_clickable(self):
        g = self.g
        self.restore_north()
        g.journal.open = True
        self.click(g.journal.tabs(g.screen)[3])
        self.click(g.journal.life_rows(g.screen)[0])
        self.assertFalse(g.journal.open)
        self.assertEqual(g.life.active, 'north')
        self.action(g.life.spot.position)
        self.assertTrue(g.community_menu.open)
        for round_number in range(3):
            answer = g.life.guest(round_number)[2]
            self.click(g.community_menu.geometry(g.screen)[1][answer])
            self.assertEqual(g.life.round, round_number + 1)
        self.click(g.community_menu.geometry(g.screen)[1][0])
        self.assertFalse(g.community_menu.open)
        self.assertIsNone(g.life.active)
        self.assertEqual(g.life.completed['north'], 1)
        self.assertEqual(g.cash, 200)

    def test_hire_janitors_with_clicks_in_both_scenes(self):
        g = self.g
        for outside in (False, True):
            if outside:
                self.enter_courtyard()
            g.cash = 2_000_000
            g.journal.open = True
            self.click(g.journal.tabs(g.screen)[1])
            manager, world = g.journal.staff_context(g)
            key = manager.courts(world)[0][0]
            self.click(g.journal.staff_buttons(g.journal.staff_rows(g.screen)[0])['hire'])
            self.assertIn(key, manager.people)
            self.assertLess(g.cash, 2_000_000)
            g.journal.open = False

    def test_developer_apply_and_pause_confirmation_have_mouse_actions(self):
        g = self.g
        g.developer.open = True
        self.click(g.developer.geometry(g.screen)[1][0])
        self.assertEqual(g.cash, 10_000)
        self.click(g.mouse_controls.back_rect(g))
        g.pause.show()
        self.click(g.pause.geometry(g.screen)[1][4])
        self.assertTrue(g.pause.confirm)
        self.click(g.pause.geometry(g.screen)[1][0])
        self.assertFalse(g.pause.confirm)
        self.assertTrue(g.running)
        self.click(g.pause.geometry(g.screen)[1][4])
        self.click(g.pause.geometry(g.screen)[1][1])
        self.assertFalse(g.running)

    def test_cooking_accept_timing_and_results_buttons_match_enter_actions(self):
        g = self.g
        world = self.enter_courtyard()
        for trash in world.trash:
            world.clean_trash(trash)
        for store in world.stores:
            store.restored = True
        world.refresh_businesses()
        for name in ('Orchard Juice', 'Copper Grill'):
            with self.subTest(kitchen=name):
                store = next(store for store in world.stores if store.name == name)
                g.courtyard.kitchen_requests.waits[name] = 0
                self.action(store.position)
                menu = g.cooking_menu
                self.assertTrue(menu.open)
                self.click(menu.geometry(g.screen)[2])
                self.assertTrue(menu.started)
                while not menu.round.done:
                    menu.round.elapsed = menu.round.target * menu.round.sweep_seconds
                    self.click(menu.choice_rects(g.screen)[0])
                self.assertTrue(menu.round.complete)
                self.assertEqual(g.courtyard.cooking[name]['served'], 1)
                cash = g.cash
                self.click(menu.geometry(g.screen)[2])
                self.assertFalse(menu.open)
                self.assertEqual(g.cash, cash)

