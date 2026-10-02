# Collect, sell and reinvest

## First goal: Northgate Supplies

The worker starts with a hand grabber, six bag slots and a $10-per-item recycling contract. Dust and litter both count as one carried item. Pickup cleans the floor and fills the bag; it no longer pays cash immediately. Walk to either SELL dumpster and press E to sell the whole load. Empty loads pay nothing; full bags prevent further pickup and leave the blocked task unchanged.

Reopen Northgate Supplies for $100. It is the first business in the storefront row and the sole place to buy upgrades. Press E at its open marker to enter. Supplies does not pay rent. Completing the initial sweep then unlocks Pages, followed by Retro Replay, Bean Street and The Tailor.

## Shop controls

Use the mouse to click an upgrade row. Keys 1/2/3 select Gear/Furniture/Garden; left/right or Tab switch menu tabs; up/down select a row; Enter/Space purchase; Esc/E close the menu. Esc closes the menu before it quits the game. Gameplay, litter and rent timers pause while shopping.

Unaffordable purchases and already installed fixtures do not deduct money. Gear advances one tier at a time and cannot exceed its last tier. The menu reports the purchase result and updates its prices/stats immediately.

## Gear prices

| Track | Starting equipment | Tier 1 | Tier 2 | Tier 3 |
| --- | --- | --- | --- | --- |
| Carry capacity | 6 items | 12 items / $75 | 24 items / $180 | 40 items / $400 |
| Recycling contract | $10 per item | $15 per item / $120 | $22 per item / $300 | $30 per item / $600 |
| Pickup tool | Hand grabber / 72px / 1 item | Long grabber / 110px / 1 item / $100 | Cleanup kit / 135px / up to 3 items / $250 | Pro kit / 155px / up to 5 items / $550 |

Tool batches collect the nearest tasks within reach, capped by remaining bag space. Store and dumpster interaction stays at 72px, regardless of tool reach. Sales use the current recycling contract, including items already in the bag when a contract is upgraded.

## Individual scenery purchases

| Fixture | Count | Price each |
| --- | --- | --- |
| West/east bench restoration | 2 | $70 |
| Lamps by west/middle/east shops and entrance | 4 | $40 |
| Planters by west/east walls and courtyard | 4 | $35 |
| Courtyard fountain | 1 | $180 |
| Courtyard mosaic | 1 | $150 |

Scenery is installed immediately at its named location. Each item is a one-time purchase. There are no free fixture unlocks or world-scene cycling; Tab only switches tabs inside the shop.

## Businesses and recurring work

| Order | Business | Cost | Rent every 5 seconds |
| --- | --- | --- | --- |
| 1 | Northgate Supplies | $100 | Upgrade shop / no rent |
| 2 | Pages Bookshop | $100 | $5 |
| 3 | Retro Replay | $250 | $8 |
| 4 | Bean Street | $450 | $12 |
| 5 | The Tailor | $700 | $16 |

There are currently 51 reachable starting tasks, with tile-coverage checks ensuring the entire playable floor can be cleaned. Starting positions avoid storefront entrances and dumpsters. Once the first sweep is complete and Supplies is open, fresh litter returns every four seconds instead of eight, capped at twelve active piles. The pool stays bounded and spawns stay away from the player.

Returning litter permits earning more money even if all initial proceeds were spent on upgrades before opening a rent-paying business. Clearing fresh litter restores its dirty floor patch; overlapping piles retain their remaining dirt. Dumpster sales and rents fund both equipment and business progression. The two current dumpsters serve the playable north arcade; other galleries remain closed.

## Review checklist

1. Fill the initial six-slot bag. Confirm further pickup is blocked, with no money awarded yet.
2. Sell at the west dumpster. Confirm $60 payout and an empty bag; retry selling an empty bag.
3. Earn $100 and reopen Supplies before any other business. Buy capacity or a tool with mouse and keyboard controls.
4. Buy just one bench or lamp. Confirm that only that fixture changes and that repeat purchases do not charge again.
5. Clear the first sweep and sell your load. Confirm 100% floor cleanliness and Pages availability.
6. After closing the menu, wait four seconds for fresh litter. Collect it, test both dumpsters, and grow toward later businesses.
7. Buy a recycling contract, then sell carried items and verify the higher payout. Try a multi-item tool with only one or two bag slots free.
8. Resize to 800x600 and inspect all three menu tabs. Try Esc/E to close, M for audio, and Tab outside the menu (it should not change scenery).

Progress still resets on close. Saving, shoppers, additional wings and further economic balancing remain future work. Automated checks cover collection/sales, capacity, prices, purchase limits, input handling, fixture ownership, tool range/batches, full-floor coverage, business order, rent, doubled spawns and the existing animation/audio/collision behaviors.
