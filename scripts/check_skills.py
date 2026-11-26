"""Check the skills in skills/ before release.

Frontmatter is parsed as real YAML and checked against the Agent Skills
specification. The script also checks that every expected skill is present,
that relative links resolve in the skills and the READMEs, and that shared
reference files are identical in every skill that contains them.

Usage:
    python scripts/check_skills.py              check the repository
    python scripts/check_skills.py --self-test  confirm the checks catch known breakages
    python scripts/check_skills.py --expected   print the expected skill names
"""

import re
import shutil
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent

# The skills this repository ships. A missing skill is an error, not a smaller count.
EXPECTED = ["refine-performance", "refine-structure"]

# Agent Skills specification: https://agentskills.io/specification
ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)")
FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)

# Files that must be identical in every skill that contains them.
SHARED = ["references/fact-ownership.md"]
READMES = ["README.md", "README.zh-CN.md"]


def read(path):
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def parse_frontmatter(text):
    """Return (fields, error). Exactly one of them is None."""
    if not text.startswith("---\n"):
        return None, "SKILL.md must start with a --- frontmatter line"
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, "frontmatter is not closed by a --- line"
    try:
        fields = yaml.safe_load(text[4:end])
    except yaml.YAMLError as e:
        return None, "frontmatter is not valid YAML: " + " ".join(str(e).split())
    if not isinstance(fields, dict):
        return None, "frontmatter must be a YAML mapping"
    return fields, None


def check_fields(skill, fields, errors):
    def err(msg):
        errors.append(f"{skill}: {msg}")

    extra = set(fields) - ALLOWED_FIELDS
    if extra:
        err(f"non-spec frontmatter fields {sorted(extra)}")

    name = fields.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        err(f"invalid name {name!r}")
    elif name != skill:
        err(f"name {name!r} does not match its directory")

    desc = fields.get("description")
    if not isinstance(desc, str) or not desc.strip():
        err("description must be a non-empty string")
    elif len(desc) > 1024:
        err(f"description has {len(desc)} characters; the limit is 1024")

    for key in ("license", "compatibility", "allowed-tools"):
        if key in fields and not isinstance(fields[key], str):
            err(f"{key} must be a string")
    if isinstance(fields.get("compatibility"), str) and len(fields["compatibility"]) > 500:
        err("compatibility has more than 500 characters")

    meta = fields.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            err("metadata must be a mapping")
        elif not all(isinstance(k, str) and isinstance(v, str) for k, v in meta.items()):
            err("metadata keys and values must be strings (quote numbers such as versions)")


def check_links(root, path, errors):
    text = FENCE_RE.sub("", read(path))
    for target in LINK_RE.findall(text):
        if re.match(r"^[a-z]+:", target):
            continue
        if not (path.parent / target).exists():
            errors.append(f"{path.relative_to(root).as_posix()}: broken link {target}")


def check(root):
    errors = []
    skill_dirs = sorted(p for p in (root / "skills").iterdir() if p.is_dir())

    found = {d.name for d in skill_dirs}
    for name in EXPECTED:
        if name not in found:
            errors.append(f"expected skill {name} is missing")
    for name in sorted(found - set(EXPECTED)):
        errors.append(f"skills/{name} is not in EXPECTED; add it there if it should ship")

    for d in skill_dirs:
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"{d.name}: SKILL.md is missing")
            continue
        text = read(skill_md)
        fields, error = parse_frontmatter(text)
        if error:
            errors.append(f"{d.name}: {error}")
        else:
            check_fields(d.name, fields, errors)
        lines = text.count("\n")
        if lines > 500:
            errors.append(f"{d.name}: SKILL.md has {lines} lines; keep it under 500")
        for md in [skill_md, *sorted(d.glob("references/*.md"))]:
            check_links(root, md, errors)

    for readme in READMES:
        if (root / readme).exists():
            check_links(root, root / readme, errors)

    for rel in SHARED:
        copies = [d / rel for d in skill_dirs if (d / rel).exists()]
        if len({read(c) for c in copies}) > 1:
            listed = ", ".join(c.relative_to(root).as_posix() for c in copies)
            errors.append(f"shared file {rel} differs between copies: {listed}")

    return errors, len(skill_dirs)


# Self-test: each case edits a fresh copy of the repository and names the error it
# must produce, or None if it must pass. A check that has never been seen to fail is
# not yet evidence, and one that fails for the wrong reason is not either.

def edit(rel, old, new):
    def apply(root):
        path = root / rel
        text = read(path)
        if old not in text:
            raise RuntimeError(f"self-test is stale: {old!r} not found in {rel}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
    return apply


def replace_line(rel, prefix, new):
    def apply(root):
        path = root / rel
        text, n = re.subn(rf"^{re.escape(prefix)}.*$", lambda _: new, read(path), count=1, flags=re.M)
        if not n:
            raise RuntimeError(f"self-test is stale: no line starting {prefix!r} in {rel}")
        path.write_text(text, encoding="utf-8", newline="\n")
    return apply


def delete(rel):
    def apply(root):
        path = root / rel
        shutil.rmtree(path) if path.is_dir() else path.unlink()
    return apply


STRUCTURE = "skills/refine-structure/SKILL.md"
LONG = " ".join(["word"] * 206)
CASES = [
    ("unchanged repository", None, lambda root: None),
    ("inline comment after name", None,
     edit(STRUCTURE, "name: refine-structure\n", "name: refine-structure  # comment\n")),
    ("short folded description", None,
     edit(STRUCTURE, "description: Run a deep", "description: >\n  Run a deep")),
    ("unquoted colon in description", "not valid YAML",
     edit(STRUCTURE, "description: Run a deep", "description: Run: a deep")),
    ("unclosed list in metadata", "not valid YAML",
     edit(STRUCTURE, 'version: "', 'version: ["')),
    ("empty folded description", "description must be a non-empty string",
     replace_line(STRUCTURE, "description:", "description: >")),
    ("folded description over 1024", "the limit is 1024",
     replace_line(STRUCTURE, "description:", f"description: >\n  {LONG}")),
    ("metadata as a list", "metadata must be a mapping",
     replace_line(STRUCTURE, "  version:", '  - "0.0.0"')),
    ("unquoted numeric version", "metadata keys and values must be strings",
     replace_line(STRUCTURE, "  version:", "  version: 0.2")),
    ("unknown frontmatter field", "non-spec frontmatter fields",
     edit(STRUCTURE, "license: MIT\n", "license: MIT\ndisable-model-invocation: true\n")),
    ("name differs from directory", "does not match its directory",
     edit(STRUCTURE, "name: refine-structure\n", "name: refine-structures\n")),
    ("missing SKILL.md", "SKILL.md is missing", delete(STRUCTURE)),
    ("missing skill directory", "expected skill refine-structure is missing",
     delete("skills/refine-structure")),
    ("broken link in a reference", "broken link",
     edit("skills/refine-structure/references/abstraction-judgment.md", "\n", "\n[x](nowhere.md)\n")),
    ("broken link in README", "broken link", edit("README.md", "\n", "\n[x](nowhere.md)\n")),
    ("drifted shared file", "differs between copies",
     edit("skills/refine-performance/references/fact-ownership.md", "\n", "\ndrift\n")),
]


def self_test():
    failures = 0
    for label, expected, mutate in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "skills", root / "skills")
            for name in [*READMES, "LICENSE"]:
                shutil.copy(ROOT / name, root / name)
            mutate(root)
            errors, _ = check(root)
        if expected is None:
            ok = not errors
        else:
            ok = any(expected in e for e in errors)
        failures += not ok
        want = "pass" if expected is None else f"fail with '{expected}'"
        print(f"{'ok  ' if ok else 'FAIL'} {label}: expected {want}")
        if not ok:
            for e in errors or ["(no errors)"]:
                print(f"       {e}")
    print(f"{len(CASES)} self-test cases, {failures} failures")
    return 1 if failures else 0


def main(argv):
    if "--expected" in argv:
        print("\n".join(EXPECTED))
        return 0
    if "--self-test" in argv:
        return self_test()
    errors, count = check(ROOT)
    for e in errors:
        print(f"error: {e}")
    print(f"{count} skills checked, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
