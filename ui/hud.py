import pygame


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 25)
        self.title = pygame.font.Font(None, 34)
        self.small = pygame.font.Font(None, 20)

    def wrap(self, text, width):
        lines = []
        line = ''
        for word in text.split():
            candidate = f'{line} {word}'.strip()
            if line and self.font.size(candidate)[0] > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        return lines

    def directory(self, surface, mall, player):
        width, height = surface.get_size()
        panel = pygame.Rect(width-214, height-240, 190, 142)
        pygame.draw.rect(surface, (24,36,39), panel)
        pygame.draw.rect(surface, (74,95,91), panel, 2)
        surface.blit(self.small.render('MALL DIRECTORY',True,(184,192,169)), (panel.x+10,panel.y+9))
        bounds = pygame.Rect(panel.x+10,panel.y+32,170,85)
        sx,sy = bounds.width/mall.size[0], bounds.height/mall.size[1]
        pygame.draw.rect(surface, (49,62,62), bounds)
        opening = mall.opening_area
        corner = pygame.Rect(bounds.x+opening.x*sx,bounds.y+opening.y*sy,opening.width*sx,opening.height*sy)
        pygame.draw.rect(surface, (109,139,108) if mall.cleaned_count else (94,110,93),corner)
        for gate in mall.gates:
            rect = pygame.Rect(bounds.x+gate.x*sx,bounds.y+gate.y*sy,max(2,gate.width*sx),max(2,gate.height*sy))
            pygame.draw.rect(surface, (194,162,100),rect)
        for store in mall.stores + mall.distant_stores:
            rect = pygame.Rect(bounds.x+store.rect.x*sx,bounds.y+store.rect.y*sy,store.rect.width*sx,store.rect.height*sy)
            pygame.draw.rect(surface,(224,199,111) if store.restored else (29,43,45),rect)
        point = (round(bounds.x+player[0]*sx),round(bounds.y+player[1]*sy))
        pygame.draw.rect(surface,(235,230,191),(point[0]-2,point[1]-2,4,4))
        surface.blit(self.small.render('YOU / NORTH ARCADE',True,(177,190,174)), (panel.x+8,panel.bottom-18))

    def draw(self, surface, cash, cleaned, total, target, message, restored,
             cleaned_count=0, decor=0, mall=None, player=(0,0), muted=False):
        width, height = surface.get_size()
        pygame.draw.rect(surface, (24,34,39),(0,0,width,118))
        surface.blit(self.title.render('NORTHGATE',True,(237,225,199)),(24,14))
        surface.blit(self.small.render('NORTH ARCADE / A SMALL BEGINNING',True,(165,184,172)),(24,45))
        if restored:
            objective = 'Keep tending this corner. Bring the fountain back.' if cleaned < total else 'A welcoming corner. The rest of Northgate awaits.'
        elif cleaned < 3:
            objective = 'Start here: clear three patches near Pages Bookshop.'
        elif cash < 100:
            objective = f'A little at a time: earn ${100-cash} more to reopen Pages.'
        else:
            objective = 'Your first light: reopen Pages at its gold door marker.'
        surface.blit(self.font.render(objective,True,(191,204,183)),(24,67))
        unlock = 'Greenery at 5 steps / Mosaic at 10' if cleaned_count < 5 else ('Tab: greenery / Mosaic at 10' if cleaned_count < 10 else 'Tab: choose this corner\'s scenery')
        surface.blit(self.small.render(unlock,True,(173,191,157)),(24,95))
        surface.blit(self.title.render(f'${cash}',True,(140,216,174)),(width-160,17))
        surface.blit(self.font.render(f'{cleaned}/{total} small steps',True,(214,211,188)),(width-190,49))
        bar = pygame.Rect(width-190,83,166,6)
        pygame.draw.rect(surface,(60,78,73),bar)
        pygame.draw.rect(surface,(149,176,119),(bar.x,bar.y,round(bar.width*cleaned/max(1,total)),bar.height))
        pygame.draw.rect(surface,(24,34,39),(0,height-82,width,82))
        text = 'E  ' + target.label if target else 'Find a small patch of litter or dust. Every one helps.'
        surface.blit(self.font.render(text,True,(239,205,138)),(24,height-70))
        controls = f'WASD / Arrows: move   E: tend   Tab: scenery   M: sound {"off" if muted else "on"}   Esc: quit'
        surface.blit(self.small.render(controls,True,(166,186,180)),(24,height-36))
        if mall:
            self.directory(surface,mall,player)
        if message:
            max_width = width-280 if mall else width-80
            lines = self.wrap(message,max_width-24)
            box = pygame.Rect(24,height-103-len(lines)*25,max_width,len(lines)*25+16)
            pygame.draw.rect(surface,(35,49,48),box)
            pygame.draw.rect(surface,(116,133,108),box,1)
            for i,line in enumerate(lines):
                surface.blit(self.font.render(line,True,(243,229,182)),(box.x+12,box.y+8+i*25))
