import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from systems.upgrades import Upgrades


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def open_shop(self):
        g = self.game
        g.cash = g.mall.stores[0].cost
        g.player.rect.center = g.mall.stores[0].position
        g.interact()
        self.assertTrue(g.shop_menu.open)

    def test_capacity_blocks_cleanup_and_selling_pays_only_once(self):
        g = self.game
        for trash in g.mall.trash[:1]:
            g.player.rect.center = trash.position
            g.interact()
        self.assertEqual(g.upgrades.held,1)
        self.assertEqual(g.cash,0)
        blocked = g.mall.trash[1]
        dirty = set(g.mall.dirty_tiles)
        g.player.rect.center = blocked.position
        g.interact()
        self.assertFalse(blocked.cleaned)
        self.assertEqual(g.mall.dirty_tiles,dirty)
        self.assertIn('Bag full',g.message)
        trash_bin = g.mall.trash_bins[0]
        g.player.rect.center = trash_bin.position
        g.interact()
        self.assertEqual(g.cash,1)
        self.assertEqual(g.upgrades.held,0)
        with patch.object(g,'target',return_value=trash_bin):
            g.interact()
        self.assertEqual(g.cash,1)

    def test_first_business_is_supplies_and_shop_is_required(self):
        g = self.game
        self.assertEqual(g.mall.stores[0].name,'Northgate Supplies')
        self.assertFalse(g.mall.stores[1].available)
        g.cash = 1000
        message = g.buy_upgrade('capacity')
        self.assertIn('Visit',message)
        self.assertEqual(g.upgrades.capacity,1)
        self.assertEqual(g.cash,1000)
        self.open_shop()
        self.assertEqual(g.cash,0)
        g.cash = 5
        g.buy_upgrade('capacity')
        self.assertEqual(g.cash,0)
        self.assertEqual(g.upgrades.capacity,2)

    def test_purchase_bounds_and_individual_fixtures(self):
        upgrades = Upgrades()
        cash,message,bought = upgrades.purchase('fountain',179)
        self.assertFalse(bought)
        self.assertEqual(cash,179)
        self.assertEqual(upgrades.decor,set())
        cash,message,bought = upgrades.purchase('bench_0',200)
        self.assertTrue(bought)
        self.assertEqual(cash,130)
        self.assertEqual(upgrades.decor,{'bench_0'})
        cash,message,bought = upgrades.purchase('bench_0',cash)
        self.assertFalse(bought)
        self.assertEqual(cash,130)
        cash,message,bought = upgrades.purchase('lamp_1',cash)
        self.assertTrue(bought)
        self.assertNotIn('lamp_0',upgrades.decor)
        cash,message,bought = upgrades.purchase('missing',cash)
        self.assertFalse(bought)
        for key,attribute,maximum in [('capacity','capacity',20),('value','unit_value',30)]:
            for _ in range(len(upgrades.CAPACITY_PRICES if key == 'capacity' else upgrades.VALUE_PRICES)):
                _,_,bought = upgrades.purchase(key,10000)
                self.assertTrue(bought)
            self.assertEqual(getattr(upgrades,attribute),maximum)
            cash,_,bought = upgrades.purchase(key,500)
            self.assertFalse(bought)
            self.assertEqual(cash,500)

    def test_sale_uses_upgraded_contract(self):
        g = self.game
        self.open_shop()
        g.cash = 8
        g.upgrades.held = 1
        g.buy_upgrade('value')
        self.assertEqual(g.cash,0)
        g.shop_menu.open = False
        g.player.rect.center = g.mall.trash_bins[1].position
        g.interact()
        self.assertEqual(g.cash,2)
        self.assertEqual(g.upgrades.held,0)

    def test_tool_range_and_batch_obey_remaining_capacity(self):
        g = self.game
        for t in g.mall.trash:
            g.mall.clean_trash(t)
        g.upgrades.tool_level = 2
        first,second,third = g.mall.trash[:3]
        g.player.rect.center = (1000,800)
        for i,t in enumerate((first,second,third)):
            t.position = pygame.Vector2(1090+i*10,800)
            g.mall.respawn_trash(t)
        g.upgrades.capacity_level = 2  # four slots, with two already occupied
        g.upgrades.held = 2
        g.interact()
        self.assertEqual(g.upgrades.held,4)
        self.assertTrue(first.cleaned)
        self.assertTrue(second.cleaned)
        self.assertFalse(third.cleaned)
        self.assertEqual(g.cash,0)

    def test_shop_pauses_world_and_mouse_keyboard_work(self):
        g = self.game
        self.open_shop()
        g.screen = pygame.display.set_mode((800,600))
        g.cash = 500
        before = g.player.rect.center
        active = g.mall.active_litter_count
        g.update(20,(1,0))
        self.assertEqual(g.player.rect.center,before)
        self.assertEqual(g.mall.active_litter_count,active)
        self.assertEqual(g.cash,500)
        # First gear row is the capacity upgrade.
        rect = g.shop_menu.rows(g)[0][1]
        g.shop_menu.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=rect.center),g)
        self.assertEqual(g.upgrades.capacity,2)
        g.shop_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_2),g)
        g.shop_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN),g)
        self.assertEqual(g.upgrades.decor,{'bench_0'})
        g.shop_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_3),g)
        g.draw()
        panel,_ = g.shop_menu.geometry(g.screen)
        self.assertLess(g.shop_menu.rows(g)[-1][1].bottom,panel.bottom-65)
        g.shop_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE),g)
        self.assertFalse(g.shop_menu.open)
        self.assertTrue(g.running)

    def test_cleaning_and_tab_do_not_grant_free_scenery(self):
        g = self.game
        for t in g.mall.trash:
            g.mall.clean_trash(t)
        self.assertEqual(g.upgrades.decor,set())
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_TAB))
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_DOWN))
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
        g.run()
        self.assertEqual(g.upgrades.decor,set())

    def test_trash_bins_are_clear_reachable_and_not_inside_shops(self):
        g = self.game
        self.assertEqual(len(g.mall.trash_bins),2)
        for trash_bin in g.mall.trash_bins:
            self.assertFalse(any(s.rect.colliderect(trash_bin.rect) for s in g.mall.stores))
            self.assertTrue(g.mall.opening_area.contains(trash_bin.rect))
            self.assertTrue(all(t.position.distance_to(trash_bin.position)>80 for t in g.mall.trash))

    def test_supplies_with_no_cash_or_rent_still_allows_earning(self):
        g = self.game
        for trash in g.mall.trash:
            g.mall.clean_trash(trash)
        g.mall.stores[0].restored = True
        g.mall.refresh_businesses()
        self.assertEqual(g.cash,0)
        self.assertEqual(sum(s.rent for s in g.mall.stores if s.restored),0)
        g.update(3.9,(0,0))
        self.assertEqual(g.mall.active_litter_count,0)
        g.update(0.2,(0,0))
        self.assertEqual(g.mall.active_litter_count,1)
        fresh = next(t for t in g.mall.trash if not t.cleaned)
        g.player.rect.center = fresh.position
        g.interact()
        self.assertEqual(g.cash,0)
        self.assertEqual(g.upgrades.held,1)
        g.player.rect.center = g.mall.trash_bins[0].position
        g.interact()
        self.assertEqual(g.cash,1)


if __name__ == '__main__':
    unittest.main()
