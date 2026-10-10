"""Scene changes and every modal must share rent, saving and input rules."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import unittest
from unittest.mock import patch

from tests import test_feature_expansion as helpers


class RuntimeLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.helper = helpers.FeatureTests()
        self.helper.setUp()
        self.world = self.helper.enter()
        self.game = self.helper.g
        for trash in self.world.trash:
            self.world.clean_trash(trash)
        for store in self.world.stores[:2]:
            store.restored = True
        self.world.refresh_businesses()

    def tearDown(self):
        self.helper.tearDown()

    def test_rent_and_autosave_preserve_phase_across_both_scene_changes(self):
        game = self.game
        game.rent_timer = 4
        game.save_store.elapsed = 29
        game.save_started = True
        expected = game.rent_income
        before = game.cash
        with patch.object(game, "save_checkpoint") as save:
            game.update(1, (0, 0))
            self.assertEqual(game.cash - before, expected)
            self.assertEqual(game.rent_timer, 0)
            save.assert_called_once_with()
        game.save_started = False
        game.update(2, (0, 0))
        game.leave_courtyard()
        before = game.cash
        game.update(3, (0, 0))
        self.assertEqual(game.cash - before, game.rent_income)
        self.assertEqual(game.rent_timer, 0)
        # The shared autosave clock also survives the return indoors.
        self.assertEqual(game.save_store.elapsed, 35)

    def test_all_registered_menus_block_keyboard_and_mouse_world_actions(self):
        game = self.game
        for scene in ("courtyard", "mall"):
            if scene == "mall":
                game.leave_courtyard()
            for menu in (*game.modal_menus, game.welcome):
                with self.subTest(scene=scene, menu=type(menu).__name__):
                    menu.open = True
                    self.assertTrue(game.world_paused)
                    with (
                        patch.object(game, "target") as target,
                        patch.object(game.courtyard, "pickup_at") as pickup,
                    ):
                        game.interact()
                        game.pickup_at((400, 300))
                        target.assert_not_called()
                        pickup.assert_not_called()
                    menu.open = False
            self.assertFalse(game.world_paused)

    def test_indoor_hud_still_reports_courtyard_rent_when_indoor_floor_is_dirty(self):
        game = self.game
        game.leave_courtyard()
        game.mall.dirty_tiles = set(game.mall.floor_tiles)
        self.assertGreater(game.rent_income, 0)
        before = game.cash
        with patch.object(game.feedback, "burst") as burst:
            game.update(5, (0, 0))
            self.assertEqual(game.cash - before, game.rent_income)
            self.assertTrue(
                any("rent" in call.args[1] for call in burst.call_args_list)
            )
