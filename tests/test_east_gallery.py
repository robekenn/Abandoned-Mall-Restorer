import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from game.audio import Audio
from systems.upgrades import Upgrades


class EastGalleryTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def prepare_gate(self):
        g = self.game
        for t in g.mall.north_trash:
            g.mall.clean_trash(t)
        for store in g.mall.stores:
            store.restored = True
        g.mall.refresh_businesses()
        g.player.rect.center = g.mall.east.position

    def open_gallery(self):
        self.prepare_gate()
        self.game.cash = 1500
        self.game.interact()
        self.assertTrue(self.game.mall.east.unlocked)
        self.assertEqual(self.game.cash,0)

    def open_workshop(self):
        self.open_gallery()
        g = self.game
        workshop = g.mall.east.stores[0]
        g.player.rect.center = workshop.position
        g.cash = 2000
        g.interact()
        self.assertTrue(g.shop_menu.open)
        self.assertEqual(g.shop_menu.shop,'east')
        self.assertEqual(g.cash,0)

    def test_gallery_prerequisite_price_collision_and_single_purchase(self):
        g = self.game
        gate = g.mall.gates[0]
        g.cash = 1500
        g.player.rect.center = (gate.left-30,800)
        g.player.move((1,0),1,g.mall.obstacles,1.5)
        self.assertLessEqual(g.player.rect.right,gate.left)
        g.player.rect.center = g.mall.east.position
        self.assertIsNot(g.target(),g.mall.east)
        # The transaction guard also rejects an ineligible target if called directly.
        with patch.object(g,'target',return_value=g.mall.east),patch.object(g.audio,'play') as sound:
            g.interact()
            sound.assert_called_with('blocked')
        self.assertFalse(g.mall.east.unlocked)
        self.assertEqual(g.cash,1500)
        self.prepare_gate()
        g.cash = 1499
        g.interact()
        self.assertFalse(g.mall.east.unlocked)
        self.assertEqual(g.cash,1499)
        old_tiles = set(g.mall.floor_tiles)
        g.cash = 1500
        g.interact()
        self.assertEqual(g.cash,0)
        self.assertTrue(g.mall.east.unlocked)
        self.assertNotIn(gate,g.mall.obstacles)
        self.assertEqual(set(g.mall.floor_tiles),old_tiles|set(g.mall.east.floor_tiles))
        self.assertEqual(g.mall.dirty_tiles,set(g.mall.east.floor_tiles))
        self.assertTrue(g.mall.initial_cleanup_complete)
        self.assertLess(g.mall.cleanliness,1)
        g.player.move((1,0),1,g.mall.obstacles)
        self.assertGreater(g.player.rect.centerx,gate.right)
        size = len(g.mall.trash)
        self.assertFalse(g.mall.unlock_east())
        self.assertEqual(len(g.mall.trash),size)
        self.assertEqual(g.cash,0)
        g.player.rect.center = (2500,1030)
        g.player.move((0,1),1,g.mall.obstacles,1.5)
        self.assertLessEqual(g.player.rect.bottom,g.mall.east.south_gate.top)

    def test_gate_marker_and_prompt_stay_hidden_until_all_north_stores_open(self):
        g = self.game
        g.player.rect.center = g.mall.east.position
        with patch.object(g.mall.east,'draw_marker') as marker:
            g.draw()
            marker.assert_not_called()
            self.assertIsNot(g.target(),g.mall.east)
            for t in g.mall.north_trash:
                g.mall.clean_trash(t)
            for store in g.mall.north_stores[:-1]:
                store.restored = True
            g.mall.refresh_businesses()
            g.draw()
            marker.assert_not_called()
            self.assertIsNot(g.target(),g.mall.east)
            g.mall.north_stores[-1].restored = True
            g.mall.refresh_businesses()
            g.draw()
            marker.assert_called_once()
            self.assertIs(g.target(),g.mall.east)
            self.assertFalse(g.mall.east.unlocked)
            self.assertIn('$1,500',g.target().label)

    def test_workshop_price_access_and_shop_specific_upgrade_caps(self):
        self.open_gallery()
        g = self.game
        workshop = g.mall.east.stores[0]
        g.player.rect.center = workshop.position
        g.cash = 1999
        g.interact()
        self.assertFalse(workshop.restored)
        self.assertEqual(g.cash,1999)
        g.cash = 2000
        g.interact()
        self.assertTrue(workshop.restored)
        self.assertEqual(g.cash,0)
        self.assertEqual(g.shop_menu.shop,'east')
        g.cash = 10000
        g.buy_upgrade('advanced_capacity')
        self.assertEqual(g.upgrades.capacity,1)
        self.assertEqual(g.cash,10000)
        self.assertFalse(any(o.key == 'capacity' for o in g.upgrades.offers('Gear','east')))
        for _ in Upgrades.CAPACITY_PRICES:
            cash,_,bought = g.upgrades.purchase('capacity',g.cash)
            self.assertTrue(bought)
            g.cash = cash
        self.assertEqual(g.upgrades.capacity,20)
        before = g.cash
        g.buy_upgrade('capacity')  # Supplies gear is not sold at Workshop.
        self.assertEqual(g.cash,before)
        for capacity,price in zip((25,30,35,40),Upgrades.ADVANCED_CAPACITY_PRICES):
            before = g.cash
            g.buy_upgrade('advanced_capacity')
            self.assertEqual(g.upgrades.capacity,capacity)
            self.assertEqual(g.cash,before-price)
        before = g.cash
        g.buy_upgrade('advanced_capacity')
        self.assertEqual(g.cash,before)
        self.assertEqual(g.upgrades.capacity,40)
        # Revisit Supplies: no capacity beyond 20 is sold, no gear is lost.
        g.open_upgrade_shop(g.mall.stores[0])
        g.buy_upgrade('capacity')
        self.assertEqual((g.cash,g.upgrades.capacity),(before,40))
        g.buy_upgrade('speed')
        self.assertEqual(g.upgrades.speed_multiplier,1)

    def test_speed_purchases_change_movement_and_preserve_collision(self):
        self.open_workshop()
        g = self.game
        g.cash = 1900
        for speed in (1.15,1.3,1.5):
            g.buy_upgrade('speed')
            self.assertEqual(g.upgrades.speed_multiplier,speed)
        self.assertEqual(g.cash,0)
        before = g.cash
        g.buy_upgrade('speed')
        self.assertEqual(g.cash,before)
        g.shop_menu.open = False
        g.player.rect.center = (800,800)
        g.update(1,(1,0))
        self.assertAlmostEqual(g.player.rect.centerx,1160,places=3)
        g.player.rect.center = (670,650)
        g.update(1,(1,0))
        self.assertLessEqual(g.player.rect.right,g.mall.fountain.left)
        self.assertTrue(g.player.walking)

    def test_east_cleanup_coverage_business_order_and_returning_litter(self):
        self.open_workshop()
        g = self.game
        g.shop_menu.open = False
        east = g.mall.east
        self.assertFalse(east.stores[1].available)
        for tile in east.floor_tiles:
            self.assertTrue(any(t.position.distance_squared_to(tile)<115**2 for t in east.trash),tile)
        for t in east.trash:
            footprint = pygame.Rect(t.position.x-13,t.position.y-15,26,30)
            self.assertFalse(any(w.colliderect(footprint) for w in g.mall.obstacles))
            self.assertTrue(all(t.position.distance_to(s.position)>90 for s in east.stores))
            self.assertTrue(all(t.position.distance_to(b.position)>80 for b in east.bins))
        g.upgrades.capacity_level = len(Upgrades.CAPACITY_PRICES)
        for t in east.trash:
            if g.upgrades.held == g.upgrades.capacity:
                g.player.rect.center = east.bins[0].position
                g.interact()
            g.player.rect.center = t.position
            g.interact()
        g.player.rect.center = east.bins[1].position
        g.interact()
        self.assertEqual(g.cash,len(east.trash))
        self.assertTrue(east.initial_cleanup_complete)
        self.assertEqual(g.mall.cleanliness,1)
        self.assertTrue(all(g.mall.tile_restored(tile) for tile in east.floor_tiles))
        self.assertTrue(east.stores[1].available)
        self.assertFalse(east.stores[2].available)
        for store in east.stores[1:]:
            g.cash = store.cost
            g.player.rect.center = store.position
            g.interact()
            self.assertTrue(store.restored)
            self.assertEqual(g.cash,0)
        self.assertIsNone(g.mall.next_store)
        # Both completed sections remain eligible, with a bounded shared pool.
        self.assertEqual(set(g.mall.recurring_trash),set(g.mall.trash))
        for _ in range(60):
            g.litter_spawner.update(4,g.mall,g.player.rect.center)
        self.assertEqual(g.mall.active_litter_count,24)
        self.assertEqual(sum(not t.cleaned for t in east.trash),12)
        self.assertEqual(sum(not t.cleaned for t in g.mall.north_trash),12)
        for t in g.mall.trash:
            g.mall.clean_trash(t)
        self.assertEqual(g.mall.cleanliness,1)

    def test_new_section_initial_work_does_not_block_north_recurring_work(self):
        self.open_gallery()
        g = self.game
        self.assertEqual(g.mall.recurring_trash,g.mall.north_trash)
        g.litter_spawner.update(4,g.mall,g.player.rect.center)
        self.assertEqual(sum(not t.cleaned for t in g.mall.north_trash),1)
        self.assertEqual(sum(not t.cleaned for t in g.mall.east.trash),len(g.mall.east.trash))

    def test_east_menu_and_scenery_render_at_minimum_window(self):
        self.open_workshop()
        g = self.game
        g.screen = pygame.display.set_mode((800,600))
        g.shop_menu.open = False
        g.update(0,(0,0))
        g.draw()
        for category in ('Furniture','Garden'):
            for offer in g.upgrades.offers(category,'east'):
                g.upgrades.purchase(offer.key,10000,'east')
        g.draw()
        g.open_upgrade_shop(g.mall.east.stores[0])
        for category in range(3):
            g.shop_menu.category = category
            g.draw()
            panel,_ = g.shop_menu.geometry(g.screen)
            self.assertLess(g.shop_menu.rows(g)[-1][1].bottom,panel.bottom-65)
            g.shop_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_DOWN),g)
        g.shop_menu.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE),g)
        self.assertFalse(g.shop_menu.open)


class FixtureAndSoundTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def test_each_fixture_adds_one_base_rent_only_once(self):
        g = self.game
        for category in ('Furniture','Garden'):
            for offer in g.upgrades.offers(category):
                before = g.upgrades.fixture_rent
                _,_,bought = g.upgrades.purchase(offer.key,10000)
                self.assertTrue(bought)
                self.assertEqual(g.upgrades.fixture_rent,before+1)
                _,_,bought = g.upgrades.purchase(offer.key,10000)
                self.assertFalse(bought)
                self.assertEqual(g.upgrades.fixture_rent,before+1)
        self.assertEqual(g.upgrades.fixture_rent,12)
        # No paying stores are needed for fixtures to earn; normal cleanliness tiers apply.
        with patch.object(g.litter_spawner,'update'),patch.object(g.audio,'play') as sound:
            for dirty_count,payout in [(len(g.mall.floor_tiles),0),(len(g.mall.floor_tiles)-1,6),(1,12),(0,18)]:
                g.mall.dirty_tiles = set(g.mall.floor_tiles[:dirty_count])
                g.cash = 0
                g.rent_timer = 0
                sound.reset_mock()
                g.update(5,(0,0))
                self.assertEqual(g.cash,payout)
                if payout == 18:
                    sound.assert_called_once_with('bonus_rent')
                else:
                    sound.assert_not_called()

    def test_blocked_actions_have_feedback_and_do_not_charge_or_clean(self):
        g = self.game
        with patch.object(g.audio,'play') as sound:
            g.upgrades.held = 1
            dirt = set(g.mall.dirty_tiles)
            g.collect(g.mall.trash[0])
            self.assertEqual(g.mall.dirty_tiles,dirt)
            sound.assert_called_with('blocked')
            g.upgrades.held = 0
            sound.reset_mock()
            g.sell_trash(g.mall.trash_bins[0])
            sound.assert_called_once_with('blocked')
            g.player.rect.center = g.mall.stores[0].position
            g.interact()
            self.assertEqual(g.cash,0)
            self.assertFalse(g.mall.stores[0].restored)
            sound.assert_called_with('blocked')
            g.mall.stores[0].restored = True
            g.open_upgrade_shop(g.mall.stores[0])
            sound.reset_mock()
            g.buy_upgrade('capacity')
            self.assertEqual(g.upgrades.capacity,1)
            self.assertEqual(g.cash,0)
            sound.assert_called_once_with('blocked')
            g.shop_menu.open = False
            g.player.rect.center = (800,950)
            with patch.object(g,'target',return_value=None):
                g.interact()
            sound.assert_called_with('blocked')
        self.assertIn('Nothing within reach',g.message)

    def test_bonus_and_blocked_sounds_support_mute_and_no_device(self):
        audio = self.game.audio
        self.assertIn('bonus_rent',audio.sounds)
        self.assertIn('blocked',audio.sounds)
        for name in ('bonus_rent','blocked'):
            with patch.dict(audio.sounds,{name:unittest.mock.Mock()}) as sounds:
                audio.muted = True
                audio.play(name)
                sounds[name].play.assert_not_called()
                audio.muted = False
                audio.play(name)
                sounds[name].play.assert_called_once()
        pygame.mixer.quit()
        with patch('pygame.mixer.init',side_effect=pygame.error('No audio device')):
            silent = Audio()
        silent.play('bonus_rent')
        silent.play('blocked')
        self.assertEqual(silent.sounds,{})
