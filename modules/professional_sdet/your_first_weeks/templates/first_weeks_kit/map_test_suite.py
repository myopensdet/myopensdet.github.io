# Template from myOpenSDET: https://myopensdet.github.io/
"""Map a pytest test suite you didn't write: how many tests and where, the fixtures and
where they live, markers, skipped tests and why, the settings it reads, fixed waits,
and the addresses it calls. It only reads the code; nothing is run.

    python map_test_suite.py path/to/their/tests
"""

import ast
import sys
from collections import Counter, defaultdict
from pathlib import Path

URL_START = ("http://", "https://")
ENV_CALLS = ("os.environ.get", "os.getenv")
SKIP_DIRS = {".venv", "venv", "node_modules", ".git", "__pycache__", "site-packages"}
CONFIG_FILES = ["pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini", "conftest.py",
                "requirements.txt", ".github/workflows", "Dockerfile", ".env.example"]  # fmt: skip


def dotted(node: ast.AST) -> str:
    """pytest.mark.skip -> 'pytest.mark.skip'."""
    if isinstance(node, ast.Call):
        return dotted(node.func)
    if isinstance(node, ast.Attribute):
        return f"{dotted(node.value)}.{node.attr}"
    if isinstance(node, ast.Name):
        return node.id
    return ""


def scope_of(decorator: ast.AST) -> str:
    for keyword in getattr(decorator, "keywords", []):
        if keyword.arg == "scope" and isinstance(keyword.value, ast.Constant):
            return keyword.value.value
    return "function"


def first_text(call: ast.Call) -> str:
    for arg in [*call.args, *(k.value for k in call.keywords if k.arg == "reason")]:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value
    return ""


class Map:
    def __init__(self) -> None:
        self.tests = Counter()
        self.fixtures = []
        self.markers = Counter()
        self.skips = []
        self.env = defaultdict(set)
        self.sleeps = []
        self.urls = Counter()

    def read(self, path: Path, root: Path) -> None:
        name = str(path.relative_to(root))
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=name)
        is_test_file = path.name.startswith("test_") or path.name.endswith("_test.py")
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                self.function(node, name, is_test_file)
            elif isinstance(node, ast.Call):
                self.call(node, name)
            elif isinstance(node, ast.Subscript) and dotted(node.value) == "os.environ":
                if isinstance(node.slice, ast.Constant):
                    self.env[node.slice.value].add(name)
            elif isinstance(node, ast.Constant) and str(node.value).startswith(URL_START):
                self.urls[node.value.split("/")[2]] += 1

    def function(self, node, name: str, is_test_file: bool) -> None:
        for decorator in node.decorator_list:
            label = dotted(decorator)
            if label.endswith("fixture"):
                self.fixtures.append((node.name, scope_of(decorator), name))
            elif ".mark." in label:
                marker = label.split(".mark.")[1]
                self.markers[marker] += 1
                if marker in ("skip", "skipif", "xfail"):
                    reason = first_text(decorator) if isinstance(decorator, ast.Call) else ""
                    self.skips.append((marker, node.name, reason, name))
        if is_test_file and node.name.startswith("test"):
            self.tests[name] += 1

    def call(self, node: ast.Call, name: str) -> None:
        label = dotted(node)
        if label in ("time.sleep", "sleep", "page.wait_for_timeout"):
            self.sleeps.append((name, node.lineno, ast.unparse(node)))
        elif label in ENV_CALLS and node.args and isinstance(node.args[0], ast.Constant):
            self.env[node.args[0].value].add(name)


def plural(count: int, word: str) -> str:
    return f"{count} {word}{'s' * (count != 1)}"


def main() -> int:
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        print("Usage: python map_test_suite.py <folder with the tests>")
        return 2
    root = Path(sys.argv[1])
    found = Map()
    broken = []
    files = [p for p in sorted(root.rglob("*.py")) if not SKIP_DIRS & set(p.parts)]
    for path in files:
        try:
            found.read(path, root)
        except SyntaxError as error:
            broken.append(f"{path.relative_to(root)}: line {error.lineno}")

    tests = sum(found.tests.values())
    print(f"== {root}: {plural(len(files), 'Python file')}, {plural(tests, 'test function')}")
    print("\n== Set-up files found")
    print("  " + ", ".join(c for c in CONFIG_FILES if (root / c).exists()) or "  none")
    print("\n== Tests per file")
    for name, count in found.tests.most_common():
        print(f"  {count:>3}  {name}")
    print("\n== Fixtures (name, scope, file)")
    for fixture, scope, name in sorted(found.fixtures, key=lambda f: f[2]):
        print(f"  {fixture:<22} {scope:<9} {name}")
    print("\n== Markers used")
    print("  " + ", ".join(f"{m} x{n}" for m, n in found.markers.most_common()) or "  none")
    print("\n== Skipped or expected to fail")
    for marker, test, reason, name in found.skips:
        print(f"  {marker:<7} {test} ({name}): {reason or 'NO REASON GIVEN'}")
    print("\n== Settings it reads (environment variables)")
    for variable in sorted(found.env):
        print(f"  {variable:<22} in {', '.join(sorted(found.env[variable]))}")
    print("\n== Fixed waits (often the cause of slow or flaky tests)")
    for name, line, code in found.sleeps:
        print(f"  {name}:{line}  {code}")
    print("\n== Addresses in the code")
    for host, count in found.urls.most_common():
        print(f"  {host} x{count}")
    for line in broken:
        print(f"\nCould not read {line} (not valid Python)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
