# Northgate keeps growing

The opening offers an optional first-steps guide. Click its On/Off option before starting, press T or click Skip during play, and press H to replay it. It follows actual movement, collection, sale, reopening Supplies, buying its first bag upgrade and opening the journal. It grants no money or equipment and does not pause the mall.

Pickup and sale keep their floating rewards and effects without bottom notices. Successful purchases update the shop directly. Blocked actions still explain the problem. Shoppers talk in bubbles above their heads and pause briefly; owners give bubbles when you accept or finish work. The journal holds detailed progress, including paged countdowns for all thirty-six owners.

## Work that comes back

Finish an owner's three initial projects to start their recurring favors. Each owner rotates through all twelve before repeating, with a different starting point. Every claim begins another three-minute wait of live play. Menus pause the wait. There is one active request, no deadline and no penalty for taking time.

| Favor | Work | North cash | Added base rent / 5s |
| --- | --- | --- | --- |
| The missing sketchbook | Recover a misplaced sketchbook | $90 | — |
| Names worth remembering | Polish two neighborhood plaques | $120 | $0.50 |
| Neighborhood recycling drive | Collect five pieces in the owner's section | $100 | — |
| News for the neighborhood | Collect notices at deliveries and post three | $130 | — |
| A local maker's window | Match the owner's product display plan | $160 | $0.50 |
| Opening stories | Greet three distinct visible shoppers | $130 | — |
| Tomorrow's opening fund | Sell eight pieces at that section's bins | $150 | $0.50 |
| A borrowed toolkit | Collect the delivery toolkit and repair a display stand | $120 | — |
| A light along the way | Check two lamp connections | $180 | $0.50 |
| Northgate memories | Recover three old photographs | $110 | — |
| A path back home | Refresh three chalk directions | $100 | — |
| Room for one more | Prepare a welcome board and greet two shoppers | $150 | — |

Recurring cash scales by area: north 1×, east 2×, Garden 4×, Commons 6×. Half-dollar rent rewards stay $0.50 in every area and use the existing cleanliness multiplier. Return to the owner to claim; rewards cannot be claimed twice. The three gold storefront badges remain the initial improvement milestones. Favor props do not use trash capacity or grant free fixture purchases. Collection and sale favors count only actions in their owner's section.

## Four neighborhoods

A later gate becomes visible after the preceding area's first sweep and all ten business reopenings. Pay once to enter. Each area has its own first sweep, two bins, delivery station, nine rent-paying businesses and an equipment shop. After the sweep, open the rent businesses in their listed order. Each section's recurring litter pool becomes eligible after its first sweep and equipment shop reopen. One pile returns globally every four seconds, capped at twelve recurring piles per eligible section.

| Area | Entry | Equipment shop | Following business costs / base rent per 5s |
| --- | --- | --- | --- |
| North arcade | Start | Supplies $10 | Pages $100 / $5; Retro Replay $250 / $8; Bean Street $450 / $12; The Tailor $700 / $16 |
| East gallery | $1,500 | Workshop $2,000 | Vinyl $3,000 / $25; Green Table $4,500 / $40; Copper Kettle $6,000 / $55; Secondhand Stars $8,000 / $70 |
| Garden Arcade | $10,000 | Garden Supply $12,000 | Seed & Stem $15,000 / $90; Little Lantern $18,500 / $115; Market Kitchen $22,000 / $145; Patchwork Studio $26,000 / $180 |
| Community Commons | $35,000 | Commons Exchange $40,000 | Book Nook $48,000 / $230; Radio Room $56,000 / $280; Sunday Table $65,000 / $340; Homeward Goods $75,000 / $410 |

Each equipment shop sells twelve separate local fixtures, each adding $1 base rent once. Equipment shops themselves pay no store rent. Freshly opened areas add dirty floors to the global cleanliness calculation. All tiles, including under props, can reach 100% clean.

| Later equipment | Garden Supply tiers / prices | Commons Exchange tiers / prices |
| --- | --- | --- |
| Bag | 45/$2,000; 50/$3,500; 55/$5,000; 60/$7,000 | 65/$10,000; 70/$14,000; 75/$20,000; 80/$28,000 |
| Value per piece | $100/$5,000; $140/$9,000; $180/$14,000 | $220/$20,000; $280/$30,000; $360/$45,000 |
| Tool reach / batch | 180px/6/$4,000; 200px/8/$7,000; 220px/10/$11,000 | 260px/12/$20,000 |
| Walking speed | 2×/$9,000 | 2.3×/$20,000; 2.6×/$35,000 |

Each track requires the preceding shop's maximum in that track; Garden tools require Supplies' pro kit. Upgrades advance one tier per purchase. Returning to earlier shops preserves better equipment.

## Story seeds and review

Short dialogue mentions the neighbors who built Northgate, lost photographs, a winter lantern walk and returning local makers. These are story seeds for a later storyline pass. Shopper dialogue lives in `game/lore.py`; favor descriptions live in `systems/favors.py`.

For review, try the guide's On/Off, Skip and H controls; greet a moving shopper; complete each original project then wait for a favor; verify local collection/sale counts and one-time rewards; fill all four neighborhoods in order; inspect the six overview journal pages and the Janitors tab and every shop at 800×600. Automated tests exercise all twelve favors for all thirty-six owners, full-floor coverage, safe routes, gated purchases, all equipment caps, tutorial actions, and forty-business progression. The smoke test renders all four regional shops, requests, speech, the guide and journal pages. Progress still resets on close.

Each listed original business row is now followed by five opposing stores. The next section waits for both rows. See [courts and janitors](courts-and-janitors.md) for their prices, rents and automation.
