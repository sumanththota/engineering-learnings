# Engineering Learnings

A personal, general-purpose store of engineering learnings, structured so AI agents can search it. See [CONTEXT.md](CONTEXT.md) for the domain glossary and `docs/adr/` for the decisions behind this structure.

## One-time setup

This repo commits a pre-commit hook under `.githooks/` instead of the untracked `.git/hooks/`. Point git at it once per clone:

```
git config core.hooksPath .githooks
```

After that, every `git commit` automatically rebuilds `INDEX.json` from `learnings/*.md` and stages the result. If the build fails — for example a new or edited Learning links to an `id` that doesn't exist — the commit is aborted with nothing staged.

## Adding a Learning

Add a new `learnings/<slug>.md` file with the required frontmatter (see an existing file for the shape), then commit as usual. The hook regenerates `INDEX.json` for you.
