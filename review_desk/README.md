# Review Desk (owner SOP, 2026-10-17)

One artifact holds everything the owner must review or decide: https://claude.ai/artifact/R3AF86rbem8AQxpNkdqPSd

- `items.json` holds the open items. Each item has an id, a group, a title, the question, answer options, and links (review pages, or `#doc-…` anchors to the embedded reports).
- `build.py` fills `template.html` with the items, the reports and the screenshots, and writes `review_desk.html`.
- Publish it with the Artifact tool to the same URL (capabilities `db` + `user`).
- Answers are stored in the page database, collection `answers`, one document per item id (`choice`, `note`, `updatedAt`). Read them with ArtifactData.

Every round:
1. Read the answers.
2. Act on them.
3. Remove settled items from `items.json`.
4. Add new items.
5. Rebuild and republish.
6. End the message to the owner with direct links.
