"""Named checkpoints without an index file or changes to legacy save paths."""

from dataclasses import dataclass
from pathlib import Path
import re
from uuid import uuid4

from game.storage import save_directory
from systems.saves import SaveStore, number


def save_name(value):
    return (
        " ".join("".join(c for c in str(value) if c.isprintable()).split())[:28]
        or "My Northgate"
    )


@dataclass(frozen=True)
class SaveSlot:
    identifier: str | None
    name: str
    cash: float = 0
    businesses: int = 0
    courts: int = 1
    seconds: float = 0
    updated: float = 0
    playable: bool = False
    recovered: bool = False


class SaveSlots:
    def __init__(self, directory=None, developer=False, enabled=False):
        self.directory = Path(directory or save_directory())
        self.developer = developer
        self.enabled = enabled
        self.status = ""

    def store(self, identifier=None, name="My Northgate"):
        return SaveStore(
            self.directory,
            self.developer,
            self.enabled,
            slot=identifier,
            name=save_name(name),
        )

    def entries(self):
        if not self.enabled:
            return []
        self.status = ""
        identifiers = set()
        legacy = self.store()
        try:
            if legacy.path.exists() or legacy.backup.exists():
                identifiers.add(None)
        except OSError:
            self.status = "Could not list the original save. Check that your save folder is accessible."
        directory = (
            self.directory / "slots" / ("developer" if self.developer else "normal")
        )
        try:
            for path in directory.iterdir() if directory.exists() else ():
                if path.suffix in (".json", ".bak") and re.fullmatch(
                    r"[0-9a-f]{32}", path.stem
                ):
                    identifiers.add(path.stem)
        except OSError:
            self.status = "Some saves could not be listed. Check that your save folder is accessible."
        entries = []
        for identifier in identifiers:
            store = self.store(identifier)
            fallback = "Original Northgate" if identifier is None else "Northgate save"
            for path in (store.path, store.backup):
                try:
                    envelope = store.read_envelope(path)
                    data = envelope["data"]
                    cash = data["cash"]
                    stores = data["stores"]
                    courtyard = data.get("courtyard", {})
                    businesses = sum(bool(row[0]) for row in stores.values())
                    businesses += sum(
                        bool(opened) for opened in courtyard.get("stores", [])
                    )
                    courts = (
                        1 + len(data["unlocked"]) + int(bool(courtyard.get("unlocked")))
                    )
                    seconds = data.get("play_seconds", 0)
                    number(cash)
                    number(seconds)
                    entries.append(
                        SaveSlot(
                            identifier,
                            save_name(envelope.get("name", fallback)),
                            cash,
                            businesses,
                            courts,
                            seconds,
                            path.stat().st_mtime,
                            True,
                            path == store.backup,
                        )
                    )
                    break
                except (
                    OSError,
                    ValueError,
                    KeyError,
                    TypeError,
                    IndexError,
                    AttributeError,
                ):
                    continue
            else:
                entries.append(SaveSlot(identifier, fallback))
        return sorted(
            entries, key=lambda slot: (-slot.updated, slot.name, slot.identifier or "")
        )

    def allocate(self, name):
        """Choose an unused destination; creating a new game never replaces a save."""
        if not self.enabled:
            return self.store(name=name)
        legacy = self.store()
        if not legacy.path.exists() and not legacy.backup.exists():
            return self.store(name=name)
        while True:
            store = self.store(uuid4().hex, name)
            if not store.path.exists() and not store.backup.exists():
                return store

    def delete(self, identifier):
        if not self.enabled:
            return False
        store = self.store(identifier)
        try:
            # Keep the latest primary if a filesystem error interrupts deletion.
            store.backup.unlink(missing_ok=True)
            store.path.unlink(missing_ok=True)
        except OSError:
            self.status = (
                "Could not delete this save. It is still listed; please try again."
            )
            return False
        self.status = "Save deleted."
        return True
