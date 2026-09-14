# Android publication preparation

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
