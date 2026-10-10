"""Storage refactors must retain per-platform paths and safe failed writes."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from game.storage import atomic_write, save_directory


class StorageTests(unittest.TestCase):
    def test_platform_directories_keep_existing_player_saves(self):
        with patch("game.storage.Path.home", return_value=Path("/test-home")):
            cases = (
                ("win32", {"APPDATA": "/roaming"}, Path("/roaming/MallRestorer")),
                (
                    "darwin",
                    {},
                    Path("/test-home/Library/Application Support/MallRestorer"),
                ),
                ("linux", {"XDG_DATA_HOME": "/data"}, Path("/data/MallRestorer")),
                ("win32", {}, Path("/test-home/MallRestorer")),
                ("linux", {}, Path("/test-home/.local/share/MallRestorer")),
            )
            for platform, environment, expected in cases:
                with self.subTest(platform=platform, environment=environment):
                    with (
                        patch("game.storage.sys.platform", platform),
                        patch.dict(os.environ, environment, clear=True),
                    ):
                        self.assertEqual(save_directory(), expected)

    def test_atomic_write_creates_directory_and_replaces_existing_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "progress.json"
            atomic_write(path, b"original")
            atomic_write(path, b"replacement")
            self.assertEqual(path.read_bytes(), b"replacement")
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_failed_flush_or_replace_preserves_checkpoint_and_removes_temporary(self):
        for operation in ("os.fsync", "os.replace"):
            with (
                self.subTest(operation=operation),
                tempfile.TemporaryDirectory() as directory,
            ):
                path = Path(directory) / "progress.json"
                path.write_bytes(b"valid checkpoint")
                with patch(
                    "game.storage." + operation, side_effect=OSError("disk failure")
                ):
                    with self.assertRaises(OSError):
                        atomic_write(path, b"new checkpoint")
                self.assertEqual(path.read_bytes(), b"valid checkpoint")
                self.assertEqual(list(path.parent.iterdir()), [path])
