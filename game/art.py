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
                box(s, 'wood', (x-2, 30, 9, 1))
                box(s, 'cream', (x+5, 26, 3, 3))
                box(s, 'rust', (x+6, 27, 1, 1))
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


def person(facing, frame, shirt, hair, work=False):
    """Soft silhouettes and shaded clothes on the established 16x24 pixel grid."""
    s=canvas((16,24));stride=(0,-1,0,1)[frame];bob=frame%2
    for x,step in ((5,stride),(9,-stride)):
        box(s,'ink',(x,16+bob,3,6+step));box(s,'blue' if work else 'shadow',(x,17+bob,2,3+step))
        box(s,'ink',(x-1,21+bob+step,4,1));box(s,'stone',(x,20+bob+step,2,1))
    # Rounded shoulders, a collar, pockets, and a warm seam highlight.
    box(s,'ink',(4,10+bob,8,7));box(s,'ink',(5,9+bob,6,9))
    box(s,shirt,(5,10+bob,6,6));box(s,'shadow',(10,11+bob,1,5))
    box(s,'cream',(6,10+bob,4,1));box(s,'wood',(5,16+bob,6,1))
    for x,step in ((2,-stride),(12,stride)):
        box(s,'ink',(x,11+bob+step,2,5));box(s,shirt,(x,11+bob+step,2,3))
        box(s,'skin',(x,14+bob+step,2,2))
    if work:
        for x in (5,10):box(s,'gold',(x,11+bob,1,4))
        box(s,'blue',(7,13+bob,2,2));box(s,'light',(7,13+bob,2,1))
    elif facing=='down':box(s,'light',(6,12+bob,1,3))
    # Cut corners and a visible neck replace the old square head block.
    box(s,'ink',(5,2+bob,6,8));box(s,'ink',(4,3+bob,8,6))
    box(s,hair,(5,2+bob,6,3));box(s,'skin' if facing!='up' else hair,(5,5+bob,6,4))
    if facing=='up':
        box(s,hair,(4,3+bob,8,5));box(s,'shadow',(5,7+bob,6,1))
    elif facing=='down':
        box(s,hair,(4,3+bob,8,2));box(s,hair,(5,5+bob,1,1))
        box(s,'ink',(6,6+bob,1,1));box(s,'ink',(9,6+bob,1,1));box(s,'rust',(8,8+bob,2,1))
    else:
        x=3 if facing=='left' else 11
        box(s,'skin',(x,5+bob,2,3));box(s,'ink',(x,5+bob,1,1))
        box(s,hair,(9 if facing=='left' else 4,4+bob,3,4))
    if work:
        box(s,'rust',(5,2+bob,6,2));box(s,'gold',(5,2+bob,5,1))
        box(s,'wood',(3 if facing=='left' else 9,4+bob,4,1))
    return s


def worker(facing, frame):return person(facing,frame,'teal','wood',True)


def shopper(variant, facing, frame):
    s=person(facing,frame,('rust','green','blue','cream')[variant],('wood','ink','rust','stone')[variant])
    if variant==0:box(s,'gold',(6,10+frame%2,2,3))  # knitted scarf
    if variant==1:box(s,'ink',(11,3+frame%2,2,5))   # tied hair
    if variant==2:box(s,'teal',(5,11+frame%2,2,4))  # jacket panels
    if variant==3:box(s,'wood',(9,11+frame%2,1,5))  # long coat seam
    return s


def seated_shopper(variant, facing):
    s=shopper(variant,'down',0);s.fill((0,0,0,0),(0,17,16,7))
    for x in (4,9):
        box(s,'ink',(x,17,4,3));box(s,'shadow',(x+1,17,2,2))
        box(s,'ink',(x+1,20,3,2));box(s,'stone',(x+1,20,2,1))
    return s


def north_lantern(frame):
    """Foreshortened facade lamp on the north storefront's six-pixel grid."""
    s=canvas((8,8))
    # A short hanging loop meets the building's front coping, not the court.
    box(s,'wood',(3,0,1,2))
    box(s,'ink',(1,2,6,5))
    # Broad top cap and shaded right edge match the shallow roof perspective.
    box(s,'wood',(2,2,4,1));box(s,'light',(2,2,3,1))
    box(s,'gold',(2,3,3,3));box(s,'cream',(2,3,3,1))
    box(s,'cream' if frame else 'rust',(3,4,1,2))
    box(s,'rust',(5,3,1,3))
    box(s,'wood',(2,6,4,1));box(s,'gold',(3,7,1,1))
    return pygame.transform.flip(s,False,True)


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
    # Reach and retract the tool-side hand in time with the four tool strokes.
    x=2 if facing in ('left','up') else 12
    s.fill((0,0,0,0),(x,10,2,8))
    y=(10,11,13,11)[frame]
    box(s,'ink',(x,y,2,6));box(s,'teal',(x,y,2,3));box(s,'cream',(x,y+3,2,1))
    box(s,'skin',(x,y+4,2,2))
    return s


def janitor_uniform(s):
    s=s.copy()
    for x in range(16):
        for y in range(24):
            if s.get_at((x,y))==pygame.Color(PALETTE['gold']):s.set_at((x,y),PALETTE['light'])
    return s


def community_table(variant):
    s=canvas((32,24))
    box(s,'ink',(3,9,26,10));box(s,'wood',(4,10,24,8));box(s,'cream',(4,10,24,2))
    box(s,('teal','rust','green','blue')[variant],(4,12,24,6))
    for x in (5,25):box(s,'ink',(x,18,2,5));box(s,'wood',(x,18,1,4))
    for x in (7,14,21):
        if variant==0:
            box(s,'gold',(x,6,5,4));box(s,'cream',(x+1,7,3,1))
        elif variant==1:
            box(s,'ink',(x,7,4,3));box(s,'cream',(x+1,6,3,3));box(s,'rust',(x+1,8,2,1))
        elif variant==2:
            box(s,'rust',(x,7,4,3));box(s,'green',(x+1,3,2,4));box(s,'leaf',(x-1,4,3,2))
        else:
            box(s,'wood',(x,5,4,5));box(s,'gold',(x+1,6,2,3))
    return s



def chapter_board(variant):
    s=prop('community_board')
    # Completed chapters remember what each court contributes.
    box(s,('teal','blue','green','rust')[variant],(5,6,14,9))
    if variant==0:
        box(s,'cream',(7,8,4,5));box(s,'gold',(12,8,4,5));box(s,'wood',(11,8,1,5))
    elif variant==1:
        pygame.draw.circle(s,PALETTE['ink'],(12,10),4);pygame.draw.circle(s,PALETTE['gold'],(12,10),1)
        box(s,'cream',(17,7,1,5));box(s,'cream',(18,7,2,1))
    elif variant==2:
        box(s,'wood',(8,7,8,1));box(s,'gold',(9,8,6,5));box(s,'cream',(11,9,2,3))
    else:
        box(s,'wood',(7,10,10,3));box(s,'cream',(8,8,3,2));box(s,'gold',(13,8,3,2))
    return s


def event_item(index):
    if index<3:
        s=prop('plant_clean')
        if index==0:
            box(s,'green',(8,6,8,5));box(s,'leaf',(10,4,4,3))
        elif index==1:
            for x,y in ((7,6),(13,4),(16,8)):
                box(s,'gold',(x-1,y-1,3,3));box(s,'cream',(x,y,1,1))
        else:
            for y in (4,7,10):box(s,'leaf',(6,y,12,2))
    else:
        s=canvas()
        if index==3:
            box(s,'wood',(4,7,16,12));box(s,'cream',(5,5,13,10));box(s,'gold',(7,8,9,2))
        elif index==4:
            box(s,'ink',(5,6,14,12));box(s,'rust',(6,7,12,10));box(s,'gold',(11,7,2,10));box(s,'cream',(6,11,12,2))
        else:
            box(s,'wood',(5,5,14,14));box(s,'ink',(8,8,8,8));box(s,'gold',(5,5,14,2))
    return s


def young_shopper(age,variant,facing,frame):
    s=shopper(variant,facing,frame)
    bob=frame%2
    if age=='teen':
        box(s,'teal' if variant%2 else 'rust',(5,10+bob,6,5))
        box(s,'cream',(7,11+bob,2,1));box(s,'blue',(6,16+bob,4,4))
        if facing=='up':box(s,'wood',(5,10+bob,6,6));box(s,'gold',(6,11+bob,4,1))
        else:box(s,'ink',(4,6+bob,1,3));box(s,'ink',(11,6+bob,1,3))
    else:
        box(s,'teal' if variant%2 else 'gold',(4,2+bob,8,2));box(s,'cream',(4,4+bob,7,1))
        box(s,'leaf' if variant%2 else 'rust',(5,11+bob,6,4));box(s,'cream',(7,12+bob,2,2))
    return s


def social_table():
    s=canvas((32,24))
    box(s,'ink',(6,10,20,4));box(s,'wood',(7,8,18,5));box(s,'cream',(9,9,14,1))
    box(s,'shadow',(9,14,3,7));box(s,'shadow',(21,14,3,7))
    for x in (0,27):
        box(s,'teal',(x,9,5,8));box(s,'wood',(x,16,5,4));box(s,'ink',(x+1,20,2,3))
    box(s,'cream',(12,6,3,3));box(s,'rust',(19,6,3,3));box(s,'leaf',(16,4,2,5))
    return s


class Art:
    def __init__(self):
        self.sprites = {}
        self.cache = {}
        for i in range(4):self.sprites[f'chapter_board_{i}']=chapter_board(i)
        for i in range(6):self.sprites[f'event_item_{i}']=event_item(i)
        for kind in ('bookshop', 'cafe'):
            for state in ('dirty', 'clean'):
                self.sprites[f'{kind}_{state}'] = store(kind, state == 'clean')
            self.sprites[f'{kind}_clean_open'] = store(kind,True,True)
        for name in ('trash_bags', 'litter', 'litter_paper', 'litter_cup', 'litter_bottle', 'dirt', 'bench_dirty', 'bench_clean',
                     'fountain_dirty', 'fountain_clean', 'plant_dirty', 'plant_clean', 'lamp', 'lamp_off', 'trash_bin', 'mosaic', 'request_plant', 'request_parcel', 'request_display', 'request_sign', 'request_keepsake', 'request_plaque', 'request_notice', 'request_toolkit', 'request_lantern', 'request_chalk'):
            self.sprites[name] = prop(name)
        for kind in ('bookshop','cafe'):
            for state in ('dirty','clean','clean_open'):
                self.sprites[f'{kind}_{state}_up']=north_store(kind,state!='dirty',state=='clean_open')
        self.sprites['delivery_station'] = delivery_station()
        self.sprites['main_entrance']=entrance()
        self.sprites['request_plant']=prop('plant_clean')
        for frame in range(2):self.sprites[f'festival_lantern_north_{frame}']=north_lantern(frame)
        for name in ('community_board','festival_lantern_0','festival_lantern_1','story_north','story_east','story_garden','story_commons'):
            self.sprites[name]=prop(name)
        for facing in ('down', 'up', 'left', 'right'):
            for frame in range(4):
                self.sprites[f'player_{facing}_{frame}'] = worker(facing, frame)
                self.sprites[f'player_{facing}_clean_{frame}']=cleaning_worker(facing,frame)
                for tool in ('broom','grabber','water','setup'):
                    self.sprites[f'{tool}_{facing}_{frame}']=cleaning_tool(tool,facing,frame)
                self.sprites[f'janitor_{facing}_{frame}']=janitor_uniform(worker(facing,frame))
                self.sprites[f'janitor_{facing}_clean_{frame}']=janitor_uniform(cleaning_worker(facing,frame))

        self.sprites['social_table']=social_table()
        for variant in range(4):
            self.sprites[f'community_table_{variant}']=community_table(variant)
            for facing in ('down','up','left','right'):
                for frame in range(4):
                    self.sprites[f'shopper_{variant}_{facing}_{frame}'] = shopper(variant,facing,frame)
                    owner=shopper(variant,facing,frame);box(owner,'teal',(5,13,6,4));box(owner,'cream',(5,13,6,1))
                    self.sprites[f'owner_{variant}_{facing}_{frame}']=owner
                self.sprites[f'shopper_{variant}_{facing}_sit']=seated_shopper(variant,facing)

        for age in ('child','teen'):
            for variant in range(4):
                for facing in ('up','down','left','right'):
                    for frame in range(4):self.sprites[f'{age}_{variant}_{facing}_{frame}']=young_shopper(age,variant,facing,frame)
                    seated=young_shopper(age,variant,'down',0);seated.fill((0,0,0,0),(0,17,16,7))
                    for x in (4,9):box(seated,'blue',(x,17,4,3));box(seated,'ink',(x+1,20,3,2))
                    self.sprites[f'{age}_{variant}_{facing}_sit']=seated

        bag=canvas((8,8));box(bag,'ink',(1,2,6,6));box(bag,'wood',(2,3,4,4));box(bag,'cream',(3,4,2,2));box(bag,'gold',(3,1,2,2))
        self.sprites['purchase_bag']=bag
        cup=canvas((6,6));box(cup,'cream',(1,1,4,4));box(cup,'rust',(2,2,2,2));self.sprites['visitor_cup']=cup
        book=canvas((6,6));box(book,'ink',(0,1,6,4));box(book,'gold',(1,1,4,4));box(book,'cream',(3,1,1,4));self.sprites['visitor_book']=book

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
