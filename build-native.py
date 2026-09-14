"""Build the Android shared library inside WSL, using the configured source tree.

Usage: python3 build-native.py /var/tmp/unnethack-build.XXXXXX
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

build = Path(sys.argv[1]).resolve()
source = build / 'target'
tools = build / 'android-ndk-r28c/toolchains/llvm/prebuilt/linux-x86_64/bin'
lua = build / 'lua-5.4.8/src'
objects = build / 'objects-arm64'
objects.mkdir(exist_ok=True)

makefile = (source / 'sys/autoconf/Makefile.src').read_text()
hobj = re.search(r'^HOBJ = (.*?)(?=\n#)', makefile, re.M | re.S).group(1)
names = list(dict.fromkeys(['monst', 'objects', 'alloc', 'rip'] + re.findall(r'\b([a-z_0-9]+)\.o', hobj)))
sources = [source / 'src' / (name + '.c') for name in names]
sources += [source / 'sys/android' / (name + '.c') for name in ['androidmain', 'androidunix', 'androidsave', 'winandroid']]
sources += [source / 'sys/share' / (name + '.c') for name in ['ioctl', 'unixtty', 'posixregex']]
sources += [source / 'sys/unix/unixres.c', source / 'util/recover.c']
flags = ['--target=aarch64-linux-android23', '-std=gnu11', '-O1', '-g', '-fPIC',
         '-DANDROID', '-DAUTOCONF', '-DNO_MAIN', '-fno-common',
         '-I' + str(source / 'include'), '-I' + str(lua), '-Werror=implicit-function-declaration']
header_hash = hashlib.sha256()
for header in sorted((source / 'include').glob('*.h')):
    header_hash.update(header.read_bytes())

def compile_one(path):
    if not path.exists():
        return str(path), 'Source is missing', None
    obj = objects / (path.stem + '.o')
    stamp = obj.with_suffix('.sha256')
    digest = hashlib.sha256(path.read_bytes() + header_hash.digest() + repr(flags).encode()).hexdigest()
    if obj.exists() and stamp.exists() and stamp.read_text() == digest:
        return str(path), '', obj
    result = subprocess.run([str(tools / 'clang'), *flags, '-c', str(path), '-o', str(obj)],
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (objects / (path.stem + '.log')).write_text(result.stdout)
    if result.returncode:
        return str(path), result.stdout, None
    stamp.write_text(digest)
    return str(path), '', obj

with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(compile_one, sources))
errors = [(path, error) for path, error, obj in results if obj is None]
(build / 'native-errors.json').write_text(json.dumps(errors, indent=2))
print(f'Compiled {len(results) - len(errors)}/{len(results)} source files.', flush=True)
for path, error in errors:
    print('\n' + path + '\n' + error, flush=True)
if errors:
    raise SystemExit(1)
library = build / 'libunnethack.so'
command = [str(tools / 'clang'), '--target=aarch64-linux-android23', '-shared',
           '-Wl,--no-undefined', '-Wl,-z,max-page-size=16384', '-Wl,-soname,libunnethack.so',
           '-o', str(library), *[str(obj) for _, _, obj in results], str(lua / 'liblua.a'), '-llog', '-ldl', '-lm']
result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(build / 'native-link.log').write_text(result.stdout)
print(result.stdout)
if result.returncode:
    raise SystemExit(result.returncode)
print(f'Linked {library} ({library.stat().st_size} bytes).')
