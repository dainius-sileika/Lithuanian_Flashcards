# Audio inbox

Drop the ZIP that `recorder_A2.html` exports (**Export new takes**) here. Nothing in this folder is committed.
Then: `python3 tools/ingest_takes.py --inbox` (converts each clip to `media/audio/<key>.mp3`, records it in
`data/audio_source.tsv`, keeps leftovers in `_archive/takes/<zip>/`), then `python3 build_recorder.py A2`,
then rebuild the package. Guide: `docs/RECORDING_GUIDE.md`.
