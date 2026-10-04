"""Native pixel art for patio kitchens, dining and planting."""
import pygame
from game.art import canvas,box


def food_stall(variant,opened,north=False):
    s=canvas((60,40));accent=('teal','rust','green','gold','wood','rust','green','teal')[variant]
    box(s,'ink',(1,3,58,35));box(s,'wood' if opened else 'shadow',(3,6,54,29))
    box(s,'cream' if opened else 'stone',(4,7,52,7))
    for x in range(3,57,6):box(s,accent if opened else 'shadow',(x,14,5,6))
    box(s,'ink',(8,21,43,12));box(s,'gold' if opened else 'shadow',(10,23,39,9))
    box(s,'wood',(7,31,46,3));box(s,'cream',(8,31,43,1))
    if opened:
        # Each kitchen has a distinct counter display: oven, noodles, fruit or pastries.
        for x in (13,25,37):
            if variant==0:
                box(s,'wood',(x,25,7,6));box(s,'cream',(x+1,27,5,1));box(s,'leaf',(x+2,24,3,2))
            elif variant==1:
                box(s,'rust',(x,25,7,5));box(s,'ink',(x+2,26,3,3));box(s,'gold',(x+3,28,1,1))
            elif variant==2:
                box(s,'cream',(x,28,7,2));box(s,'leaf',(x+1,26,5,2));box(s,'wood',(x+2,23,1,5))
            elif variant==3:
                box(s,'cream',(x+1,25,5,6));box(s,'rust',(x+2,27,3,3));box(s,'leaf',(x+3,22,1,4))
            elif variant==4:
                box(s,'cream',(x,29,7,1));box(s,'wood',(x+1,26,5,3));box(s,'gold',(x+2,26,1,2))
            elif variant==5:
                box(s,'ink',(x,26,7,4));box(s,'stone',(x+1,27,5,1));box(s,'rust',(x+2,24,4,2))
            elif variant==6:
                box(s,'cream',(x,27,7,3));box(s,'green',(x+1,25,5,3));box(s,'leaf',(x+2,24,2,2))
            else:
                box(s,'cream',(x,27,7,3));box(s,'rust',(x+1,25,5,3));box(s,'gold',(x+3,24,1,1))
    else:
        for y in range(22,32,3):box(s,'stone',(9,y,41,1))
    for x in (4,54):box(s,'green',(x,30,3,6))
    if north:
        # Draw a north-facing counter, keeping signage, food and plants upright.
        counter=s.subsurface((7,21,46,13)).copy()
        roof=s.subsurface((3,7,54,13)).copy()
        box(s,'wood' if opened else 'shadow',(3,6,54,29))
        s.blit(counter,(7,6));s.blit(roof,(3,23))
        box(s,'ink',(3,35,54,2));box(s,'cream' if opened else 'stone',(4,34,52,1))
        for x in (4,54):box(s,'green',(x,17,3,6))
    return s


def doors():
    s=canvas((32,44))
    # Broad stone piers, a shared lintel and two full-height glazed leaves.
    box(s,'ink',(0,1,32,42));box(s,'stone',(1,2,30,40))
    box(s,'cream',(2,3,28,3));box(s,'wood',(4,8,24,31))
    box(s,'ink',(6,10,20,27))
    for x in (7,17):
        box(s,'teal',(x,11,8,25));box(s,'water',(x+1,12,6,15))
        box(s,'light',(x+2,13,1,12));box(s,'wood',(x,28,8,1))
        box(s,'gold',(x+5 if x==7 else x+1,30,1,3))
    box(s,'wood',(15,10,2,27));box(s,'gold',(5,7,22,2))
    for x in (1,28):
        box(s,'light',(x,9,3,29))
        for y in (15,23,31):box(s,'stone',(x,y,3,1))
    box(s,'cream',(2,39,28,2));box(s,'shadow',(1,42,30,1))
    return s


def picnic(broken=False):
    s=canvas((40,36));wood='stone' if broken else 'wood'
    box(s,'ink',(9,9,22,17));box(s,'shadow',(10,10,20,15))
    for y in (9,13,17,21):
        box(s,wood,(10,y,20,3));box(s,'cream' if not broken else 'shadow',(11,y,18,1))
    for x in (11,27):box(s,'ink',(x,25,2,7))
    for x in (1,33):
        box(s,'ink',(x,19,6,16));box(s,wood,(x+1,20,4,14))
        box(s,'gold' if not broken else 'shadow',(x+1,20,1,13))
    if broken:
        box(s,'shadow',(16,9,8,3));box(s,'shadow',(11,17,7,3))
        box(s,'green',(25,22,4,2));box(s,'ink',(2,26,4,4))
        pygame.draw.line(s,'#856448',(16,26),(25,30),2)
    else:
        box(s,'cream',(16,14,8,6));box(s,'rust',(18,15,4,4))
        box(s,'leaf',(21,14,2,2))
    return s


def food(kind):
    s=canvas((24,24))
    if kind=='pizza':
        pygame.draw.polygon(s,'#dfb45e',[(4,5),(21,5),(12,21)])
        box(s,'wood',(4,4,17,3))
        for x,y in ((8,9),(15,9),(11,14)):box(s,'rust',(x,y,3,3))
    elif kind in ('noodles','salad'):
        box(s,'ink',(3,12,18,7));box(s,'cream',(4,13,16,5));box(s,'stone',(6,18,12,2))
        for x in (5,9,13,17):
            box(s,'gold' if kind=='noodles' else 'leaf',(x,9,3,4))
            box(s,'cream' if kind=='noodles' else 'green',(x,8,2,2))
        if kind=='noodles':pygame.draw.line(s,'#856448',(15,3),(12,14),1)
    elif kind=='juice':
        box(s,'ink',(7,7,11,15));box(s,'cream',(8,8,9,13));box(s,'gold',(9,11,7,9))
        box(s,'leaf',(16,2,2,9));box(s,'cream',(9,10,2,7));box(s,'rust',(5,8,5,5))
    elif kind=='pastry':
        for x,y,w,h in ((3,12,5,5),(6,9,6,8),(11,8,6,9),(16,12,5,5)):
            box(s,'wood',(x,y,w,h));box(s,'gold',(x+1,y,w-2,h-2))
        box(s,'cream',(9,10,1,5));box(s,'cream',(14,10,1,5))
    elif kind=='grill':
        pygame.draw.line(s,'#856448',(4,21),(20,3),2)
        for x,y,c in ((5,15,'rust'),(9,11,'leaf'),(13,7,'rust')):
            box(s,c,(x,y,6,5));box(s,'gold',(x+1,y+1,3,1))
    else:
        box(s,'ink',(6,13,12,9));box(s,'cream',(7,14,10,6))
        box(s,'gold',(8,19,8,1));box(s,'rust',(6,10,12,4));box(s,'cream',(8,7,8,4))
        box(s,'rust',(11,5,3,3));box(s,'leaf',(14,5,2,1))
    return s


def herbs():
    s=canvas((24,32));box(s,'ink',(3,19,18,10));box(s,'rust',(4,20,16,8));box(s,'wood',(2,18,20,3))
    for x in (7,12,17):
        box(s,'green',(x,7,2,13));box(s,'leaf',(x-3,9,3,3));box(s,'leaf',(x+2,5,3,4));box(s,'green',(x-2,14,3,3))
    box(s,'cream',(6,24,12,1));return s


def lights():
    s=canvas((48,24));box(s,'wood',(2,2,2,21));box(s,'wood',(44,2,2,21))
    pygame.draw.lines(s,'#856448',False,[(3,3),(24,8),(45,3)],1)
    for x,y in ((9,5),(18,7),(28,7),(37,5)):
        box(s,'cream',(x,y,3,4));box(s,'gold',(x+1,y+1,1,3))
    return s


def patio_tree():
    s=canvas((24,36));box(s,'ink',(10,22,5,12));box(s,'wood',(11,20,3,12))
    for rect,color in (((4,5,15,19),'green'),((1,10,21,10),'green'),((7,2,10,9),'leaf'),((3,9,10,7),'leaf'),((13,15,7,6),'teal')):box(s,color,rect)
    box(s,'rust',(6,31,13,4));box(s,'cream',(7,31,11,1));return s


def install(art):
    for v in range(8):
        for opened in (True,False):art.sprites[f'food_stall_{v}_'+('open' if opened else 'closed')]=food_stall(v,opened)
    for v in range(8):
        for state in ('open','closed'):
            art.sprites[f'food_stall_{v}_{state}_up']=food_stall(v,state=='open',north=True)
    art.sprites.update(courtyard_doors=doors(),courtyard_table=picnic(),courtyard_table_broken=picnic(True),herb_planter=herbs(),patio_lights=lights(),patio_tree=patio_tree())

    for kind in ('pizza','noodles','juice','pastry','grill','salad','dessert'):
        art.sprites['food_'+kind]=food(kind)
