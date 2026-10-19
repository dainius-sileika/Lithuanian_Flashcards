#!/bin/sh
# One line: link the repo's hooks into this clone (run once per clone).
cd "$(git rev-parse --show-toplevel)" && ln -sf ../../tools/hooks/pre-commit .git/hooks/pre-commit && echo "pre-commit hook installed"
