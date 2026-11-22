# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""<One line: what this script does.>

Usage:
    python script_starter.py <input file> [--verbose]

Copy this file when you start a new helper script. Change the docstring,
the arguments and run(), and keep the rest.
"""

import argparse
import sys
from pathlib import Path


def run(path: Path, verbose: bool) -> int:
    """Do the work. Return 0 when all is well, 1 when you found a problem."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if verbose:
        print(f"Read {len(lines)} lines from {path.name}")
    print(f"{len(lines)} lines")
    return 0


def main(args: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", type=Path, help="the file to read")
    parser.add_argument("--verbose", action="store_true", help="say more about what happens")
    options = parser.parse_args(args)
    if not options.path.exists():
        print(f"No such file: {options.path}")
        return 2
    return run(options.path, options.verbose)


# This runs only when you start the file as a script, not when a test imports it.
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
