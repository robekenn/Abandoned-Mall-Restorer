# Automated checks and releases

## Layout

- `.github/workflows/ci.yml`: push-to-main, pull-request, manual, and reusable entry point. Runs dependency checks, Python syntax checks, regression tests, and headless launch/render checks on Windows, Ubuntu 22.04 and macOS 14 with Python 3.12 and 3.13. Packaging starts only when all tests pass.
- `.github/workflows/build.yml`: reusable native build matrix with Python 3.12. Builds and tests each executable before uploading archives and SHA-256 checksum files.
- `.github/workflows/release.yml`: merging a VERSION change into main runs CI and packages, verifies all three archives and their checksums, then publishes a playable preview. Version-tag pushes retain the manual draft-release path. Only the release-writing job has repository write permission.
- `scripts/build_release.py`: shared local/CI packaging implementation. Uses PyInstaller in folder mode, includes the data directory, smoke-tests from outside the repository, adds player instructions, and creates a platform/architecture-specific archive.
- `requirements.txt` and `requirements-build.txt`: pinned runtime and packaging dependencies. Update intentionally and let CI validate the change.

## Check or download a development build

Open the repository's **Actions** tab, select **CI**, then open a run. Green tests and package jobs mean the regression checks and packaged launch tests passed. Download the appropriate `game-...` artifact from the run summary. Extract the artifact, then extract the archive inside it. Keep the executable and `_internal` folder together. Python is not required on the player's computer.

Use **CI → Run workflow → main** to generate fresh test builds without making a commit. Artifacts expire after 14 days. Published release assets are the durable downloads.

Tests simulate keyboard events, movement/collisions, cleanup and income, scenery unlocks, pixel frames, walking/idle transitions and shutdown. Headless checks cannot verify the feel of controls or real display/audio drivers; play-test every release candidate on target hardware.

## First playable release

PR #15 adds VERSION `0.1.0` and `docs/releases/v0.1.0.md`. Merging the PR changes VERSION on main and triggers **Prepare release**. After all six test jobs and three package jobs pass, the workflow verifies the three archives and SHA-256 checksums, creates tag `v0.1.0` at the tested merge commit, uploads the downloads into a draft, and publishes it as **v0.1.0 — First Playable Preview** with the pre-release flag.

Checksum files are written with LF on every platform; release verification also normalizes CRLF files from older Windows packages. Updating the release workflow on main or using **Prepare release → Run workflow → main** retries an unpublished version with the corrected workflow.

The tag created by GitHub's workflow token does not start a second workflow run. Nothing publishes from the PR branch. A failed check or missing platform archive prevents publication. The workflow refuses to modify a published release or reuse a tag pointing at another commit. If a failed upload leaves a draft, rerun the failed workflow on the same commit to finish it.

For future preview releases, update VERSION and add matching `docs/releases/vX.Y.Z.md` notes in a PR. The current preview title is intended for the first release and should be revised when planning the second. Published tags must never be moved. A manually pushed version tag still produces a draft for human review, following the existing procedure.

No personal access token is required; the release job uses GitHub's short-lived token with contents-write permission.

Packages: Windows x64 ZIP, Linux x64 tar.gz (Ubuntu 22.04 or compatible desktop), and macOS arm64 tar.gz. macOS and Windows executables are unsigned; signing/notarization and an Intel Mac build are separate future work. The Windows build uses a console so startup errors remain visible during this prototype phase.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python main.py --smoke-test
python -m pip install -r requirements-build.txt
python scripts/build_release.py
```

Build on the target operating system. Archives appear in `dist/releases/`. `--smoke-test` uses SDL dummy drivers, renders the dirty and restored states, and exits without starting the interactive game loop.

## Repository settings

Workflows must be enabled under **Settings → Actions → General**. CI reports failures; it does not itself block direct pushes to main. To enforce green checks before merging, configure a main-branch ruleset with pull requests and required CI test/build checks after the first successful run. We have not changed branch rules because the project currently allows direct pushes to main.
