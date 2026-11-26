"""Check every skill in skills/ for spec compliance, broken links, and drifted shared files.

Usage: python scripts/check_skills.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

# Agent Skills specification: https://agentskills.io/specification
ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")
FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)

# Files that must be identical in every skill that contains them.
SHARED = ["references/fact-ownership.md"]


def read(path):
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    return None if end == -1 else text[4:end]


def top_level_fields(fm):
    fields = {}
    for line in fm.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip("\"'")
    return fields


def check_links(path, errors):
    text = FENCE_RE.sub("", read(path))
    for target in LINK_RE.findall(text):
        if re.match(r"^[a-z]+:", target):
            continue
        if not (path.parent / target).exists():
            errors.append(f"{path.relative_to(ROOT)}: broken link {target}")


def main():
    errors = []
    skill_dirs = sorted(p.parent for p in SKILLS.glob("*/SKILL.md"))
    if not skill_dirs:
        errors.append("no skills found under skills/")

    for d in skill_dirs:
        skill_md = d / "SKILL.md"
        text = read(skill_md)
        fm = frontmatter(text)
        if fm is None:
            errors.append(f"{skill_md.relative_to(ROOT)}: missing or malformed frontmatter")
            continue
        fields = top_level_fields(fm)
        extra = set(fields) - ALLOWED_FIELDS
        if extra:
            errors.append(f"{d.name}: non-spec frontmatter fields {sorted(extra)}")
        name = fields.get("name", "")
        if not NAME_RE.fullmatch(name) or len(name) > 64:
            errors.append(f"{d.name}: invalid name {name!r}")
        if name != d.name:
            errors.append(f"{d.name}: name {name!r} does not match directory")
        desc = fields.get("description", "")
        if not desc or len(desc) > 1024:
            errors.append(f"{d.name}: description must be 1-1024 characters (has {len(desc)})")
        lines = text.count("\n")
        if lines > 500:
            errors.append(f"{d.name}: SKILL.md has {lines} lines; keep it under 500")
        for md in [skill_md, *sorted(d.glob("references/*.md"))]:
            check_links(md, errors)

    for rel in SHARED:
        copies = [d / rel for d in skill_dirs if (d / rel).exists()]
        if len({read(c) for c in copies}) > 1:
            listed = ", ".join(str(c.relative_to(ROOT)) for c in copies)
            errors.append(f"shared file {rel} differs between copies: {listed}")

    for e in errors:
        print(f"error: {e}")
    print(f"{len(skill_dirs)} skills checked, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
