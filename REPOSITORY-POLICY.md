# Repository retention policy

Permanent user preference: keep the current Cloudcourt release and the two
previous releases in the public repository's main tree. Apply this on every
release. Current retained releases are v28, v27 and v26.

Retain shared runtime/authoring/test dependencies even when their filenames
carry an older feature suffix. Put reusable fonts, licenses and sound inputs
under assets/shared/. Remove obsolete delivery scripts, checkpoints, generated
previews and validation folders older than the retained three after checking
imports, C includes and dynamic source references.

Preserve local release ZIPs, recovery backups, sources/ reference files and Git
history. Publish only source, delivery instructions and own/verified licensed
art. Derived validation reports and local metadata stay on the computer.
Never use a force update or rewrite history for this routine cleanup.
