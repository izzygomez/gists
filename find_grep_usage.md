### Quick `find`/`grep` usage notes for searching files on command line

* `grep -ri "string" .` will do a case-insensitive search for "string" inside "."
* `find . -type f -iname '*pattern*` will do a case-insensitive search for file names that match given pattern inside "."