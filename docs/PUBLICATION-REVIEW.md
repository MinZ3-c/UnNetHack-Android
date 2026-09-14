# Publication review â€” 2026-09-14

## Completed

- Read and separated the original source and private/device/build material.
- Fetched the actual upstream history; upstream HEAD matched pinned 439b8d63.
- Preserved upstream root layout and ancestry; moved the former port contents
  to the root and adjusted the ForkFront Gradle reference.
- Retained original copyright/license text; added prominent preparation-date
  notices to modified C/header files and updated build helpers.
- Corrected actual app credits (the app overrides the frontend credits).
- Copied the complete NetHack license, Apache-2.0 text and Lua 5.4.8 notice.
  Lua's actual 5.4.8 notice says 1994â€“2025, not 1994â€“2026.
- Identified monobold.ttf as GNU FreeMono using embedded font metadata.
- Inventoried binary assets with SHA-256 and matching reference paths.
- Added staged-content audit; private save/backups, SDK/NDK, keys, caches,
  generated native libraries and APKs are not part of the export.

## Publication decision (2026-09-14)

The maintainer has chosen to publish an experimental source snapshot while
continuing third-party licensing clarification. The findings below remain
open; this decision does not supply missing permissions. Original notices
are retained and the unresolved scope is prominently disclosed in the README.

## Outstanding review findings (source and binaries)

1. **ForkFront scope of permission.** The pinned upstream tree contains 93
   tracked files and no LICENSE/COPYING/README granting a repository-wide
   license. Some Java/keyboard files contain Apache-2.0 headers. Do not apply
   those headers to the remaining files by assumption. Obtain an explicit
   license statement covering the relevant files and inherited contributions.
2. **Artwork and fonts.** Exact-file provenance is recorded, but attribution
   alone is not a redistribution grant. Resolve tiles, overlays, app icon and
   frontend resource graphics individually. FreeMono has GPLv3-or-later with
   font exception in its metadata; obtain matching preferred source and the
   complete accompanying notices, or make an explicitly reviewed replacement.
   The embedded exception for documents is not a blanket relicense of the app.
3. **Historical modification dates.** The ZIP has no original Git history.
   NetHack license paragraph 2(a) requires prominent change/date notices.
   Notices here identify 2026-09-13 preparation; recover dates for earlier
   edits from the original work history rather than inventing exact dates.
4. **Build reconstruction — resolved 2026-09-14.** Original WSL scripts and
   JBR version recovered. Portable setup-native.py and prepare-android.py
   completed a fresh host/native/Gradle build. See BUILD-ANDROID.md.
   The new APK has not been installed or device-tested.
5. **Binary release notices.** Include third-party license/NOTICE material in
   the actual APK or accompanying distribution and complete source/access
   information under NetHack license paragraph 3. The packaging script now includes LICENSE, NOTICE, dependencies.json and
   THIRD_PARTY_LICENSES in the APK; their presence was checked. This does not
   resolve missing permission grants or prove completeness. The cached
   httpclient 4.4.1.2 JAR contains no LICENSE/NOTICE entry; its dependency
   notice requirements still need review.

## Verification limits

JSON/XML/Python parsing and publication-file checks can validate packaging;
they cannot establish ownership, license compatibility, gameplay correctness
or a successful native/Gradle build. Remote publication status must be checked on GitHub; local preparation alone is not a push.
Do not upload the original ZIP: it includes personal save/checkpoint backups.

## ForkFront follow-up (2026-09-14)

The original gurrhack/ForkFront-Android history was inspected through
`14803a118ace2b74474257c4de940cb7ff49b74b` (2026-01-02). ForkFront.java,
SliderPreference.java, qwerty.xml and symbols.xml contain Apache-2.0 notices.
No repository-wide grant was found in the inspected tree/history.
NetHack-Android commit `a96d4ee6f32656594e8d0b33b3f5710a6419a24f`
records the 2016 extraction into ForkFront; the preceding NetHack README
points to dat/license. This is provenance evidence, not a definitive license
determination for every file or subsequent contribution.

- https://github.com/gurrhack/ForkFront-Android
- https://github.com/gurrhack/NetHack-Android/commit/a96d4ee6f32656594e8d0b33b3f5710a6419a24f
