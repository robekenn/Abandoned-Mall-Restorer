"""The Windows checksum must be readable by the Linux release job."""
from pathlib import Path
import hashlib
import tempfile
import unittest
from scripts.build_release import write_checksum


class ReleaseChecksumTests(unittest.TestCase):
    def test_checksum_uses_lf_and_names_the_archive_on_every_platform(self):
        with tempfile.TemporaryDirectory() as directory:
            archive=Path(directory)/'MallRestorer-windows-amd64.zip'
            archive.write_bytes(b'first playable archive')
            checksum=write_checksum(archive)
            row=checksum.read_bytes()
            self.assertTrue(row.endswith(b'\n'))
            self.assertNotIn(b'\r',row)
            digest,name=row.decode('utf-8').strip().split('  ',1)
            self.assertEqual(name,archive.name)
            self.assertEqual(digest,hashlib.sha256(archive.read_bytes()).hexdigest())
