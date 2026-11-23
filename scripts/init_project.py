#!/usr/bin/env python3
"""Turn this template into your own project. Run it once, right after cloning.

    python3 scripts/init_project.py

It asks for the project name, author, etc. (or pass them as options, see
--help), then:

1. replaces the placeholder names in every text file
   (my-project, my_project, MY_PROJECT, My Project, Your Name, ...);
2. renames src/my_project/ to src/<your_package>/;
3. puts your name and the current year in LICENSE and CITATION.cff;
4. deletes TEMPLATE.md and this script (use --keep-script to keep them).

Only the standard library is used, so it runs before any venv exists, even
on an old system Python.
"""

from __future__ import annotations

import argparse
import datetime
import keyword
import pkgutil
import re
import subprocess
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_PACKAGE = "my_project"

# Folders that are never edited.
SKIP_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache",
    "build", "dist", "site", "node_modules", ".ipynb_checkpoints",
}  # fmt: skip

# Names that would shadow the standard library or common packages.
RESERVED = {
    "test", "tests", "src", "scripts", "docs", "data", "config", "utils",
    "numpy", "scipy", "pandas", "matplotlib", "pydantic", "pytest", "setuptools",
}  # fmt: skip


def run_git(*args: str) -> str:
    """Return git's output, or "" if git is unavailable."""
    try:
        out = subprocess.run(
            ["git", *args], capture_output=True, text=True, cwd=ROOT, timeout=10
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip()


def to_dist_name(name: str) -> str:
    """'Spin Qubit Analysis' -> 'spin-qubit-analysis'."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def to_title(name: str) -> str:
    """Keep a human title as typed; prettify a slug like 'spin-qubit-analysis'."""
    if re.search(r"[A-Z ]", name):
        return name.strip()
    return " ".join(w.capitalize() for w in re.split(r"[-_]+", name) if w)


def stdlib_modules() -> set[str]:
    """Names of standard-library modules."""
    if hasattr(sys, "stdlib_module_names"):  # Python 3.10+
        return set(sys.stdlib_module_names)
    stdlib_dir = sysconfig.get_paths()["stdlib"]
    found = {m.name for m in pkgutil.iter_modules([stdlib_dir])}
    return found | set(sys.builtin_module_names)


def check_package_name(package: str) -> str | None:
    """Return a problem description, or None if the name is fine."""
    if not package.isidentifier() or keyword.iskeyword(package):
        return f"'{package}' is not a valid Python identifier"
    if package in stdlib_modules() or package in RESERVED:
        return f"'{package}' would shadow an existing module; pick a more specific name"
    return None


def ask(prompt: str, default: str, interactive: bool) -> str:
    """Prompt for a value, falling back to the default."""
    if not interactive:
        return default
    answer = input(f"{prompt} [{default}]: ").strip()
    return answer or default


def text_files(root: Path):
    """Yield every editable text file below root."""
    for path in sorted(root.rglob("*")):
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS or part.endswith(".egg-info") for part in rel_parts):
            continue
        if not path.is_file() or path.resolve() == Path(__file__).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable
        yield path, text


def main(argv: list[str] | None = None) -> int:
    """Rename the template; return the exit code."""
    parser = argparse.ArgumentParser(
        description="Initialise a project from this template."
    )
    parser.add_argument(
        "--name", help="project name, e.g. 'Spin Qubit Analysis' or spin-qubit-analysis"
    )
    parser.add_argument("--package", help="import name (default: derived from --name)")
    parser.add_argument("--description", help="one-line description")
    parser.add_argument("--author", help="author's full name")
    parser.add_argument("--email", help="author's email")
    parser.add_argument(
        "--github", help="GitHub user or organisation that will host the repo"
    )
    parser.add_argument(
        "--yes", "-y", action="store_true", help="no prompts: use options/defaults"
    )
    parser.add_argument(
        "--keep-script", action="store_true", help="keep TEMPLATE.md and this script"
    )
    args = parser.parse_args(argv)

    if not (ROOT / "src" / OLD_PACKAGE).is_dir():
        print(
            f"src/{OLD_PACKAGE}/ not found: this project seems to be initialised already."
        )
        return 1

    interactive = not args.yes and sys.stdin.isatty()
    remote = run_git("remote", "get-url", "origin")
    gh_match = re.search(r"github\.com[:/]([^/]+)/", remote)

    name = args.name or ask("Project name", ROOT.name, interactive)
    dist = to_dist_name(name)
    package = args.package or ask(
        "Python package (import) name", dist.replace("-", "_"), interactive
    )
    problem = check_package_name(package)
    if problem:
        print(f"Error: {problem}. Use --package to choose another.")
        return 1
    title = to_title(name)
    description = args.description or ask(
        "One-line description", f"Analysis code for {title}.", interactive
    )
    author = args.author or ask(
        "Author", run_git("config", "user.name") or "Your Name", interactive
    )
    email = args.email or ask(
        "Email", run_git("config", "user.email") or "you@example.com", interactive
    )
    github = args.github or ask(
        "GitHub user/organisation",
        gh_match.group(1) if gh_match else "your-github-username",
        interactive,
    )

    replacements = {
        "my-project": dist,
        OLD_PACKAGE: package,
        OLD_PACKAGE.upper(): package.upper(),
        "My Project": title,
        "A short description of the project.": description,
        "Your Name": author,
        "you@example.com": email,
        "your-github-username": github,
    }
    print("\nAbout to apply:")
    for old, new in replacements.items():
        print(f"  {old!r:40} -> {new!r}")
    if interactive:
        answer = input("Proceed? [Y/n]: ").strip().lower()
        if answer not in ("", "y", "yes"):
            print("Aborted; nothing changed.")
            return 1

    # 1. Replace placeholders (one pass, longest match first, so no chaining).
    pattern = re.compile(
        "|".join(re.escape(k) for k in sorted(replacements, key=len, reverse=True))
    )
    changed = 0
    for path, text in text_files(ROOT):
        new_text = pattern.sub(lambda m: replacements[m.group(0)], text)
        if path.name == "LICENSE":
            new_text = re.sub(
                r"Copyright \(c\) \d{4}",
                f"Copyright (c) {datetime.date.today().year}",
                new_text,
            )
        if path.name == "CITATION.cff":
            given, _, family = author.rpartition(" ")
            new_text = new_text.replace(
                'family-names: "Name"', f'family-names: "{family or author}"'
            )
            given_line = f'given-names: "{given}"' if given else ""
            new_text = new_text.replace('given-names: "Your"', given_line)
            new_text = re.sub(r"\n[ \t]+\n", "\n", new_text)  # drop emptied line
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed += 1

    # 2. Rename the package folder.
    (ROOT / "src" / OLD_PACKAGE).rename(ROOT / "src" / package)

    # 3. Remove template-only files.
    if not args.keep_script:
        (ROOT / "TEMPLATE.md").unlink(missing_ok=True)
        Path(__file__).unlink()

    print(
        f"\nDone: updated {changed} files and renamed src/{OLD_PACKAGE} -> src/{package}."
    )
    print("\nNext steps:")
    print("  make setup      # create .venv, install everything, enable git hooks")
    print("  make format     # re-wrap any lines that the new names made too long")
    print("  make check      # lint + tests + docs should all pass")
    print('  git add -A && git commit -m "Initialise project from template"')
    if "python-project-template" in remote:
        print("\nNote: 'origin' still points at the template repository:")
        print("  git remote set-url origin <url-of-your-new-repo>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
