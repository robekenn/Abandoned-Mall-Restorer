# Abandoned Mall Restorer

[![CI](https://github.com/robekenn/Abandoned-Mall-Restorer/actions/workflows/ci.yml/badge.svg)](https://github.com/robekenn/Abandoned-Mall-Restorer/actions/workflows/ci.yml)

A top-down 2D restoration game built with Python and pygame-ce, without a commercial game engine.

## First playable prototype

Restore the north arcade of Northgate Mall. Collect litter and dust into a one-item bag, then sell the load at either of two marked trash bins for $1 per item. A full bag blocks further cleanup until sold. The HUD shows capacity, sale value, floor cleanliness and the next business goal.

Reopen **Northgate Supplies** first for $10. Return to its marker and press E to open the upgrade shop. Buy larger bags (2/4/8/16/24/40 slots), better recycling contracts ($2/$4/$8/$15/$30 per item), and tools with longer reach and multi-item pickup. Each bench, lamp, planter, fountain and mosaic is purchased separately; there is no automatic scenery restoration or Tab scene cycling.

The 48 starting cleanup tasks cover every walkable floor tile. Clearing all of them makes the opening floor 100% clean and unlocks the next business after Supplies: Pages Bookshop ($100, $5 rent), Retro Replay ($250, $8 rent), Bean Street ($450, $12 rent), and The Tailor ($700, $16 rent). Open businesses pay rent every five seconds according to the playable arcade’s floor cleanliness: 0% pays nothing; above 0% and below 50% pays half; 50% through less than 100% pays normal rent; exactly 100% pays 1.5 times rent. Half-dollar payouts are retained. The HUD shows the current payout and multiplier. Supplies is an upgrade shop and does not pay rent.

After the first sweep and Supplies reopening, litter returns every **four seconds** (twice the previous rate), capped at twelve active piles. Reclean it, fill your bag and sell another load. Floor cleanliness recovers fully when all litter is collected; purchased fixtures and businesses remain upgraded.

The game uses crisp pixel sprites with a four-direction animated worker displayed at 48x72. Cleaning produces a brief tool stroke, dust, an item popup and quiet audio. Progress resets on close; saving, shoppers and additional playable wings remain future milestones. See [the upgrade and opening guide](docs/opening-arcade.md) for prices, controls and a review checklist.

## Run on Windows

Install Python 3.12 or newer. Download this repository or pull the latest changes, open a terminal in its folder, then run:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

## Run on macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

## Controls

- **WASD / Arrow keys:** move
- **E:** collect nearby litter, sell at a trash bin, reopen a business or enter Supplies
- **M:** toggle sound
- **Esc:** quit (or close the upgrade menu while shopping)

Inside Supplies, click an upgrade row to buy. Use **1/2/3** or **Tab** to select menu tabs, **Up/Down** to select a row, **Enter** to buy, and **Esc/E** to close. Gameplay pauses while the menu is open.

The camera follows the player. Walls, storefronts, trash bins, benches, and the fountain block movement. The window is resizable (minimum 800 x 600).

## Development

`game/` owns the loop, settings, and camera; `entities/` owns the player and litter; `mall/` owns the layout and storefronts; `ui/` owns the HUD. Remaining starter modules are placeholders for later systems.

Run the movement, collision, camera, shutdown, and restoration-loop checks:

```bash
python -m unittest discover -s tests -v
```

Tests use SDL's dummy display driver, so they also run without a desktop.

## CI and downloadable builds

GitHub Actions tests Windows, Linux and macOS with Python 3.12/3.13, then builds and smoke-tests standalone packages. Download development builds from the CI run artifacts. Pushing a `v` version tag prepares a draft release after all checks pass. See [CI and release guide](docs/ci-and-releases.md) for local packaging and publishing steps.
