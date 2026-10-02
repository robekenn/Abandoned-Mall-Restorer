"""Build on the target OS, test the frozen executable, then archive it."""
import hashlib
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NAME = 'MallRestorer'


def main():
    subprocess.run([
        sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
        '--onedir', '--name', NAME, '--distpath', str(ROOT / 'dist'),
        '--workpath', str(ROOT / 'build' / 'pyinstaller'),
        '--specpath', str(ROOT / 'build'),
        '--add-data', f'{ROOT / "data"}:data',
        str(ROOT / 'main.py'),
    ], cwd=ROOT, check=True)
    folder = ROOT / 'dist' / NAME
    executable = folder / (NAME + ('.exe' if sys.platform == 'win32' else ''))
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               PYGAME_HIDE_SUPPORT_PROMPT='1')
    # A different launch directory detects accidental source-tree dependencies.
    subprocess.run([str(executable), '--smoke-test'], cwd=ROOT.parent,
                   env=env, check=True, timeout=30)
    shutil.copy2(ROOT / 'packaging' / 'README.txt', folder / 'README.txt')
    destination = ROOT / 'dist' / 'releases'
    destination.mkdir(parents=True, exist_ok=True)
    archive_name = f'{NAME}-{platform.system().lower()}-{platform.machine().lower()}'
    archive_format = 'zip' if sys.platform == 'win32' else 'gztar'
    archive = Path(shutil.make_archive(str(destination / archive_name), archive_format,
                                      root_dir=folder.parent, base_dir=folder.name))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_name(archive.name + '.sha256').write_text(f'{digest}  {archive.name}\n')
    print(f'Built and verified: {archive.name}')


if __name__ == '__main__':
    main()
