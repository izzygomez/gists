### `find`/`grep` usage notes for searching files on command line

* `grep -ri "string" .` will do a case-insensitive search for "string" in files inside the current directory
* `find . -iname '*pattern*` will do a case-insensitive search for directory & file names that match given pattern inside current directory
* `find . -type f -iname '*pattern*` will do same as above, but just for files