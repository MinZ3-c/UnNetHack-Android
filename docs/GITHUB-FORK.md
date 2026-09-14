# Import into an actual GitHub fork

The maintainer has chosen an experimental publication with licensing clarification still pending. See PUBLICATION-REVIEW.md for unresolved findings.
The source-export directory alone has no GitHub fork relationship.

1. Use GitHub's **Fork** action on https://github.com/UnNetHack/UnNetHack.
   Forking the unchanged public upstream is distinct from publishing this port.
2. Clone YOUR fork and add the original as upstream:

   ```sh
   git clone https://github.com/YOUR-ACCOUNT/UnNetHack.git
   cd UnNetHack
   git remote add upstream https://github.com/UnNetHack/UnNetHack.git
   git fetch upstream
   git switch -c android-port 439b8d63d3d1ca78fb08588dd43f61874114b21a
   ```

3. Apply the accompanying `android-port-review.patch` from outside the clone:

   ```sh
   git apply --check ../android-port-review.patch
   git apply --index ../android-port-review.patch
   python3 scripts/audit-publication.py
   git diff --cached --stat
   ```

   The patch retains the original UnNetHack root layout and existing ancestry.
   Do not copy the former port/ over a newly initialized unrelated repository.

4. Resolve outstanding licenses, dates and build verification locally, then
   stage only the reviewed changes and repeat the audit. Configure your real
   Git identity before committing. Keep upstream development on its own branch;
   Android changes belong on android-port. No historical author identities or
   dates have been synthesized by this preparation.

5. Commit and push the reviewed android-port branch to
   YOUR fork. Set it as the default branch if desired. Do not push to upstream.
   Any APK release must refer to the exact source commit and include required
   licenses/notices and source-access information.

The original uploaded ZIP contains saves; never attach it to GitHub Releases.
