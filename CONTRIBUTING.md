# Contributing

Use Python 3.12 or 3.13 and read [AGENTS.md](AGENTS.md) and the
[architecture guide](docs/architecture.md) before changing a shared system.

## Local setup

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python main.py --dev --windowed
```

On Windows PowerShell, activation isn't required:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe main.py --dev --windowed
```

The commands below assume `python` is your venv interpreter. On Windows,
substitute `.venv\Scripts\python.exe` if the environment isn't activated.
F3 provides developer playtesting shortcuts. Developer launches use a separate
checkpoint slot; settings and keybindings remain shared. See
[developer playtesting](docs/developer-playtesting.md).

## Before opening a PR

Start new work on a branch from updated `origin/main`. Keep the PR focused and
describe the user-visible outcome, relevant implementation choices and checks.
Preserve existing checkpoints and avoid unrelated balance or layout changes.

```bash
python -m pip check
python -m ruff check .
python -m compileall -q game entities mall systems ui scripts main.py tests
python -m unittest discover -s tests -v
python main.py --smoke-test
python main.py --smoke-test --dev
```

For a focused iteration, run a module such as
`python -m unittest tests.test_cooking -v`. Tests configure SDL dummy drivers
and use temporary directories for persistence. Smoke tests exercise all courts,
menus, story, helpers, kitchens and real checkpoint roundtrips without touching
the player's saves. Gameplay normally runs at up to 60 FPS with frame time
clamped to avoid large simulation jumps.

Ruff checks imports, undefined names and basic correctness. Formatting isn't a
global gate; use readable code and match nearby conventions. Format only new
or intentionally refactored files. Test visual changes at 800 × 600 and a larger
window, and playtest interactions in both maps when shared.

## Packaging and releases

For launch, import, storage or packaging changes:

```bash
python -m pip install -r requirements-build.txt
python scripts/build_release.py
```

The builder runs frozen normal and developer smoke checks from outside the
repository, then produces an archive and SHA-256 file in `dist/releases/`.
Keep the executable with its `_internal` folder. CI repeats tests on Windows,
Linux and macOS and builds a native package on each.

Runtime dependencies belong in `requirements.txt`; development tools belong in
`requirements-dev.txt`; packaging tools belong in `requirements-build.txt`.
Keep pins intentional. Package building doesn't need the developer tools.

Release publication is a separate change: update `VERSION` and add matching
release notes only when requested. Follow [CI and releases](docs/ci-and-releases.md)
and leave PRs for maintainer review.
