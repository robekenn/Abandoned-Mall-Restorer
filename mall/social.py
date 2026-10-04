"""Shared, reachable seating rather than decoration-only dining tables."""
from dataclasses import dataclass
import pygame


@dataclass(eq=False)
class SocialTable:
    position: pygame.Vector2
    seats: tuple
    section: str

    @property
    def footprint(self):
        return pygame.Rect(self.position.x-27,self.position.y-19,54,38)


def place_tables(area, floor, obstacles, trash, section, count=2):
    tables=[]
    # Put seats on the existing navigation lattice, clear of cleanup patches.
    for goal in ((area.left+480,area.top+820),(area.right-480,area.top+900))[:count]:
        for p in sorted(floor,key=lambda p:pygame.Vector2(p).distance_squared_to(goal)):
            seats=(pygame.Vector2(p[0]-64,p[1]),pygame.Vector2(p[0]+64,p[1]))
            table=SocialTable(pygame.Vector2(p[0],p[1]-30),seats,section)
            if not area.contains(table.footprint.inflate(180,140)):continue
            if any(w.colliderect(table.footprint.inflate(30,30)) for w in obstacles):continue
            if any(table.footprint.inflate(32,32).collidepoint(t.position) for t in trash):continue
            if any(tuple(seat) not in floor or any(w.colliderect(pygame.Rect(seat.x-12,seat.y-14,24,28)) for w in obstacles+[table.footprint]) for seat in seats):continue
            if any(table.position.distance_to(t.position)<240 for t in tables):continue
            tables.append(table);obstacles.append(table.footprint);break
    return tables
