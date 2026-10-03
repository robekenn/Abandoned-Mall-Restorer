# Northgate remembers

You visited Northgate as a child. Its winter lantern walk was a neighborhood tradition, made from borrowed chairs, homemade lanterns and people making room for one another. Returning with the keys begins a new chapter. Restoring the mall gives the community somewhere to belong again.

The story runs alongside normal business progression. Court gates keep their existing prices and prerequisites; story chapters are optional and do not require a perfectly clean mall every time litter returns. There are no story deadlines. Owner work completed before finding the community board counts toward its goals.

## Four chapters

Find the gold community board in each court and press E, then Enter to begin. Two small keepsakes appear in distant corners of that court; a neighbor near the west seating area holds the third. Exact positions and the held item vary between new games and persist in checkpoints. E recovers them without taking bag space. They remain readable in **J → Story → R**. Gold dots on the journal map mark community boards; outlined gold squares mark deliveries. Left/Right selects chapters.

| Court | Neighbor and chapter | What the court contributes | One-time thank-you |
| --- | --- | --- | --- |
| North | Mara — First lights | A reading circle; the photograph, fountain drawing and festival program | $1,000 |
| East | Remy — The sound of returning | A record afternoon; the dedication, cassette and neighbor's invitation | $5,000 |
| Garden | Fern — Things made by hand | A lantern workshop; the flower pattern, shared thread and mended lantern | $12,000 |
| Commons | Wren — A place for everyone | A neighborhood supper; the guest book, extended table plan and undated invitation | $30,000 |

Each chapter asks for three recovered keepsakes, that court's first sweep, six reopened businesses, two claimed owner requests and three purchased local fixtures. Any combination of initial projects or recurring favors counts. The Story journal shows the checklist; the HUD keeps a single current action. Return to the community board and confirm to complete a chapter. Claims pay once; repeating a conversation cannot pay again.

A completed chapter hangs four animated paper lanterns on each restored business’s front and invites a few real shoppers to gather along normal obstacle-safe paths. Brief confetti celebrates the opening. Gathering destinations return for thirty seconds every two and a half minutes of active play. Read a completed board to invite neighbors again without generating money. Visitor counts remain bounded.

After all four chapters, read the Commons board to begin the lantern walk and its epilogue. All courts gather; normal cleanup, store progression and owner favors remain playable. This is a moment of belonging, rather than a requirement to finish every purchase. The story's question is whether small acts can keep making room for others.

## Continue and checkpoints

Normal launches enable persistent progress. **Continue** appears on the opening screen when a readable checkpoint or backup exists. Enter continues; **New game / N** asks for a second confirmation before replacing progress. Opening and quitting without starting a game does not overwrite a checkpoint. The introduction fades into a continued world without restarting the saved guide.

- Autosave runs every thirty seconds of active play, after any rent due that frame.
- F5 saves manually, including while a journal or shop is open.
- Exiting saves; story encounters, business/court openings, equipment purchases, staff purchases and owner acceptance/reward claims also checkpoint.
- The Overview journal displays save status.
- Paused menus pause autosave, story, rent, litter, janitor and owner timers.

The checkpoint includes cash and fractional payouts, bag, equipment, fixtures, opened courts/stores, every litter/floor state, owner progression and cooldowns, active request work and greetings, janitor positions/upgrades/current work/earnings, rent and litter timers, tutorial stage, audio preference and story progress. Shoppers restart their ordinary visits on Continue; previously credited greeting identities cannot be credited again. There is no offline income or cooldown advancement.

| Platform | Save folder |
| --- | --- |
| Windows | `%APPDATA%\MallRestorer` |
| macOS | `~/Library/Application Support/MallRestorer` |
| Linux | `$XDG_DATA_HOME/MallRestorer`, or `~/.local/share/MallRestorer` |

`progress.json` is the normal slot. `--dev` uses only `developer.json`; shortcuts cannot overwrite the normal playthrough. Each has its own `.bak` recovery file. Checkpoints have a version and checksum, use an atomic file replacement, and retain the preceding verified checkpoint. Loading constructs and validates a replacement world before changing live state. Damaged primary files fall back to their backup; a failed save preserves the previous file. A recovered backup is retained on the first subsequent save. Unsupported versions or two unreadable files show a message instead of crashing.

For a backup copy, close the game and copy the save folder. Save format version 1 is introduced here; older builds did not write checkpoints. Source tests and smoke tests use temporary folders or disable persistence, so CI cannot alter real progress.

## Cleanup with helpers

Recurring litter still spawns once every four seconds globally, capped at twelve pieces per eligible court. Eligible courts now take turns, skipping full courts. Opening more courts no longer makes the first available pool consume every spawn.

For an active local litter-collection favor, the spawner prioritizes that court until it has enough pieces for the remaining goal. Its janitor leaves that many pieces for you and works on surplus litter. Protected work is canceled safely if a janitor had already selected it. Once collected or after the request goal is reached, ordinary cleaning resumes. Janitor sales remain 75% of current trash value and never count toward personal pickup/sale requests. Store prices, gate prices, equipment caps and three-minute owner pacing remain unchanged.

## Review the story quickly

Start with `python main.py --dev --windowed`. Choose a new developer game or Continue its separate slot. F3 → **6: Prepare next story chapter** completes that chapter's prerequisites, opens preceding courts in order, and moves you to the board. Close F3, press E and Enter to claim through the actual encounter. Repeat for all four chapters, then read the Commons board once more for the lantern walk. This shortcut does not auto-claim or bypass one-time reward checks.

Also try the regular opening, a partial owner request followed by exit/Continue, a working janitor followed by Continue, New game's second confirmation, and the Story journal's keepsake view at 800×600. Automated checks cover all twelve recurring favor modes, initial owner projects, mid-work janitors, save failures/backups, separate slots, paused/autosave/manual/exit paths, fair litter rotation and the four-chapter ending. Frozen-build smoke tests also finish every chapter and write/load a temporary checkpoint.
