import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
import pygame
from game.game import Game
from systems.litter import LitterSpawner


class ProgressionTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def finish_sweep(self):
        g = self.game
        for trash in g.mall.trash:
            g.player.rect.center = trash.position
            g.interact()

    def test_initial_tasks_cover_every_walkable_tile(self):
        mall = self.game.mall
        self.assertGreater(mall.initial_litter_count, 15)
        for tile in mall.floor_tiles:
            if not any(w.collidepoint(tile) for w in mall.obstacles):
                self.assertTrue(any(t.position.distance_squared_to(tile) < 115**2 for t in mall.trash), tile)
        self.finish_sweep()
        self.assertEqual(mall.active_litter_count, 0)
        self.assertEqual(mall.cleanliness, 1)
        self.assertTrue(all(mall.tile_restored(p) for p in mall.floor_tiles))
        self.assertTrue(mall.initial_cleanup_complete)
        self.assertEqual(self.game.cash, mall.initial_litter_count * 10)

    def test_business_order_costs_and_combined_rent(self):
        g = self.game
        pages, retro, cafe, tailor = g.mall.stores
        g.cash = 100
        g.player.rect.center = pages.position
        g.interact()
        self.assertTrue(pages.restored)
        self.assertFalse(retro.available)
        g.update(8, (0, 0))
        self.assertEqual(g.mall.active_litter_count, g.mall.initial_litter_count)
        self.finish_sweep()
        self.assertTrue(retro.available)
        self.assertFalse(cafe.available)
        g.cash = 250
        g.player.rect.center = retro.position
        g.interact()
        self.assertEqual(g.cash, 0)
        self.assertTrue(retro.restored)
        self.assertTrue(cafe.available)
        self.assertFalse(tailor.available)
        g.player.rect.center = cafe.position
        g.interact()
        self.assertFalse(cafe.restored)
        self.assertIn('450', g.message)
        g.rent_timer = 0
        g.update(5, (0, 0))
        self.assertEqual(g.cash, pages.rent + retro.rent)
        g.cash = cafe.cost
        g.interact()
        self.assertTrue(cafe.restored)
        self.assertTrue(tailor.available)
        g.cash = tailor.cost
        g.player.rect.center = tailor.position
        g.interact()
        self.assertTrue(all(s.restored for s in g.mall.stores))
        self.assertIsNone(g.mall.next_store)
        g.rent_timer = 0
        g.update(5, (0, 0))
        self.assertEqual(g.cash, sum(s.rent for s in g.mall.stores))

    def test_new_litter_waits_then_is_bounded_and_recleanable(self):
        g = self.game
        spawner = LitterSpawner()
        spawner.update(100, g.mall, g.player.rect.center)
        self.assertEqual(g.mall.active_litter_count, g.mall.initial_litter_count)
        self.finish_sweep()
        # No shop means no returning foot traffic yet.
        spawner.update(100, g.mall, g.player.rect.center)
        self.assertEqual(g.mall.active_litter_count, 0)
        g.mall.stores[0].restored = True
        g.player.rect.center = g.mall.stores[0].position
        spawner.update(7.9, g.mall, g.player.rect.center)
        self.assertEqual(g.mall.active_litter_count, 0)
        spawner.update(0.2, g.mall, g.player.rect.center)
        self.assertEqual(g.mall.active_litter_count, 1)
        self.assertLess(g.mall.cleanliness, 1)
        self.assertEqual(g.mall.cleaned_count, g.mall.initial_litter_count)
        self.assertTrue(g.mall.initial_cleanup_complete)
        active = next(t for t in g.mall.trash if not t.cleaned)
        self.assertGreater(active.position.distance_to(g.player.rect.center), 100)
        g.player.rect.center = active.position
        cash = g.cash
        g.interact()
        self.assertEqual(g.cash, cash+10)
        self.assertEqual(g.mall.cleanliness, 1)
        for _ in range(30):
            spawner.update(8, g.mall, g.player.rect.center)
        self.assertEqual(g.mall.active_litter_count, spawner.cap)
        self.assertEqual(len(g.mall.trash), g.mall.initial_litter_count)
        for t in g.mall.trash:
            if not t.cleaned:
                g.mall.clean_trash(t)
        self.assertEqual(g.mall.cleanliness, 1)

    def test_previous_character_scale_and_door_clearance(self):
        g = self.game
        self.assertEqual(g.player.rect.size, (26, 30))
        for store in g.mall.stores:
            self.assertTrue(all(t.position.distance_to(store.position) > 90 for t in g.mall.trash))
        for trash in g.mall.trash:
            footprint = pygame.Rect(trash.position.x-13, trash.position.y-15, 26, 30)
            self.assertFalse(any(w.colliderect(footprint) for w in g.mall.obstacles))

    def test_overlapping_fresh_piles_keep_remaining_dirt(self):
        mall = self.game.mall
        self.finish_sweep()
        first = mall.trash[0]
        second = min((t for t in mall.trash if t is not first),
                     key=lambda t: t.position.distance_squared_to(first.position))
        self.assertLess(first.position.distance_to(second.position), 230)
        mall.respawn_trash(first)
        mall.respawn_trash(second)
        mall.clean_trash(first)
        expected = {p for p in mall.floor_tiles if second.position.distance_squared_to(p) < 115**2}
        self.assertEqual(mall.dirty_tiles, expected)
        self.assertEqual(mall.active_litter_count, 1)
        mall.clean_trash(second)
        self.assertEqual(mall.cleanliness, 1)


if __name__ == '__main__':
    unittest.main()
