"""Quiet synthesized effects, with graceful fallback when audio is unavailable."""
from array import array
from game.music import soundtrack
import math
import random
import pygame


class Audio:
    def __init__(self):
        self.muted = False
        self.sounds = {}
        self.music = None
        self.music_channel = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, allowedchanges=0)
            rate, sample_format, channels = pygame.mixer.get_init()
            if sample_format != -16:
                return
            self.sounds['sweep'] = self._sound(rate, channels, 0.18, noise=True)
            self.sounds['pickup'] = self._sound(rate, channels, 0.12, notes=(440, 660))
            self.sounds['bonus_rent'] = self._sound(rate, channels, 0.32, notes=(660, 880, 1100))
            self.sounds['blocked'] = self._sound(rate, channels, 0.14, notes=(220, 165))
            self.sounds['milestone'] = self._sound(rate, channels, 0.5, notes=(330, 440, 550, 660))
            self.music = pygame.mixer.Sound(buffer=soundtrack(rate,channels))
            # Reserve a dedicated channel so effects cannot interrupt the soundtrack.
            pygame.mixer.set_reserved(1)
            self.music_channel = pygame.mixer.Channel(0)
            self.music_channel.play(self.music,loops=-1)
        except pygame.error:
            self.sounds.clear()
            self.music = None
            self.music_channel = None

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

    def set_volumes(self, music, effects):
        if self.music_channel:self.music_channel.set_volume(music)
        for sound in self.sounds.values():sound.set_volume(effects)

    def play(self, name):
        if not self.muted and name in self.sounds:
            self.sounds[name].play()

    def toggle(self):
        self.muted = not self.muted
        if self.muted and pygame.mixer.get_init():
            if self.music_channel:
                self.music_channel.pause()
            for channel in range(1,pygame.mixer.get_num_channels()):
                pygame.mixer.Channel(channel).stop()
        elif not self.muted and self.music_channel and pygame.mixer.get_init():
            self.music_channel.unpause()
        return self.muted
