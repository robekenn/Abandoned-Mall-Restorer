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
        variant=(int(self.position.x)//64*31+int(self.position.y)//64*17)%4
        name='dirt' if self.kind=='dirt' else ('trash_bags','litter_paper','litter_cup','litter_bottle')[variant]
        art.draw(surface,name,point,(48,48))
