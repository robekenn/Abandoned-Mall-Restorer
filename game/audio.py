"""Quiet synthesized effects, with graceful fallback when audio is unavailable."""
from array import array
import math
import random
import pygame


class Audio:
    def __init__(self):
        self.muted = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, allowedchanges=0)
            rate, sample_format, channels = pygame.mixer.get_init()
            if sample_format != -16:
                return
            self.sounds['sweep'] = self._sound(rate, channels, 0.18, noise=True)
            self.sounds['pickup'] = self._sound(rate, channels, 0.12, notes=(440, 660))
            self.sounds['milestone'] = self._sound(rate, channels, 0.5, notes=(330, 440, 550, 660))
        except pygame.error:
            self.sounds.clear()

    @staticmethod
    def _sound(rate, channels, duration, noise=False, notes=(440,)):
        rng = random.Random(19)
        samples = array('h')
        count = int(rate * duration)
        for i in range(count):
            t = i / rate
            envelope = min(1, t / 0.008) * (1 - i / count) ** 2
            frequency = notes[min(len(notes) - 1, i * len(notes) // count)]
            wave = rng.uniform(-1, 1) if noise else math.sin(2 * math.pi * frequency * t)
            value = int(3800 * envelope * wave)
            samples.extend([value] * channels)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name):
        if not self.muted and name in self.sounds:
            self.sounds[name].play()

    def toggle(self):
        self.muted = not self.muted
        if self.muted and pygame.mixer.get_init():
            pygame.mixer.stop()
        return self.muted
