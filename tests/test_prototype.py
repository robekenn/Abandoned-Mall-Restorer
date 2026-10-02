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

    def test_first_shop_and_income(self):
        g = self.game
        supplies,pages = g.mall.stores[:2]
        g.player.rect.center = supplies.position
        g.interact()
        self.assertFalse(supplies.restored)
        g.cash = supplies.cost
        g.interact()
        self.assertTrue(supplies.restored)
        self.assertTrue(g.shop_menu.open)
        g.shop_menu.open = False
        for trash in g.mall.trash:
            g.mall.clean_trash(trash)
        self.assertTrue(pages.available)
        g.cash = pages.cost
        g.player.rect.center = pages.position
        g.interact()
        self.assertTrue(pages.restored)
        g.update(10,(0,0))
        self.assertEqual(g.cash,10)
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
            g.mall.clean_trash(trash)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        g.run()
        self.assertEqual(g.upgrades.decor, set())


if __name__ == '__main__':
    unittest.main()
