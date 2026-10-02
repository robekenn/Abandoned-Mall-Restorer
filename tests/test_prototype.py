import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
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

    def test_camera_and_quit_event(self):
        g = self.game
        g.camera.update((1800, 1100), (1100, 720))
        self.assertEqual(g.camera.offset, (700, 380))
        g.camera.update((0, 0), (2000, 1200))
        self.assertEqual(g.camera.offset, (0, 0))
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        g.run()
        self.assertFalse(g.running)


if __name__ == '__main__':
    unittest.main()
