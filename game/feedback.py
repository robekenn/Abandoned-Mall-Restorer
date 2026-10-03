"""Short-lived world-space particles and reward labels."""
from dataclasses import dataclass
import random
import pygame


@dataclass
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    life: float
    color: tuple
    size: int = 3


@dataclass
class Popup:
    position: pygame.Vector2
    text: str
    life: float = 1.4


class Feedback:
    def __init__(self):
        self.particles = []
        self.popups = []
        self.random = random.Random(7)

    def burst(self, position, text, restored=False, kind=None):
        colors = [(211, 180, 118), (156, 173, 141)] if restored else [(168, 152, 118), (203, 193, 155)]
        if kind=='dirt':colors=[(172,120,79),(189,190,164),(125,136,128)]
        elif kind:colors=[(228,214,164),(113,175,188),(189,190,164)]
        for _ in range(18 if restored else 10):
            velocity = pygame.Vector2(self.random.uniform(-50, 50), self.random.uniform(-65, -15))
            self.particles.append(Particle(pygame.Vector2(position), velocity, 0.65, self.random.choice(colors),2 if kind else 3))
        self.popups.append(Popup(pygame.Vector2(position) + (0, -30), text))

    def update(self, dt):
        for p in self.particles:
            p.position += p.velocity * dt
            p.velocity.y += 75 * dt
            p.life -= dt
        for popup in self.popups:
            popup.position.y -= 24 * dt
            popup.life -= dt
        self.particles = [p for p in self.particles if p.life > 0]
        self.popups = [p for p in self.popups if p.life > 0]

    def draw(self, surface, camera, font):
        for p in self.particles:
            point = camera.point(p.position)
            pygame.draw.rect(surface, p.color, (round(point.x), round(point.y), p.size, p.size))
        for popup in self.popups:
            point = camera.point(popup.position)
            label = font.render(popup.text, True, (230, 221, 160))
            shadow = font.render(popup.text, True, (29, 40, 39))
            surface.blit(shadow, shadow.get_rect(center=(round(point.x) + 1, round(point.y) + 2)))
            surface.blit(label, label.get_rect(center=(round(point.x), round(point.y))))
