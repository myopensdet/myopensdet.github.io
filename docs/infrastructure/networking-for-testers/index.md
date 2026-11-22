---
title: "Networking for Testers: Find Where a Request Breaks, Step by Step"
description: "Networking for testers at work, step by step: how a request travels, names and DNS, ports, refused vs timed out, HTTPS certificates, redirects, slow answers, cookie flags and CORS. With a ready Python script that checks an address and names the step that fails, and a troubleshooting checklist."
level: Beginner
tags:
  - Networking
  - Debugging
  - Templates
nav_title: "Networking for testers"
order: 20
group: "Your toolkit"
summary: "Name, port, certificate, answer: find which step breaks, with a ready script."
updated: "2026-11-22"
---

# Networking for Testers: Find Where a Request Breaks, Step by Step

"The test site doesn't work" can mean ten different things, and only some of them are bugs in the app. A tester who can say **which step** fails saves everyone an hour: "the name doesn't resolve on the VPN", "the certificate expired yesterday", "the port is open but the app doesn't answer". This guide teaches those steps, with a script that checks them for you.

!!! example "The situation"
    **A developer, in the team chat:** "Tests failed with 'connection error' again. Is it the network or the app?"

## Step 1: Get the kit

You need **Python 3.13**. If you don't have it, follow [environment setup](../../start-here/environment-setup/index.md) first.

1. **Get the files**: copy them from [Templates](#templates) below into a new folder, or take the whole folder [from GitHub](https://github.com/arshaduzzaman-sm/myopensdet/tree/main/modules/infrastructure/networking_for_testers/templates). Then open a terminal in the `net_kit` folder.
2. Optional, for HTTPS on some computers: `python -m pip install -r requirements.txt` (installs `certifi`, a list of trusted certificates. If you have requests, you have it).
3. **Start the practice server** in this terminal, and open a second terminal for the checks:

    ```bash
    python practice_server.py
    ```

    ```text
    Practice server on http://127.0.0.1:8790  (Ctrl+C to stop)
    ```

## Step 2: Know the four steps of every request

When a test calls `https://shop.example.com/api/orders`, four things happen, in order. Each can fail on its own:

| Step | What happens | When it fails, you see |
| --- | --- | --- |
| **1. Name** | The computer asks DNS: "which address is `shop.example.com`?" | "not found", "Name or service not known" |
| **2. Connect** | It opens a connection to that address, on a **port** (443 for https, 80 for http, or one in the address like `:8790`) | "Connection refused", or a timeout |
| **3. HTTPS** | For `https`, the server shows its **certificate**, and your computer checks it | "certificate has expired", "Hostname mismatch", "self-signed" |
| **4. Answer** | The app reads the request and answers with a status code | A 4xx or 5xx status, or no answer in time |

Steps 1 to 3 are the **network**. Step 4 is the **app**. Find the first step that fails, and you know who to talk to.

The kit's `net_check.py` does the four steps one by one and says where it stops:

```bash
python net_check.py https://example.com
```

```text
Checking https://example.com
  1. Name      example.com -> 2606:4700:10::ac42:93f3 (3 ms)
  2. Connect   port 443 open (9 ms)
  3. HTTPS     certificate valid for 37 more days (20 ms)
  4. Answer    200 OK (49 ms)
```

All four passed. That's what healthy looks like.

## Step 3: Name problems

```bash
python net_check.py https://exmaple-shop.invalid
```

```text
Checking https://exmaple-shop.invalid
  1. Name      FAILED: exmaple-shop.invalid not found (nodename nor servname provided, or not known)
     Check the spelling, your VPN, or ask which address the test site has.
```

Stopped at step 1: nothing else was even tried. The usual causes:

- **A typo.** `exmaple` instead of `example`. Read the address letter by letter.
- **A name that only works on the company network.** Test sites like `shop.test.internal` exist only on the VPN. Turn the VPN on, or ask.
- **A name that moved.** The test environment got a new address and nobody told you.

`127.0.0.1` and `localhost` both mean "this computer". An app started on **your** computer is only reachable from your computer, not from a colleague's, and not from inside a Docker container.

## Step 4: Port problems: refused vs timed out

```bash
python net_check.py http://127.0.0.1:8791/
```

```text
Checking http://127.0.0.1:8791/
  1. Name      127.0.0.1 -> 127.0.0.1 (1 ms)
  2. Connect   FAILED: port 8791 refused
     Nothing is listening there: the app isn't running, or the port is wrong.
```

Two different failures at step 2. Learn to tell them apart:

| Message | Means | Usually |
| --- | --- | --- |
| **Connection refused** | The computer answered, fast: "nothing here on that port" | The app isn't running, crashed, or uses another port |
| **Timed out** | Nobody answered at all | A firewall, VPN or security group blocks it, or the server is off |

"Refused" is good news, oddly: you reached the right machine. Check the app is running and the port number (see [Linux and shell, step 8](../linux-and-shell/index.md#step-8-ports-processes-and-variables) to find what's on a port).

## Step 5: HTTPS and certificate problems

An HTTPS certificate proves "this really is `shop.example.com`". Browsers and test tools refuse to talk when it's wrong. [badssl.com](https://badssl.com/) is a public site with broken certificates on purpose, made for this kind of practice:

```bash
python net_check.py https://expired.badssl.com/
```

```text
Checking https://expired.badssl.com/
  1. Name      expired.badssl.com -> 104.154.89.105 (3 ms)
  2. Connect   port 443 open (192 ms)
  3. HTTPS     FAILED: certificate has expired
     Don't click past this in a browser. Report it, with the address.
```

The certificate failures you'll meet at work:

| Message | Means | Who fixes it |
| --- | --- | --- |
| `certificate has expired` | Someone forgot to renew it | The team that runs the server. Test sites often expire first: report it |
| `Hostname mismatch, certificate is not valid for 'wrong.host.badssl.com'.` | The certificate is for another name | Ops: the address or the certificate is wrong |
| `self-signed certificate` | Made by the team itself, not a trusted authority | Normal on some test sites. Ask for the team's certificate file, never turn checking off for everything |
| `unable to get local issuer certificate` | **Your** computer doesn't have the list of trusted authorities, or a company proxy replaces certificates | Install `certifi` (step 1), or ask IT for the company certificate |

The last one is common with Python. A plain `urllib` call on a computer without the list gives:

```text
urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1035)>
```

When `net_check.py` shows "valid for N more days" with a small N, the script adds `<- renew soon!` under 30 days. Put that in your release checklist.

!!! warning "Never switch certificate checks off in tests"
    `verify=False` in requests, or "proceed anyway" in a browser, makes the error go away, and also hides the day someone really is in the middle. Fix the certificate, or point your tool at the right certificate file.

## Step 6: Answer problems: redirects and slow apps

Once steps 1 to 3 pass, problems are in the **app**. Two that look like network problems but aren't:

**Redirects.** A 301 or 302 sends you somewhere else:

```bash
python net_check.py http://127.0.0.1:8790/old
```

```text
Checking http://127.0.0.1:8790/old
  1. Name      127.0.0.1 -> 127.0.0.1 (1 ms)
  2. Connect   port 8790 open (0 ms)
  3. Answer    301 Moved Permanently (0 ms)
     Sends you on to: /login
```

A test that expects 200 but gets 301 usually has an old address. A redirect from `https` to `http` is a bug: report it.

**No answer in time.** The connection opens, then nothing:

```bash
python net_check.py http://127.0.0.1:8790/slow --timeout 3
```

```text
Checking http://127.0.0.1:8790/slow
  1. Name      127.0.0.1 -> 127.0.0.1 (1 ms)
  2. Connect   port 8790 open (0 ms)
  3. Answer    FAILED: connected, but no answer in 3 s
     The server is up but slow or stuck: an app problem, not the network.
```

Connected fine, so the network is OK. The app is stuck or slow. That's for the developers, with the time it happened. For speed problems, see [check API speed, step by step](../../work-playbooks/check-api-speed/index.md).

## Step 7: Cookies and CORS

Two more things live in the answer's **headers**, and testers should check them on every login page.

**Cookie flags.** A login cookie is the user's key. Three flags protect it:

| Flag | Protects against |
| --- | --- |
| `Secure` | Sending the cookie over plain `http` |
| `HttpOnly` | Scripts on the page reading the cookie (a common way to steal logins) |
| `SameSite` | Other websites sending requests with the user's cookie |

```bash
python net_check.py http://127.0.0.1:8790/login
```

```text
Checking http://127.0.0.1:8790/login
  1. Name      127.0.0.1 -> 127.0.0.1 (1 ms)
  2. Connect   port 8790 open (0 ms)
  3. Answer    200 OK (1 ms)
     Cookie session: missing Secure, HttpOnly, SameSite
```

A session cookie missing all three: **report it as a security bug.**

**CORS** decides which **other websites'** scripts may call your API from a user's browser. `--origin` pretends to be another website:

```bash
python net_check.py http://127.0.0.1:8790/api/me --origin http://evil.example
```

```text
Checking http://127.0.0.1:8790/api/me
  1. Name      127.0.0.1 -> 127.0.0.1 (1 ms)
  2. Connect   port 8790 open (0 ms)
  3. Answer    200 OK (0 ms)
     CORS for http://evil.example: Allow-Origin=http://evil.example, Allow-Credentials=true
```

The API says yes to **any** website, **with** the user's cookies. Any page the user visits could read their account. Also a security bug: the allowed origins should be a fixed list of your own sites.

CORS errors only show up **in the browser**: the server log looks fine. Open the developer tools (F12), **Console** tab, and look for "blocked by CORS policy". The **Network** tab shows every request with its status, headers and timing: it's the best network tool you already have.

## Step 8: Use the checklist

When something "doesn't work", go down the kit's checklist and stop at the first step that fails. That's what you report:

```markdown
--8<-- "modules/infrastructure/networking_for_testers/templates/net_kit/network_checklist.md"
```

## Step 9: When it goes wrong

| You see | What it means | Fix |
| --- | --- | --- |
| `Not a full address: 'example.com'. Start with http:// or https://` | The script needs the whole address | `python net_check.py https://example.com` |
| `the secure connection broke off ([Errno 54] Connection reset by peer)` | Something cut the connection during the HTTPS step: a proxy, a firewall, or a busy server | Run it again. If it keeps happening only on your network, it's the network. (badssl.com does this now and then) |
| Works in the browser, fails in tests | The browser uses the company proxy or certificate; your tests don't | Ask IT for the proxy setting (`HTTPS_PROXY`) and the company certificate |
| Works on your computer, fails in the pipeline | The pipeline can't reach the test site (not on the VPN), or uses another address | Run `net_check.py` from the pipeline too, and compare |
| Works for you, fails for a colleague | Different network, VPN, or their own `localhost` | Remember: `localhost` is always "my own computer" |
| `OSError: [Errno 48] Address already in use` when starting the practice server | It's already running | Use it, or stop the other one |

When you're done: **Ctrl+C** stops the practice server.

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/arshaduzzaman-sm/myopensdet/tree/main/modules/infrastructure/networking_for_testers/templates).

=== "net_check.py"

    ```python
    --8<-- "modules/infrastructure/networking_for_testers/templates/net_kit/net_check.py"
    ```

=== "practice_server.py"

    ```python
    --8<-- "modules/infrastructure/networking_for_testers/templates/net_kit/practice_server.py"
    ```

## References

- [MDN: An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [MDN: Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [MDN: Using HTTP cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [badssl.com: test sites with broken HTTPS](https://badssl.com/)
- [Python: ssl module](https://docs.python.org/3/library/ssl.html)

Written for Python 3.13. Outputs captured November 2026. Links checked: November 2026.
