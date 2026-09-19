"""Print a map of the shipbill package straight from its source code.

An AI assistant's description of a codebase is a set of claims. This script makes
the same kinds of claims mechanically, by parsing the code with Python's ast
module, so you have something to check the assistant against. It doesn't run any
of the code it reads.

    uv run codemap.py
"""

import ast
import sys
from collections import defaultdict
from pathlib import Path

PACKAGE = "shipbill"
ENTRY_POINTS = ["run_billing.py"]


def parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def module_name(path: Path) -> str:
    return path.stem if path.parent.name != PACKAGE else f"{PACKAGE}.{path.stem}"


def internal_imports(tree: ast.Module) -> set[str]:
    """Modules from the package that a file imports, in either import style."""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == PACKAGE:
            found.update(f"{PACKAGE}.{alias.name}" for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and (node.module or "").startswith(PACKAGE + "."):
            found.add(node.module)
        elif isinstance(node, ast.Import):
            found.update(a.name for a in node.names if a.name.startswith(PACKAGE + "."))
    return found


def external_imports(tree: ast.Module) -> set[str]:
    """Top-level names of everything imported from outside the package."""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.add(node.module.split(".")[0])
    return {name for name in found if name != PACKAGE}


def referenced_names(tree: ast.Module) -> set[str]:
    """Every bare name and attribute name used anywhere in a file."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    return names


def main() -> int:
    root = Path(__file__).resolve().parent
    package_files = sorted((root / PACKAGE).glob("*.py"))
    files = package_files + [root / name for name in ENTRY_POINTS]
    trees = {module_name(p): parse(p) for p in files}

    print("Imports inside the package (who depends on whom)")
    imported_by = defaultdict(set)
    for name, tree in trees.items():
        deps = sorted(internal_imports(tree))
        for dep in deps:
            imported_by[dep].add(name)
        print(f"  {name:<20} -> {', '.join(d.split('.')[-1] for d in deps) or '(nothing)'}")

    print("\nModules nothing imports")
    for name in trees:
        if name.startswith(PACKAGE + ".") and name not in imported_by and not name.endswith("__init__"):
            print(f"  {name}")

    print("\nOutside libraries")
    stdlib = set(sys.stdlib_module_names)
    for name, tree in trees.items():
        third_party = sorted(m for m in external_imports(tree) if m not in stdlib and m != "sample_data")
        if third_party:
            print(f"  {name:<20} uses {', '.join(third_party)}")

    print("\nTop-level functions that nothing calls (dead code candidates)")
    used_anywhere = {}
    for name, tree in trees.items():
        used_anywhere[name] = referenced_names(tree)
    for name, tree in trees.items():
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                callers = [m for m, used in used_anywhere.items() if node.name in used]
                if not callers and node.name != "main":
                    print(f"  {name}.{node.name}  (line {node.lineno})")

    print("\nModule state changed with 'global'")
    for name, tree in trees.items():
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Global):
                        print(f"  {name}.{', '.join(stmt.names)}  (set in {node.name}, line {stmt.lineno})")

    print("\nSQL built by gluing strings together (lines with + or % next to SQL)")
    for path in files:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            upper = line.upper()
            if any(k in upper for k in ("SELECT ", "WHERE ", "LIKE '")) and ("+" in line or "%" in line):
                print(f"  {path.relative_to(root).as_posix()}:{n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
