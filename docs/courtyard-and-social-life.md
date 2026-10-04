# Courtyard and social life

This feature PR addresses #29–#35. VERSION stays at 0.1.1; CI creates review builds, and a future release PR can publish these features.

| Issue | New behavior |
| --- | --- |
| #29 | Visitor arrivals rotate between individuals, families with two adults and a child, and teen pairs. Followers use safe routes to stay near their leader, accompany store visits and leave together. Children have smaller sprites and caps; teens have hoodies/headphones/backpacks and alternate walking with running. |
| #30 | Two permanent social tables per indoor court. After two regular businesses reopen and the matching seating upgrade is purchased in that court, visitors can reserve separate reachable seats and chat. Tables participate in collision and depth sorting; reservations end when the visitor leaves. |
| #31 | Story community boards sit along alternate west/east room edges. Keepsakes and gatherings retain their separate roles; the map marks boards. |
| #32 | Keepsake-givers hand over their item once, then depart as ordinary walking visitors. Collected-memory flags prevent stationary givers from reappearing after Continue. |
| #33 | The Courtyard food court is a separate 2000×1440 map loaded on first entry, with eight distinct kiosk sprites, patio dining, brick pads, trees, herb pots and evening lights. Visitor routes run on both maps; litter, cleaning work and rendering remain local to the active map. |
| #34 | The original indoor connecting paths remain open, with their original paving. Added service overlays and wall caps have been removed following playtest feedback. |
| #35 | An eight-minute live-play visitor cycle alternates steady, quiet and busy periods. The HUD names the period. Arrivals slow to twelve seconds during quiet hours and accelerate to 3.5 seconds during busy hours; populations remain bounded and visitors leave naturally. Menus pause the cycle and checkpoints retain its phase. |

## Enter the Courtyard

In Community Commons, finish the first sweep and reopen six businesses. A 176px opening connects the Commons east exterior wall to the patio west wall. Walk right through it to enter and left through the matching opening to return; E is unnecessary. The existing one-time $50,000 passage restoration still applies on first entry (E at the restoration marker can also pay it). Return visits are free, and arrival positions keep held movement from bouncing you straight back.

The North arcade now has two aligned seating areas flanking the central fountain, with tables toward the shops, benches below, bins along the central approach and planters on the outer edges. Shop doors, delivery access and connecting paths stay clear. All four indoor sections start with collapsed benches, tables and seats. Each section’s two Furniture seating purchases restore their matching bench and table seats together, using the existing prices and fixture IDs. Previously purchased furniture remains restored.

Cash, carried items and existing equipment travel with you. Visitors continue their journeys on both maps; inactive litter, cleaning work, story and owner-task timers pause. Both maps earn their rent during active play, and gameplay menus pause both. A collection favor accepted indoors also counts player pickups outside; return indoors to claim it. J outside opens the Courtyard map and progression guide, and F2/Pause keeps the usual settings and save/exit controls.

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

- Kitchen service training: +15% courtyard restaurant income per tier, before the courtyard cleanliness multiplier, and counter service drops from 7 seconds to 3.25 seconds across the three tiers.
- Patio comfort: eight extra seconds at dining tables and two extra visitor slots per tier.
- Compost partnerships: +25% per tier on player recycling sales at courtyard stations. Indoor recycling values are unchanged.

Furniture restores six picnic tables with clearly drawn side benches for $4,000 each. Garden installs four herb boxes in kitchen-wall gaps for $2,500 each and four light strings for $3,500 each. Each purchased fixture adds $1 local base income per five seconds. Purchases retain the inspect-then-Purchase behavior.

## Saves and testing

v0.1.1 checkpoints load with an unopened Courtyard and default new service tracks. New checkpoints preserve both maps, restaurant progress, cleanup, fixtures, service tiers, visitor-cycle phase, carried items, indoor requests and the active map. Original North arcade litter IDs remain stable. A saved player or janitor on a moved fixture relocates to a safe navigation node; older gatherings and event tasks overlapping the moved fountain or bins also relocate while retaining their progress. A saved gathering that overlaps new seating temporarily hides that seating until the gathering ends.

Try busy/quiet periods after reopening several businesses, follow a family through a store visit, sit two visitors at a social table, and collect a keepsake then Continue. Walk the connecting paths after each unlock. Enter the courtyard, reopen Provisions, finish its sweep, open the kitchens, compare each service upgrade, and save/Continue both inside and outside. Automated checks cover navigation to every restaurant, cleanup patch and dining seat, population bounds, followers, menus, purchases, income, mouse pickup, legacy migration, corrupt-save rejection and minimum-size rendering. Normal and developer frozen smoke checks include courtyard transitions and save/load.

The courtyard uses the same HUD, objective card, contextual action strip, notifications and four-tab journal as the indoor mall. Its Overview shows the local map and restaurant list. Indoor gatherings can be inspected outside; return indoors to host them. Open passages in the Commons east exterior wall and the patio west boundary share a continuous paved threshold. Warm pavers, a continuous entrance walk, bounded brick dining courts and upright north-facing counters refine the patio.

## Courtyard service and connected journeys

Food-court customers spawn at the North arcade front entrance and walk through the unlocked indoor courts to the Commons courtyard opening. The same visitor, identity and carried dish move between maps. Customers route to the tail of their restaurant line, wait for the counter, order and receive that kitchen’s dish, then use available seating or walk back through the Commons and out the front entrance. Restaurants never hide visitors inside. Six reservations per restaurant and the shared population limits bound arrivals. Menus pause both visitor systems and transfers. Normal live play continues routes in the inactive map, so entering/leaving the patio does not reset its visitors. Allow about a minute for the first trip from the front entrance; service and seating can extend visits.

Hearth Pizza serves slices, Mint & Noodles serves noodle bowls, Orchard Juice serves juice, Sunrise Bakery serves croissants, Copper Grill serves skewers, Garden Bowls serves salads, and Moonrise Desserts serves sundaes. Each dish has a distinct carried sprite, visible indoors on the return journey. Visitors remain transient across Continue, like earlier mall shoppers; restaurant progress, visitor-period phase and identity counters still persist.

While outside, open **J → Janitors** to hire the Courtyard cleaner for $320,000, then use the usual cleaning/walking upgrades. Cleanup pays 75% of your trash value and protects litter needed for an active pickup favor. The cleaner’s position, target, partial work, upgrades and earnings persist across save/load. Courtyard rent now uses the same five-second character popup and clean-floor sound as inside. Indoor benches show obvious broken slats/supports until their existing Furniture restoration is purchased; earlier purchased benches stay restored.

The courtyard’s open passage has broad, clearly marked edges and a continuous approach. Provisions has a framed gold upgrade plaque. The dining fixtures have readable tabletops and separate side benches; unpurchased ones have broken slats. Herb boxes sit in planted gaps between kitchens, outside the walking and queue lanes.
