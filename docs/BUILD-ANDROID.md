# Android build

The Android host generators use `ANDROID_HOST_TOOLS` so their MAIL setting
matches the Android runtime. The native build checks generated object/monster
counts and compares all table entries with `scripts/check-android-tables.py`.
Do not copy headers or nhdat from a generic Linux build. Native build copies
normalize UTF-8 text line endings from Windows checkouts; the legacy host make
runs serially because its shared generators can race under parallel make.

Regression tests: `tests/android/test-save-preservation.py` runs on Linux/WSL
with gcc without touching real saves. `tests/android/gold-name.c` can be built
with the NDK, AUTOCONF and ANDROID defines, and the target include and Lua
include directories; link with `-ldl` and run on Android with the built
`libunnethack.so` path. It checks the actual library's singular/plural gold
names without starting a game or opening save files.

The reorganized source was built from scratch on 2026-09-14: host utilities,
nhdat, ARM64 Lua, the native library and a debug APK. Build outputs remain
outside this source tree. Download caches and the already installed NDK/SDK
were reused; no prior object files or generated game data were reused.

## Requirements

- Linux x86_64 or WSL2 for native compilation; Python 3.12 or newer.
- GCC, make, bison, flex, pkg-config, lua5.4 and liblua5.4-dev.
  On the tested Ubuntu 26.04 host these are available via apt; also install
  build-essential, unzip, zip and libncurses-dev.
- Linux NDK r28c (28.2.13676358).
- Official Lua 5.4.8 source archive, checksum in dependencies.json.
- For Gradle: JDK 21, Android SDK platform 36 and Build Tools 36.0.0.
  Tested JDK: JetBrains Runtime 21.0.10+-14961533-b1163.108.
- Gradle 9.5.1 wrapper and AGP 9.2.1, pinned in the checked-in configuration.

## Native build (Linux/WSL)

Obtain android-ndk-r28c-linux.zip from the URL in dependencies.json and extract
it outside this repository. Obtain lua-5.4.8.tar.gz from the recorded official
Lua URL. The NDK archive SHA-1 recorded from Google's repository metadata is
also in dependencies.json; the script checks the installed NDK revision and
verifies the Lua archive SHA-256 before extraction.

Set paths for your machine, then run from the repository root:

```sh
python3 scripts/setup-native.py \
  --build-root /var/tmp/unnethack-clean-build \
  --ndk /opt/android-ndk-r28c \
  --lua-archive /path/to/lua-5.4.8.tar.gz
```

The build root must not already exist. The script creates independent host
and target copies of this source, configures the host with dummy graphics,
no FILE_AREAS, no external compression and no STATUS_HILITES, builds host
utilities and data, then builds Lua as Android ARM64 PIC code and configures
the Android target. ANDROID selects the Android window bridge and classic
STATUS_COLORS. with_luajit=no avoids configure selecting host Lua headers for
the target. Generated headers and sources from the host are transferred to
the target before build-native.py compiles and links it.

Outputs: libunnethack.so and nhdat in the external build root. The script
replaces the original machine-specific work/wsl-host.sh and
work/wsl-native-setup.sh; those original files are not required.

## APK build

Create a new external Gradle copy:

```sh
python3 scripts/prepare-android.py \
  --native-dir /var/tmp/unnethack-clean-build \
  --output /var/tmp/unnethack-gradle-build
export JAVA_HOME=/path/to/jdk-21
export ANDROID_HOME=/path/to/android-sdk
cd /var/tmp/unnethack-gradle-build/sys/android
sh gradlew --no-daemon :app:assembleDebug
```

On Windows use python and gradlew.bat. Copy the two native outputs from WSL
to a Windows directory and give that directory to --native-dir. Set JAVA_HOME
and ANDROID_HOME in PowerShell. If the default Android user directory is
not writable, set ANDROID_USER_HOME to a writable directory outside the
repository; that is where the local debug keystore will be created. Gradle
dependencies may require network access.

prepare-android.py stages the native library, nhdat, LICENSE, NOTICE,
dependencies.json and THIRD_PARTY_LICENSES inside the disposable app assets.
Do not bypass it with a bare source-tree Gradle build: the source export
intentionally contains no generated library or nhdat.

APK output: sys/android/app/build/outputs/apk/debug/app-debug.apk in the
external copy. It is debug-signed by the local Android debug key, not unsigned.
No public-release signing identity is created or included.

## Verification

From the external copy, run javap -s -private on
forkfront/lib/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes/
com/tbd/forkfront/NetHackIO.class and save its output outside the source tree.
Run python check-jni.py with that text file: all 26 callbacks and the native
entry point must match. Use apksigner verify on the APK and inspect its ZIP
entries for lib/arm64-v8a/libunnethack.so, assets/unnethackdir/nhdat and the
staged assets/licenses files.

A successful fresh build is not evidence of byte-for-byte deterministic
binaries or resolved third-party rights. Device validation of this reorganized
build remains separate; publication blockers are in PUBLICATION-REVIEW.md.
