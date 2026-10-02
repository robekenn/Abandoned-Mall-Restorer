import pygame


class Camera:
    def __init__(self, world_size):
        self.world_size = world_size
        self.offset = pygame.Vector2()

    def update(self, target, viewport):
        for axis in range(2):
            maximum = max(0, self.world_size[axis] - viewport[axis])
            self.offset[axis] = max(0, min(maximum, target[axis] - viewport[axis] / 2))

    def rect(self, rect):
        return pygame.Rect(rect).move(-round(self.offset.x), -round(self.offset.y))

    def point(self, point):
        return pygame.Vector2(point) - self.offset
