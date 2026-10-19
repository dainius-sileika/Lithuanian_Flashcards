# Retired A2 list builders (2026-10-20)

`build_a2.py` (built `a2_build/a2_wordlist.csv` from the queue and minted `A2-####` ids) and
`apply_benchmark.py` (its first data pass) are retired with the key rename of 2026-10-20
(spec §12, `a2_build/rename/PLAN_rename_v1.md` §8.11). The A2 list has been edited directly since
2026-10-11 (rounds 3–7), so a re-run would regress it, and every card key is now `NNNN_slug`.

A new card gets its key from `python3 tools/rename_keys.py --mint "<headword>"` (next free number +
slug) and is appended to the list and to `study_order.csv`. The `a2_build/src/apply_round*.py`
scripts stay in place as history: they are keyed by the pre-rename ids and must not be re-run.
