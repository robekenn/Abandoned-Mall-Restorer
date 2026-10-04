"""Inventory and priced, one-time upgrades; transactions are handled by Game."""
from dataclasses import dataclass
from systems.economy import money


@dataclass(frozen=True)
class Offer:
    key: str
    title: str
    detail: str
    price: int
    owned: bool = False


class Upgrades:
    REGIONAL_TRACKS = {
        'garden': (
            ('garden_capacity',(40,45,50,55,60),(2000,3500,5000,7000),'advanced_capacity_level',4,'Carry capacity','slots'),
            ('garden_value',(80,100,140,180),(5000,9000,14000),'advanced_value_level',3,'Recycling value','per item'),
            ('garden_tool',(('Pro cleanup kit',155,5),('Wide rake',180,6),('Sorting kit',200,8),('Community kit',220,10)),
             (4000,7000,11000),'tool_level',3,'Pickup tools',''),
            ('garden_speed',(1.5,2),(9000,),'speed_level',3,'Walking speed','×'),
        ),
        'commons': (
            ('commons_capacity',(60,65,70,75,80),(10000,14000,20000,28000),'garden_capacity_level',4,'Carry capacity','slots'),
            ('commons_value',(180,220,280,360),(20000,30000,45000),'garden_value_level',3,'Recycling value','per item'),
            ('commons_tool',(('Community kit',220,10),('Mall keeper kit',260,12)),(20000,),'garden_tool_level',3,'Pickup tools',''),
            ('commons_speed',(2,2.3,2.6),(20000,35000),'garden_speed_level',1,'Walking speed','×'),
        ),
    }
    CAPACITIES = (1, 2, 4, 8, 16, 20)
    CAPACITY_PRICES = (5, 15, 40, 90, 180)
    ADVANCED_CAPACITIES = (20, 25, 30, 35, 40)
    ADVANCED_CAPACITY_PRICES = (500, 750, 1000, 1250)
    ADVANCED_VALUES = (30, 45, 60, 80)
    ADVANCED_VALUE_PRICES = (900, 1800, 3200)
    SPEEDS = (1, 1.15, 1.3, 1.5)
    SPEED_PRICES = (300, 600, 1000)
    VALUES = (1, 2, 4, 8, 15, 30)
    VALUE_PRICES = (8, 30, 90, 220, 500)
    TOOLS = (('Hand grabber', 72, 1), ('Long grabber', 110, 1),
             ('Cleanup kit', 135, 3), ('Pro cleanup kit', 155, 5))
    TOOL_PRICES = (100, 250, 550)

    def __init__(self):
        self.held = 0
        self.capacity_level = 0
        self.advanced_capacity_level = 0
        self.speed_level = 0
        self.advanced_value_level = 0
        self.value_level = 0
        self.tool_level = 0
        self.decor = set()
        for tracks in self.REGIONAL_TRACKS.values():
            for key,*_ in tracks:setattr(self,key+'_level',0)

    @property
    def capacity(self):
        for shop in ('commons','garden'):
            level=getattr(self,shop+'_capacity_level')
            if level:return self.REGIONAL_TRACKS[shop][0][1][level]
        if self.advanced_capacity_level:
            return self.ADVANCED_CAPACITIES[self.advanced_capacity_level]
        return self.CAPACITIES[self.capacity_level]

    @property
    def unit_value(self):
        for shop in ('commons','garden'):
            level=getattr(self,shop+'_value_level')
            if level:return self.REGIONAL_TRACKS[shop][1][1][level]
        return (self.ADVANCED_VALUES[self.advanced_value_level] if self.advanced_value_level
                else self.VALUES[self.value_level])

    @property
    def tool(self):
        for shop in ('commons','garden'):
            level=getattr(self,shop+'_tool_level')
            if level:return self.REGIONAL_TRACKS[shop][2][1][level]
        return self.TOOLS[self.tool_level]

    @property
    def speed_multiplier(self):
        for shop in ('commons','garden'):
            level=getattr(self,shop+'_speed_level')
            if level:return self.REGIONAL_TRACKS[shop][3][1][level]
        return self.SPEEDS[self.speed_level]

    @property
    def fixture_rent(self):
        return len(self.decor)

    def offers(self, category, shop='north'):
        if shop in self.REGIONAL_TRACKS:
            if category=='Gear':
                result=[]
                for key,levels,prices,prerequisite,required,title,unit in self.REGIONAL_TRACKS[shop]:
                    level=getattr(self,key+'_level');maxed=level==len(prices)
                    if maxed:detail='Fully upgraded'
                    elif getattr(self,prerequisite)<required:detail='Finish the previous section’s '+title.lower()+' upgrades first'
                    elif 'tool' in key:
                        name,reach,batch=levels[level+1];detail=f'{name}: {reach/64:.2g} tiles reach, up to {batch} items'
                    else:detail=f'{levels[level]} to {levels[level+1]} {unit}'
                    result.append(Offer(key,title,detail,0 if maxed else prices[level],maxed))
                return result
            ordinal=('north','east','garden','commons').index(shop)
            if category=='Furniture':
                specs=[(f'bench_{2*ordinal+i}',f'{shop.title()} bench {i+1}',300*ordinal) for i in range(2)]
                specs += [(f'fountain_{shop}',f'{shop.title()} fountain',900*ordinal),(f'mosaic_{shop}',f'{shop.title()} mosaic',750*ordinal)]
            else:
                specs=[(f'lamp_{4*ordinal+i}',f'{shop.title()} lamp {i+1}',180*ordinal) for i in range(4)]
                specs += [(f'plant_{4*ordinal+i}',f'{shop.title()} planter {i+1}',150*ordinal) for i in range(4)]
            return [Offer(key,title,'Install fixture / +$1 base rent per 5s',price,key in self.decor) for key,title,price in specs]
        if shop == 'east':
            if category == 'Gear':
                level = self.advanced_capacity_level
                maxed = level == len(self.ADVANCED_CAPACITY_PRICES)
                ready = self.capacity_level == len(self.CAPACITY_PRICES)
                detail = 'Fully upgraded' if maxed else (
                    f'{self.capacity} to {self.ADVANCED_CAPACITIES[level+1]} slots' if ready
                    else 'Requires the 20-slot bag from Supplies')
                speed_maxed = self.speed_level == len(self.SPEED_PRICES)
                speed_detail = 'Fully upgraded' if speed_maxed else (
                    f'{self.speed_multiplier:g}x to {self.SPEEDS[self.speed_level+1]:g}x walking speed')
                value_maxed = self.advanced_value_level == len(self.ADVANCED_VALUE_PRICES)
                value_ready = self.value_level == len(self.VALUE_PRICES)
                value_detail = 'Fully upgraded' if value_maxed else (
                    f'${self.unit_value} to ${self.ADVANCED_VALUES[self.advanced_value_level+1]} per item' if value_ready
                    else 'Requires the $30 contract from Supplies')
                return [Offer('advanced_value','Recycling value',value_detail,
                              0 if value_maxed else self.ADVANCED_VALUE_PRICES[self.advanced_value_level],value_maxed),
                        Offer('advanced_capacity','Workshop carry capacity',detail,
                              0 if maxed else self.ADVANCED_CAPACITY_PRICES[level],maxed),
                        Offer('speed','Walking speed',speed_detail,
                              0 if speed_maxed else self.SPEED_PRICES[self.speed_level],speed_maxed)]
            if category == 'Furniture':
                specs = [('bench_2','East gallery west bench',140),('bench_3','East gallery east bench',140),
                         ('fountain_east','East gallery fountain',350),('mosaic_east','East gallery mosaic',300)]
            else:
                specs = [(f'lamp_{i+4}',f'East gallery lamp {i+1}',80) for i in range(4)]
                specs += [(f'plant_{i+4}',f'East gallery planter {i+1}',70) for i in range(4)]
            return [Offer(key,title,'Install fixture / +$1 base rent per 5s',price,key in self.decor)
                    for key,title,price in specs]

        if category == 'Gear':
            result = []
            tracks = [('capacity', self.capacity_level, self.CAPACITY_PRICES, 'Carry capacity',
                       f'{self.CAPACITIES[self.capacity_level]} slots', self.CAPACITIES),
                      ('value', self.value_level, self.VALUE_PRICES, 'Recycling contract',
                       f'${self.VALUES[self.value_level]} per item', self.VALUES),
                      ('tool', self.tool_level, self.TOOL_PRICES, 'Pickup tools', self.tool[0], self.TOOLS)]
            for key, level, prices, title, current, levels in tracks:
                maximum = level == len(prices)
                next_value = levels[min(level+1,len(levels)-1)]
                if key == 'capacity':
                    detail = f'{current} to {next_value} slots'
                elif key == 'value':
                    detail = f'{current} to ${next_value} per item at sale'
                else:
                    name, reach, batch = next_value
                    detail = f'{current} to {name}: {reach/64:.2g} tiles reach, up to {batch} items'
                result.append(Offer(key,title,'Fully upgraded' if maximum else detail,
                                    0 if maximum else prices[level],maximum))
            return result
        if category == 'Furniture':
            specs = [('bench_0','West bench',70),('bench_1','East bench',70),
                     ('fountain','Courtyard fountain',180),('mosaic','Courtyard mosaic',150)]
        else:
            specs = [(f'lamp_{i}',f'Lamp {i+1} / '+name,40)
                     for i,name in enumerate(('Supplies / Pages','Pages / Retro','Retro / Bean','Bean / Tailor'))]
            specs += [(f'plant_{i}',f'Planter {i+1} / '+name,35)
                      for i,name in enumerate(('west wall','east wall','west courtyard','east courtyard'))]
        return [Offer(key,title,'Install fixture / +$1 base rent per 5s',price,key in self.decor)
                for key,title,price in specs]

    def purchase(self, key, cash, shop='north'):
        offer = next((o for c in ('Gear','Furniture','Garden') for o in self.offers(c,shop) if o.key == key), None)
        if offer is None or offer.owned:
            return cash, 'That upgrade is already installed or unavailable.', False
        if key == 'advanced_capacity' and self.capacity_level < len(self.CAPACITY_PRICES):
            return cash, 'Buy the 20-slot bag at Northgate Supplies first.', False
        if key == 'advanced_value' and self.value_level < len(self.VALUE_PRICES):
            return cash, 'Buy the $30 recycling contract at Supplies first.', False
        regional=next((track for track in self.REGIONAL_TRACKS.get(shop,()) if track[0]==key),None)
        if regional and getattr(self,regional[3])<regional[4]:
            return cash,'Finish the previous section’s '+regional[5].lower()+' upgrades first.',False
        if cash < offer.price:
            return cash, f'You need {money(offer.price-cash)} more for {offer.title.lower()}.', False
        if regional or key in ('capacity','value','tool','advanced_capacity','advanced_value','speed'):
            field = key+'_level'
            setattr(self,field,getattr(self,field)+1)
        else:
            self.decor.add(key)
        return cash-offer.price, f'Purchased: {offer.title}.', True
