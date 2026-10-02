# Abandoned Mall Restorer

[![CI](https://github.com/robekenn/Abandoned-Mall-Restorer/actions/workflows/ci.yml/badge.svg)](https://github.com/robekenn/Abandoned-Mall-Restorer/actions/workflows/ci.yml)

A top-down 2D restoration game built with Python and pygame-ce, without a commercial game engine.

## First playable prototype

Explore Northgate Mall, collect litter and sweep dirt for $10 each, then spend $100 at the gold marker outside Pages Bookshop. The boarded storefront becomes an open shop and earns $5 every five seconds. There are 15 cleanup spots, three other shuttered storefronts, benches, and a fountain in the north arcade. A larger mall surrounds this first corner, with closed galleries and distant shops visible beyond grilles.

The game now uses crisp retro pixel sprites (24x24 props, a 16x24 worker, and 48x40 storefronts): dirty/restored bookstores and cafés, litter, dirt, benches, fountains, planters, lamps, the player, and a mosaic. Cleaning five spots unlocks greenery and lamps; ten unlocks the mosaic courtyard. The small worker has four-direction walking animations and returns to idle when stopped. Cleanup adds a brief tool stroke, dust particles, a reward popup, quiet sounds and a locally brighter floor patch. A mall directory shows how this corner fits into the larger building. Press Tab to cycle scenery. Benches recover after five spots and the fountain is restored when all fifteen are clean. Progress resets when you close the game; saving, tenants, shoppers, audio, and additional wings are future milestones.

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
- **E:** interact with the closest nearby cleanup spot or shop marker
- **Tab:** cycle unlocked scenery
- **M:** toggle sound
- **Esc:** quit

The camera follows the player. Walls, storefronts, benches, and the fountain block movement. The window is resizable (minimum 800 x 600).

## Development

`game/` owns the loop, settings, and camera; `entities/` owns the player and litter; `mall/` owns the layout and storefronts; `ui/` owns the HUD. Remaining starter modules are placeholders for later systems.

Run the movement, collision, camera, shutdown, and restoration-loop checks:

```bash
python -m unittest discover -s tests -v
```

Tests use SDL's dummy display driver, so they also run without a desktop.

## CI and downloadable builds

GitHub Actions tests Windows, Linux and macOS with Python 3.12/3.13, then builds and smoke-tests standalone packages. Download development builds from the CI run artifacts. Pushing a `v` version tag prepares a draft release after all checks pass. See [CI and release guide](docs/ci-and-releases.md) for local packaging and publishing steps.

See [the opening arcade guide](docs/opening-arcade.md) for the first-five-minutes design and review checklist.
