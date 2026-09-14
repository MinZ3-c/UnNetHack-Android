# Validation performed on 2026-09-13

- Source basis fetched from official UnNetHack repository; HEAD was 439b8d63.
- ForkFront fetched at recorded 1ce8a040; inspected tracked files and license headers.
- Official Lua 5.4.8 source archive SHA-256 matched the recorded checksum;
  exact version-specific copyright/license notice extracted from src/lua.h.
- GNU FreeMono identity and embedded license read from actual bundled TTF metadata.
- Python audit self-checks covered device backups/checkpoints, native libraries,
  signing keys and tokens, and retained legitimate save.c/wrapper source paths.
- Export/staged audit found no flagged private paths or secret patterns. This
  is a heuristic scan; it is not a guarantee covering arbitrary secret formats.
- Parsed source metadata JSON, Python helpers and 36 Android XML files.
- Confirmed frontend Gradle path resolves correctly in the revised root layout.
- Confirmed LICENSE is byte-identical to dat/license.

Not performed: full host/native/Lua/Gradle rebuild, APK validation, runtime/JNI
comparison against newly compiled classes, new device tests, binary determinism.

## Fresh build verification — 2026-09-14

- Recovered the original WSL configure commands and confirmed JBR
  21.0.10+-14961533-b1163.108.
- Built the reorganized source in a new external Linux directory using
  scripts/setup-native.py: host executable/tools, generated headers, nhdat,
  Lua 5.4.8 ARM64 PIC archive, all 134 Android source files and shared library.
- Reused downloaded dependencies and installed NDK/SDK; no existing compiled
  game objects, generated game data or old libunnethack.so were copied in.
- Created an external Gradle copy with prepare-android.py; assembleDebug passed.
  The first attempt could not create the default debug key in the protected
  Android user directory. Setting ANDROID_USER_HOME to an external writable
  directory resolved this without adding keys or signing paths to the source.
- JNI descriptor check against freshly compiled Java: 26 callbacks plus entry
  point passed. apksigner verified v1/v2 signatures. It also reported the
  standard META-INF app-metadata.properties entry is not protected by the JAR
  signature; v2 verification passed. This is a debug build, not a release.
- APK metadata: org.unnethack.android, version 6.0.15-dev/6001501, min API 23,
  target API 34, native ABI arm64-v8a.
- License assets are staged by prepare-android.py. Their inclusion does not
  resolve the rights gaps recorded in PUBLICATION-REVIEW.md.

Not performed on this rebuilt APK: device gameplay/save compatibility tests,
byte-identical repeated builds, complete dependency-license clearance.
The installed working app and device data were not changed in this review.
