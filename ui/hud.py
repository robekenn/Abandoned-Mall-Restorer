import pygame


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 25)
        self.title = pygame.font.Font(None, 34)

    def draw(self, surface, cash, cleaned, total, target, message, restored, cleaned_count=0, decor=0):
        width, height = surface.get_size()
        pygame.draw.rect(surface, (24, 34, 39), (0, 0, width, 98))
        surface.blit(self.title.render("NORTHGATE / MALL RESTORER", True, (237, 225, 199)), (24, 16))
        objective = "First shop reopened! More wings coming soon." if restored else "Earn $100 cleaning, then reopen Pages Bookshop."
        surface.blit(self.font.render(objective, True, (166, 186, 180)), (24, 56))
        surface.blit(self.title.render(f"${cash}", True, (140, 216, 174)), (width-150, 17))
        surface.blit(self.font.render(f"Cleaned {cleaned}/{total}", True, (214, 211, 188)), (width-150, 57))
        pygame.draw.rect(surface, (24, 34, 39), (0, height-80, width, 80))
        text = "E  " + target.label if target else "Walk near litter or the gold marker to interact."
        surface.blit(self.font.render(text, True, (239, 205, 138)), (24, height-69))
        surface.blit(self.font.render("WASD / Arrows: move    E: interact    Tab: scenery    Esc: quit", True, (166, 186, 180)), (24, height-35))
        unlock = "Scenery locked: clean 5 spots" if cleaned_count < 5 else ("Greenery unlocked | Mosaic at 10 cleaned" if cleaned_count < 10 else "All scenery unlocked | Tab to change")
        text = self.font.render(unlock, True, (178,201,165))
        surface.blit(text, (24,79))
        if message:
            label = self.font.render(message, True, (255, 243, 202))
            box = label.get_rect(center=(width//2, height-111)).inflate(30, 20)
            pygame.draw.rect(surface, (35, 49, 48), box, border_radius=8)
            surface.blit(label, label.get_rect(center=box.center))
