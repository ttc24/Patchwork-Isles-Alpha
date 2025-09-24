#!/usr/bin/env python3
"""Validate world JSON structure and basic authoring rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORLD = REPO_ROOT / "world" / "world.json"

TAGLESS_CONDITION_TYPES: Set[str | None] = {None, "has_item", "flag_eq", "rep_at_least", "missing_item"}


def load_world(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_keys(data: Dict[str, Any], keys: Iterable[str], errors: List[str], context: str) -> None:
    for key in keys:
        if key not in data:
            errors.append(f"Missing key '{key}' in {context}.")


def validate_world(world: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    ensure_keys(world, ("title", "nodes", "starts", "endings", "factions"), errors, "world")

    if not isinstance(world.get("factions"), list) or len(world.get("factions", [])) < 1:
        errors.append("Factions list must be present and non-empty.")

    if not isinstance(world.get("starts"), list) or len(world.get("starts", [])) < 1:
        errors.append("At least one start definition is required.")

    endings = set(world.get("endings", {}).keys())
    if len(endings) < 2:
        errors.append("Define at least two endings.")

    nodes = world.get("nodes", {})
    if not isinstance(nodes, dict):
        errors.append("'nodes' must be a dictionary.")
        return errors

    for start in world.get("starts", []):
        ensure_keys(start, ("title", "node", "tags"), errors, "start")
        if start.get("node") not in nodes:
            errors.append(f"Start references unknown node '{start.get('node')}'.")

    for node_id, node in nodes.items():
        ensure_keys(node, ("title", "text"), errors, f"node '{node_id}'")
        text = node.get("text", "")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"Node '{node_id}' must include descriptive text.")

        choices = node.get("choices")
        if node_id in endings:
            # Ending nodes may omit choices.
            continue

        if not isinstance(choices, list):
            errors.append(f"Node '{node_id}' must define a list of choices.")
            continue

        if not (3 <= len(choices) <= 5):
            errors.append(f"Node '{node_id}' must contain 3-5 choices (found {len(choices)}).")

        tag_gate_present = False
        tagless_present = False

        for idx, choice in enumerate(choices, start=1):
            if "text" not in choice:
                errors.append(f"Choice {idx} in node '{node_id}' is missing text.")
            target = choice.get("target")
            if not target:
                errors.append(f"Choice '{choice.get('text', idx)}' in node '{node_id}' is missing a target.")
            elif target not in nodes and target not in endings:
                errors.append(f"Choice '{choice.get('text', idx)}' in node '{node_id}' targets unknown node '{target}'.")

            condition = choice.get("condition")
            condition_type = None
            if isinstance(condition, dict):
                condition_type = condition.get("type")

            if condition_type == "has_tag":
                tag_gate_present = True
            elif condition_type in TAGLESS_CONDITION_TYPES:
                tagless_present = True
            elif condition is None:
                tagless_present = True

        if not tag_gate_present:
            errors.append(f"Node '{node_id}' must include at least one tag-gated choice.")
        if not tagless_present:
            errors.append(f"Node '{node_id}' must include at least one tagless choice (item/rep/flag/no condition).")

    return errors


def main(argv: List[str]) -> None:
    path = Path(argv[1]).resolve() if len(argv) > 1 else DEFAULT_WORLD
    world = load_world(path)
    errors = validate_world(world)
    if errors:
        print("Validation failed:")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)
    print(f"Validation passed for {path}.")


if __name__ == "__main__":
    main(sys.argv)
