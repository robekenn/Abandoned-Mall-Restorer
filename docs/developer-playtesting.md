# Jump ahead while reviewing the game

Start from the repository folder with developer controls enabled:

```powershell
py main.py --dev
```

For a windowed preview:

```powershell
py main.py --dev --windowed
```

On macOS/Linux, use `python3` in place of `py` (or the Python executable in your virtual environment). Standalone builds accept the same flags, for example `MallRestorer.exe --dev`. Launch normally without `--dev` to play the regular progression.

After the opening screen, press **F3** to open the Developer playtest panel. Movement, rent, litter, owner timers and janitors pause while the panel is open.

| Key / button | Effect |
| --- | --- |
| 1 | Add $10,000 |
| 2 | Add $100,000 |
| 3 | Add $1,000,000 |
| 4 | Clean all litter in your current unlocked court |
| 5 | Finish the preceding court's sweep and reopen its stores, open the next court without charging, then move to its equipment shop |
| 6 | Prepare the next story chapter's care goals and move to its board; E / Enter there claims it normally |
| Up/Down + Enter | Select and apply an action |
| F3 / Esc / E | Close the panel |

Actions also work by clicking. You can add money repeatedly. Jumping follows North → East → Garden → Commons; the newly opened court begins dirty with closed businesses, so you can still test its progression. Jumping skips the introductory guide. Cleaning and jumps do not grant personal pickup/sale progress or extra cash. A DEV · F3 label identifies enabled sessions.

F3 opens the panel from the mall after other menus are closed. Normal launches ignore F3 and cannot use developer actions. These shortcuts do not change the regular economy. Developer progress saves to `developer.json`; normal launches use a separate `progress.json`. Continue and New game apply only to the current mode. See [saving and story](saving-and-lantern-story.md) for backup locations and a fast four-chapter review.

For automated rendering checks, run `python main.py --smoke-test` and `python main.py --smoke-test --dev`. Regression tests also cover developer input, pause behavior, cash grants, sequential jumps, normal-mode gating and the new shallow shop art.
