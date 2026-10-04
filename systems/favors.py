"""Repeatable community work; a stable rotation avoids immediate duplicates."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Favor:
    key: str
    title: str
    lore: str
    mode: str
    cash: int
    bonus: float = 0
    amount: int = 0


FAVORS=(
    Favor('sketchbook','The missing sketchbook','Someone left drawings of the old mall on a bench. Let’s get them home.','lost',90),
    Favor('nameplates','Names worth remembering','The brass plaques are dull. They carry the names of our first neighbors.','polish',120,.5),
    Favor('recycle','Neighborhood recycling drive','Every little load helps us keep Northgate welcoming. Collect litter from anywhere in the mall.','collect',100,0,5),
    Favor('notice','News for the neighborhood','Put up three community notices. There are still people who remember this place.','route',130),
    Favor('maker','A local maker’s window','A neighbor brought new work to show. Help arrange a window people will stop for.','display',160,.5),
    Favor('stories','Opening stories','Ask three different shoppers about Northgate. A mall is made of people, too.','greet',130,0,3),
    Favor('fund','Tomorrow’s opening fund','Sell eight pieces at our section’s bins. The proceeds can fund a better welcome.','sell',150,.5,8),
    Favor('toolkit','A borrowed toolkit','Collect our toolkit from deliveries and repair the little display stand.','repair',120),
    Favor('lantern','A light along the way','Check two lamp connections. These halls used to glow on winter evenings.','lantern',180,.5),
    Favor('memories','Northgate memories','Three old photographs turned up around the concourse. Bring them back for safekeeping.','memories',110),
    Favor('chalk','A path back home','Refresh three chalk directions. Help returning neighbors find their way.','chalk',100),
    Favor('welcome','Room for one more','Prepare a welcome board and greet two shoppers. There is always room for another neighbor.','welcome',150,0,2),
)
