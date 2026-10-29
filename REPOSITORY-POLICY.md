# Permanent three-release repository policy

Keep exactly the current Cloudcourt release and its previous two releases,
each in its own V<number>/ folder. Current folders are V29/,V28/ andV26/.
When V30 ships, keep V30/,V29/,V28/ and remove V27/ from the main file tree.
Use the matching published source snapshot for each version; do not populate an
older folder with current runtime code. Keep every folder's required imports,
C includes, authoring helpers, font/audio inputs and licenses. Feature suffixes
on shared component filenames are not separate retained releases.

Keep only navigation, project instructions and this policy at repository root.
Preserve local ZIPs, recovery backups, synced sources/ reference files and normal
Git history. Routine cleanup uses a new commit, never a force update or rewrite.
Publish source, delivery notes and own/verified licensed art only. Derived test
reports and machine-specific metadata stay local. Never include original game
binaries/assets, binary deltas or release ZIPs in the public repository.
