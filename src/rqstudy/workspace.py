"""Executable role programs and inheritance rules; weights and scoring live in the host."""
from __future__ import annotations


def instruction(text: str) -> str:
    """Represent a text-only edit as an executable instruction function."""
    return "def instruct(context):\n    return " + repr(text.strip())


ROOT = {
    "writer": instruction("Write a concise scientific manuscript based on the provided title and abstract. Explain the question, method, supporting evidence and limitations. Ground claims and numerical results in the supplied material."),
    "reviewer": instruction("Review the manuscript for a top ML venue. Identify its contribution and limitations, then decide whether to accept or reject it."),
    "meta": instruction("Improve the scientific writer, human-decision reviewer and procedure for making future improvements. Inspect the supplied ancestor training feedback and inherited programs. Make a specific, justified edit. When a selector is editable, consider how the program should choose productive archive parents."),
    "selector": "def select_parent(archive_snapshot, rng):\n    return rng.choice(archive_snapshot['nodes'])['id']",
}


def apply_changes(parent: dict, changes: dict, editable: bool) -> dict:
    """Copy the selected parent's programs; an omitted role inherits its exact source."""
    if not isinstance(changes, dict) or not changes:
        raise ValueError("No workspace edits")
    child = dict(parent)
    for role, value in changes.items():
        if role not in ROOT or (role == "selector" and not editable):
            raise ValueError(f"Undeclared editable role {role}")
        if not isinstance(value, str) or not value.strip() or len(value) > 16000:
            raise ValueError(f"Invalid source for {role}")
        value = value.strip()
        if role == "selector" or "def instruct(" in value:
            child[role] = value
        else:
            child[role] = instruction(value)
    if child == parent:
        raise ValueError("Unchanged workspace")
    return child
