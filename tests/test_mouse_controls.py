"""Mouse journeys exercise real input routing, nearby actions and paused overlays."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import tempfile
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from systems.saves import snapshot
from tests import test_feature_expansion as helpers


class MouseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.g = Game(persistence=True, save_dir=self.temp.name, developer=True)
        self.g.frame_camera(self.g.screen.get_size())

    def tearDown(self):
        pygame.quit()
        self.temp.cleanup()

    def down(self, point, button=1):
        self.g.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=point, button=button)
        )

    def click(self, point, button=1):
        self.down(point, button)
        self.g.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, pos=point, button=button)
        )

    def toolbar(self, action):
        self.click(self.g.hud.button_rects(self.g.screen)[action].center)

    def back(self):
        self.click(self.g.mouse_controls.back_rect(self.g).center)

    def enter_courtyard(self):
        helper = helpers.FeatureTests()
        helper.g = self.g
        return helper.enter()

    def test_toolbar_and_back_buttons_never_click_through_or_advance_the_world(self):
        g = self.g
        for action in ("journal", "settings", "pause", "help"):
            with self.subTest(action=action):
                self.toolbar(action)
                self.assertTrue(g.world_paused)
                before = snapshot(g)
                self.click((12, 260))
                g.update(30, (1, 0), True)
                self.assertEqual(snapshot(g), before)
                if action == "help":
                    self.back()
                    self.assertTrue(g.pause.open)
                    self.back()
                    self.click(g.tutorial.geometry(g.screen)[2].center)
                else:
                    self.back()
                self.assertFalse(g.world_paused)

    def test_create_two_saves_switch_delete_and_return_with_only_mouse_buttons(self):
        g = self.g
        g.welcome.tutorial_enabled = False
        self.toolbar("pause")
        self.click(g.pause.geometry(g.screen)[1][2].center)
        self.click(g.pause.geometry(g.screen)[1][1].center)
        original = g.save_store.slot
        self.assertTrue(g.welcome.open)
        self.click(g.welcome.new_rect(g.screen).center)
        self.click(g.welcome.dialog_geometry(g.screen)[3].center)
        g.update(0.9, (0, 0))
        if g.tutorial.active:
            self.click(g.tutorial.skip_rect(g.screen).center)
        second = g.save_store.slot
        self.assertNotEqual(original, second)
        g.cash = 123
        self.toolbar("pause")
        self.click(g.pause.geometry(g.screen)[1][2].center)
        self.click(g.pause.geometry(g.screen)[1][1].center)
        self.assertEqual(len(g.welcome.saves), 2)
        self.click(g.welcome.delete_rect(g.screen).center)
        self.click(g.welcome.dialog_geometry(g.screen)[2].center)
        self.assertEqual(len(g.welcome.saves), 2)
        self.click(g.welcome.delete_rect(g.screen).center)
        self.click(g.welcome.dialog_geometry(g.screen)[3].center)
        self.assertEqual(len(g.welcome.saves), 1)
        self.click(g.welcome.geometry(g.screen)[1].center)
        g.update(0.9, (0, 0))
        self.assertFalse(g.welcome.open)
        self.assertEqual(g.cash, 0)

    def test_clicking_store_and_bin_performs_the_chosen_action(self):
        g = self.g
        store = g.mall.stores[0]
        g.cash = 100
        g.player.rect.center = store.position
        g.frame_camera(g.screen.get_size())
        self.click(g.camera.point(store.position))
        self.assertTrue(store.restored)
        self.assertTrue(g.shop_menu.open)
        cash = g.cash
        self.back()
        self.assertFalse(g.shop_menu.open)
        self.assertEqual(g.cash, cash)
        bin_ = g.mall.trash_bins[0]
        g.player.rect.center = bin_.position
        g.upgrades.held = 1
        g.frame_camera(g.screen.get_size())
        self.click(g.camera.point(bin_.position))
        self.assertEqual(g.upgrades.held, 0)
        self.assertEqual(g.cash, cash + g.upgrades.unit_value)

    def test_distant_or_ui_clicks_do_not_reopen_a_store_or_clean_litter(self):
        g = self.g
        store = g.mall.stores[0]
        g.cash = 100
        g.player.rect.center = store.position + pygame.Vector2(180, 0)
        g.frame_camera(g.screen.get_size())
        self.click(g.camera.point(store.position))
        self.assertFalse(store.restored)
        self.assertEqual(g.cash, 100)
        self.toolbar("journal")
        before = snapshot(g)
        self.click(g.camera.point(store.position))
        self.assertEqual(snapshot(g), before)

    def test_shop_paging_and_purchase_work_without_keyboard(self):
        g = self.g
        store = g.mall.stores[0]
        store.restored = True
        g.cash = 10000
        g.open_upgrade_shop(store)
        menu = g.shop_menu
        self.click(menu.geometry(g.screen)[1][1].center)
        self.click(menu.page_buttons(g)[1].center)
        self.assertGreater(menu.scroll, 0)
        offer, rect = next(
            (offer, rect) for offer, rect in menu.rows(g) if not offer.owned
        )
        self.click(rect.center)
        cash = g.cash
        self.click(menu.purchase_rect(g).center)
        self.assertLess(g.cash, cash)
        self.back()
        self.assertFalse(menu.open)

    def test_story_keepsakes_and_display_undo_have_mouse_controls(self):
        g = self.g
        self.toolbar("journal")
        self.click(g.journal.tabs(g.screen)[2].center)
        self.click(g.journal.memories_rect(g.screen).center)
        self.assertTrue(g.journal.memories_view)
        self.click(g.journal.memories_rect(g.screen).center)
        self.assertFalse(g.journal.memories_view)
        self.back()
        g.display_menu.visit()
        g.display_menu.arrangement = [1, 2]
        self.click(g.display_menu.undo_rect(g.screen).center)
        self.assertEqual(g.display_menu.arrangement, [1])
        self.back()
        self.assertFalse(g.display_menu.open)

    def test_every_conversation_and_playtest_panel_has_a_safe_back_button(self):
        g = self.g
        for menu in (
            g.shop_menu,
            g.owner_menu,
            g.display_menu,
            g.story_menu,
            g.community_menu,
            g.developer,
        ):
            with self.subTest(menu=type(menu).__name__):
                menu.open = True
                cash = g.cash
                self.back()
                self.assertFalse(menu.open)
                self.assertEqual(g.cash, cash)

    def test_settings_control_pages_are_mouse_navigable_in_both_directions(self):
        g = self.g
        self.toolbar("settings")
        menu = g.settings_menu
        self.click(menu.geometry(g.screen)[1][1].center)
        for page in (1, 0):
            self.click(menu.geometry(g.screen)[2][len(menu.actions())].center)
            self.assertEqual(menu.page, page)
            self.assertIsNone(menu.capture)
        self.back()
        self.assertFalse(menu.open)

    def test_floor_clicks_never_move_the_player_in_either_scene(self):
        g = self.g
        for outside in (False, True):
            if outside:
                self.enter_courtyard()
                g.player.rect.center = (500, 740)
            else:
                g.player.rect.center = (650, 720)
            g.frame_camera(g.screen.get_size())
            point = pygame.Vector2(g.player.rect.center) + (80, 40)
            self.assertIsNone(g.mouse_controls.world_target(g, point))
            origin = g.player.rect.center
            for button in (1, 3):
                with self.subTest(outside=outside, button=button):
                    self.click(g.camera.point(point), button)
                    for _ in range(10):
                        g.update(0.05, (0, 0))
                    self.assertEqual(g.player.rect.center, origin)
            g.update(0.1, (1, 0))
            self.assertGreater(g.player.rect.centerx, origin[0])
            self.assertFalse(any(g.player.rect.colliderect(wall) for wall in
                                 (g.courtyard.world if outside else g.mall).obstacles))

    def test_right_clicking_objects_never_interacts_or_moves(self):
        g = self.g
        store = g.mall.stores[0]
        g.cash = 100
        g.player.rect.center = store.position
        g.frame_camera(g.screen.get_size())
        origin = g.player.rect.center
        self.click(g.camera.point(store.position), 3)
        g.update(0.2, (0, 0))
        self.assertFalse(store.restored)
        self.assertFalse(g.shop_menu.open)
        self.assertEqual(g.cash, 100)
        self.assertEqual(g.player.rect.center, origin)

    def test_hold_action_and_mouse_release_control_owner_work(self):
        g = self.g
        store = g.mall.stores[1]
        store.restored = True
        store.request_level = 2
        store.request_wait = 0
        self.assertTrue(g.owner_requests.accept(store, g.mall))
        spot = next(spot for spot in g.owner_requests.visible_spots if spot.duration)
        g.player.rect.center = spot.position
        g.frame_camera(g.screen.get_size())
        self.down(g.hud.button_rects(g.screen)["action"].center)
        g.update(0.5, (0, 0))
        self.assertGreater(spot.progress, 0)
        g.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(12, 260))
        )
        g.update(0.5, (0, 0))
        self.assertEqual(spot.progress, 0)
        self.down(g.hud.button_rects(g.screen)["action"].center)
        g.update(spot.duration, (0, 0))
        self.assertTrue(spot.completed)

    def test_courtyard_buttons_and_kitchen_close_keep_existing_rules(self):
        g = self.g
        world = self.enter_courtyard()
        for trash in world.trash:
            world.clean_trash(trash)
        for store in world.stores:
            store.restored = True
        world.refresh_businesses()
        store = world.stores[1]
        g.courtyard.kitchen_requests.waits[store.name] = 0
        g.player.rect.center = store.position
        g.frame_camera(g.screen.get_size())
        self.click(g.camera.point(store.position))
        self.assertTrue(g.cooking_menu.open)
        cash = g.cash
        self.click(g.cooking_menu.geometry(g.screen)[2].center)
        self.assertTrue(g.cooking_menu.started)
        self.click(g.cooking_menu.pause_rect(g.screen).center)
        self.assertTrue(g.pause.open)
        elapsed = g.cooking_menu.round.elapsed
        g.update(20, (0, 0))
        self.assertEqual(g.cooking_menu.round.elapsed, elapsed)
        self.back()
        self.assertTrue(g.cooking_menu.open)
        self.back()
        self.assertFalse(g.cooking_menu.open)
        self.assertLess(g.cash, cash)
        self.assertEqual(g.courtyard.cooking[store.name]["failed"], 1)
        self.toolbar("journal")
        self.back()
    def test_courtyard_passage_can_be_used_in_both_directions_with_clicks(self):
        g = self.g
        self.enter_courtyard()
        g.player.rect.center = g.courtyard.world.return_door.position
        g.frame_camera(g.screen.get_size())
        self.click(g.camera.point(g.courtyard.world.return_door.position))
        self.assertEqual(g.scene, "mall")
        self.click(g.camera.point(g.courtyard.door(g.mall).position))
        self.assertEqual(g.scene, "courtyard")

    def test_hover_and_hud_controls_render_in_both_scenes_at_minimum_size(self):
        g = self.g
        for outside in (False, True):
            if outside:
                self.enter_courtyard()
            g.screen = pygame.display.set_mode((800, 600))
            g.frame_camera(g.screen.get_size())
            buttons = g.hud.button_rects(g.screen)
            for rect in buttons.values():
                self.assertTrue(g.screen.get_rect().contains(rect))
            for key, rect in buttons.items():
                self.assertFalse(
                    any(
                        rect.colliderect(other)
                        for name, other in buttons.items()
                        if name != key
                    )
                )
            with patch("pygame.mouse.get_pos", return_value=buttons["journal"].center):
                g.draw()
            self.toolbar("journal")
            g.draw()
            self.back()
