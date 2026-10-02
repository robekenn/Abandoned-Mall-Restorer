import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
import pygame
from game.game import Game
from entities.player import Player


class PrototypeTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def test_complete_restoration_loop(self):
        g = self.game
        g.player.rect.center = (1700, 950)
        g.interact()
        self.assertEqual(g.cash, 0)
        store = g.mall.stores[0]
        g.player.rect.center = store.position
        g.interact()
        self.assertFalse(store.restored)
        for trash in g.mall.trash[:10]:
            g.player.rect.center = trash.position
            g.interact()
            g.interact()
        self.assertEqual(g.cash, 100)
        g.player.rect.center = store.position
        g.interact()
        self.assertTrue(store.restored)
        self.assertEqual(g.cash, 0)
        g.interact()
        self.assertEqual(g.cash, 0)
        g.update(10, (0, 0))
        self.assertEqual(g.cash, 10)
        g.draw()

    def test_movement_and_collision(self):
        p = Player((100, 100))
        p.move((1, 1), 1, [])
        self.assertAlmostEqual(p.rect.centerx-100, p.rect.centery-100, places=4)
        self.assertAlmostEqual(pygame.Vector2(p.rect.center).distance_to((100,100)), 240, places=3)
        p = Player((100, 100))
        wall = pygame.Rect(150, 0, 20, 500)
        p.move((1, 0), 1, [wall])
        self.assertLessEqual(p.rect.right, wall.left)

    def test_scenery_unlocks(self):
        g = self.game
        g.change_decor()
        self.assertEqual(g.decor, 0)
        for t in g.mall.trash[:5]: t.cleaned = True
        g.change_decor()
        self.assertEqual(g.decor, 1)
        g.change_decor()
        self.assertEqual(g.decor, 0)
        for t in g.mall.trash[:10]: t.cleaned = True
        g.change_decor()
        g.change_decor()
        self.assertEqual(g.decor, 2)
        g.draw()

    def test_camera_and_quit_event(self):
        g = self.game
        g.camera.update((1800, 1100), (1100, 720))
        self.assertEqual(g.camera.offset, (1250, 740))
        g.camera.update((0, 0), (4000, 2400))
        self.assertEqual(g.camera.offset, (0, 0))
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        g.run()
        self.assertFalse(g.running)

    def test_walking_animation_and_idle(self):
        p = Player((100, 100))
        for direction, facing in (((1, 0), 'right'), ((-1, 0), 'left'),
                                  ((0, -1), 'up'), ((0, 1), 'down')):
            p.move((0, 0), 0, [])
            p.move(direction, 0.13, [])
            self.assertEqual(p.facing, facing)
            self.assertTrue(p.walking)
            self.assertEqual(p.animation_frame, 1)
            p.move(direction, 0.13, [])
            self.assertEqual(p.animation_frame, 2)
        p.move((0, 0), 0.13, [])
        self.assertFalse(p.walking)
        self.assertEqual(p.animation_frame, 0)
        p.rect.right = 150
        p.move((1, 0), 0.13, [pygame.Rect(150, 0, 20, 500)])
        self.assertFalse(p.walking)
        self.assertEqual(p.animation_frame, 0)

    def test_pixel_sprites_and_keyboard_events(self):
        g = self.game
        for facing in ('down', 'up', 'left', 'right'):
            for frame in range(4):
                sprite = g.art.sprites[f'player_{facing}_{frame}']
                self.assertEqual(sprite.get_size(), (16, 24))
                self.assertGreater(sprite.get_bounding_rect().width, 0)
                g.player.facing, g.player.animation_frame = facing, frame
                g.draw()
        for trash in g.mall.trash[:5]:
            trash.cleaned = True
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        g.run()
        self.assertEqual(g.decor, 1)


if __name__ == '__main__':
    unittest.main()
