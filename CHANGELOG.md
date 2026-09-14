# Android publication preparation

## 2026-09-14 — Android preview 5

- Restore optional autokick with “Kick it open?” confirmation.
- Fix branch wall tiles and missing end-of-game log files.
- Restore upstream defaults with B/U/C and status colors; add commented autokick.

## 2026-09-14 — Android preview 3

- Enable force_invmenu by default on Android and open the appropriate inventory
  directly for item selection, including wear and drop. The option remains
  configurable; other platforms keep their existing behavior.
- Keep filtered/full inventory selection, quantities and command replay paths;
  closing an automatic menu cancels instead of reopening it.
- Verified the actual Android getobj implementation with simulated menu
  callbacks on an S22 Ultra. VersionCode 6001503; saves match preview 2.

## 2026-09-14 — Android preview 2

- Generate host data and Android tables with the same MAIL setting, fixing
  gold named "white gems" and shifted object/monster identifiers.
- Check generated counts, gold identity and every host/Android table entry
  before native compilation; add an Android library naming regression test.
- Preserve incompatible saves and stop loading instead of deleting them.
  Earlier Android saves require the older build; use a new character name.
- Normalize Windows-checkout text in native build copies and serialize the
  legacy host build to avoid shared-generator races.
- Increment Android versionCode to 6001502 and data revision to 411.

## 2026-09-13

- Preserved pinned UnNetHack history and root layout; imported working Android
  port and embedded ForkFront source from the supplied snapshot.
- Fixed frontend relative path and Gradle JVM-property spelling.
- Corrected effective app credits and included exact component license evidence.
- Added file-level preparation notices and a source-change inventory.
- Excluded private data and build products; added staged-file publication audit.

Original maintainer-reported device checks: save/load, pet-heart and classic
STATUSCOLOR on Samsung S22 Ultra. The reorganized source has not been rebuilt.
Earlier individual edit dates and complete third-party permissions remain open.
