from __future__ import annotations

import json
import os


SKILL_ACTIVATION_TARGETS_ENV = "STET_SKILL_ACTIVATION_TARGETS_JSON"
_PREAMBLE_MARKER = "Stet staged skill activation requirement:"


def with_skill_activation_preamble(instruction: str) -> str:
    targets = _activation_targets()
    if not targets:
        return instruction
    if _PREAMBLE_MARKER in instruction:
        return instruction

    lines = [
        _PREAMBLE_MARKER,
        "Before doing any repository inspection or task work, load and apply the staged skill file(s) below.",
        "Read each listed SKILL.md file directly from /skills before using any matching native skill name.",
        "Do not satisfy this requirement with a host-global skill, a skill listing, or a similarly named skill.",
    ]
    for target in targets:
        path = target.get("path", "").strip()
        if not path:
            continue
        sha = target.get("sha256", "").strip()
        suffix = f" (sha256: {sha})" if sha else ""
        lines.append(f"- {path}{suffix}")
    if len(lines) == 4:
        return instruction
    return "\n".join(lines) + "\n\n" + instruction


def _activation_targets() -> list[dict[str, str]]:
    raw = os.environ.get(SKILL_ACTIVATION_TARGETS_ENV, "").strip()
    if not raw:
        return []
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(decoded, list):
        return []
    targets: list[dict[str, str]] = []
    for item in decoded:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        targets.append({
            "path": path,
            "sha256": str(item.get("sha256", "")).strip(),
        })
    return targets
