# Automated checks and releases

## Layout

- `.github/workflows/ci.yml`: push-to-main, pull-request, manual, and reusable entry point. Runs dependency checks, Python syntax checks, regression tests, and headless launch/render checks on Windows, Ubuntu 22.04 and macOS 14 with Python 3.12 and 3.13. Packaging starts only when all tests pass.
- `.github/workflows/build.yml`: reusable native build matrix with Python 3.12. Builds and tests each executable before uploading archives and SHA-256 checksum files.
- `.github/workflows/release.yml`: version tags trigger the same CI and build checks, then attach the archives to a draft GitHub release. Only the draft-writing job has repository write permission.
- `scripts/build_release.py`: shared local/CI packaging implementation. Uses PyInstaller in folder mode, includes the data directory, smoke-tests from outside the repository, adds player instructions, and creates a platform/architecture-specific archive.
- `requirements.txt` and `requirements-build.txt`: pinned runtime and packaging dependencies. Update intentionally and let CI validate the change.

## Check or download a development build

Open the repository's **Actions** tab, select **CI**, then open a run. Green tests and package jobs mean the regression checks and packaged launch tests passed. Download the appropriate `game-...` artifact from the run summary. Extract the artifact, then extract the archive inside it. Keep the executable and `_internal` folder together. Python is not required on the player's computer.

Use **CI → Run workflow → main** to generate fresh test builds without making a commit. Artifacts expire after 14 days. Published release assets are the durable downloads.

Tests simulate keyboard events, movement/collisions, cleanup and income, scenery unlocks, pixel frames, walking/idle transitions and shutdown. Headless checks cannot verify the feel of controls or real display/audio drivers; play-test every release candidate on target hardware.

## Prepare a release

1. Wait for the chosen main commit's CI run to pass, download its build and play-test it.
2. From a clean, up-to-date local main checkout, create and push an unused version tag:

   ```bash
   git switch main
   git pull --ff-only origin main
   git tag -a v0.1.0 -m "First playable preview"
   git push origin v0.1.0
   ```

3. Wait for **Prepare release** to finish. It reruns tests and builds on the tagged commit. Any failed check prevents draft creation.
4. Open **Releases**, edit the prepared draft, review the generated notes and attached downloads, mark early versions as pre-releases, then click **Publish release** when ready.

No personal access token is required: GitHub supplies the workflow's short-lived token. Rerunning a failed release workflow can update an existing draft, but refuses to overwrite a published release. Use a new tag for a new public version; do not move published tags.

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
