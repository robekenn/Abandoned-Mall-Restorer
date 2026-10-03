"""Small, hand-authored pixel sprites; no atlas download is required."""
import pygame

PALETTE = {
    'ink': '#29383b', 'shadow': '#455354', 'stone': '#7d8880',
    'light': '#bdbea4', 'cream': '#e4d6a4', 'wood': '#856448',
    'rust': '#ac784f', 'teal': '#548b83', 'green': '#709657',
    'leaf': '#a5bf65', 'water': '#71afbc', 'blue': '#426b83',
    'skin': '#d6a875', 'gold': '#dfb45e',
}


def canvas(size=(24, 24)):
    return pygame.Surface(size, pygame.SRCALPHA)


def box(s, color, rect):
    pygame.draw.rect(s, PALETTE[color], rect)


def store(kind, clean, door_open=False):
    s = canvas((48, 40))
    box(s, 'ink', (1, 2, 46, 36))
    box(s, 'teal' if clean else 'shadow', (3, 4, 42, 32))
    box(s, 'cream' if clean else 'stone', (4, 5, 40, 6))
    box(s, 'ink', (5, 16, 15, 18))
    box(s, 'ink', (28, 16, 15, 18))
    box(s, 'gold' if clean else 'stone', (7, 18, 11, 13))
    box(s, 'gold' if clean else 'stone', (30, 18, 11, 13))
    box(s, 'ink', (21, 16, 6, 20))
    box(s, 'water' if clean else 'shadow', (22, 18, 4, 12))
    if door_open:
        # Right-hand hinge and folded leaf; the left half reveals the interior.
        box(s,'ink',(22,18,4,12))
        box(s,'water',(24,18,2,12))
        box(s,'light',(26,17,1,18))
        box(s,'cream',(24,28,1,1))
    else:
        box(s, 'cream', (22, 28, 1, 1))
    if clean:
        for x in range(4, 44, 5):
            box(s, 'rust' if kind == 'cafe' else 'teal', (x, 12, 3, 3))
        if kind == 'bookshop':
            for x in (8, 11, 14, 31, 34, 37):
                box(s, 'wood' if x % 2 else 'teal', (x, 24, 2, 5))
            box(s, 'wood', (7, 29, 11, 1))
            box(s, 'wood', (30, 29, 11, 1))
        else:
            for x in (9, 33):
                box(s, 'cream', (x, 25, 5, 3))
                box(s, 'rust', (x, 28, 5, 1))
    else:
        for x in (5, 28):
            box(s, 'wood', (x, 20, 15, 4))
            box(s, 'rust', (x, 28, 15, 3))
            box(s, 'light', (x + 2, 21, 1, 1))
            box(s, 'light', (x + 12, 29, 1, 1))
        box(s, 'rust', (37, 7, 5, 2))
        box(s, 'stone', (3, 33, 5, 2))
    box(s, 'light' if clean else 'stone', (0, 37, 48, 3))
    return s


def prop(name):
    s = canvas()
    if name.startswith('bench'):
        clean = name.endswith('clean')
        # Curved cast-metal arms and warm slats match Northgate's restored shops.
        box(s,'ink',(2,6,20,12));box(s,'shadow',(3,7,18,10))
        for y in (7,10,14):
            box(s,'rust' if clean else 'wood',(4,y,16,2))
            if clean:box(s,'cream',(5,y,13,1))
        box(s,'ink',(1,12,3,5));box(s,'ink',(20,12,3,5))
        box(s,'teal' if clean else 'stone',(2,12,2,3));box(s,'teal' if clean else 'stone',(20,12,2,3))
        for x in (4,18):
            box(s,'ink',(x,17,2,5));box(s,'stone',(x,17,1,4))
        if not clean:
            box(s,'shadow',(10,7,4,2));box(s,'ink',(14,10,3,2))
            box(s,'green',(4,15,3,1));box(s,'wood',(18,17,2,2))
    elif name.startswith('fountain'):
        clean = name.endswith('clean')
        box(s, 'ink', (3, 12, 18, 10))
        box(s, 'stone', (1, 13, 22, 6))
        box(s, 'water' if clean else 'shadow', (3, 14, 18, 3))
        box(s, 'light', (4, 20, 16, 2))
        box(s, 'stone', (10, 7, 4, 8))
        box(s, 'light', (7, 6, 10, 3))
        if clean:
            box(s, 'water', (11, 2, 2, 5))
            box(s, 'cream', (11, 2, 1, 2))
            box(s, 'cream', (5, 15, 3, 1))
        else:
            box(s, 'wood', (5, 15, 4, 1))
            box(s, 'rust', (15, 16, 3, 1))
    elif name.startswith('plant'):
        box(s, 'ink', (6, 14, 12, 8))
        box(s, 'rust', (7, 16, 10, 5))
        box(s, 'wood', (6, 14, 12, 2))
        box(s, 'wood', (11, 6, 2, 9))
        if name.endswith('clean'):
            for rect in ((5, 6, 7, 6), (10, 3, 7, 7), (13, 8, 7, 6)):
                box(s, 'green', rect)
            box(s, 'leaf', (10, 4, 4, 3))
            box(s, 'leaf', (6, 7, 3, 2))
        else:
            box(s, 'wood', (7, 7, 5, 2))
            box(s, 'rust', (13, 4, 3, 4))
    elif name in ('lamp','lamp_off'):
        box(s, 'ink', (9, 20, 7, 3))
        box(s, 'shadow', (11, 7, 3, 14))
        box(s, 'ink', (7, 2, 11, 6))
        box(s, 'gold' if name == 'lamp' else 'stone', (9, 3, 7, 4))
        box(s, 'cream' if name == 'lamp' else 'shadow', (10, 3, 2, 3))
        box(s, 'shadow', (9, 1, 7, 1))
    elif name == 'trash_bin':
        # Indoor stainless-steel recycling station with a warm teal inset.
        box(s,'ink',(5,4,14,19));box(s,'stone',(6,5,12,16))
        box(s,'light',(6,6,2,14));box(s,'shadow',(16,6,2,15))
        box(s,'cream',(6,4,12,2));box(s,'ink',(8,7,8,3))
        box(s,'shadow',(9,9,6,1));box(s,'teal',(8,12,8,8))
        box(s,'cream',(10,13,4,5));box(s,'green',(11,14,2,3))
        box(s,'ink',(6,21,12,2));box(s,'shadow',(7,21,10,1))
    elif name == 'request_parcel':
        box(s,'ink',(3,8,18,14))
        box(s,'teal',(4,9,16,12))
        box(s,'cream',(10,9,4,12))
        box(s,'cream',(6,12,3,3))
    elif name == 'request_display':
        box(s,'ink',(2,14,20,8))
        box(s,'wood',(3,15,18,6))
        for x,color in ((4,'teal'),(10,'gold'),(16,'rust')):
            box(s,color,(x,7,4,8))
            box(s,'cream',(x+1,9,2,2))
    elif name == 'request_sign':
        box(s,'wood',(4,6,2,16))
        box(s,'wood',(18,6,2,16))
        box(s,'ink',(2,4,20,13))
        box(s,'cream',(3,5,18,11))
        box(s,'teal',(5,8,14,2))
        box(s,'gold',(8,12,8,2))
    elif name in ('request_keepsake','request_plaque','request_notice','request_toolkit','request_lantern','request_chalk'):
        box(s,'ink',(3,5,18,16))
        color={'request_keepsake':'cream','request_plaque':'gold','request_notice':'cream',
               'request_toolkit':'wood','request_lantern':'shadow','request_chalk':'teal'}[name]
        box(s,color,(4,6,16,14))
        if name=='request_toolkit':
            box(s,'light',(8,11,9,3));box(s,'rust',(10,4,5,3))
        elif name=='request_lantern':
            box(s,'gold',(8,8,8,8));box(s,'cream',(10,9,3,5))
        elif name=='request_keepsake':
            box(s,'teal',(7,9,10,7));box(s,'gold',(10,10,3,3))
        else:
            box(s,'wood' if name=='request_plaque' else 'light',(7,10,10,2))
            box(s,'wood' if name=='request_plaque' else 'light',(7,14,7,2))
    elif name=='community_board':
        box(s,'ink',(3,2,18,16));box(s,'wood',(4,3,16,14))
        box(s,'cream',(6,5,5,5));box(s,'teal',(13,6,5,6))
        box(s,'gold',(8,13,10,2));box(s,'wood',(5,18,2,6));box(s,'wood',(17,18,2,6))
    elif name.startswith('festival_lantern_'):
        box(s,'wood',(11,0,2,5));box(s,'ink',(6,5,12,16))
        box(s,'gold',(7,6,10,14));box(s,'cream' if name.endswith('1') else 'rust',(10,7,4,12))
        box(s,'wood',(7,5,10,2));box(s,'wood',(7,19,10,2));box(s,'gold',(11,21,2,3))
    elif name in ('story_north','story_east','story_garden','story_commons'):
        box(s,'ink',(3,5,18,15));box(s,'cream',(4,6,16,13))
        if name=='story_north':
            box(s,'teal',(6,8,12,8));box(s,'gold',(10,10,4,5))
        elif name=='story_east':
            box(s,'ink',(6,9,12,7));box(s,'stone',(8,11,3,3));box(s,'stone',(13,11,3,3))
        elif name=='story_garden':
            box(s,'green',(11,8,2,9));box(s,'leaf',(7,10,5,3));box(s,'rust',(10,7,5,3))
        else:
            box(s,'teal',(6,9,12,2));box(s,'wood',(6,13,9,1));box(s,'wood',(6,16,11,1))
    elif name == 'trash_bags':
        for x,y in ((2,10),(11,6)):
            box(s,'ink',(x,y+4,10,9));box(s,'shadow',(x+1,y+3,8,8))
            box(s,'stone',(x+2,y+4,2,5));box(s,'teal',(x+5,y+7,2,3))
            box(s,'ink',(x+3,y,4,3));box(s,'light',(x+4,y+1,2,1))
        box(s,'cream',(5,19,5,2))
    elif name in ('litter','litter_paper'):
        box(s,'ink',(3,8,15,12));box(s,'cream',(4,9,13,10))
        box(s,'light',(4,15,5,4));box(s,'wood',(7,11,7,1))
        box(s,'wood',(7,14,5,1));box(s,'light',(13,9,4,4))
        box(s,'ink',(17,17,5,4));box(s,'teal',(18,18,3,2))
    elif name == 'litter_cup':
        box(s,'ink',(7,7,10,14));box(s,'cream',(8,9,8,10))
        box(s,'rust',(9,13,6,3));box(s,'light',(6,7,12,2))
        box(s,'wood',(9,5,5,2));box(s,'stone',(15,17,2,2))
        box(s,'cream',(3,19,3,2))
    elif name == 'litter_bottle':
        box(s,'ink',(9,3,6,4));box(s,'stone',(10,3,4,2))
        box(s,'ink',(6,8,12,13));box(s,'teal',(7,9,10,11))
        box(s,'water',(8,10,2,8));box(s,'cream',(7,13,10,4))
        box(s,'green',(10,14,4,2));box(s,'shadow',(14,18,2,2))
    elif name == 'dirt':
        for rect in ((2,13,8,3),(6,10,12,7),(16,14,6,3),(4,19,3,1)):
            box(s,'wood',rect)
        for rect in ((8,12,4,1),(15,15,3,1),(3,14,2,1)):box(s,'rust',rect)
        box(s,'shadow',(11,18,7,1));box(s,'stone',(18,11,2,2))
    elif name == 'mosaic':
        box(s, 'ink', (1, 1, 22, 22))
        box(s, 'cream', (2, 2, 20, 20))
        for y in range(4, 21, 4):
            for x in range(4, 21, 4):
                box(s, 'teal' if (x + y) % 8 else 'gold', (x, y, 2, 2))
        box(s, 'rust', (9, 9, 6, 6))
        box(s, 'gold', (11, 11, 2, 2))
    return s


def north_store(kind, clean, door_open=False):
    """A shallow roof seen from above, with its court-facing edge at the top."""
    s=canvas((48,24))
    box(s,'ink',(1,1,46,23))
    box(s,'teal' if clean else 'shadow',(3,8,42,13))
    box(s,'light' if clean else 'stone',(3,1,42,2))
    # Narrow glazing reads as an edge, rather than an upside-down tall facade.
    for x in (5,28):
        box(s,'ink',(x,3,15,5))
        box(s,'gold' if clean else 'stone',(x+1,4,13,3))
        if not clean:box(s,'wood',(x,5,15,2))
        elif kind=='cafe':
            for dx in range(0,13,4):box(s,'rust',(x+1+dx,4,2,2))
        else:
            for dx in (2,6,10):box(s,'wood',(x+dx,5,2,2))
    box(s,'ink',(21,0,6,8))
    box(s,'water' if clean else 'shadow',(22,1,4,6))
    if door_open:
        box(s,'ink',(22,1,4,6));box(s,'water',(24,1,2,6))
        box(s,'light',(26,0,1,8))
    else:box(s,'cream',(22,2,1,1))
    box(s,'stone',(4,9,40,1))
    box(s,'ink',(7,12,9,6));box(s,'stone',(8,13,7,4))
    for y in (13,15):box(s,'shadow',(9,y,5,1))
    box(s,'ink',(34,13,7,5));box(s,'light' if clean else 'stone',(35,14,5,3))
    box(s,'shadow',(4,21,40,2))
    if not clean:
        box(s,'rust',(24,13,4,2));box(s,'wood',(19,19,5,1))
    return s


def delivery_station():
    s=canvas((48,32))
    box(s,'ink',(4,22,40,9))
    box(s,'wood',(5,23,38,6))
    for x in (7,20,33):
        box(s,'rust',(x,24,8,2))
    for x,y in ((7,12),(23,10),(15,1)):
        box(s,'ink',(x,y,15,13))
        box(s,'teal' if x==23 else 'wood',(x+1,y+1,13,11))
        box(s,'cream',(x+6,y+1,3,11))
        box(s,'light',(x+2,y+4,3,3))
    return s


def worker(facing, frame):
    """16x24 worker: idle, left stride, passing pose, right stride."""
    s = canvas((16, 24))
    stride = (0, -1, 0, 1)[frame]
    bob = 1 if frame in (1, 3) else 0
    # Legs are separate so each stride visibly alternates boots.
    for x, offset in ((5, stride), (9, -stride)):
        box(s, 'blue', (x, 16 + bob, 3, 5 + offset))
        box(s, 'ink', (x - (1 if facing == 'left' else 0), 20 + bob + offset, 4, 2))
    box(s, 'ink', (4, 9 + bob, 8, 8))
    box(s, 'teal', (5, 10 + bob, 6, 6))
    box(s, 'gold', (5, 11 + bob, 1, 4))
    box(s, 'gold', (10, 11 + bob, 1, 4))
    for x, offset in ((2, -stride), (12, stride)):
        box(s, 'teal', (x, 10 + bob + offset, 2, 5))
        box(s, 'skin', (x, 14 + bob + offset, 2, 2))
    box(s, 'ink', (4, 2 + bob, 8, 8))
    box(s, 'skin' if facing != 'up' else 'wood', (5, 4 + bob, 6, 5))
    box(s, 'rust', (4, 2 + bob, 8, 3))
    box(s, 'gold', (5, 2 + bob, 5, 1))
    if facing == 'down':
        box(s, 'ink', (6, 6 + bob, 1, 1))
        box(s, 'ink', (9, 6 + bob, 1, 1))
    elif facing in ('left', 'right'):
        x = 4 if facing == 'left' else 11
        box(s, 'skin', (x, 5 + bob, 2, 3))
        box(s, 'ink', (x, 5 + bob, 1, 1))
        box(s, 'rust', (x, 3 + bob, 2, 1))
    return s


def shopper(variant, facing, frame):
    """Friendly 16x24 visitors, distinct clothing and hair, four directional strides."""
    s = canvas((16,24))
    stride = (0,-1,0,1)[frame]
    shirt = ('rust','green','blue','cream')[variant]
    hair = ('wood','ink','rust','stone')[variant]
    for x,offset in ((5,stride),(9,-stride)):
        box(s,'shadow',(x,16,3,5+offset))
        box(s,'ink',(x-1,20+offset,4,2))
    box(s,'ink',(4,9,8,8))
    box(s,shirt,(5,10,6,7))
    for x,offset in ((2,-stride),(12,stride)):
        box(s,shirt,(x,10+offset,2,4))
        box(s,'skin',(x,14+offset,2,2))
    box(s,'ink',(4,2,8,8))
    box(s,'skin' if facing != 'up' else hair,(5,4,6,5))
    box(s,hair,(4,2,8,3))
    if facing == 'down':
        box(s,'ink',(6,6,1,1));box(s,'ink',(9,6,1,1))
    elif facing in ('left','right'):
        x = 4 if facing == 'left' else 11
        box(s,'skin',(x,5,2,3));box(s,'ink',(x,5,1,1))
    # A shopping bag replaces the worker's reflective vest and hat.
    box(s,'wood',(12,16,3,5));box(s,'gold',(12,15,2,1))
    return s


def north_lantern(frame):
    """Round paper lantern viewed downwards at an angle, with a broad top plane."""
    s=canvas((24,24))
    # Rear bracket recedes diagonally to the coping; it sits behind the globe.
    pygame.draw.lines(s,PALETTE['ink'],False,[(13,12),(17,19),(17,23)],3)
    pygame.draw.lines(s,PALETTE['stone'],False,[(13,12),(17,19),(17,23)],1)
    box(s,'wood',(14,22,7,2));box(s,'light',(15,22,5,1))
    # Stepped ellipses provide a visible top and a curved, shaded near side.
    pygame.draw.ellipse(s,PALETTE['ink'],(3,4,18,14))
    pygame.draw.ellipse(s,PALETTE['gold'],(4,5,16,12))
    pygame.draw.polygon(s,PALETTE['rust'],[(16,6),(19,9),(17,14),(13,16),(8,15),(14,13)])
    pygame.draw.ellipse(s,PALETTE['cream'],(5,5,14,7))
    pygame.draw.ellipse(s,PALETTE['gold'],(6,6,12,5))
    box(s,'cream',(6,9,2,3))
    # Curved bamboo ribs follow the round surface, rather than a flat rectangle.
    for rib in (((8,6),(7,9),(8,13),(10,16)),((12,5),(11,9),(12,14),(13,16)),
                ((16,6),(17,9),(16,13),(15,15))):
        pygame.draw.lines(s,PALETTE['wood'],False,rib,1)
    pygame.draw.ellipse(s,PALETTE['wood'],(9,4,7,4))
    pygame.draw.ellipse(s,PALETTE['light'],(10,4,5,2))
    box(s,'ink',(12,1,2,3));box(s,'stone',(12,1,1,2))
    box(s,'cream' if frame else 'gold',(9,10,2,3))
    box(s,'wood',(11,17,3,1));box(s,'gold',(12,18,1,3))
    return s


def entrance():
    """West-wall glass doors and a welcome mat; the shared visitor portal."""
    s=canvas((16,32))
    box(s,'ink',(0,1,12,30));box(s,'stone',(1,2,10,28))
    for y in (4,17):
        box(s,'ink',(2,y,8,11));box(s,'teal',(3,y+1,6,9))
        box(s,'water',(4,y+2,2,5));box(s,'cream',(9,y+5,1,3))
    box(s,'gold',(1,2,1,27));box(s,'wood',(12,9,4,16))
    box(s,'light',(13,11,1,12));box(s,'rust',(15,11,1,12))
    return s


def cleaning_tool(kind, facing, frame):
    s=canvas();swing=(0,2,3,1)[frame]
    box(s,'wood',(11,5,2,14));box(s,'light',(11,5,1,11))
    if kind=='broom':
        box(s,'teal',(7+swing,17,9,2));box(s,'cream',(6+swing,19,11,3))
        for x in range(7+swing,17+swing,3):box(s,'rust',(x,20,1,3))
    elif kind=='grabber':
        box(s,'stone',(10,6,3,13));box(s,'teal',(9,5,5,3))
        box(s,'ink',(7+swing,18,3,3));box(s,'ink',(14-swing,18,3,3))
        box(s,'light',(8+swing,19,2,3));box(s,'light',(14-swing,19,2,3))
    elif kind=='water':
        box(s,'teal',(7,12,11,8));box(s,'water',(8,13,3,5))
        box(s,'stone',(15,11,5,3));box(s,'water',(20,15+frame,2,2))
    else:
        box(s,'wood',(6,14,12,7));box(s,'gold',(10,12,4,3));box(s,'light',(8,16,8,2))
    return pygame.transform.rotate(s,{'down':0,'up':180,'left':-90,'right':90}[facing])


def cleaning_worker(facing, frame):
    s=worker(facing,0)
    # The reaching arm changes with the tool stroke, without changing body scale.
    x=2 if facing=='left' else 12
    s.fill((0,0,0,0),(x,10,2,7))
    y=(10,12,13,11)[frame]
    box(s,'teal',(x,y,2,4));box(s,'skin',(x,y+4,2,2))
    return s


class Art:
    def __init__(self):
        self.sprites = {}
        self.cache = {}
        for kind in ('bookshop', 'cafe'):
            for state in ('dirty', 'clean'):
                self.sprites[f'{kind}_{state}'] = store(kind, state == 'clean')
            self.sprites[f'{kind}_clean_open'] = store(kind,True,True)
        for name in ('trash_bags', 'litter', 'litter_paper', 'litter_cup', 'litter_bottle', 'dirt', 'bench_dirty', 'bench_clean',
                     'fountain_dirty', 'fountain_clean', 'plant_dirty', 'plant_clean', 'lamp', 'lamp_off', 'trash_bin', 'mosaic', 'request_parcel', 'request_display', 'request_sign', 'request_keepsake', 'request_plaque', 'request_notice', 'request_toolkit', 'request_lantern', 'request_chalk'):
            self.sprites[name] = prop(name)
        for kind in ('bookshop','cafe'):
            for state in ('dirty','clean','clean_open'):
                self.sprites[f'{kind}_{state}_up']=north_store(kind,state!='dirty',state=='clean_open')
        self.sprites['delivery_station'] = delivery_station()
        self.sprites['main_entrance']=entrance()
        for frame in range(2):self.sprites[f'festival_lantern_north_{frame}']=north_lantern(frame)
        for name in ('community_board','festival_lantern_0','festival_lantern_1','story_north','story_east','story_garden','story_commons'):
            self.sprites[name]=prop(name)
        for facing in ('down', 'up', 'left', 'right'):
            for frame in range(4):
                self.sprites[f'player_{facing}_{frame}'] = worker(facing, frame)
                self.sprites[f'player_{facing}_clean_{frame}']=cleaning_worker(facing,frame)
                for tool in ('broom','grabber','water','setup'):
                    self.sprites[f'{tool}_{facing}_{frame}']=cleaning_tool(tool,facing,frame)
                uniform=worker(facing,frame)
                for x in range(16):
                    for y in range(24):
                        if uniform.get_at((x,y))==pygame.Color(PALETTE['gold']):uniform.set_at((x,y),PALETTE['blue'])
                self.sprites[f'janitor_{facing}_{frame}']=uniform

        for variant in range(4):
            for facing in ('down','up','left','right'):
                for frame in range(4):
                    self.sprites[f'shopper_{variant}_{facing}_{frame}'] = shopper(variant,facing,frame)

    def draw(self, surface, name, center, size):
        key = name, tuple(size)
        if key not in self.cache:
            sprite = self.sprites[name]
            # Integer nearest-neighbor scaling keeps every source pixel square.
            scale = max(1, int(min(size[0] / sprite.get_width(), size[1] / sprite.get_height())))
            dimensions = sprite.get_width() * scale, sprite.get_height() * scale
            self.cache[key] = pygame.transform.scale(sprite, dimensions)
        image = self.cache[key]
        surface.blit(image, image.get_rect(center=(round(center[0]), round(center[1]))))
