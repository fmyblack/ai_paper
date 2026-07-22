# Project Instructions

This directory is an Obsidian vault for reading, connecting, and reproducing AI research papers.

## Vault Entry Order

Before working in this vault, read:

1. `me.md`
2. `vault-map.md`
3. `workflows.md`
4. `README.md`

## Working Rules

- Keep original PDFs under `library/raw/`; do not edit them in place.
- Keep extracted plain text under `library/text/` and paper notes under `notes/papers/`.
- Distinguish paper claims, experimental evidence, personal inference, and open questions.
- Preserve page, section, figure, table, or equation locators for important claims.
- Do not overwrite an existing paper note unless explicitly asked.
- Use stable, reusable topic names in frontmatter instead of creating near-duplicate tags.
- Put cross-paper synthesis in `notes/topics/`, not only inside an individual paper note.
- Put implementation and reproduction records in `notes/reproductions/`.
- Use dates only for actual deadlines; keep undated research questions as ordinary open tasks.

## Git Sync Rule

The GitHub repository for this project is:

`git@github.com:fmyblack/ai_paper.git`

Before starting a new research task in this repository:

1. Check the worktree with `git status --short`.
2. If the worktree is clean, run `git pull --ff-only` from the repository root.
3. If the worktree is dirty, do not overwrite local changes. Inspect the changes
   and either continue with them or ask the user how to handle unrelated work.

After completing a new research task:

1. Review changed files with `git status --short`.
2. Stage only the files that belong to the completed research.
3. Create a concise commit.
4. Push the branch to GitHub to keep the cloud copy synchronized.

Do not commit API keys, cookies, access tokens, signed URLs, local environment
files, or other secrets.
