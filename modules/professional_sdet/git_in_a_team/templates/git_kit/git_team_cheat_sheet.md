<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Git in a team: cheat sheet

## Start a change

| Command | Does |
| --- | --- |
| `git switch main` then `git pull` | Get the newest main before you start |
| `git switch -c test/<short-name>` | A new branch for one change |
| `git status` | What changed, what's staged |
| `git diff` | The exact lines you changed |
| `git add <file>` | Choose what goes into the next commit |
| `git commit -m "Add the lockout test"` | Save it, with a message that says what and why |
| `git push -u origin test/<short-name>` | Send the branch; then open a pull request |

## Stay up to date

| Command | Does |
| --- | --- |
| `git fetch origin` | Download what others pushed; changes nothing of yours |
| `git rebase origin/main` | Put your commits on top of the newest main |
| `git push --force-with-lease` | Send a rebased branch. Refuses if someone else pushed to it meanwhile |
| `git merge origin/main` | The other way: a merge commit instead of rewriting your commits |

## Conflicts

| Command | Does |
| --- | --- |
| `git status` | Lists the files in conflict ("both modified") |
| Edit the file | Keep the right lines, delete `<<<<<<<`, `=======`, `>>>>>>>` |
| `git add <file>` | Mark it resolved |
| `git rebase --continue` | Carry on |
| `git rebase --abort` | Undo the whole rebase, back to before |

## Oops

| Command | Does |
| --- | --- |
| `git restore <file>` | Throw away your changes to a file (not committed yet) |
| `git restore --staged <file>` | Un-stage it, keep the changes |
| `git commit --amend` | Fix the last commit (only before you push it) |
| `git stash` / `git stash pop` | Put changes aside, then bring them back |
| `git log --oneline --graph --all` | See all branches as a picture |

Never: `git push --force` to main, or commit `.env`, reports or passwords.
