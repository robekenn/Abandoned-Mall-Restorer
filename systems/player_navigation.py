"""Optional click-to-walk using the same obstacle graph as mall visitors."""

import pygame
from game.settings import PLAYER_SPEED
from systems.shoppers import Walkways


class PlayerNavigation:
    def __init__(self):
        self.walkways = Walkways((28, 32))
        self.path = []
        self.scene = None

    def cancel(self):
        self.path.clear()

    def start(self, game, destination):
        self.cancel()
        world = game.courtyard.world if game.scene == "courtyard" else game.mall
        destination = pygame.Vector2(destination)
        body = game.player.rect.copy()
        body.center = destination
        if not any(area.collidepoint(destination) for area in world.playable_areas):
            return False
        if any(body.colliderect(wall) for wall in world.obstacles):
            return False
        self.walkways.refresh(world)
        origin = pygame.Vector2(game.player.rect.center)
        if not any(wall.clipline(origin, destination) for wall in self.walkways.walls):
            path = [destination]
        else:
            path = self.walkways.route(origin, destination)
        if path is None:
            return False
        # Skip visible intermediate nodes without cutting through furniture.
        while path:
            index = next(
                i
                for i in range(len(path) - 1, -1, -1)
                if not any(
                    wall.clipline(origin, path[i]) for wall in self.walkways.walls
                )
            )
            origin = path[index]
            self.path.append(origin)
            path = path[index + 1 :]
        self.scene = game.scene
        return True

    def direction(self, game, dt, manual):
        if any(manual) or self.scene != game.scene:
            self.cancel()
            return manual
        position = pygame.Vector2(game.player.rect.center)
        while self.path and position.distance_to(self.path[0]) < 1:
            self.path.pop(0)
        if not self.path or dt <= 0:
            return (0, 0)
        delta = self.path[0] - position
        step = PLAYER_SPEED * game.upgrades.speed_multiplier * dt
        return delta.normalize() * min(1, delta.length() / step)
