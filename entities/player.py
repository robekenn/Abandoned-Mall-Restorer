import pygame
from game.settings import PLAYER_SPEED


class Player:
    def __init__(self, position):
        self.rect = pygame.FRect(0, 0, 20, 20)
        self.rect.center = position
        self.facing = 'down'
        self.animation_time = 0.0
        self.animation_frame = 0
        self.walking = False
        self.action_time = 0.0
        self.action_kind = 'trash'

    def use_tool(self, kind, target=None):
        self.action_kind = kind
        self.action_time = 0.32
        if target is not None:
            direction = pygame.Vector2(target) - self.rect.center
            if direction.length_squared():
                if abs(direction.x) > abs(direction.y):
                    self.facing = 'right' if direction.x > 0 else 'left'
                else:
                    self.facing = 'down' if direction.y > 0 else 'up'

    def move(self, direction, dt, obstacles):
        self.action_time = max(0, self.action_time - dt)
        direction = pygame.Vector2(direction)
        if direction.length_squared() > 1:
            direction.normalize_ip()
        previous = self.rect.center
        if direction.length_squared():
            if abs(direction.x) > abs(direction.y):
                self.facing = 'right' if direction.x > 0 else 'left'
            else:
                self.facing = 'down' if direction.y > 0 else 'up'
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

        self.walking = pygame.Vector2(self.rect.center).distance_squared_to(previous) > 0.0001
        if self.walking:
            self.animation_time += dt
            self.animation_frame = int(self.animation_time / 0.12) % 4
        else:
            self.animation_time = 0.0
            self.animation_frame = 0

    def draw(self, surface, camera, art):
        point = camera.point(self.rect.center)
        art.draw(surface, f'player_{self.facing}_{self.animation_frame}',
                 (point.x, point.y-12), (32, 48))
        if self.action_time > 0:
            offsets = {'down': (0, 16), 'up': (0, -24), 'left': (-18, 0), 'right': (18, 0)}
            end = point + offsets[self.facing]
            swing = 5 if self.action_time > 0.16 else -5
            end.x += swing
            pygame.draw.line(surface, (171, 132, 78), point, end, 3)
            if self.action_kind == 'dirt':
                pygame.draw.rect(surface, (207, 187, 121), (end.x-7, end.y-2, 14, 5))
            else:
                pygame.draw.line(surface, (188, 203, 183), end + (-4, -3), end, 2)
                pygame.draw.line(surface, (188, 203, 183), end + (4, -3), end, 2)
