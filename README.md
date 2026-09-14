General information about UnNetHack
===================================

UnNetHack is a fork of NetHack, originally based on NetHack version 3.4.3.

It features more randomness, more levels, more challenges and more fun than
vanilla NetHack.

In a nutshell I would describe UnNetHack as "how NetHack would look today if
the DevTeam didn't stop releasing", following a modern open source project
approach of development.


The project page with detailed information about changes from NetHack, the
development blog, public servers, source code repository and ways to reach the
developer can be found at: https://unnethack.wordpress.com/

For discussions, join the IRC channel #unnethack on Libera.Chat, post to the
Reddit group r/nethack or the Usenet group rec.games.roguelike.nethack.


 -- Good luck, and happy Hacking
 
# UnNetHack 6 for Android

An unofficial, experimental ARM64 Android port of UnNetHack 6.0.15-dev,
based on upstream commit `439b8d63d3d1ca78fb08588dd43f61874114b21a`.

The port combines the current UnNetHack engine with the NetHack Android shell
and ForkFront interface. It includes Android save/recovery integration, pet
heart markers and classic `STATUSCOLOR` support.

## Download

Get the [Android preview APK](https://github.com/MinZ3-c/UnNetHack-Android/releases/tag/android-v6.0.15-dev.5)
for ARM64 devices running Android 6.0 or newer. Read the release notes for the
test status, debug-signing details and outstanding licensing questions.

## Current status

Preview 5 restores optional utokick with confirmation, fixes branch wall
tiles and end-of-game logs, and updates the default color settings. Existing
options files are preserved; enable OPTIONS=autokick to use the new prompt.

Preview 3 opens inventory selection automatically for item commands such as
wear and drop. Android enables `force_invmenu` by default; `OPTIONS=!force_invmenu`
restores letter prompts. Preview 3 uses the same save format as preview 2.

Preview 2 fixes mismatched generated object and monster IDs (including gold
being named "white gems"). Start with a new character name: saves from the
earlier builds are incompatible. Incompatible saves are preserved rather than
deleted when loading fails.

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
