"""Multi-save actions through real menu input, recovery and scene transitions."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from systems.save_slots import SaveSlots
from systems.saves import canonical, snapshot, restore_state
from tests import test_feature_expansion as helpers
from ui.welcome import fit_text


class SaveMenuTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.g = Game(start_screen=True, persistence=True, save_dir=self.directory.name)
        self.g.welcome.tutorial_enabled = False

    def tearDown(self):
        pygame.quit()
        self.directory.cleanup()

    def key(self, key):
        self.g.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))

    def click(self, point):
        self.g.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=point)
        )

    def new(self, name):
        self.key(pygame.K_n)
        self.g.handle_event(pygame.event.Event(pygame.TEXTINPUT, text=name))
        self.key(pygame.K_RETURN)
        self.g.update(0.9, (0, 0))
        self.assertFalse(self.g.welcome.open)
        self.g.tutorial.skip()
        return self.g.save_store

    def menu(self):
        g = self.g
        self.key(pygame.K_ESCAPE)
        self.click(g.pause.geometry(g.screen)[1][2].center)
        self.assertEqual(g.pause.destination, "main")
        self.assertTrue(g.pause.confirm)
        self.key(pygame.K_DOWN)
        self.key(pygame.K_RETURN)
        self.assertTrue(g.welcome.open)
        self.assertFalse(g.pause.open)
        self.assertFalse(g.save_started)

    def test_named_games_keep_independent_progress_and_latest_selection(self):
        first = self.new("Weekend Mall")
        g = self.g
        g.cash = 321
        g.play_seconds = 90
        g.mall.clean_trash(g.mall.trash[0])
        self.menu()
        original = first.path.read_bytes()
        second = self.new("Lantern Walk")
        self.assertNotEqual(first.path, second.path)
        self.assertEqual(g.cash, 0)
        self.assertEqual(g.total_collected, 0)
        self.assertFalse(g.mall.trash[0].cleaned)
        self.assertEqual(first.path.read_bytes(), original)
        g.cash = 777
        g.play_seconds = 180
        self.menu()
        self.assertEqual(g.welcome.selected.identifier, second.slot)
        self.assertEqual(
            {s.name for s in g.welcome.saves}, {"Weekend Mall", "Lantern Walk"}
        )
        g.welcome.selection = next(
            i for i, s in enumerate(g.welcome.saves) if s.identifier == first.slot
        )
        self.key(pygame.K_RETURN)
        g.update(0.9, (0, 0))
        self.assertEqual(g.cash, 321)
        self.assertEqual(g.play_seconds, 90)
        self.assertTrue(g.mall.trash[0].cleaned)
        self.assertEqual(g.save_store.path, first.path)
        self.assertEqual(second.read(second.path)["cash"], 777)
        self.assertEqual(g.save_store.name, "Weekend Mall")

    def test_legacy_checkpoint_is_listed_without_being_rewritten(self):
        first = self.new("Old Mall")
        self.g.cash = 42
        self.g.save_checkpoint()
        # Remove newer envelope metadata to model an existing v1 checkpoint.
        data = first.read_envelope(first.path)
        data.pop("name")
        data.pop("saved_at")
        data["data"].pop("play_seconds")
        import hashlib

        data["checksum"] = hashlib.sha256(canonical(data["data"])).hexdigest()
        first.path.write_bytes(canonical(data))
        before = first.path.read_bytes()
        g = Game(start_screen=True, persistence=True, save_dir=self.directory.name)
        self.g = g
        self.assertEqual(first.path.read_bytes(), before)
        self.assertEqual(g.welcome.selected.name, "Original Northgate")
        self.key(pygame.K_RETURN)
        g.update(0.9, (0, 0))
        self.assertEqual(g.cash, 42)
        self.assertEqual(g.play_seconds, 0)

    def test_menu_creation_and_continue_work_after_courtyard_session(self):
        g = self.g
        old = self.new("Courtyard Mall")
        helper = helpers.FeatureTests()
        helper.g = g
        world = helper.enter()
        for trash in world.trash:
            world.clean_trash(trash)
        world.stores[0].restored = True
        world.stores[1].restored = True
        world.refresh_businesses()
        g.courtyard.kitchen_requests.waits["Hearth Pizza"] = 0
        g.play_seconds = 400
        g.cash = 54321
        self.menu()
        new = self.new("Fresh Mall")
        self.assertEqual(g.scene, "mall")
        self.assertIsNone(g.courtyard.world)
        self.assertFalse(g.courtyard.unlocked)
        self.assertFalse(g.mall.commons.unlocked)
        self.assertEqual(g.cash, 0)
        self.assertEqual(g.upgrades.decor, set())
        self.menu()
        self.assertTrue(g.continue_game(old.slot))
        g.update(0.9, (0, 0))
        g.draw()
        self.assertEqual(g.scene, "courtyard")
        self.assertEqual(g.cash, 54321)
        self.assertEqual(g.play_seconds, 400)
        self.assertTrue(g.courtyard.kitchen_requests.ready("Hearth Pizza"))
        self.assertEqual(new.read(new.path)["cash"], 0)

    def test_delete_defaults_to_cancel_then_removes_only_selected_save_and_backup(self):
        first = self.new("Keep Me")
        self.g.cash = 13
        self.menu()
        original = first.path.read_bytes()
        second = self.new("Delete Me")
        self.g.cash = 24
        self.g.save_checkpoint()
        self.menu()
        self.assertTrue(second.backup.exists())
        self.key(pygame.K_d)
        self.key(pygame.K_RETURN)
        self.assertIsNone(self.g.welcome.dialog)
        self.assertTrue(second.path.exists())
        self.key(pygame.K_d)
        self.key(pygame.K_RIGHT)
        self.key(pygame.K_RETURN)
        self.assertFalse(second.path.exists())
        self.assertFalse(second.backup.exists())
        self.assertEqual(first.path.read_bytes(), original)
        self.assertEqual(len(self.g.welcome.saves), 1)
        self.assertEqual(self.g.welcome.selected.name, "Keep Me")
        self.g.welcome.choose_delete()
        self.click(self.g.welcome.dialog_geometry(self.g.screen)[3].center)
        self.assertEqual(self.g.welcome.saves, [])
        self.assertTrue(self.g.start_new_game("After deleting"))
        self.g.update(0.9, (0, 0))
        self.assertEqual(self.g.cash, 0)

    def test_delete_failure_keeps_latest_primary_visible_and_other_games_safe(self):
        first = self.new("Keep Me")
        self.menu()
        second = self.new("Cannot Delete")
        self.menu()
        original = first.path.read_bytes()
        latest = second.path.read_bytes()
        unlink = Path.unlink

        def fail(path, *args, **kwargs):
            if path == second.path:
                raise OSError("permission denied")
            return unlink(path, *args, **kwargs)

        self.key(pygame.K_d)
        with patch.object(Path, "unlink", fail):
            self.g.welcome.dialog_action(self.g, True)
        self.assertEqual(second.path.read_bytes(), latest)
        self.assertEqual(first.path.read_bytes(), original)
        self.assertEqual(len(self.g.welcome.saves), 2)
        self.assertEqual(self.g.welcome.dialog, "delete")
        self.assertIn("Could not delete", self.g.welcome.status)

    def test_failed_new_save_stays_in_menu_without_overwriting_existing_game(self):
        first = self.new("Original")
        self.menu()
        original = first.path.read_bytes()
        self.key(pygame.K_n)
        with patch("game.storage.os.replace", side_effect=OSError("disk full")):
            self.key(pygame.K_RETURN)
        self.assertTrue(self.g.welcome.open)
        self.assertFalse(self.g.welcome.leaving)
        self.assertFalse(self.g.save_started)
        self.assertEqual(first.path.read_bytes(), original)
        self.assertEqual(len(self.g.save_slots.entries()), 1)
        self.assertIn("Could not create", self.g.welcome.status)
        self.assertEqual(list(Path(self.directory.name).rglob("*.tmp")), [])

    def test_save_failure_on_return_keeps_session_until_explicit_discard(self):
        g = self.g
        store = self.new("Save Failure")
        before = store.path.read_bytes()
        g.cash = 99
        self.key(pygame.K_ESCAPE)
        g.pause.activate(g, 2)
        with patch.object(g, "save_checkpoint", return_value=False):
            g.pause.activate(g, 1)
        self.assertTrue(g.running)
        self.assertFalse(g.welcome.open)
        self.assertTrue(g.pause.save_failed)
        self.assertEqual(g.cash, 99)
        self.assertEqual(store.path.read_bytes(), before)
        g.pause.activate(g, 2)
        self.assertTrue(g.welcome.open)
        self.assertTrue(g.running)
        self.assertEqual(store.path.read_bytes(), before)

    def test_menu_freezes_session_and_quitting_cannot_save_stale_memory(self):
        g = self.g
        store = self.new("Safe Mall")
        g.cash = 25
        self.menu()
        before = store.path.read_bytes()
        state = snapshot(g)
        g.update(600, (1, 0), True)
        g.interact()
        self.assertEqual(snapshot(g), state)
        g.cash = 99999
        events = [
            [pygame.event.Event(pygame.QUIT)],
            [
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN),
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
            ],
        ]
        with patch("pygame.event.get", side_effect=events), patch.object(g, "draw"):
            g.run()
        self.assertEqual(store.path.read_bytes(), before)

    def test_corrupt_slot_recovers_its_own_backup_without_cross_loading(self):
        g = self.g
        first = self.new("First")
        g.cash = 11
        self.menu()
        second = self.new("Recover Me")
        g.cash = 22
        g.save_checkpoint()
        g.cash = 33
        g.save_checkpoint()
        self.menu()
        second.path.write_text("broken")
        g.welcome.refresh(g, selected=second.slot)
        self.assertTrue(g.welcome.selected.recovered)
        self.key(pygame.K_RETURN)
        g.update(0.9, (0, 0))
        self.assertEqual(g.cash, 33)
        self.assertTrue(g.save_store.recovering)
        self.assertEqual(first.read(first.path)["cash"], 11)
        g.cash = 44
        g.save_checkpoint()
        second.path.write_text("broken")
        self.assertTrue(g.save_store.load(g))
        self.assertEqual(g.cash, 33)

    def test_corrupt_and_unavailable_slots_remain_deletable_and_load_is_atomic(self):
        g = self.g
        store = self.new("Bad Save")
        self.menu()
        before = snapshot(g)
        data = copy.deepcopy(store.read(store.path))
        data["held"] = 500
        import hashlib

        envelope = {
            "version": 1,
            "data": data,
            "checksum": hashlib.sha256(canonical(data)).hexdigest(),
        }
        store.path.write_bytes(canonical(envelope))
        store.backup.unlink(missing_ok=True)
        self.assertFalse(g.continue_game())
        self.assertEqual(snapshot(g), before)
        store.path.write_text("broken")
        g.welcome.refresh(g)
        self.assertFalse(g.welcome.selected.playable)
        self.key(pygame.K_RETURN)
        self.assertTrue(g.welcome.open)
        self.key(pygame.K_d)
        self.key(pygame.K_RIGHT)
        self.key(pygame.K_RETURN)
        self.assertFalse(store.path.exists())

    def test_normal_and_developer_libraries_are_separate_and_slot_ids_are_safe(self):
        normal = self.new("Normal")
        self.menu()
        extra = self.new("Another Normal")
        self.menu()
        dev = SaveSlots(self.directory.name, True, True)
        store = dev.allocate("Developer")
        store.save(self.g)
        extra_dev = dev.allocate("Developer Two")
        extra_dev.save(self.g)
        self.assertEqual(len(dev.entries()), 2)
        self.assertEqual(len(self.g.save_slots.entries()), 2)
        self.assertNotEqual(extra.path, extra_dev.path)
        self.assertEqual(normal.path.name, "progress.json")
        self.assertEqual(store.path.name, "developer.json")
        for identifier in ("../progress", "../../settings", "X" * 32, "a" * 31):
            with self.assertRaises(ValueError):
                self.g.save_slots.store(identifier)

    def test_unicode_name_input_does_not_trigger_game_keys_and_fixed_menu_navigation_survives_rebinding(
        self,
    ):
        g = self.g
        g.preferences.bind("right", pygame.K_l)
        self.key(pygame.K_n)
        muted = g.audio.muted
        self.key(pygame.K_m)
        self.key(pygame.K_j)
        g.handle_event(pygame.event.Event(pygame.TEXTINPUT, text="Mara’s Café"))
        self.assertEqual(g.welcome.name, "Mara’s Café")
        self.assertEqual(g.audio.muted, muted)
        self.assertFalse(g.journal.open)
        self.key(pygame.K_RETURN)
        g.update(0.9, (0, 0))
        g.tutorial.skip()
        self.menu()
        self.key(pygame.K_d)
        self.assertEqual(g.welcome.dialog, "delete")
        self.key(pygame.K_ESCAPE)
        self.assertIsNone(g.welcome.dialog)

    def test_pagination_and_all_menu_dialogs_fit_minimum_and_large_windows(self):
        g = self.g
        for i in range(11):
            store = g.save_slots.allocate("W" * 28 if i == 0 else f"Mall {i}")
            self.assertTrue(store.save(g))
        g.welcome.refresh(g)
        for size in ((800, 600), (1280, 720), (1920, 1080)):
            g.screen = pygame.display.set_mode(size)
            g.draw()
            panel, start, quit = g.welcome.geometry(g.screen)
            self.assertTrue(g.screen.get_rect().contains(panel))
            self.assertTrue(panel.contains(start))
            self.assertTrue(panel.contains(quit))
            area, rows, _, count = g.welcome.save_geometry(g.screen)
            self.assertLessEqual(rows[-1].bottom, area.bottom - 76)
            self.key(pygame.K_PAGEDOWN)
            self.assertEqual(g.welcome.selection, count % len(g.welcome.saves))
            self.assertLessEqual(
                g.welcome.card_title.size(
                    fit_text(g.welcome.card_title, "W" * 28, area.width - 28)
                )[0],
                area.width - 28,
            )
            g.draw()
            self.key(pygame.K_n)
            g.draw()
            self.assertTrue(
                g.screen.get_rect().contains(g.welcome.dialog_geometry(g.screen)[0])
            )
            self.key(pygame.K_ESCAPE)
            self.key(pygame.K_d)
            g.draw()
            self.key(pygame.K_ESCAPE)
            g.welcome.selection = 0
        # No arbitrary slot limit; keyboard, scroll and click navigation all work.
        self.g.screen = pygame.display.set_mode((800, 600))
        self.g.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, y=-1))
        self.assertEqual(g.welcome.selection, 1)
        self.click(g.welcome.save_geometry(g.screen)[1][2].center)
        self.assertEqual(g.welcome.selection, 2)

    def test_old_save_missing_playtime_and_new_roundtrip_preserve_runtime_clock(self):
        g = self.g
        self.new("Clock")
        g.update(2, (0, 0))
        self.assertEqual(g.play_seconds, 2)
        g.pause.open = True
        g.update(90, (1, 0))
        self.assertEqual(g.play_seconds, 2)
        g.pause.open = False
        data = snapshot(g)
        restore_state(data, g)
        self.assertEqual(g.play_seconds, 2)
        data.pop("play_seconds")
        restore_state(data, g)
        self.assertEqual(g.play_seconds, 0)
