# Cloudcourt repository instructions

- Permanent user rule: keep the current release and the previous two in the
  main public file tree. Apply this cleanup on every new release.
- Read REPOSITORY-POLICY.md before publishing. Current retained releases:
  v28, v27 and v26. Advance this three-release window when a new version ships.
- Retain shared source dependencies even when a filename has an older feature
  suffix. Audit C includes, Python imports and dynamic source references before
  removing anything. Reusable fonts, audio inputs and licenses live in assets/shared/.
- Preserve local ZIPs, recovery backups, sources/ references and Git history.
  Routine cleanup is a new commit, with no force update or history rewrite.
- Publish source, delivery notes and own/verified licensed art only. Keep
  derived test reports and machine-specific metadata local.
- Never publish original game binaries/assets or binary-difference ZIPs here.
- Only install changes with the game closed; never force-close a user's game.
- Distinguish local/native checks from physical Quest3 and real two-PC tests.
