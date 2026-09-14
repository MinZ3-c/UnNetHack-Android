# UnNetHack 6 for Android

An unofficial, experimental ARM64 Android port of UnNetHack 6.0.15-dev,
based on upstream commit `439b8d63d3d1ca78fb08588dd43f61874114b21a`.

The port combines the current UnNetHack engine with the NetHack Android shell
and ForkFront interface. It includes Android save/recovery integration, pet
heart markers and classic `STATUSCOLOR` support.

## Download

Get the [Android preview APK](https://github.com/MinZ3-c/UnNetHack-Android/releases/tag/android-v6.0.15-dev.1)
for ARM64 devices running Android 6.0 or newer. Read the release notes for the
test status, debug-signing details and outstanding licensing questions.

## Current status

The original working build was tested on a Samsung S22 Ultra, including
save/load, pet markers and status colors. The reorganized source completed a
fresh native and Android debug build on 2026-09-14. That rebuilt APK has not
yet been tested on a device. Checkpoint recovery and wider device compatibility
need further testing; this is a development port.

## Build

See [BUILD-ANDROID.md](docs/BUILD-ANDROID.md) for the Linux/WSL native build and
Android packaging steps, and [VALIDATION.md](docs/VALIDATION.md) for checks and
known limits. The build uses Lua 5.4.8 and Android NDK r28c.
Pinned source revisions and toolchain versions are in `dependencies.json`.

The UnNetHack source remains at the repository root. Android integration is
under `sys/android/`, and the vendored frontend is under `forkfront/`.

## Licensing status

**Third-party licensing clarification is still in progress.** In particular,
the repository-wide license scope of ForkFront and the redistribution details
of some graphics, fonts and dependency notices remain unresolved. See
[PUBLICATION-REVIEW.md](docs/PUBLICATION-REVIEW.md) for the current findings.
Publishing this development snapshot does not resolve those questions or
establish additional rights to the included third-party material.

The NetHack General Public License is retained in `LICENSE` and `dat/license`.
Original per-file notices remain in place. `NOTICE`, `THIRD_PARTY_LICENSES/`
and `docs/ASSET-PROVENANCE.json` record attribution and available evidence;
the root license is not a blanket relicensing of all bundled components.

## Source hygiene

Save files, device backups, signing keys, APKs, SDK/NDK installations and build
caches are excluded. Run `python3 scripts/audit-publication.py` to inspect the
staged Git tree before a commit. This heuristic check does not establish
license clearance or guarantee the absence of every possible secret.
