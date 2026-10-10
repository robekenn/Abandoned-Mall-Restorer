# Courtyard and social life

This feature PR addresses #29–#35. VERSION stays at 0.1.1; CI creates review builds, and a future release PR can publish these features.

| Issue | New behavior |
| --- | --- |
| #29 | Visitor arrivals rotate between individuals, families with two adults and a child, and teen pairs. Followers use safe routes to stay near their leader, accompany store visits and leave together. Children have smaller sprites and caps; teens have hoodies/headphones/backpacks and alternate walking with running. |
| #30 | Two permanent social tables per indoor court. After two regular businesses reopen and the table and that individual chair are repaired in that court, visitors can reserve separate reachable seats and chat. Tables participate in collision and depth sorting; reservations end when the visitor leaves. |
| #31 | Story community boards sit along alternate west/east room edges. Keepsakes and gatherings retain their separate roles; the map marks boards. |
| #32 | Keepsake-givers hand over their item once, then depart as ordinary walking visitors. Collected-memory flags prevent stationary givers from reappearing after Continue. |
| #33 | The Courtyard food court is a separate 2000×1440 map loaded on first entry, with eight distinct kiosk sprites, patio dining, brick pads, trees, herb pots and evening lights. Visitor routes, litter and janitor work run on both maps during live play; rendering follows the active map. |
| #34 | The original indoor connecting paths remain open, with their original paving. Added service overlays and wall caps have been removed following playtest feedback. |
| #35 | An eight-minute live-play visitor cycle alternates steady, quiet and busy periods. The HUD names the period. Arrivals slow to twelve seconds during quiet hours and accelerate to 3.5 seconds during busy hours; populations remain bounded and visitors leave naturally. Menus pause the cycle and checkpoints retain its phase. |

## Enter the Courtyard

In Community Commons, finish the first sweep and reopen six businesses. A 176px opening connects the Commons east exterior wall to the patio west wall. Small wooden plaques hang from wall brackets and show only “Courtyard” or “Community Commons”; they leave the community board visible. The opening cost appears in the E interaction prompt. Press E at the passage to pay that cost once after meeting the prerequisites; walking into the locked opening does not spend money. Rubble blocks the passage until it is restored. Once open, walk right through it to enter and left through the matching opening to return, without pressing E. Return visits are free, and arrival positions keep held movement from bouncing you straight back.

All four indoor sections share North arcade’s two aligned seating areas flanking their central fountain, with tables toward the shops, benches below, bins along the central approach and planters on the outer edges. Shop doors, delivery access and connecting paths stay clear. All four indoor sections start with collapsed benches, tables and seats. Furniture now lists two individual benches, two individual tables, and each table’s left and right chair separately in every section. Repair the matching table before buying its chairs; visitors reserve only repaired chairs. Use arrows or the mouse wheel to browse the expanded list, or click a visible row to inspect and then Purchase. Earlier bundle purchases from this PR retain their repaired bench, table and both chairs after Continue; new bench purchases repair only that bench. Every mosaic is positioned from its own fountain. The East, Garden and Commons plans also retain their original cleanup IDs; older players, janitors, gatherings and event tasks overlapping moved fixtures migrate to safe positions.

| Indoor section | Each bench | Each table | Each chair |
| --- | ---: | ---: | ---: |
| North arcade | $70 | $70 | $35 |
| East gallery | $140 | $140 | $70 |
| Garden court | $600 | $600 | $300 |
| Community Commons | $900 | $900 | $450 |

Cash, carried items and existing equipment travel with you. Visitors, recurring litter and hired janitors continue on both maps during live play; inactive story and owner-task timers pause. The HUD’s Clean percentage counts clean floor tiles across every opened indoor section and the unlocked Courtyard, weighted by floor size, and stays the same when changing maps. Unopened areas do not count. Local cleanliness still determines each building’s rent bonus; background janitor earnings are credited without showing popups on the wrong map. Both maps earn their rent during active play, and gameplay menus pause both. A collection favor accepted indoors also counts player pickups outside; return indoors to claim it. J outside opens the Courtyard map and progression guide, and F2/Pause keeps the usual settings and save/exit controls.

## Reopen the kitchens

Reopen Provisions first. Finish the courtyard's first sweep, then reopen the seven restaurants in order. The courtyard maintains its own cleanliness and recurring litter, with a twelve-item local cap, matching each indoor court. Recurring litter on each map follows its own traffic: every 2 seconds during Busy hours, 4 seconds during Steady hours, and 8 seconds during Quiet hours. The indoor spawner rotates fairly between eligible sections, spawning one patch per interval; the courtyard has its own spawner. Both keep running on the inactive map after its first sweep and upgrade shop reopening. Only the active map excludes spots within 100px of the player. Menus, tutorial explanations and cooking pause both spawners. Traffic changes preserve accumulated fractional spawn progress, which saves in baseline four-second units for compatibility with existing checkpoints.

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


## Cook with the neighbors

Each reopened restaurant has its own random **3–10 minute cooldown of live play**. When its countdown ends, that kitchen asks for help; its request stays available, with a HUD notice on both maps and the same exclamation-point marker used for indoor requests at its counter. Visit that counter and press **E**, or click its storefront/counter while standing close. Idle kitchens cannot start cooking. **J → Overview → Restaurants** lists each reopened kitchen’s own next-request countdown. Once a request is ready, its row highlights “Needs cooking help”; other kitchens show their individual remaining times, and unopened ones remain “Store closed.” The footer explains that every kitchen has its own cooldown. Like other gameplay menus, the journal pauses the countdown while open. Several kitchens can need help at the same time. Accepting one resets only its own cooldown; other requests stay ready and other timers keep their progress. Provisions keeps its equipment shop. Cooking is optional: restaurants keep their normal rent and visitor service without player involvement.

| Kitchen | Your activity | Controls |
| --- | --- | --- |
| Hearth Pizza | Add three varied toppings in ticket order | 1–5 or ingredient buttons |
| Mint & Noodles | Alternate six spoon turns | Left/right arrows or buttons |
| Orchard Juice | Fill two glasses to a varied target | Space/Enter or stop button in the gold band |
| Sunrise Bakery | Fold and roll dough along a varied four-arrow sequence | Arrow keys or buttons |
| Copper Grill | Time cooking on each side, flip, then plate | Space/Enter or action button in the gold band |
| Garden Bowls | Layer three varied salad ingredients | 1–5 or ingredient buttons |
| Moonrise Desserts | Stack three varied scoop flavors from bottom to top | 1–5 or ingredient buttons |

Read the visible ticket, then choose Accept cooking request. Each attempt requires an ingredient deposit of **10% of the kitchen's base five-second rent** (rounded to whole dollars). The deposit is returned on success, plus a tip equal to 25% of that base rent scaled by the score. A wrong action loses **20 score points**; wrong ingredients also remove **two seconds** from the overall ingredient timer without advancing the recipe. **Three mistakes or a timeout fail the order**, paying no tip and forfeiting the deposit. Esc/Close after starting also forfeits it. Closing the preview before accepting costs nothing and keeps the request available. You need enough cash for the displayed deposit to accept.

Difficulty is separate for each restaurant, increasing every **three successful orders** to a maximum of challenge 6. Failures do not raise it.

| Challenge | Timing band width | Marker sweep (one way) | Ingredient order deadline | Pour/grill deadline |
| --- | ---: | ---: | ---: | ---: |
| 1 | 20% of gauge | 2.1s | 12s total | 20s total |
| 6 (maximum) | 10% of gauge | 1.2s | 4.5s total | 10s total |

The overall ingredient timer continues across successful steps, so it cannot be reset by selecting an ingredient. The marker resets between glasses or grill sides, while the overall timing-game deadline continues. Spoon turns and pastry shaping retain their arrow mechanics and three-mistake limit. Mouse controls provide every action without keyboard shortcuts. The result returns to the courtyard; it cannot immediately start another order.

The world pauses during cooking, including movement, litter, customers, rent and both janitor crews. F2 settings and the exit/pause overlay also freeze cooking timers. Every opened kitchen’s cooldown runs on either map during live play and pauses in menus or cooking. A ready request remains ready until accepted. Accepting starts a new random cooldown for only that kitchen, including attempts later failed or abandoned. Closed kitchens’ timers pause until they reopen.

Orders served, failures, best score, cumulative tips, all individual cooldowns and ready requests persist through Continue in both save slots. Older cooking saves retain existing records, default failures to zero and begin their individual request cooldowns without resetting progress. Earlier shared-timer saves keep the ready kitchen or the last accepted kitchen’s remaining cooldown while other kitchens receive their own random timers. Accepting saves the deposit deduction and consumed request immediately: leaving or reloading an unfinished order does not refund ingredients or restore that request. Regular visitors keep using the normal food queues when play resumes.
