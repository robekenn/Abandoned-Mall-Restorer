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
        for dumpster in mall.dumpsters:
            point = (round(bounds.x+dumpster.position.x*sx),round(bounds.y+dumpster.position.y*sy))
            pygame.draw.rect(surface,(129,196,185),(point[0]-2,point[1]-2,5,5))
        point = (round(bounds.x+player[0]*sx),round(bounds.y+player[1]*sy))
        pygame.draw.rect(surface,(235,230,191),(point[0]-2,point[1]-2,4,4))
        surface.blit(self.small.render('YOU / NORTH ARCADE',True,(177,190,174)), (panel.x+8,panel.bottom-18))

    def draw(self, game, target):
        surface = game.screen
        mall,upgrades = game.mall,game.upgrades
        width,height = surface.get_size()
        pygame.draw.rect(surface,(24,34,39),(0,0,width,118))
        surface.blit(self.title.render('NORTHGATE',True,(237,225,199)),(24,14))
        surface.blit(self.small.render('NORTH ARCADE / A SMALL BEGINNING',True,(165,184,172)),(24,45))
        next_shop = mall.next_store
        if upgrades.held == upgrades.capacity:
            objective = 'Bag full. Sell your load at a SELL dumpster.'
        elif not mall.stores[0].restored:
            objective = 'Collect and sell litter. Reopen Supplies for $100.'
        elif not mall.initial_cleanup_complete:
            objective = f'First sweep: {mall.active_litter_count} patches left. E at Supplies: upgrades.'
        elif next_shop:
            objective = f'Next: {next_shop.name} / ${next_shop.cost} / +${next_shop.rent} rent.'
        else:
            objective = 'All businesses open. Buy upgrades and keep the arcade welcoming.'
        objective_font = self.small if self.font.size(objective)[0] > width-250 else self.font
        surface.blit(objective_font.render(objective,True,(191,204,183)),(24,67))
        bag_color = (239,181,109) if upgrades.held == upgrades.capacity else (173,191,157)
        inventory = f'Bag {upgrades.held}/{upgrades.capacity} / Sale ${upgrades.unit_value} each / {upgrades.tool[0]}'
        surface.blit(self.small.render(inventory,True,bag_color),(24,95))
        surface.blit(self.title.render(f'${game.cash}',True,(140,216,174)),(width-160,17))
        status = f'{round(mall.cleanliness*100)}% clean / {mall.active_litter_count} litter'
        surface.blit(self.small.render(status,True,(214,211,188)),(width-190,49))
        rent = sum(s.rent for s in mall.stores if s.restored)
        surface.blit(self.small.render(f'Rent +${rent} / 5s',True,(164,186,168)),(width-190,67))
        bar = pygame.Rect(width-190,91,166,6)
        pygame.draw.rect(surface,(60,78,73),bar)
        pygame.draw.rect(surface,(149,176,119),(bar.x,bar.y,round(bar.width*mall.cleanliness),bar.height))
        pygame.draw.rect(surface,(24,34,39),(0,height-82,width,82))
        text = 'E  '+target.label if target else 'Collect litter / sell at dumpsters / upgrade at Supplies.'
        surface.blit(self.font.render(text,True,(239,205,138)),(24,height-70))
        controls = f'WASD / Arrows: move   E: interact   M: sound {"off" if game.audio.muted else "on"}   Esc: quit'
        surface.blit(self.small.render(controls,True,(166,186,180)),(24,height-36))
        self.directory(surface,mall,game.player.rect.center)
        if game.message_timer:
            max_width = width-280
            lines = self.wrap(game.message,max_width-24)
            box = pygame.Rect(24,height-103-len(lines)*25,max_width,len(lines)*25+16)
            pygame.draw.rect(surface,(35,49,48),box)
            pygame.draw.rect(surface,(116,133,108),box,1)
            for i,line in enumerate(lines):
                surface.blit(self.font.render(line,True,(243,229,182)),(box.x+12,box.y+8+i*25))
