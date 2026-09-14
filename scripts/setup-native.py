#!/usr/bin/env python3
"""Prepare and build host tools, game data, Lua and Android code on Linux/WSL.

Added 2026-09-14. NetHack may be freely redistributed; see LICENSE.
Uses a NEW external directory; never deletes or reuses an old build tree.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--build-root', required=True, type=Path)
parser.add_argument('--ndk', required=True, type=Path)
parser.add_argument('--lua-archive', required=True, type=Path)
parser.add_argument('--jobs', type=int, default=4)
args = parser.parse_args()
repo = Path(__file__).resolve().parents[1]
build = args.build_root.resolve()
ndk = args.ndk.resolve()
archive = args.lua_archive.resolve()
metadata = json.loads((repo / 'dependencies.json').read_text())
if os.name != 'posix':
    parser.error('Run inside Linux or WSL, not Windows Python.')
if build.exists() or build.is_relative_to(repo) or repo.is_relative_to(build):
    parser.error('--build-root must be a new directory outside the source tree.')
if args.jobs < 1:
    parser.error('--jobs must be positive.')
if hashlib.sha256(archive.read_bytes()).hexdigest() != metadata['lua']['sha256']:
    parser.error('Lua archive checksum mismatch.')
if 'Pkg.Revision = ' + metadata['ndk'] not in (ndk / 'source.properties').read_text():
    parser.error('Expected the pinned NDK version from dependencies.json.')
toolchain = ndk / 'toolchains/llvm/prebuilt/linux-x86_64/bin'
cc = toolchain / 'aarch64-linux-android23-clang'
if not cc.is_file():
    parser.error('Expected the Linux x86_64 NDK toolchain.')
for command in ['make', 'gcc', 'bison', 'flex', 'lua5.4', 'pkg-config']:
    if not shutil.which(command):
        parser.error('Missing host dependency: ' + command)
build.mkdir(parents=True)
(build / 'android-ndk-r28c').symlink_to(ndk, target_is_directory=True)

def run(command, cwd, env=None):
    print('+ ' + ' '.join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=cwd, env=env, check=True)

def ignore(directory, names):
    excluded = {'.git', '.gradle', 'build', '__pycache__', 'local.properties',
                'forkfront', 'Makefile', 'config.log', 'config.status',
                'autoconf.h', 'autoconf_paths.h'}
    return [name for name in names if name in excluded
            or name.endswith(('.o', '.so', '.exe', '.apk', '.class'))
            or (Path(directory).name == 'include' and name == 'win32api.h')]

# Build copies also include all maintained Android code; the host configuration
# does not define ANDROID. All generated files stay outside the source export.
def copy_native_file(src, dst):
    result = shutil.copy2(src, dst)
    # Native scripts, configure inputs and roff sources need Unix line endings.
    data = Path(dst).read_bytes()
    if b'\0' not in data and b'\r\n' in data:
        try:
            data.decode('utf-8')
        except UnicodeDecodeError:
            pass
        else:
            Path(dst).write_bytes(data.replace(b'\r\n', b'\n'))
    return result

for name in ['host', 'target']:
    shutil.copytree(repo, build / name, ignore=ignore, copy_function=copy_native_file)
with tarfile.open(archive) as tar:
    tar.extractall(build, filter='data')
common = ['sh', 'configure', '--enable-dummy-graphics', '--disable-tty-graphics',
          '--disable-file-areas', '--with-compression=no', '--disable-status-hilites',
          '--with-owner=' + str(os.getuid()), '--with-group=' + str(os.getgid())]
host = build / 'host'
run(common + ['CFLAGS=-O2 -std=gnu11 -DANDROID_HOST_TOOLS',
              'CPPFLAGS=-DANDROID_HOST_TOOLS'], host)
run(['make', 'include/autoconf_paths.h'], host)
run(['make', '-C', 'util', 'makedefs', '../include/pm.h', '../include/onames.h'], host)
run(['make', '-C', 'src', '../include/date.h'], host)
# The legacy top-level targets can race while rebuilding shared generators.
run(['make', '-j1', 'all'], host)
lua = build / 'lua-5.4.8/src'
run(['make', '-j' + str(args.jobs), 'a', 'CC=' + str(cc),
     'AR=' + str(toolchain / 'llvm-ar') + ' rcu',
     'RANLIB=' + str(toolchain / 'llvm-ranlib'), 'MYCFLAGS=-fPIC -DLUA_USE_POSIX'], lua)
target = build / 'target'
env = dict(os.environ, with_luajit='no')
run(common + ['--host=aarch64-linux-android', 'CC=' + str(cc),
              'CFLAGS=-O1 -g -std=gnu11 -fPIC', 'CPPFLAGS=-DANDROID',
              'LUA=lua5.4', 'LUA_INCLUDE=-I' + str(lua),
              'LUA_LIB=' + str(lua / 'liblua.a') + ' -lm'], target, env)
run(['make', 'include/autoconf_paths.h'], target)
for header in ['pm.h', 'onames.h', 'date.h', 'vis_tab.h']:
    shutil.copy2(host / 'include' / header, target / 'include' / header)
for source in ['monstr.c', 'vis_tab.c', 'tile.c']:
    shutil.copy2(host / 'src' / source, target / 'src' / source)
run(['python3', repo / 'build-native.py', build], repo)
shutil.copy2(host / 'dat/nhdat', build / 'nhdat')
print('Native library and game data are in ' + str(build), flush=True)
