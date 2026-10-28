"""Key hints stay readable, fit their panels and follow rebound controls."""

import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import unittest
import pygame
from game.preferences import Preferences, HintFont
from ui import theme


class KeycapTests(unittest.TestCase):
    def setUp(self):
        pygame.font.init()
        self.font = pygame.font.Font(None, 20)

    def tearDown(self):
        pygame.quit()

    def test_rebound_keys_render_once_and_movement_uses_four_keycaps(self):
        preferences = Preferences('/unused', enabled=False)
        preferences.bind('journal', pygame.K_i)
        preferences.bind('interact', pygame.K_j)
        preferences.bind('up', pygame.K_z)
        custom = theme.KeycapFont(HintFont(self.font, preferences))
        literal = theme.KeycapFont(self.font)
        actual = custom.render('Hold [E] · [WASD] · [J] map', True, theme.TEXT)
        expected = literal.render('Hold [J] · [Z] [A] [S] [D] · [I] map', True, theme.TEXT)
        self.assertEqual(actual.get_size(), expected.get_size())
        self.assertEqual(pygame.image.tobytes(actual, 'RGBA'),
                         pygame.image.tobytes(expected, 'RGBA'))

    def test_measurement_and_wrapping_include_keycap_padding_and_long_key_names(self):
        font = theme.KeycapFont(self.font)
        text = '[Left Shift] move · [Enter] / click: confirm · [Esc]: return'
        lines = font.wrap(text, 200)
        self.assertGreater(len(lines), 1)
        self.assertIn('[Left Shift]', lines[0])
        for line in lines:
            image = font.render(line, True, theme.TEXT)
            self.assertEqual(image.get_size(), font.size(line))
            self.assertLessEqual(image.get_width(), 200)
        self.assertGreater(font.size('[Enter]')[0], self.font.size('Enter')[0])

    def test_footer_wraps_inside_small_panels_and_light_background_hints_fit(self):
        screen = pygame.Surface((800, 600))
        panel = pygame.Rect(120, 40, 560, 520)
        bounds = theme.hint_footer(screen, panel, self.font,
                                   '[1]–[7] / click: apply   [Enter]: selected   [F3] / [Esc]: close')
        self.assertTrue(panel.contains(bounds))
        self.assertLess(bounds.bottom, panel.bottom)
        area = pygame.Rect(320, 460, 440, 44)
        bounds = theme.hint(screen, self.font,
                            '[Up] / [Down]: saves · [Enter]: play · [N]: new · [D]: delete',
                            area.topleft, (45, 68, 57), width=area.width)
        self.assertTrue(area.contains(bounds))

