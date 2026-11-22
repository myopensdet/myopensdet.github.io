<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->

# Shell cheat sheet for testers

## Move around

| Command | Does |
| --- | --- |
| `pwd` | Where am I? |
| `ls`, `ls -l` | What's here (with sizes and dates) |
| `cd logs`, `cd ..`, `cd ~` | Go into a folder, up one, home |
| `find . -name '*.log'` | Find files by name, in all folders below |

## Read files

| Command | Does |
| --- | --- |
| `cat file` | Print a small file |
| `less file` | Read a big file. `/word` searches, `n` next, `q` quits |
| `head -n 20 file`, `tail -n 20 file` | First or last 20 lines |
| `tail -f file` | Watch new lines as they arrive. Ctrl+C stops |
| `wc -l file` | Count lines |

## Search

| Command | Does |
| --- | --- |
| `grep ERROR file` | Lines with ERROR |
| `grep -i error file` | Ignore upper or lower case |
| `grep -n`, `grep -c` | Show line numbers; just count |
| `grep -C 2 req-01333 file` | 2 lines before and after each match |
| `grep -v INFO file` | Lines **without** INFO |
| `grep -r req-01019 logs` | Search every file in a folder |

## Pipes: join commands with `|`

| Command | Does |
| --- | --- |
| `grep ERROR app.log \| wc -l` | Count error lines |
| `... \| sort \| uniq -c \| sort -rn` | Count each different line, most first |
| `awk '{print $5}'` | The 5th word of each line |
| `cut -c1-13` | Characters 1 to 13 of each line |
| `... \| head -n 5` | Only the first 5 |

## Processes, ports, variables

| Command | Does |
| --- | --- |
| `lsof -ti tcp:8000 -sTCP:LISTEN` | Which process listens on port 8000 (macOS, Linux) |
| `ps -o command= -p 1234` | What process 1234 is |
| `kill 1234` | Stop process 1234 |
| `export NAME=value`, `echo $NAME` | Set and read a variable for this terminal |
| `echo $?` | Exit code of the last command: 0 means OK |
| `a && b`, `a \|\| b` | Run b only if a worked; only if a failed |
| `chmod +x script.sh` | Allow a script to run |
