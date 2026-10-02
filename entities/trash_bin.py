import pygame


class TrashBin:
    def __init__(self, position, name):
        self.position = pygame.Vector2(position)
        self.name = name
        self.rect = pygame.Rect(0, 0, 32, 34)
        self.rect.center = position

    @property
    def label(self):
        return f'Sell carried trash / {self.name}'

    def draw(self, surface, camera, art, font, selected=False):
        point = camera.point(self.position)
        art.draw(surface, 'trash_bin', point, (48, 48))
        label = font.render('SELL', True, (211, 222, 167))
        surface.blit(label, label.get_rect(center=(round(point.x), round(point.y)-34)))
        if selected:
            pygame.draw.rect(surface, (229,204,127), camera.rect(self.rect.inflate(16,16)), 2)
