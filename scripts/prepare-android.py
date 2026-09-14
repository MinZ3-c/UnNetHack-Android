#!/usr/bin/env python3
"""Create a disposable Gradle build copy with native outputs and notices.

Added 2026-09-14. NetHack may be freely redistributed; see LICENSE.
This does not grant redistribution rights for unresolved third-party assets.
"""
import argparse
from pathlib import Path
import shutil

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--native-dir', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
repo = Path(__file__).resolve().parents[1]
out = args.output.resolve()
native = args.native_dir.resolve()
if out.exists() or out.is_relative_to(repo) or repo.is_relative_to(out):
    parser.error('--output must be a new directory outside the source tree.')
for name in ['libunnethack.so', 'nhdat']:
    if not (native / name).is_file():
        parser.error('Missing native build output: ' + name)
shutil.copytree(repo, out, ignore=shutil.ignore_patterns(
    '.git', '.gradle', 'build', '__pycache__', 'local.properties', '*.apk', '*.so', '*.o'))
app = out / 'sys/android/app'
(app / 'libs/arm64-v8a').mkdir(parents=True, exist_ok=True)
shutil.copy2(native / 'libunnethack.so', app / 'libs/arm64-v8a/libunnethack.so')
shutil.copy2(native / 'nhdat', app / 'assets/unnethackdir/nhdat')
notices = app / 'assets/licenses'
notices.mkdir(parents=True, exist_ok=True)
for name in ['LICENSE', 'NOTICE', 'dependencies.json']:
    shutil.copy2(repo / name, notices / name)
shutil.copytree(repo / 'THIRD_PARTY_LICENSES', notices / 'third-party', dirs_exist_ok=True)
print('Run Gradle in ' + str(out / 'sys/android'))
