import pygame


class Trash:
    def __init__(self, position, kind="trash"):
        self.position = pygame.Vector2(position)
        self.kind = kind
        self.reward = 10
        self.cleaned = False

    @property
    def label(self):
        return "Sweep dirt (+$10)" if self.kind == "dirt" else "Collect litter (+$10)"

    def draw(self, surface, camera, selected=False):
        if self.cleaned:
            return
        p = camera.point(self.position)
        if selected:
            pygame.draw.circle(surface, (239, 197, 109), p, 25, 2)
        if self.kind == "dirt":
            pygame.draw.ellipse(surface, (114, 99, 76), (p.x-19, p.y-8, 38, 16))
            for dx, dy in [(-9, -3), (3, 4), (11, -2)]:
                pygame.draw.circle(surface, (86, 79, 64), p + (dx, dy), 3)
        else:
            pygame.draw.circle(surface, (58, 64, 61), p, 12)
            pygame.draw.rect(surface, (188, 169, 129), (p.x+8, p.y-3, 12, 9))
            pygame.draw.line(surface, (143, 150, 141), p + (-4, -11), p + (3, -15), 3)
