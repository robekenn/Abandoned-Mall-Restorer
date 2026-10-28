"""Marty's first story project uses real menus and existing save-compatible state."""

import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import tempfile
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from systems.saves import snapshot, restore_state
from systems.story import READING_FIXTURES
from ui import theme


class MaraOpeningTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.g = Game(developer=True, persistence=True, save_dir=self.directory.name)
        self.g.screen = pygame.display.set_mode((800, 600))

    def tearDown(self):
        pygame.quit()
        self.directory.cleanup()

    def click(self, rect):
        self.g.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center))
        self.g.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=rect.center))

    def board(self):
        return next(point for point in self.g.story.points if point.chapter == 0 and point.memory < 0)

    def begin(self):
        self.g.story.action(self.board(), self.g)
        self.click(self.g.story_menu.geometry(self.g.screen)[1])
        self.assertTrue(self.g.story.started[0])

    def sweep(self):
        for trash in self.g.mall.north_trash:
            self.g.mall.clean_trash(trash)

    def buy_reading_places(self):
        g = self.g
        g.cash = 1_000
        for store in g.mall.north_stores[:2]:
            g.player.rect.center = store.position
            g.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
            self.assertTrue(store.restored)
            if g.shop_menu.open:
                self.click(g.mouse_controls.back_rect(g))
        g.open_upgrade_shop(g.mall.north_stores[0])
        g.shop_menu.category = 1
        for key in READING_FIXTURES:
            g.shop_menu.selection = next(i for i, offer in enumerate(g.shop_menu.offers(g)) if offer.key == key)
            g.shop_menu.keep_visible(g)
            self.click(g.shop_menu.purchase_rect(g))
            self.assertIn(key, g.upgrades.decor)
        self.click(g.mouse_controls.back_rect(g))

    def recover_keepsakes(self):
        g = self.g
        for point in (point for point in g.story.points if point.chapter == 0 and point.memory >= 0):
            g.player.rect.center = point.position
            g.interact(point)
            if g.story_menu.open:
                self.click(g.story_menu.geometry(g.screen)[1])
        self.assertEqual(g.story.memories[0], [True] * 3)

    def test_first_circle_can_finish_with_two_shops_and_no_owner_grind(self):
        g = self.g
        self.begin()
        self.sweep()
        self.buy_reading_places()
        self.recover_keepsakes()
        self.assertEqual(sum(store.restored for store in g.mall.north_stores), 2)
        self.assertEqual(sum(store.request_level for store in g.mall.north_stores), 0)
        self.assertTrue(g.story.ready(g, 0))
        cash = g.cash
        g.story.action(self.board(), g)
        self.assertEqual(g.story_menu.action, 'claim')
        before = snapshot(g)
        g.update(20, (1, 0), True)
        self.assertEqual(snapshot(g), before)
        self.click(g.story_menu.geometry(g.screen)[1])
        self.assertTrue(g.story.completed[0])
        self.assertEqual(g.cash, cash + 1_000)
        self.assertFalse(g.story.confirm(g, 0, 'claim'))
        self.assertEqual(g.cash, cash + 1_000)
        goals = g.story.gathering_goals(g.mall, 0)
        self.assertEqual(set(g.mall.community_spots), {tuple(goal) for goal in goals})
        readers = [person for person in g.shoppers.people if person.activity == 'gathering']
        self.assertEqual(len(readers), 3)
        for person in readers:
            self.assertIn(person.goal, goals)
            self.assertTrue(person.path)

    def test_unrelated_fixtures_and_missing_chairs_cannot_claim_the_circle(self):
        g = self.g
        self.sweep()
        self.begin()
        g.mall.north_stores[1].restored = True
        self.recover_keepsakes()
        g.upgrades.decor.update(('bench_0', 'bench_1', 'fountain'))
        self.assertFalse(g.story.ready(g, 0))
        self.assertIn('table 1', g.story.hud_goal(g)[1])
        for missing in READING_FIXTURES:
            g.upgrades.decor.update(READING_FIXTURES)
            g.upgrades.decor.remove(missing)
            cash = g.cash
            g.story.action(self.board(), g)
            self.assertIsNone(g.story_menu.action)
            self.click(g.story_menu.geometry(g.screen)[1])
            self.assertFalse(g.story.completed[0])
            self.assertEqual(g.cash, cash)

    def test_earlier_restoration_counts_and_partial_project_survives_continue(self):
        g = self.g
        self.sweep()
        self.buy_reading_places()
        self.begin()
        self.recover_keepsakes()
        g.upgrades.decor.remove('table_0_seat_1')
        self.assertTrue(g.save_checkpoint())
        h = Game(developer=True, persistence=True, save_dir=self.directory.name)
        self.assertTrue(h.save_store.load(h))
        self.assertTrue(h.story.started[0])
        self.assertEqual(h.story.memories[0], [True] * 3)
        self.assertEqual(h.upgrades.decor, g.upgrades.decor)
        self.assertFalse(h.story.ready(h, 0))
        self.assertIn('chairs', h.story.mara_chat(h))
        h.upgrades.decor.add('table_0_seat_1')
        self.assertTrue(h.story.ready(h, 0))

    def test_older_completed_chapter_keeps_its_reward_and_achievement(self):
        g = self.g
        self.sweep()
        for store in g.mall.north_stores[:6]:
            store.restored = True
        g.mall.refresh_businesses()
        g.upgrades.decor.update(('bench_0', 'bench_1', 'fountain'))
        g.story.started[0] = g.story.completed[0] = True
        g.story.memories[0] = [True] * 3
        g.cash = 1_000
        h = Game()
        restore_state(snapshot(g), h)
        self.assertEqual(h.story.current, 1)
        self.assertEqual(h.cash, 1_000)
        self.assertNotIn('table_0', h.upgrades.decor)
        self.assertTrue(all(count >= goal for _, count, goal in h.story.requirements(h, 0)))
        self.assertFalse(h.story.confirm(h, 0, 'claim'))
        self.assertEqual(h.cash, 1_000)

    def test_mara_chat_follows_the_project_without_accepting_an_owner_request(self):
        g = self.g
        store = g.mall.north_stores[1]
        store.restored = True
        before = g.life.chat(g, store)
        self.assertIn('Marty', before)
        self.assertIn('community board', before)
        self.assertIsNone(g.owner_requests.store)
        self.sweep()
        self.begin()
        self.recover_keepsakes()
        g.life.chat(g, store)
        self.assertIn('table 1', g.life.chat(g, store))
        self.assertIsNone(g.owner_requests.store)

    def test_developer_preparation_does_not_change_an_active_owner_request(self):
        g = self.g
        self.sweep()
        store = g.mall.north_stores[1]
        store.restored = True
        store.request_wait = 0
        g.owner_requests.accept(store, g.mall)
        before = snapshot(g)['request']
        cash = g.cash
        self.assertTrue(g.story.prepare(g))
        self.assertEqual(snapshot(g)['request'], before)
        self.assertEqual(store.request_level, 0)
        self.assertEqual(g.cash, cash)
        self.assertTrue(g.story.ready(g, 0))

    def test_opening_and_project_text_fit_minimum_size_with_clickable_returns(self):
        g = self.g
        g.tutorial.start(g)
        panel, proceed, skip = g.tutorial.geometry(g.screen)
        story = g.tutorial.STEPS[0][1]
        task = g.tutorial.STEPS[0][2]
        bottom = panel.y + 115 + 25 * len(theme.wrap(g.hud.font, story, panel.width - 48)) + 16
        bottom += 23 * len(theme.KeycapFont(g.hud.small).wrap(task, panel.width - 48))
        self.assertLess(bottom, proceed.top)
        self.assertTrue(panel.contains(skip))
        g.draw()
        self.click(proceed)
        self.assertFalse(g.tutorial.paused)
        g.tutorial.skip()
        self.begin()
        g.story.action(self.board(), g)
        panel, button = g.story_menu.geometry(g.screen)
        bottom = panel.y + 107 + 26 * len(theme.wrap(g.hud.font, g.story_menu.text, panel.width - 48))
        self.assertLessEqual(bottom, panel.bottom - 112)
        with patch('pygame.mouse.get_pos', return_value=button.center):
            g.draw()
        self.click(g.mouse_controls.back_rect(g))
        self.assertFalse(g.story_menu.open)
        g.journal.open = True
        g.journal.tab = 2
        g.draw()

