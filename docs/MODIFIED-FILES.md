# Source changes

Compared with pinned UnNetHack 439b8d63, ignoring CRLF/LF differences.
Original edit dates are unavailable; 2026-09-13 is the publication preparation date.

- `src/restore.c`
- `src/botl.c`
- `src/files.c`
- `src/rip.c`
- `src/end.c`
- `src/windows.c`
- `include/config.h`
- `include/global.h`
- `include/tradstdc.h`
- `sys/autoconf/config.guess`
- `sys/autoconf/config.sub`
- `sys/share/unixtty.c`

New Android integration files are under `sys/android/` and `include/androidconf.h`.
See the accompanying Git patch for the exact changes and preserved history.

## Recovered work history (2026-09-14 review)

The original local task history is available again. The WSL native build,
NHFILE/startup fixes, Android checkpoint recovery, pet overlay translation and
classic STATUSCOLOR integration were performed on 2026-09-13. Initial Android
scaffolding and dependency preparation began on 2026-09-12. These are work
intervals, not reconstructed Git commit timestamps; imported upstream authors
and dates have not been fabricated.

New build orchestration scripts setup-native.py and prepare-android.py were
added on 2026-09-14. Existing per-file preparation notices are retained.
