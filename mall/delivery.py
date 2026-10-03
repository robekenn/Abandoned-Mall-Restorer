"""Permanent, signed delivery stations with reachable collection points."""
import pygame


class DeliveryPoint:
    def __init__(self, position, section):
        self.rect=pygame.Rect(*position,120,36)
        self.section=section
        self.name=f'{section} deliveries'
        self.position=pygame.Vector2(self.rect.centerx,self.rect.bottom+36)

    def draw(self, surface, camera, art, font):
        point=camera.point((self.rect.centerx,self.rect.centery-30))
        art.draw(surface,'delivery_station',point,(144,96))
        label=font.render('DELIVERIES',True,(228,214,164))
        sign=label.get_rect(midbottom=(point.x,point.y-42)).inflate(12,8)
        pygame.draw.rect(surface,(35,49,47),sign,border_radius=3)
        surface.blit(label,label.get_rect(center=sign.center))
