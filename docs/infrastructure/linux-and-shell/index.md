---
title: "Linux and Shell for Testers: Read Logs and Find Problems, Step by Step"
description: "The shell commands testers use at work, step by step: move around a server, read big log files, search with grep, count and sort with pipes, follow one request across logs, find what's using a port, and use a ready log summary script. Real outputs and a cheat sheet."
level: Beginner
tags:
  - Linux
  - Debugging
  - Templates
nav_title: "Linux and shell"
order: 10
group: "Your toolkit"
summary: "Read logs, search with grep, count with pipes, find ports, a ready log script."
updated: "2026-11-22"
---

# Linux and Shell for Testers: Read Logs and Find Problems, Step by Step

"Check the server logs" is one of the most common things a tester hears. The logs are on a Linux server, there's no mouse, and the file has 400,000 lines. This guide teaches the dozen commands that cover almost all of it, on a practice log, with a ready script for the rest.

!!! example "The situation"
    **Your lead:** "Last night's run had failures on orders and the cart. Can you look at the server logs and tell the developers what happened?"

## Step 1: Get a shell and the practice logs

A **shell** is the text window where you type commands. Servers use **bash**; macOS uses zsh, which accepts the same commands here.

| Your computer | Open |
| --- | --- |
| **macOS** | Terminal (or the terminal in VS Code) |
| **Linux** | Terminal |
| **Windows** | **Git Bash** (comes with [Git for Windows](https://git-scm.com/downloads/win)), or WSL. Not PowerShell: its commands are different |

1. **Get the files**: copy them from [Templates](#templates) below into a new folder, or take the whole folder [from GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/infrastructure/linux_and_shell/templates). Then open a terminal in the `shell_kit` folder.
2. **Make the practice logs**: one hour of a small web shop's logs, the same on every computer:

    ```bash
    python make_practice_logs.py
    ```

    ```text
    Wrote logs/app.log (400 lines) and logs/worker.log (18 lines)
    ```

    (Windows: `py -3.13 make_practice_logs.py`.)

## Step 2: Move around

```bash
pwd             # where am I?
ls logs         # what's in the logs folder?
```

```text
app.log
worker.log
```

| Command | Does |
| --- | --- |
| `cd logs`, `cd ..`, `cd ~` | Go into a folder, up one, to your home folder |
| `ls -l` | Files with sizes and dates |
| `find . -name '*.log'` | Find files by name in every folder below this one |

```bash
find . -name '*.log'
```

```text
./logs/worker.log
./logs/app.log
```

On a real server, logs usually live in `/var/log/<app name>/`, or wherever the developers tell you. Ask them.

## Step 3: Read a big file without opening it all

Never `cat` a big log: it floods the screen. Look at its size, then at the end, where the newest lines are:

```bash
wc -l logs/app.log
tail -n 3 logs/app.log
```

```text
     400 logs/app.log
2026-11-18T02:59:33Z INFO  req-01397 GET /api/search status=200 took_ms=71
2026-11-18T02:59:42Z INFO  req-01398 GET /api/search status=200 took_ms=72
2026-11-18T02:59:51Z INFO  req-01399 GET /api/cart status=200 took_ms=119
```

Each line is: **time** (UTC, the `Z`), **level**, **request id**, **method and path**, **status**, **how long it took**, and sometimes an **error**. Learn your app's log format first: everything else builds on it.

| Command | Does |
| --- | --- |
| `head -n 20 file` | The first 20 lines |
| `less file` | Scroll a big file. `/word` searches, `n` finds the next, `q` quits |
| `tail -f file` | **Watch new lines arrive** while you click in the app. Ctrl+C stops |

`tail -f` is the tester's favourite: open it in one window, do the thing that fails in the app, and watch the error appear.

## Step 4: Search with grep

`grep` prints the lines that contain a word:

```bash
grep ERROR logs/app.log | head -n 3
```

```text
2026-11-18T02:02:51Z ERROR req-01019 GET /api/orders status=500 took_ms=76 error=PaymentTimeout
2026-11-18T02:09:27Z ERROR req-01063 GET /api/orders status=500 took_ms=10 error=PaymentTimeout
2026-11-18T02:10:12Z ERROR req-01068 GET /api/orders status=500 took_ms=112 error=PaymentTimeout
```

The options you'll use every day:

| Command | Does | Practice log |
| --- | --- | --- |
| `grep -c ERROR logs/app.log` | Count matching lines | `19` |
| `grep -i error logs/app.log \| wc -l` | Ignore case (finds `ERROR` and `error=`) | `40` |
| `grep -n discount_code logs/app.log` | Show line numbers | `334:2026-11-18T02:49:57Z ERROR ...` |
| `grep -v INFO logs/app.log` | Lines **without** INFO: everything unusual | |
| `grep -r req-01019 logs` | Search every file in a folder | |

**See what happened around an error** with `-C` (context): two lines before and after.

```bash
grep -C 2 req-01333 logs/app.log
```

```text
2026-11-18T02:49:39Z INFO  req-01331 GET /api/search status=200 took_ms=44
2026-11-18T02:49:48Z INFO  req-01332 GET /api/orders status=200 took_ms=17
2026-11-18T02:49:57Z ERROR req-01333 GET /api/cart status=500 took_ms=108 error=KeyError:'discount_code'
2026-11-18T02:50:06Z INFO  req-01334 GET /api/login status=200 took_ms=92
2026-11-18T02:50:15Z WARN  req-01335 GET /api/search status=200 took_ms=2420 slow=true
```

`KeyError: 'discount_code'` is a code bug: the cart expected a discount code that wasn't there. One line, and the developer knows where to look.

## Step 5: Count and sort with pipes

The `|` (pipe) sends one command's output into the next. Chains of small commands answer big questions.

**Which pages have the errors?** Take the error lines, keep the 5th word (the path), count each:

```bash
grep ERROR logs/app.log | awk '{print $5}' | sort | uniq -c
```

```text
   1 /api/cart
  18 /api/orders
```

So: 18 errors on orders, 1 on the cart. `sort | uniq -c` is the pattern to remember: **sort, then count each different line.** Add `| sort -rn` to put the biggest count first, and `| head -n 5` to keep the top 5.

| Piece | Does |
| --- | --- |
| `awk '{print $5}'` | The 5th word of each line (words are split by spaces) |
| `cut -c1-13` | Characters 1 to 13 of each line, for example the date and hour |
| `sort`, `sort -rn` | Sort A to Z; sort numbers, biggest first |
| `uniq -c` | Count lines that repeat (after `sort`) |
| `wc -l` | Count lines |

## Step 6: Follow one request across logs

Most apps write a **request id** on every line about one request. With it, you can follow one failing click through every log file:

```bash
grep -r req-01019 logs
```

```text
logs/worker.log:2026-11-18T02:02:51Z ERROR req-01019 payment provider did not answer in 3000 ms
logs/app.log:2026-11-18T02:02:51Z ERROR req-01019 GET /api/orders status=500 took_ms=76 error=PaymentTimeout
```

The app log says "the order failed". The worker log says why: **the payment provider didn't answer in 3 seconds.** That's not a bug in the order code, and it's the sentence the developers need.

When you report a bug from the app, look for the request id in the browser's developer tools (a response header such as `X-Request-Id`) or in the error message, and put it in the report.

## Step 7: Use the ready log summary script

For the first look at any log, the kit has `log_summary.sh`: lines per level, the most common errors, the slowest requests.

The first time, allow it to run (a copied file doesn't have that setting yet):

```bash
chmod +x log_summary.sh
./log_summary.sh logs/app.log
```

```text
== logs/app.log: 400 lines

== Lines per level
 331 INFO
  50 WARN
  19 ERROR

== Most common errors
  21 error=WrongPassword
  18 error=PaymentTimeout
   1 error=KeyError:'discount_code'

== Slowest requests (ms, request id, path)
4169 req-01247 /api/search
4084 req-01078 /api/search
3833 req-01115 /api/search
3611 req-01195 /api/search
3394 req-01093 /api/search
```

In one screen: payment timeouts on orders, one code bug in the cart, wrong passwords (normal), and **search sometimes takes over 4 seconds**. That's your report.

```bash
--8<-- "modules/infrastructure/linux_and_shell/templates/shell_kit/log_summary.sh"
```

**On your own logs:** change the patterns marked `CHANGE` to your log format. Copy it to the server, or run it on a copy of the log you downloaded.

## Step 8: Ports, processes and variables

**"Address already in use"?** Find what's using the port, see what it is, stop it if it's yours:

```bash
lsof -ti tcp:8790 -sTCP:LISTEN     # which process listens on port 8790
ps -o command= -p 83050             # what is process 83050
kill 83050                          # stop it
```

```text
83050
python -m http.server 8790 --bind 127.0.0.1
```

Never `kill` a process you don't recognise on a shared server. Ask first.

**Variables** hold settings for this terminal only, like the test address:

```bash
export BASE_URL=http://127.0.0.1:8770
echo $BASE_URL
```

```text
http://127.0.0.1:8770
```

**Exit codes** tell scripts and pipelines if a command worked: `0` means yes. `grep` gives `1` when it finds nothing. `&&` runs the next command only if the first worked, `||` only if it failed:

```bash
grep -q ERROR logs/app.log && echo "errors found" || echo "clean"
```

```text
errors found
```

## Step 9: When it goes wrong

| You see | What it means | Fix |
| --- | --- | --- |
| `bash: ./log_summary.sh: Permission denied` | The file isn't allowed to run | `chmod +x log_summary.sh` |
| `No such file or directory` | Wrong name, or wrong folder | `pwd` and `ls` to see where you are |
| `bash: tial: command not found` | A typo, or the tool isn't installed | Check the spelling. `which tail` shows if it exists |
| `Usage: ./log_summary.sh <log file> [how many]` | You forgot the file name | `./log_summary.sh logs/app.log` |
| `grep` prints nothing | No match: check the case, or use `-i` | `echo $?` gives `1` when nothing matched |
| `grep: app.log: binary file matches` | The file has odd bytes in it, so grep won't print the lines | `grep -a ERROR app.log` |
| `Permission denied` reading `/var/log/...` | Logs need more rights | Ask for read access; don't use `sudo` on shared servers without permission |
| The screen fills with a giant file | You used `cat` on a big log | Ctrl+C, then use `tail`, `less` or `grep` |

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/infrastructure/linux_and_shell/templates).

=== "Cheat sheet"

    ```markdown
    --8<-- "modules/infrastructure/linux_and_shell/templates/shell_kit/shell_cheat_sheet.md"
    ```

=== "make_practice_logs.py"

    ```python
    --8<-- "modules/infrastructure/linux_and_shell/templates/shell_kit/make_practice_logs.py"
    ```

## References

- [GNU grep manual](https://www.gnu.org/software/grep/manual/grep.html)
- [GNU Coreutils: sort, uniq, cut, wc, head, tail](https://www.gnu.org/software/coreutils/manual/coreutils.html)
- [The Linux command line for beginners (Ubuntu tutorial)](https://ubuntu.com/tutorials/command-line-for-beginners)
- [Git for Windows (includes Git Bash)](https://git-scm.com/downloads/win)

Written for bash 5 on Linux and Git Bash, and zsh on macOS. Outputs captured November 2026. Links checked: November 2026.
