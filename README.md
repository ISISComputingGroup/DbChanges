# DbChanges
Checks for DB changes between releases

To use, run:

`python main.py --old 3.2.0 --new 4.0.0 > changes.txt` (changing the two release numbers to the ones you want to compare).

This will highlight API changes and removals between old and new releases. It will not highlight new APIs that are available in the new release.
