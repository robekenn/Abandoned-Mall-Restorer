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

    def draw(self, surface, camera):
        r = camera.rect(self.rect)
        pygame.draw.ellipse(surface, (42, 48, 47), r.move(0, 8))
        pygame.draw.rect(surface, (75, 173, 165), r, border_radius=7)
        pygame.draw.circle(surface, (240, 197, 149), (r.centerx, r.y + 3), 10)
        pygame.draw.line(surface, (35, 65, 69), (r.x + 5, r.bottom), (r.x + 5, r.bottom + 4), 4)
        pygame.draw.line(surface, (35, 65, 69), (r.right - 5, r.bottom), (r.right - 5, r.bottom + 4), 4)
