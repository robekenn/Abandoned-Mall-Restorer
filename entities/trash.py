import pygame


class Trash:
    def __init__(self, position, kind="trash"):
        self.position = pygame.Vector2(position)
        self.kind = kind
        self.cleaned = False
        self.ever_cleaned = False

    @property
    def label(self):
        return "Sweep dirt into bag (+1 item)" if self.kind == "dirt" else "Collect litter (+1 item)"

    def draw(self, surface, camera, art, selected=False):
        if self.cleaned:
            return
        point = camera.point(self.position)
        if selected:
            pygame.draw.ellipse(surface, (239, 197, 109), (point.x-28,point.y-16,56,32), 2)
        name = 'dirt' if self.kind == 'dirt' else ('trash_bags' if int(self.position.x)%3 else 'litter')
        art.draw(surface, name, point, (62, 42) if self.kind == 'dirt' else (48, 45))
