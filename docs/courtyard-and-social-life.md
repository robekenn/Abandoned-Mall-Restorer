# Courtyard and social life

This feature PR addresses #29–#35. VERSION stays at 0.1.1; CI creates review builds, and a future release PR can publish these features.

| Issue | New behavior |
| --- | --- |
| #29 | Visitor arrivals rotate between individuals, families with two adults and a child, and teen pairs. Followers use safe routes to stay near their leader, accompany store visits and leave together. Children have smaller sprites and caps; teens have hoodies/headphones/backpacks and alternate walking with running. |
| #30 | Two permanent social tables per indoor court. After two regular businesses reopen, visitors can reserve separate reachable seats and chat. Tables participate in collision and depth sorting; reservations end when the visitor leaves. |
| #31 | Story community boards sit along alternate west/east room edges. Keepsakes and gatherings retain their separate roles; the map marks boards. |
| #32 | Keepsake-givers hand over their item once, then depart as ordinary walking visitors. Collected-memory flags prevent stationary givers from reappearing after Continue. |
| #33 | The Courtyard food court is a separate 2000×1440 map loaded on first entry, with eight distinct kiosk sprites, patio dining, brick pads, trees, herb pots and evening lights. Only the active map updates visitors/litter and renders geometry. |
| #34 | Narrow connections have marked service passages. Permanent wall caps close seams behind the upper/lower storefront rows, while the legitimate paths between unlocked courts remain connected. |
| #35 | An eight-minute live-play visitor cycle alternates steady, quiet and busy periods. The HUD names the period. Arrivals slow to twelve seconds during quiet hours and accelerate to 3.5 seconds during busy hours; populations remain bounded and visitors leave naturally. Menus pause the cycle and checkpoints retain its phase. |

## Enter the Courtyard

In Community Commons, finish the first sweep and reopen six businesses. The patio doors are on the west side of the Commons, opposite its story board. Press E and pay $50,000 once to restore the doors. Return visits are free. The patio's return doors lead back to the same indoor position.

Cash, carried items and existing equipment travel with you. The indoor world pauses while outside; the Courtyard pauses while indoors. Both maps earn their rent during active play, and gameplay menus pause both. A collection favor accepted indoors also counts player pickups outside; return indoors to claim it. J outside opens the Courtyard map and progression guide, and F2/Pause keeps the usual settings and save/exit controls.

## Reopen the kitchens

Reopen Provisions first. Finish the courtyard's first sweep, then reopen the seven restaurants in order. The courtyard maintains its own cleanliness and recurring litter, with the same four-second global spawn interval and twelve-item local cap used by an individual indoor court.

| Business | Reopening cost | Base income per 5s |
| --- | ---: | ---: |
| Courtyard Provisions | $30,000 | Equipment shop |
| Hearth Pizza | $45,000 | $250 |
| Mint & Noodles | $60,000 | $330 |
| Orchard Juice | $75,000 | $420 |
| Sunrise Bakery | $90,000 | $510 |
| Copper Grill | $110,000 | $620 |
| Garden Bowls | $135,000 | $750 |
| Moonrise Desserts | $160,000 | $900 |

Provisions sells three Service tracks instead of walking speed. Each has three tiers priced at $15,000/$30,000/$55,000:

- Kitchen service training: +15% courtyard restaurant income per tier, before the courtyard cleanliness multiplier.
- Patio comfort: eight extra seconds at dining tables and two extra visitor slots per tier.
- Compost partnerships: +25% per tier on player recycling sales at courtyard stations. Indoor recycling values are unchanged.

Furniture restores six picnic tables with umbrellas for $4,000 each. Garden installs four herb pots for $2,500 each and four light strings for $3,500 each. Each purchased fixture adds $1 local base income per five seconds. Purchases retain the inspect-then-Purchase behavior.

## Saves and testing

v0.1.1 checkpoints load with an unopened Courtyard and default new service tracks. New checkpoints preserve both maps, restaurant progress, cleanup, fixtures, service tiers, visitor-cycle phase, carried items, indoor requests and the active map. A saved janitor on a new table location moves to the nearest safe navigation node. A saved gathering that overlaps new seating temporarily hides that seating until the gathering ends.

Try busy/quiet periods after reopening several businesses, follow a family through a store visit, sit two visitors at a social table, and collect a keepsake then Continue. Walk the service passages after each unlock. Enter the courtyard, reopen Provisions, finish its sweep, open the kitchens, compare each service upgrade, and save/Continue both inside and outside. Automated checks cover navigation to every restaurant, cleanup patch and dining seat, population bounds, followers, menus, purchases, income, mouse pickup, legacy migration, corrupt-save rejection and minimum-size rendering. Normal and developer frozen smoke checks include courtyard transitions and save/load.
