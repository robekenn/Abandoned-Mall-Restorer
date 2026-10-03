"""Opt-in playtest actions preserve normal gameplay and use valid unlock paths."""
import os
os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
import unittest
from unittest.mock import patch
import pygame
from game.game import Game


class DeveloperTests(unittest.TestCase):
    def tearDown(self):pygame.quit()

    def test_normal_game_cannot_use_developer_actions(self):
        g=Game();self.assertFalse(g.developer.enabled)
        for action,_ in g.developer.ACTIONS:self.assertFalse(g.developer.act(action,g))
        self.assertEqual(g.cash,0);self.assertFalse(g.mall.east.unlocked)

    def test_grants_add_exact_money_without_changing_progress(self):
        g=Game(developer=True);g.cash=.75
        for amount in (10000,100000,1000000):self.assertTrue(g.developer.act('cash_'+str(amount),g))
        self.assertEqual(g.cash,1110000.75);self.assertEqual(g.total_collected,0)
        self.assertFalse(g.mall.initial_cleanup_complete);self.assertFalse(g.mall.stores[0].restored)
        self.assertFalse(g.developer.act('cash_7',g));self.assertEqual(g.cash,1110000.75)

    def test_clean_current_court_and_safe_corridor_rejection(self):
        g=Game(developer=True);g.developer.act('next',g)
        self.assertTrue(g.developer.act('clean',g));self.assertTrue(g.mall.east.initial_cleanup_complete)
        self.assertEqual(g.total_collected,0);self.assertEqual(g.cash,0)
        g.player.rect.center=(1775,800)
        self.assertFalse(g.developer.act('clean',g))

    def test_jump_uses_sequential_unlocks_with_reachable_spawn_and_no_cash_charge(self):
        g=Game(developer=True);g.cash=100;g.tutorial.start(g)
        for region in g.mall.regions:
            self.assertTrue(g.developer.act('next',g))
            self.assertTrue(region.unlocked);self.assertTrue(region.ready(g.mall))
            self.assertEqual(g.player.rect.center,region.stores[0].position)
            self.assertFalse(any(w.collidepoint(g.player.rect.center) for w in g.mall.obstacles))
            self.assertTrue(region.stores[0].available);self.assertFalse(region.stores[0].restored)
            self.assertFalse(region.initial_cleanup_complete);self.assertEqual(g.cash,100)
        self.assertFalse(g.developer.act('next',g));self.assertFalse(g.tutorial.active)

    def test_panel_mouse_keyboard_and_paused_simulation(self):
        g=Game(developer=True);g.screen=pygame.display.set_mode((800,600));g.developer.open=True
        g.developer.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_2),g)
        self.assertEqual(g.cash,100000)
        row=g.developer.geometry(g.screen)[1][0]
        g.developer.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=row.center),g)
        self.assertEqual(g.cash,110000)
        before=(g.player.rect.center,g.cash,g.litter_spawner.elapsed,g.rent_timer)
        g.update(100,(1,0));self.assertEqual((g.player.rect.center,g.cash,g.litter_spawner.elapsed,g.rent_timer),before)
        panel,rows=g.developer.geometry(g.screen);self.assertTrue(all(panel.contains(r) for r in rows))
        g.draw();g.developer.handle(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE),g)
        self.assertFalse(g.developer.open);self.assertTrue(g.running)

    def test_f3_opens_panel_only_in_enabled_game_loop(self):
        for enabled in (False,True):
            g=Game(developer=enabled)
            events=[[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F3),pygame.event.Event(pygame.KEYDOWN,key=pygame.K_1)],
                    [pygame.event.Event(pygame.QUIT)]]
            with patch('pygame.event.get',side_effect=events),patch.object(g,'draw'),patch.object(g,'update'):
                g.run()
            self.assertEqual(g.developer.open,enabled)
            self.assertEqual(g.cash,10000 if enabled else 0)

    def test_short_roof_sprites_and_collision_stay_on_same_front_edge(self):
        g=Game();up=g.mall.north_stores[-1];down=g.mall.north_stores[1]
        self.assertEqual(up.rect.height,144);self.assertEqual(down.rect.height,240)
        self.assertEqual(up.position.y,up.rect.top-35)
        for kind in ('bookshop','cafe'):
            for state in ('dirty','clean','clean_open'):
                sprite=g.art.sprites[f'{kind}_{state}_up']
                self.assertEqual(sprite.get_size(),(48,24))
        self.assertNotEqual(pygame.image.tobytes(g.art.sprites['bookshop_clean_up'],'RGBA'),pygame.image.tobytes(g.art.sprites['cafe_clean_up'],'RGBA'))
        up.restored=True;up.door_open=True;up.request_level=3
        g.player.rect.center=up.position;g.update(0,(0,0));g.draw()
