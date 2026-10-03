# Collect, sell and reinvest

## First goal: Northgate Supplies

The worker starts with a hand grabber, one bag slot and a $1-per-item recycling contract. Dust and litter both count as one carried item. Pickup cleans the floor and fills the bag; it no longer pays cash immediately. Walk to either SELL trash bin and press E to sell the whole load. Empty loads pay nothing; full bags prevent further pickup and leave the blocked task unchanged.

Reopen Northgate Supplies for $10. It is the first business in the storefront row and sells the original gear and fixtures. Press E at its open marker to enter. Supplies does not pay rent. Completing the initial sweep then unlocks Pages, followed by Retro Replay, Bean Street and The Tailor.

## Shop controls

Use the mouse to click an upgrade row. Keys 1/2/3 select Gear/Furniture/Garden; left/right or Tab switch menu tabs; up/down select a row; Enter/Space purchase; Esc/E close the menu. Esc closes the menu; in the mall it opens a pause screen with a separate exit confirmation. Gameplay, litter and rent timers pause while shopping.

Unaffordable purchases and already installed fixtures do not deduct money. Gear advances one tier at a time and cannot exceed its last tier. Successful purchases update prices/stats immediately without a notice; unavailable purchases explain their prerequisite.

## Gear prices

| Upgrade | Capacity / purchase price | Recycling value / purchase price |
| --- | --- | --- |
| Start | 1 item / free | $1 per item / free |
| 1 | 2 items / $5 | $2 per item / $8 |
| 2 | 4 items / $15 | $4 per item / $30 |
| 3 | 8 items / $40 | $8 per item / $90 |
| 4 | 16 items / $90 | $15 per item / $220 |
| 5 | 20 items / $180 | $30 per item / $500 |

| Pickup tool | Reach | Batch | Purchase price |
| --- | --- | --- | --- |
| Hand grabber | 72px | 1 | Free |
| Long grabber | 110px | 1 | $100 |
| Cleanup kit | 135px | 3 | $250 |
| Pro cleanup kit | 155px | 5 | $550 |

Tool batches collect the nearest tasks within reach, capped by remaining bag space. Store and trash bin interaction stays at 72px, regardless of tool reach. Sales use the current recycling contract, including items already in the bag when a contract is upgraded.

## Individual scenery purchases

| Fixture | Count | Price each |
| --- | --- | --- |
| West/east bench restoration | 2 | $70 |
| Lamps between each pair of storefronts | 4 | $40 |
| Planters by west/east walls and courtyard | 4 | $35 |
| Courtyard fountain | 1 | $180 |
| Courtyard mosaic | 1 | $150 |

Scenery is installed immediately at its named location. Every purchased bench, lamp, planter, fountain or mosaic adds $1 to base rent every five seconds. Equipment upgrades do not add rent. Repeat purchases do not add income. Each item is a one-time purchase. There are no free fixture unlocks or world-scene cycling; Tab only switches tabs inside the shop.

## Cleanliness and rent

Every five-second payment uses the current floor cleanliness across all unlocked floor tiles. Closed galleries do not count. Opening the east gallery adds its dirty floor to this calculation immediately. Store rents in the table below are base rates; add $1 for each purchased fixture before applying the cleanliness multiplier.

| Floor cleanliness | Rent multiplier |
| --- | --- |
| 0% | 0x |
| Greater than 0%, below 50% | 0.5x |
| 50%, below 100% | 1x |
| Exactly 100% | 1.5x |

Fractional payouts are kept: Pages pays $2.5, $5 or $7.5 depending on the tier. The J-key journal shows the actual upcoming payout and multiplier; floor percentages never round up into the 100% bonus. Fresh litter removes that bonus until cleaned again.

## Businesses and recurring work

| Order | Business | Cost | Rent every 5 seconds |
| --- | --- | --- | --- |
| 1 | Northgate Supplies | $10 | Upgrade shop / no rent |
| 2 | Pages Bookshop | $100 | $5 |
| 3 | Retro Replay | $250 | $8 |
| 4 | Bean Street | $450 | $12 |
| 5 | The Tailor | $700 | $16 |

There are currently 63 reachable starting tasks, with tile-coverage checks ensuring the entire playable floor can be cleaned. Starting positions avoid storefront entrances and trash bins. Once the first sweep is complete and Supplies is open, fresh litter returns every four seconds instead of eight, capped at twelve active piles. The pool stays bounded and spawns stay away from the player.

Returning litter permits earning more money even if all initial proceeds were spent on upgrades before opening a rent-paying business. Clearing fresh litter restores its dirty floor patch; overlapping piles retain their remaining dirt. Trash-bin sales and rents fund both equipment and business progression. The two upright indoor trash bins sit beside the west/east benches and serve the playable north arcade; the east gallery can be unlocked next, then Garden Arcade and Community Commons follow.

## East gallery and Workshop

The east marker and interaction prompt are hidden until the north sweep is complete and all ten north businesses reopen. Then go to the gold marker by the east grille and press E. Pay **$1,500** once to open the gallery. Its 56 initial tasks cover all concourse floor tile, with two indoor trash bins beside benches. North cleanup and purchased upgrades stay intact. The HUD and directory show the new area and next objective.

The first east business is **Eastgate Workshop ($2,000)**. It can open before finishing the east sweep. It does not pay store rent; its individually purchased fixtures do. Supplies keeps the original tools and recycling contracts, and now caps bag capacity at 20. Workshop upgrades continue from that cap:

| Workshop bag | Purchase price | Requirement |
| --- | --- | --- |
| 25 items | $500 | 20-slot Supplies bag |
| 30 items | $750 | 25-slot bag |
| 35 items | $1,000 | 30-slot bag |
| 40 items | $1,250 | 35-slot bag |

| Walking speed | Purchase price |
| --- | --- |
| 1.15x | $300 |
| 1.3x | $600 |
| 1.5x | $1,000 |

Speed upgrades are independent of the bag prerequisite. Faster movement keeps diagonal normalization, collision stepping and the existing animation behavior. Returning to Supplies never removes Workshop upgrades.

Workshop also sells twelve individual east fixtures: two benches ($140 each), four lamps ($80 each), four planters ($70 each), a fountain ($350) and a mosaic ($300). Each adds $1 base rent. North fixtures are only sold at Supplies; east fixtures are only sold at Workshop.

Finishing the east sweep unlocks **Vinyl & Company ($3,000, $25 base rent)** after Workshop, then **The Green Table ($4,500, $40 base rent)** after Vinyl. Recurring litter becomes eligible separately in each section after its first sweep and upgrade shop reopening. One pile returns every four seconds across eligible sections, with a cap of twelve recurring piles per section. Initial east litter does not block north recurring work.

## Sound feedback

A brief rising chime accompanies each 1.5x rent payment. A short low tone signals a full bag, empty sale, insufficient money, unmet prerequisites, a maxed/owned upgrade, or an interaction with nothing in reach. The message explains what to do next. An original 80 BPM, eight-bar four-level chiptune plays quietly beneath effects on a reserved channel. Short note ramps and softened edges keep it gentle. Music loops during gameplay and shopping. M pauses the music and mutes effects; unmuting resumes the loop. Gameplay still works when audio hardware is unavailable.

## Review checklist

1. Fill the initial one-slot bag. Confirm further pickup is blocked, with no money awarded yet.
2. Sell at the west trash bin. Confirm $1 payout and an empty bag; retry selling an empty bag.
3. Earn $10 and reopen Supplies before any other business. Buy capacity or a tool with mouse and keyboard controls.
4. Buy just one bench or lamp. Confirm that only that fixture changes and that repeat purchases do not charge again.
5. Clear the first sweep and sell your load. Confirm 100% floor cleanliness and Pages availability.
6. After closing the menu, wait four seconds for fresh litter. Collect it, test both trash bins, and grow toward later businesses.
7. Buy a recycling contract, then sell carried items and verify the higher payout. Try a multi-item tool with only one or two bag slots free.
8. Check rent at dirty, partly cleaned and completely cleaned floors. Confirm half-dollar payouts and the HUD multiplier.
9. Buy fixtures and confirm +$1 base rent each, including the cleanliness multiplier.
10. Finish the north businesses, pay $1,500 at the east gate, and check the new dirty-floor rent tier. Reopen Workshop for $2,000.
11. Max Supplies capacity at 20, then buy 25/30/35/40 at Workshop. Test speed upgrades, both east bins, and the two later businesses.
12. Listen for the bonus-rent chime and blocked-action tone, then mute them with M.
13. Resize to 800x600 and inspect all three menu tabs. Try Esc/E to close, M for audio, and Tab outside the menu (it should not change scenery).

Progress now saves automatically, manually with F5 and on exit; Continue restores your world. Recurring litter rotates across eligible courts and janitors leave pieces needed for your local collection favors. See [saving and story](saving-and-lantern-story.md). The southern areas are playable; see [community favors and expansion](community-favors-and-expansion.md). Automated checks cover collection/sales, capacity, prices, purchase limits, input handling, fixture ownership, tool range/batches, full-floor coverage, business order, rent, doubled spawns and the existing animation/audio/collision behaviors.

## Owner-led shop improvements

Reopened rent-paying stores now have owners with three optional projects. Earn improvements by delivering supplies, arranging window displays and welcoming shoppers; there is no escalating building-upgrade price schedule. The first three projects add $3.5 base rent; repeatable favors can add further half-dollar increases. Equipment shops remain unchanged. See [the living mall guide](shoppers-and-requests.md) for controls, rewards and visitor behavior.

## Workshop recycling contracts

The Workshop adds three contracts after the $30-per-item Supplies contract:

| Sale value per item | Purchase price |
| --- | --- |
| $45 | $900 |
| $60 | $1,800 |
| $80 | $3,200 |

Buy them in order from the Workshop’s Gear tab. They use the same trash bag and bins, apply to the whole load at sale time, and stop at $80 per item. The Supplies contract track remains capped at $30. Equipment and fixture prices appear in a short list; only the selected upgrade’s description and location appear below it.

The main HUD keeps cash, bag space, cleanliness and one objective visible. Press **J** to open the journal for the map, rental income, equipment and owner request countdowns. **J/Esc/E** closes it; it pauses the game and request timers. Owner requests begin three minutes after their store opens, with another three-minute pause after each improvement is claimed; each rent-paying store has three initial improvements followed by recurring favors. Each court now continues through five opposing shops; see [courts and janitors](courts-and-janitors.md) for the full expansion and hiring prices.
