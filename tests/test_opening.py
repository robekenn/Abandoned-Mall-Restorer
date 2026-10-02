import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
from unittest.mock import patch
import pygame
from game.game import Game
from game.audio import Audio
from game.feedback import Feedback


class OpeningTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        pygame.quit()

    def test_first_step_has_one_reward_and_expires(self):
        g = self.game
        trash = g.mall.trash[0]
        self.assertIs(g.target(), trash)
        with patch.object(g.audio, 'play') as sound:
            g.interact()
            self.assertIn('Collected 1', g.message)
            sound.assert_any_call('sweep')
        self.assertEqual(g.cash, 0)
        self.assertEqual(len(g.feedback.popups), 1)
        self.assertGreater(len(g.feedback.particles), 0)
        self.assertGreater(g.player.action_time, 0)
        self.assertEqual(g.player.facing, 'down')
        g.interact()
        self.assertEqual(g.cash, 0)
        self.assertEqual(len(g.feedback.popups), 1)
        g.update(2, (0, 0))
        self.assertEqual(g.feedback.particles, [])
        self.assertEqual(g.feedback.popups, [])
        self.assertEqual(g.player.action_time, 0)

    def test_floor_changes_locally_and_future_wings_stay_dirty(self):
        mall = self.game.mall
        near = mall.trash[0].position
        far = mall.trash[-1].position
        self.assertFalse(mall.tile_restored(near))
        mall.clean_trash(mall.trash[0])
        self.assertTrue(mall.tile_restored(near))
        self.assertFalse(mall.tile_restored(far))
        self.assertFalse(mall.tile_restored((2200, 700)))
        self.assertLess(mall.opening_area.width, mall.size[0])
        self.assertTrue(all(mall.opening_area.collidepoint(t.position) for t in mall.trash))

    def test_future_galleries_block_movement(self):
        g = self.game
        east, south = g.mall.gates
        g.player.rect.center = (east.left-30, 800)
        g.player.move((1, 0), 1, g.mall.obstacles)
        self.assertLessEqual(g.player.rect.right, east.left)
        g.player.rect.center = (800, south.top-30)
        g.player.move((0, 1), 1, g.mall.obstacles)
        self.assertLessEqual(g.player.rect.bottom, south.top)

    def test_effects_and_ui_render_at_minimum_window(self):
        g = self.game
        g.screen = pygame.display.set_mode((800, 600))
        g.interact()
        g.update(0.05, (0, 0))
        g.draw()
        for line in g.hud.wrap('One light on in a quiet mall. Pages earns $5 every 5 seconds.', 496):
            self.assertLessEqual(g.hud.font.size(line)[0], 496)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        g.run()
        self.assertTrue(g.audio.muted)

    def test_audio_device_failure_does_not_stop_game(self):
        pygame.mixer.quit()
        with patch('pygame.mixer.init', side_effect=pygame.error('No audio device')):
            audio = Audio()
        self.assertEqual(audio.sounds, {})
        audio.play('pickup')
        self.assertTrue(audio.toggle())

    def test_restoration_effects_do_not_survive_forever(self):
        feedback = Feedback()
        feedback.burst((100, 100), 'OPEN', restored=True)
        feedback.update(0.2)
        self.assertTrue(feedback.particles)
        self.assertLess(feedback.popups[0].position.y, 70)
        feedback.update(2)
        self.assertEqual(feedback.particles, [])
        self.assertEqual(feedback.popups, [])


if __name__ == '__main__':
    unittest.main()
