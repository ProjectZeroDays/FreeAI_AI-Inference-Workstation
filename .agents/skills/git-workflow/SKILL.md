---
name: git-workflow
description: Advanced git workflows including branching strategies, interactive rebase, bisect debugging, stash management, cherry-pick, worktrees, and commit conventions. Use when the user asks about git operations, branch management, resolving merge conflicts, rebasing, bisecting bugs, stashing changes, or any advanced git technique.
---

# Git Workflow

## Branching Strategies

### Git Flow
```
main ─────────────────────────────────────
  \                    /
   develop ───────────
    \      /    \    /
    feature-1  feature-2  hotfix-1
```

- `main` — production-ready
- `develop` — integration branch
- `feature/*` — new features branched from develop
- `hotfix/*` — production fixes branched from main

### Trunk-Based
Single main branch with short-lived feature branches. Merge via PR daily. Best for CI/CD-heavy workflows.

### GitHub Flow
Branch from main → commit → open PR → review → merge → deploy.

## Interactive Rebase

Clean up commit history before merge:

```bash
# Rebase last 5 commits
git rebase -i HEAD~5

# Commands in editor:
# pick   = keep commit as-is
# reword = keep commit, edit message
# squash = meld into previous commit
# fixup  = like squash, discard this message
# drop   = remove commit entirely
```

Reorder lines to reorder commits. Save and resolve any conflicts.

## Git Bisect

Binary search for the commit that introduced a bug:

```bash
git bisect start
git bisect bad          # current commit is broken
git bisect good v1.0.0  # this tag was working

# Git checks out a middle commit. Test it, then:
git bisect good   # if it works
git bisect bad    # if it's broken

# Automate with a test script:
git bisect run npm test
```

## Stash Management

```bash
# Stash with message
git stash push -m "WIP: login form"

# Stash including untracked files
git stash -u

# Stash specific files
git stash push -m "config only" -- config.yml

# List stashes
git stash list

# Apply without removing from stash
git stash apply stash@{1}

# Apply and remove
git stash pop

# Create branch from stash
git stash branch new-branch stash@{0}

# Show stash diff
git stash show -p stash@{0}
```

## Cherry-Pick

```bash
# Apply specific commit to current branch
git cherry-pick abc123

# Cherry-pick multiple commits
git cherry-pick abc123 def456

# Cherry-pick a range (exclusive of start)
git cherry-pick abc123..ghi789

# Cherry-pick without committing (stage changes only)
git cherry-pick --no-commit abc123
```

## Worktrees

Work on multiple branches simultaneously without stashing:

```bash
# Create worktree for a branch
git worktree add ../hotfix-branch hotfix/urgent-fix

# Create worktree for new branch
git worktree add -b feature/new ../new-feature develop

# List worktrees
git worktree list

# Remove worktree
git worktree remove ../hotfix-branch
```

## Conflict Resolution

```bash
# After merge conflict, see conflicting files
git diff --name-only --diff-filter=U

# Use ours/theirs for entire files
git checkout --ours path/to/file
git checkout --theirs path/to/file

# Abort merge/rebase
git merge --abort
git rebase --abort

# Continue after resolving
git rebase --continue
```

## Commit Conventions

### Conventional Commits
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`

Examples:
```
feat(auth): add OAuth2 login flow
fix(api): handle null response from /users
perf(db): add index on users.email column
```

## Useful Aliases

```bash
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --all --decorate"
git config --global alias.last "log -1 HEAD --stat"
git config --global alias.unstage "reset HEAD --"
git config --global alias.amend "commit --amend --no-edit"
```

## Recovering Lost Work

```bash
# Find dangling commits
git fsck --lost-found

# View a dangling commit
git show <sha>

# Recover a branch
git branch recovered-branch <sha>

# Reflog — history of HEAD movements
git reflog
git checkout HEAD@{2}
```
