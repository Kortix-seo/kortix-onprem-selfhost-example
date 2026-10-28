#!/usr/bin/env python3
"""Print what each agent in a Kortix manifest may touch, and flag the wide ones.

Reads only the `agents:` map of kortix.yaml: that map is governance, and an
omitted connectors/secrets/kortix_permissions/skills grant resolves to "none"
(deny-by-default, manifest header). No dependencies.

Exit codes: 0 clean read, 3 at least one agent holds both connectors and
secrets (the grants a reviewer should read first), 2 the manifest is unreadable.
"""
from __future__ import annotations

import sys
from pathlib import Path

FULL, NONE = "all", "none"
GRANTS = ("connectors", "secrets", "kortix_permissions", "skills")


def parse_grants(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.rstrip() == "agents:"), None)
    if start is None:
        raise SystemExit("no top-level `agents:` map in the manifest")
    agents: list[dict[str, str]] = []
    for line in lines[start + 1:]:
        if line.strip() and not line.startswith(" "):
            break                      # back to the top level: the map ended
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        key, _, value = line.strip().partition(":")
        if indent == 2:
            agents.append({"agent": key.strip()})
        elif indent == 4 and agents:
            agents[-1][key.strip()] = value.split("#")[0].strip()
    for a in agents:
        for g in GRANTS:
            a.setdefault(g, NONE)      # deny-by-default
    return agents


def main(argv: list[str]) -> int:
    path = Path(argv[1] if len(argv) > 1 else "kortix.yaml")
    try:
        agents = parse_grants(path.read_text(encoding="utf-8"))
    except (OSError, SystemExit) as exc:
        print(f"cannot read {path}: {exc}", file=sys.stderr)
        return 2

    head = f"{'agent':<22}{'connectors':<13}{'secrets':<9}{'permissions':<13}{'skills':<8}"
    print(head)
    print("-" * len(head))
    wide = []
    for a in agents:
        print(f"{a['agent']:<22}{a['connectors']:<13}{a['secrets']:<9}"
              f"{a['kortix_permissions']:<13}{a['skills']:<8}")
        if a["connectors"] == FULL and a["secrets"] == FULL:
            wide.append(a["agent"])

    print()
    if wide:
        print(f"{len(wide)} of {len(agents)} agents reach every connector and every "
              f"secret: {', '.join(wide)}. Each one is a grant a reviewer reads first.")
        return 3
    print(f"There is no agent in {path.name} that reaches every connector and every secret.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
