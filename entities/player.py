import pygame
from game.settings import PLAYER_SPEED


class Player:
    def __init__(self, position):
        self.rect = pygame.FRect(0, 0, 26, 30)
        self.rect.center = position

    def move(self, direction, dt, obstacles):
        direction = pygame.Vector2(direction)
        if direction.length_squared() > 1:
            direction.normalize_ip()
        # Small steps keep collisions reliable even during a slow frame.
        movement = direction * PLAYER_SPEED * dt
        steps = max(1, int(movement.length() / 8) + 1)
        for _ in range(steps):
            for axis in (0, 1):
                delta = movement[axis] / steps
                if axis == 0:
                    self.rect.x += delta
                else:
                    self.rect.y += delta
                for wall in obstacles:
                    if self.rect.colliderect(wall):
                        if axis == 0:
                            if delta > 0: self.rect.right = wall.left
                            elif delta < 0: self.rect.left = wall.right
                        else:
                            if delta > 0: self.rect.bottom = wall.top
                            elif delta < 0: self.rect.top = wall.bottom

    def draw(self, surface, camera, art):
        point = camera.point(self.rect.center)
        art.draw(surface, 'player', (point.x, point.y-12), (48, 70))
