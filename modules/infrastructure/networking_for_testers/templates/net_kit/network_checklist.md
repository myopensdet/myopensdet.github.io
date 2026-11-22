<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->

# "It doesn't work": network checklist

Go top to bottom. Stop at the first step that fails: that's the problem to report.

| # | Question | How to check | If it fails |
| --- | --- | --- | --- |
| 1 | Is the address right? | Read it letter by letter: `http` or `https`, host, port, path | Fix it, or ask for the right one |
| 2 | Does the name resolve? | `python net_check.py <url>` step 1, or `nslookup <host>` | Spelling, VPN off, or the test site moved |
| 3 | Is the port open? | `net_check.py` step 2 | App not running, wrong port, firewall or VPN |
| 4 | Is the certificate OK? | `net_check.py` step 3 | Expired, wrong name or self-signed: report it, never click past |
| 5 | Does the app answer? | `net_check.py` last step | No answer: app stuck or slow. 5xx: app error. 4xx: your request |
| 6 | Same from another network? | Phone hotspot, a colleague, or the pipeline | Only you: your network, proxy or VPN |
| 7 | Same in another browser or a private window? | Private window has no cookies or extensions | Cookies, cache or an extension |
| 8 | What does the browser say? | Developer tools (F12) → Console and Network tabs | CORS errors show only here, not in the server log |

## Put in the bug report

- The exact address, and the time (with time zone, or UTC)
- Which step failed, and the exact message
- From where: your computer, VPN on or off, the pipeline
- What a working address gives, for comparison
