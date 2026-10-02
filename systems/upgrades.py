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
    CAPACITIES = (1, 2, 4, 8, 16, 24, 40)
    CAPACITY_PRICES = (5, 15, 40, 90, 180, 350)
    VALUES = (1, 2, 4, 8, 15, 30)
    VALUE_PRICES = (8, 30, 90, 220, 500)
    TOOLS = (('Hand grabber', 72, 1), ('Long grabber', 110, 1),
             ('Cleanup kit', 135, 3), ('Pro cleanup kit', 155, 5))
    TOOL_PRICES = (100, 250, 550)

    def __init__(self):
        self.held = 0
        self.capacity_level = 0
        self.value_level = 0
        self.tool_level = 0
        self.decor = set()

    @property
    def capacity(self):
        return self.CAPACITIES[self.capacity_level]

    @property
    def unit_value(self):
        return self.VALUES[self.value_level]

    @property
    def tool(self):
        return self.TOOLS[self.tool_level]

    def offers(self, category):
        if category == 'Gear':
            result = []
            tracks = [('capacity', self.capacity_level, self.CAPACITY_PRICES, 'Carry capacity',
                       f'{self.capacity} slots', self.CAPACITIES),
                      ('value', self.value_level, self.VALUE_PRICES, 'Recycling contract',
                       f'${self.unit_value} per item', self.VALUES),
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
                    detail = f'{current} to {name}: {reach}px reach, up to {batch} items'
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
        return [Offer(key,title,'Install this individual fixture',price,key in self.decor)
                for key,title,price in specs]

    def purchase(self, key, cash):
        offer = next((o for c in ('Gear','Furniture','Garden') for o in self.offers(c) if o.key == key), None)
        if offer is None or offer.owned:
            return cash, 'That upgrade is already installed or unavailable.', False
        if cash < offer.price:
            return cash, f'You need {money(offer.price-cash)} more for {offer.title.lower()}.', False
        if key in ('capacity','value','tool'):
            field = key+'_level'
            setattr(self,field,getattr(self,field)+1)
        else:
            self.decor.add(key)
        return cash-offer.price, f'Purchased: {offer.title}.', True
