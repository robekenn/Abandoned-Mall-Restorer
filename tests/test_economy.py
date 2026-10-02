import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from systems.economy import rent_multiplier, money, cleanliness_label


class EconomyTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def test_rent_boundaries(self):
        for clean, multiplier in [(0,0),(.0001,.5),(.49999,.5),(.5,1),(.99,1),(.99999,1),(1,1.5)]:
            with self.subTest(clean=clean):
                self.assertEqual(rent_multiplier(clean),multiplier)
        self.assertEqual(cleanliness_label(.99999),'99%')
        self.assertEqual(cleanliness_label(.0001),'<1%')
        self.assertEqual(cleanliness_label(1),'100%')
        self.assertEqual(money(7.5),'$7.5')
        self.assertEqual(money(0),'$0')

    def test_each_rent_tick_uses_current_cleanliness_and_preserves_half_dollars(self):
        g = self.game
        g.mall.stores[1].restored = True  # $5 base rent
        tiles = g.mall.floor_tiles
        with patch.object(g.litter_spawner,'update'):
            for dirty_count, expected in [(len(tiles),0),(len(tiles)-1,2.5),(len(tiles)//2,5),(1,5),(0,7.5)]:
                with self.subTest(dirty_count=dirty_count):
                    g.mall.dirty_tiles = set(tiles[:dirty_count])
                    g.cash = 0
                    g.rent_timer = 0
                    self.assertEqual(g.rent_income,expected)
                    g.update(10,(0,0))
                    self.assertEqual(g.cash,expected*2)
                    self.assertEqual(g.rent_timer,0)
                    g.draw()
            # A half-dollar balance remains usable for ordinary purchases.
            g.cash = 7.5
            g.mall.stores[0].restored = True
            g.shop_menu.open = True
            g.buy_upgrade('capacity')
            self.assertEqual(g.cash,2.5)
            self.assertEqual(g.upgrades.capacity,2)

    def test_starting_sales_fund_supplies_and_first_upgrades(self):
        g = self.game
        self.assertEqual((g.upgrades.capacity,g.upgrades.unit_value),(1,1))
        for trash in g.mall.trash[:g.mall.stores[0].cost]:
            g.player.rect.center = trash.position
            g.interact()
            g.player.rect.center = g.mall.trash_bins[0].position
            g.interact()
        g.player.rect.center = g.mall.stores[0].position
        g.interact()
        self.assertTrue(g.shop_menu.open)
        self.assertEqual(g.cash,0)
        g.shop_menu.open = False
        for trash in g.mall.trash[g.mall.stores[0].cost:g.mall.stores[0].cost+5]:
            g.player.rect.center = trash.position
            g.interact()
            g.player.rect.center = g.mall.trash_bins[0].position
            g.interact()
        g.player.rect.center = g.mall.stores[0].position
        g.interact()
        g.buy_upgrade('capacity')
        self.assertEqual((g.cash,g.upgrades.capacity),(0,2))

    def test_fixture_layout_keeps_shop_doors_and_benches_clear(self):
        mall = self.game.mall
        for lamp,left,right in zip(mall.lamps,mall.stores,mall.stores[1:]):
            self.assertEqual(lamp[0],(left.rect.right+right.rect.left)//2)
            self.assertTrue(all(pygame.Vector2(lamp).distance_to(s.position)>90 for s in mall.stores))
        for trash_bin,bench in zip(mall.trash_bins,mall.benches):
            self.assertEqual(trash_bin.rect.centery,bench.centery)
            self.assertGreater(trash_bin.rect.left,bench.right)
            self.assertLess(trash_bin.rect.left-bench.right,40)
            self.assertFalse(any(o.colliderect(trash_bin.rect) for o in mall.obstacles if o is not trash_bin.rect))
        self.assertEqual(self.game.art.sprites['trash_bin'].get_size(),(24,24))
