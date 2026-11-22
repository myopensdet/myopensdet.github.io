# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Check one address step by step and say where it breaks: the name, the connection,
the HTTPS certificate, or the answer. Also shows cookie flags and CORS. Python only.

    python net_check.py https://example.com
    python net_check.py http://127.0.0.1:8790/login --origin http://evil.example
    python net_check.py https://test.example.com --timeout 5
"""

import argparse
import http.client
import socket
import ssl
import sys
import time
from datetime import UTC, datetime
from urllib.parse import urlsplit

try:  # certifi's list of trusted certificates, if installed (it comes with requests)
    import certifi

    TRUSTED = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    TRUSTED = ssl.create_default_context()


def ms(start: float) -> str:
    return f"{(time.perf_counter() - start) * 1000:.0f} ms"


def check(url: str, timeout: float, origin: str | None) -> int:
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        print(f"Not a full address: {url!r}. Start with http:// or https://")
        return 2
    host, secure = parts.hostname, parts.scheme == "https"
    port = parts.port or (443 if secure else 80)
    print(f"Checking {url}")

    start = time.perf_counter()
    try:
        address = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)[0][4][0]
    except socket.gaierror as error:
        print(f"  1. Name      FAILED: {host} not found ({error.strerror})")
        print("     Check the spelling, your VPN, or ask which address the test site has.")
        return 1
    print(f"  1. Name      {host} -> {address} ({ms(start)})")

    start = time.perf_counter()
    try:
        sock = socket.create_connection((address, port), timeout=timeout)
    except TimeoutError:
        print(f"  2. Connect   FAILED: no answer on port {port} in {timeout:.0f} s")
        print("     A firewall or VPN may block it, or the server is down.")
        return 1
    except ConnectionRefusedError:
        print(f"  2. Connect   FAILED: port {port} refused")
        print("     Nothing is listening there: the app isn't running, or the port is wrong.")
        return 1
    print(f"  2. Connect   port {port} open ({ms(start)})")

    if secure:
        start = time.perf_counter()
        try:
            sock = TRUSTED.wrap_socket(sock, server_hostname=host)
        except ssl.SSLCertVerificationError as error:
            print(f"  3. HTTPS     FAILED: {error.verify_message}")
            print("     Don't click past this in a browser. Report it, with the address.")
            return 1
        except (ssl.SSLError, OSError) as error:
            print(f"  3. HTTPS     FAILED: the secure connection broke off ({error})")
            print("     A proxy, firewall or VPN may be in the way. Try another network.")
            return 1
        cert = sock.getpeercert()
        expires = datetime.fromtimestamp(ssl.cert_time_to_seconds(cert["notAfter"]), UTC)
        days = (expires - datetime.now(UTC)).days
        warning = "  <- renew soon!" if days < 30 else ""
        print(f"  3. HTTPS     certificate valid for {days} more days ({ms(start)}){warning}")
    sock.close()

    step = 4 if secure else 3
    connection_class = http.client.HTTPSConnection if secure else http.client.HTTPConnection
    extra = {"context": TRUSTED} if secure else {}
    connection = connection_class(host, port, timeout=timeout, **extra)
    headers = {"User-Agent": "net-check"} | ({"Origin": origin} if origin else {})
    start = time.perf_counter()
    try:
        connection.request("GET", parts.path or "/" + ("?" + parts.query if parts.query else ""),
                           headers=headers)  # fmt: skip
        answer = connection.getresponse()
        answer.read()
    except TimeoutError:
        print(f"  {step}. Answer    FAILED: connected, but no answer in {timeout:.0f} s")
        print("     The server is up but slow or stuck: an app problem, not the network.")
        return 1
    print(f"  {step}. Answer    {answer.status} {answer.reason} ({ms(start)})")
    if answer.getheader("Location"):
        print(f"     Sends you on to: {answer.getheader('Location')}")

    for cookie in answer.headers.get_all("Set-Cookie") or []:
        name = cookie.split("=", 1)[0]
        flags = cookie.lower()
        missing = [f for f in ("Secure", "HttpOnly", "SameSite") if f.lower() not in flags]
        note = f"missing {', '.join(missing)}" if missing else "Secure, HttpOnly, SameSite"
        print(f"     Cookie {name}: {note}")
    if origin:
        allowed = answer.getheader("Access-Control-Allow-Origin")
        credentials = answer.getheader("Access-Control-Allow-Credentials")
        print(f"     CORS for {origin}: Allow-Origin={allowed}, Allow-Credentials={credentials}")
    return 0 if answer.status < 500 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("url")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--origin", help="send this Origin header, to see the CORS answer")
    args = parser.parse_args()
    return check(args.url, args.timeout, args.origin)


if __name__ == "__main__":
    sys.exit(main())
