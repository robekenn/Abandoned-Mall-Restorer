import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
from array import array
import unittest
from unittest.mock import patch
import pygame
from game.audio import Audio
from game.game import Game
from game.music import four_level_wave, soundtrack, BEAT_SECONDS


class MusicTests(unittest.TestCase):
    def tearDown(self):
        pygame.quit()

    def test_original_soundtrack_is_quiet_loopable_and_supports_stereo(self):
        rate = 22050
        mono = array('h',soundtrack(rate,1))
        self.assertEqual(len(mono),round(rate*BEAT_SECONDS*32))
        self.assertGreater(max(mono),100)
        self.assertLess(max(abs(v) for v in mono),1200)
        self.assertLess(abs(mono[0]-mono[-1]),10)
        stereo = array('h',soundtrack(rate,2))
        self.assertEqual(len(stereo),len(mono)*2)
        self.assertEqual(stereo[0::2],mono)
        self.assertEqual(stereo[1::2],mono)
        self.assertEqual({four_level_wave(i/100) for i in range(100)}, {-1,-1/3,1/3,1})

    def test_music_loops_on_reserved_channel_and_effects_leave_it_playing(self):
        audio = Audio()
        self.assertIsNotNone(audio.music)
        self.assertTrue(audio.music_channel.get_busy())
        self.assertIs(audio.music_channel.get_sound(),audio.music)
        self.assertAlmostEqual(audio.music.get_length(),24,places=2)
        audio.play('pickup')
        self.assertIs(audio.music_channel.get_sound(),audio.music)
        self.assertTrue(audio.toggle())
        self.assertFalse(audio.toggle())
        self.assertTrue(audio.music_channel.get_busy())
        self.assertIs(audio.music_channel.get_sound(),audio.music)

    def test_mute_pauses_and_unmute_resumes_without_restarting_track(self):
        audio = Audio()
        with patch.object(audio,'music_channel') as channel:
            audio.toggle()
            channel.pause.assert_called_once()
            channel.unpause.assert_not_called()
            audio.toggle()
            channel.unpause.assert_called_once()
            channel.play.assert_not_called()

    def test_music_can_be_muted_while_shopping(self):
        game = Game()
        game.shop_menu.open = True
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_m))
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_DOWN))
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
        game.run()
        self.assertTrue(game.audio.muted)
        self.assertIn('muted',game.shop_menu.notice)

    def test_missing_device_disables_music_and_effects_safely(self):
        pygame.mixer.quit()
        with patch('pygame.mixer.init',side_effect=pygame.error('No audio device')):
            audio = Audio()
        self.assertIsNone(audio.music)
        self.assertIsNone(audio.music_channel)
        audio.play('pickup')
        audio.toggle()
        audio.toggle()
