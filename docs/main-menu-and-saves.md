# Main menu and multiple saves

The opening menu shows a restored concourse with warm glass, plants, lanterns
and gently walking visitors. Its animation is cosmetic: no game world, kitchen
request, rent, litter or janitor timer advances while the menu is open.

## Playing and managing malls

- Choose a save card, then **Continue selected** or **Enter/Space**. Cards show
  the save name, cash, reopened shops, opened areas and minutes of live play.
- Choose **New game** or **N**, type a name, and select **Start restoring**.
  A default name is supplied. New games always use an unused slot; your other
  malls are preserved. Names support text input and are limited to 28 characters.
- With no saves, **Start restoring** creates a first mall immediately.
- Select **Delete** or **D** to remove the chosen save and its recovery backup.
  Cancel is selected by default. Confirm with the Delete save button, or use
  Right/Tab then Enter. Deletion cannot be undone.
- Use Up/Down or the mouse wheel to select saves. Page Up/Down and the arrow
  buttons browse additional pages; there is no fixed slot limit.
- Settings and the first-steps guide toggle are available before starting. The
  name field accepts text without triggering gameplay shortcuts. Menu N/D and
  navigation keys remain fixed even when movement keys are rebound.

During play, choose **Esc → Main menu → Save and return to main menu**. The app
stays open, allowing another save or a fresh game. The current save is selected
on return. Startup selects the most recently saved available checkpoint.

If saving fails, the session stays open with a retry/stay choice. Returning
without saving requires an explicit separate action. Starting a new save also
reports write failures without replacing existing checkpoints. Exiting from the
main menu does not autosave stale session state into a previously selected slot.

## Existing saves and recovery

The current `progress.json` and `developer.json` files remain where they are and
appear as normal save cards. Older files without names appear as **Original
Northgate**. They are read without being moved or rewritten on startup. New
metadata and optional live-play time retain checkpoint envelope version 1;
older seating and kitchen migrations continue to apply.

Additional saves use random file IDs under `slots/normal/` or `slots/developer/`
inside the same per-user MallRestorer directory. Normal and developer libraries
are separate; settings and custom keys remain shared. Display names never form
file paths. Every save has its own `.bak` recovery checkpoint. A damaged primary
can recover only from that slot's backup, and a completely unreadable save stays
listed so it can be deleted deliberately.

A new game rebuilds world, player, upgrades, requests, story, visitors, janitors,
menus, timers and counters. Display, audio resources, preferences and the app
loop remain active. Continue restores the selected world, including courtyard
location, independent kitchen waits and partial janitor work. There are no
wall-clock earnings; displayed minutes count live simulation time only. Menus,
cooking and paused tutorial explanations do not add to that counter.

## Review checks

Create two named games, change cash/progression in one, return to the menu and
switch between them. Verify neither inherits the other's state. Repeat after
entering the courtyard. Cancel deletion, then delete one save and verify the
other still continues. Test settings, custom keys, mouse and keyboard navigation,
long names, and multiple pages at 800 × 600 and a larger window.

Regression checks cover real menu input, legacy saves, fresh-session reset,
independent files/backups, corruption, failed creation/deletion/return, deliberate
discard, names, paging and paused timers. Source and frozen smoke checks create,
switch and delete temporary saves without touching player progress.
