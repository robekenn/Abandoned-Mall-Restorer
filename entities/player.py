import pygame
from game.settings import PLAYER_SPEED


class Player:
    def __init__(self, position):
        self.rect = pygame.FRect(0, 0, 26, 30)
        self.rect.center = position
        self.facing = 'down'
        self.animation_time = 0.0
        self.animation_frame = 0
        self.walking = False
        self.action_time = 0.0
        self.action_kind = 'trash'

    def use_tool(self, kind, target=None):
        self.action_kind = kind
        self.action_time = 0.42
        if target is not None:
            direction = pygame.Vector2(target) - self.rect.center
            if direction.length_squared():
                if abs(direction.x) > abs(direction.y):
                    self.facing = 'right' if direction.x > 0 else 'left'
                else:
                    self.facing = 'down' if direction.y > 0 else 'up'

    def move(self, direction, dt, obstacles, speed_multiplier=1):
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
        movement = direction * PLAYER_SPEED * speed_multiplier * dt
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
        frame=min(3,max(0,int((.42-self.action_time)/.105)))
        name=f'player_{self.facing}_clean_{frame}' if self.action_time>0 else f'player_{self.facing}_{self.animation_frame}'
        art.draw(surface,name,(point.x,point.y-12),(48,72))
        if self.action_time>0:
            tool={'dirt':'broom','water':'water','setup':'setup'}.get(self.action_kind,'grabber')
            offset={'down':(12,8),'up':(-10,-30),'left':(-28,-7),'right':(28,-7)}[self.facing]
            art.draw(surface,f'{tool}_{self.facing}_{frame}',point+offset,(72,72))
