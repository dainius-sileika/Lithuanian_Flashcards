# deprecated/ — frozen older versions

Frozen snapshots of superseded files, kept for rollback and for sharing older
versions. Nothing in here is read by the live pipeline — the working files in the
project root are the current version (1.7.1). Safe to ignore during normal use.

## Layout
```
deprecated/
  code_1.6.1/            frozen source at files 1.6.1
    deck_builder.py
    go_grammars.py
    (go_generator.py:    unchanged from 1.6.1 through 1.7 — see code_1.7/)
  code_1.7/              frozen source at files 1.7 (the guessability pass)
    deck_builder.py
    go_grammars.py
    go_generator.py      (this is also the 1.6.1 engine, byte-identical)
  wordlist_2.2/
    master_wordlist.csv  the wordlist before the 2.3 (22-phrase) sharpening
  spec_1.6.1/
    GO_STYLE_SPEC_files_1_6_1.md   superseded by GO_STYLE_SPEC_files_1_7_1.md
  docs_superseded/
    files_1_7_DIFF.stale-draft.md  the first 1.7 sign-off draft that
                                   under-reported NOUN_STAGING by 5 rows
  card_images_pre_1.7/   the 33 card PNGs replaced during the 1.7 guessability
                         pass (their pre-1.7 versions)
```

## How to roll back
To restore an older version of a file, copy it from here back into the project
root, e.g. to return the code to 1.7:

    cp deprecated/code_1.7/deck_builder.py  ./deck_builder.py
    cp deprecated/code_1.7/go_grammars.py   ./go_grammars.py
    cp deprecated/code_1.7/go_generator.py  ./go_generator.py

or to return the wordlist to 2.2:

    cp deprecated/wordlist_2.2/master_wordlist.csv  ./master_wordlist.csv

Always keep the current files backed up (or committed) before overwriting.

## Version history
See `../VERSIONS.md` for the full index, and the "File batches ledger" section
of `../GO_STYLE_SPEC_files_1_7_1.md` for the narrative changelog.
