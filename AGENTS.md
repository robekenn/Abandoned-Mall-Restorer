# Working on Abandoned Mall Restorer

This file applies to the whole repository. Read it before changing code. The
user's current instructions take precedence; check for any more specific
`AGENTS.md` in a directory you edit.

## Project and workflow

- A Python 3.12+ desktop game using **pygame-ce**, not the original `pygame`
  package. CI covers Python 3.12 and 3.13 on Windows, Linux and macOS.
- Start from current `origin/main` for new work. For an existing PR, update its
  actual head branch. Inspect `git status` first and preserve unrelated work.
- Keep changes focused and explain any visible behavior changes. Refactoring
  should preserve playtester-approved layouts, balance and save compatibility.
- Open or update a PR when requested, summarize validation, and leave merging
  and release approval to the user unless explicitly authorized otherwise.
- Do not change `VERSION`, publish releases, move tags, or change repository
  rules as incidental housekeeping. See `docs/ci-and-releases.md` for releases.
- Never commit checkpoints, player settings, generated packages, caches,
  virtual environments or credentials.

## Where code belongs

| Location | Responsibility |
| --- | --- |
| `main.py` | Arguments, headless setup and launching the game |
| `game/game.py` | Frame loop, input routing, scene transitions and shared simulation |
| `game/storage.py` | Per-user directories and atomic file writes; standard library only |
| `game/preferences.py` | Settings and custom keys, separate from playthrough checkpoints |
| `game/art.py`, `game/patio_art.py` | Procedural pixel sprites and their cached rendering |
| `game/audio.py`, `game/music.py` | Synthesized effects and soundtrack, with audio fallback |
| `game/smoke.py` | Staged integration checks for source and frozen launches |
| `systems/save_slots.py` | Named save catalog, allocation and deletion |
| `ui/welcome.py`, `ui/menu_scene.py` | Main-menu controls and cosmetic restored concourse |
| `entities/` | Player, trash and bins |
| `mall/` | Layout, collision, stores, seating and courtyard scene |
| `systems/` | Progression, requests, visitors, janitors, economy and saves |
| `ui/` | HUD, menus and journal; reuse `ui/theme.py` |
| `tests/` | `unittest` regression tests with SDL dummy drivers |
| `scripts/build_release.py` | Native PyInstaller build, frozen smoke tests and checksums |
| `docs/` | Gameplay, architecture, playtest and release guidance |

Current layouts, recipes and upgrades are defined in Python. The empty JSON
files in `data/` are legacy scaffolding, not live configuration. Most art and
audio are generated locally; do not assume `assets/` files are loaded.

## Runtime rules to preserve

- `Game.update()` owns pause decisions. Register new modal menus in
  `Game.modal_menus`; use `Game.world_paused` to guard world interaction.
  Preserve input priority in `handle_event()` and add the menu's draw route.
- Settings, pause, the journal and other menus freeze simulation. The tutorial
  pauses during explanations, then allows practice. A cooking round advances
  its own timer while the mall stays paused; settings and pause also freeze it.
- Both scenes call `Game.update_shared_worlds()` exactly once per live frame.
  Visitors, litter and janitors must keep working in opened offscreen maps.
  Do not create the courtyard world merely to tick a locked area.
- Both scenes use `Game.update_income_and_autosave()`. Rent pays every five
  seconds; autosaves follow thirty seconds of live play. Scene transitions
  preserve the timer phase. There are no wall-clock or offline earnings.
- The HUD's cleanliness is weighted by floor tiles across all unlocked areas.
  Local rent and visitor calculations still use their own world's cleanliness.
- Each of the seven kitchens has its **own** random 180–600 second cooldown.
  Closed kitchens do not tick. Multiple requests can be ready together.
  Accepting one resets only that kitchen; ready requests and waits save.
- Recurring litter starts only after the area's first sweep and shop rule is
  met. Keep local caps, fair court rotation, revision checks and player buffers.
  Each map uses its own traffic: busy 2s, steady 4s, quiet 8s.
- Visitors travel from the front entrance through the mall and courtyard;
  preserve their identity and carried food when crossing maps. Courtyard
  customers queue at counters instead of entering restaurant interiors.
- Keep indoor connecting paths unobstructed. All four courts share deliberate
  seating arrangements; benches start broken, with tables and seats purchased
  separately. The courtyard uses a walk-through wall opening and short signs.

## Checkpoints and storage

- `systems/saves.py` owns snapshot validation and migrations. Validate a
  replacement world completely before assigning it to the live `Game`.
- Preserve the envelope version/checksum, recovery backup, atomic replacement,
  original `progress.json` and `developer.json` slots, and existing OS paths.
  Additional UUID slots live in `slots/normal/` or `slots/developer/`, with
  their own backups. `settings.json` stays shared by the two play modes.
- Creating a new game allocates an unused slot and resets every session system.
  Never replace another save as part of creation. Main-menu returns save before
  leaving; failure keeps the session open unless the player explicitly discards.
  Deletion requires confirmation and removes only the selected save and backup.
  Menu animation is cosmetic and must never advance world timers.
- Keep existing saves loadable, including older seating layouts, missing
  optional features and the old shared kitchen timer. Never renumber trash
  IDs or change serialized fixture/store keys without a migration.
- If a write fails, retain the last checkpoint, remove temporary files, and
  keep save failure visible to the player. Do not silently reset progress.
- Tests should default to persistence disabled. Save tests must use a
  `TemporaryDirectory` or an explicit test `save_dir`; never touch real saves.
- No runtime resource should depend on the launch working directory. Frozen
  builds must work from outside the source tree.

## Implementation and validation

- Use existing systems and UI conventions; avoid adding frameworks, dependency
  churn or placeholder modules for unimplemented features.
- Prefer named functions and readable blocks in new code. Don't reformat the
  entire repository while fixing a feature. Ruff's configured checks enforce
  correctness without demanding a rewrite of existing compact code.
- Pin runtime, developer and build dependencies in their corresponding
  requirements files. Developer tooling must not enter runtime requirements.
- Add meaningful regressions for behavioral fixes, persistence changes and
  refactors across systems. Exercise actual input and state transitions when
  relevant; avoid tests that merely copy implementation details.
- UI changes must render at the minimum **800 × 600** window, in both scenes
  if shared. Check HUD, journal, custom-key hints, collision and depth order.
- Run focused tests during development, then the complete checks below before
  submitting. Use the active venv's `python` (`py` on Windows if appropriate).

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
python -m ruff check .
python -m compileall -q game entities mall systems ui scripts main.py tests
python -m unittest discover -s tests -v
python main.py --smoke-test
python main.py --smoke-test --dev
```

For launch, import, storage or packaging changes, also run:

```bash
python -m pip install -r requirements-build.txt
python scripts/build_release.py
```

Build on the target OS. CI verifies all six OS/Python test combinations and
three native packages. Inspect failures for the PR's **current commit** and
report actual outcomes; a previous green run doesn't validate new changes.
Headless checks do not replace manual playtesting of controls and real drivers.

See `CONTRIBUTING.md` for setup and `docs/architecture.md` for the frame lifecycle.
