"""Seeded fictional brand tokens and structured creative reasoning."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any


TOKEN_VERSION = "studio.brand/v1"
REQUIRED_DECISIONS = (
    "company_name",
    "positioning",
    "messaging",
    "visual_identity",
    "product_story",
    "launch_narrative",
    "campaign",
)

NAME_PARTS = (
    ("Alder", "Aster", "Bright", "Cedar", "Clear", "Common", "Field", "Juniper", "Kindred", "Lumen", "North", "Open", "River", "Tandem", "Waymark"),
    ("Atlas", "Frame", "Harbor", "House", "Loop", "Matter", "Method", "Signal", "Studio", "Thread", "Works"),
)
TAGLINES = (
    "Make room for better work",
    "A clearer path through the work",
    "Bring the next step into view",
    "Good work, with more room to think",
    "Make thoughtful work easier",
)
PALETTES = (
    {"primary": "#2457A7", "ink": "#172033", "paper": "#F5F2EA", "accent": "#E7A64B", "muted": "#D8E1EF"},
    {"primary": "#356B57", "ink": "#1C2B25", "paper": "#F2F4EE", "accent": "#E39A73", "muted": "#D9E6DD"},
    {"primary": "#674DA8", "ink": "#262138", "paper": "#F5F1F8", "accent": "#E5A94F", "muted": "#E2DDF0"},
    {"primary": "#B54F3E", "ink": "#34211D", "paper": "#FBF2EA", "accent": "#4F8278", "muted": "#F0DCD2"},
    {"primary": "#087E8B", "ink": "#173138", "paper": "#EFF7F5", "accent": "#D99553", "muted": "#D5E9E7"},
)
MARKS = ("orbit", "beacon", "woven grid", "open frame")
PRODUCT_NAMES = ("Fieldnotes", "Workroom", "Commonplace", "Signal Desk")


def _positioning(name: str, product_name: str) -> str:
    return f"{name} helps small product teams turn scattered feedback into clear next steps with {product_name}."


def generate_brand(seed: int) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return deterministic tokens and a matching assumption-based decision log."""
    rng = random.Random(seed)
    name = f"{rng.choice(NAME_PARTS[0])} {rng.choice(NAME_PARTS[1])}"
    tagline = rng.choice(TAGLINES)
    product_name = rng.choice(PRODUCT_NAMES)
    palette = dict(rng.choice(PALETTES))
    mark = rng.choice(MARKS)
    display_font = rng.choice(("Georgia", "Arial"))
    heading_font = rng.choice(("Arial", "Georgia"))
    body_font = rng.choice(("Arial", "Georgia"))
    mono_font = "Courier New"
    positioning = _positioning(name, product_name)
    pillars = [
        {"id": "clarity", "title": "Find the signal", "message": f"Bring the useful feedback together, so {name} can help your team see what matters."},
        {"id": "focus", "title": "Choose a next step", "message": f"Turn a long list of requests into a considered next move with {product_name}."},
        {"id": "continuity", "title": "Keep the context", "message": "Give decisions a home, so the reasons behind the work stay close to the work."},
    ]
    tokens: dict[str, Any] = {
        "schema_version": TOKEN_VERSION,
        "seed": seed,
        "fictional": True,
        "company": {
            "name": name,
            "tagline": tagline,
            "positioning": positioning,
            "product_name": product_name,
        },
        "messaging_pillars": pillars,
        "voice": {
            "attributes": ["clear", "grounded", "considerate"],
            "check_words": ["clear", "practical", "thoughtful"],
            "avoid_words": ["revolutionary", "guaranteed", "world-leading", "best-in-class"],
        },
        "palette": palette,
        "typography": {
            "display": {"family": display_font, "size_px": 56, "weight": 700},
            "heading": {"family": heading_font, "size_px": 32, "weight": 700},
            "body": {"family": body_font, "size_px": 16, "weight": 400},
            "mono": {"family": mono_font, "size_px": 13, "weight": 400},
        },
        "logo": {"concept": mark, "rotation_degrees": rng.choice((0, 15, 30, 45)), "unit_count": rng.choice((3, 4, 5))},
        "product": {
            "screens": [
                {"id": "inbox", "title": "Feedback inbox", "purpose": "Gather notes from the places your team already listens."},
                {"id": "themes", "title": "Themes", "purpose": "Group related requests and keep their context nearby."},
                {"id": "roadmap", "title": "Decision board", "purpose": "Connect a considered next step to the feedback behind it."},
            ]
        },
    }
    reasoning = generate_reasoning(tokens)
    return tokens, reasoning


def generate_reasoning(tokens: dict[str, Any]) -> dict[str, Any]:
    company = tokens["company"]
    pillar_titles = [pillar["title"] for pillar in tokens["messaging_pillars"]]
    decisions = [
        {
            "id": "company_name",
            "decision": "Choose a concise fictional company name.",
            "options_considered": [company["name"], "Aster Works", "Clear Harbor"],
            "chosen_option": company["name"],
            "rationale": "A paired, familiar-word name is easy to read and leaves room for the product to grow.",
            "basis": "assumption",
        },
        {
            "id": "positioning",
            "decision": "Describe the audience, problem, and product role in one sentence.",
            "options_considered": [company["positioning"], "Lead with a feature list", "Lead with a market category"],
            "chosen_option": company["positioning"],
            "rationale": "A direct audience and outcome statement is a useful starting point for a fictional launch.",
            "basis": "assumption",
        },
        {
            "id": "messaging",
            "decision": "Organize launch messaging around three practical product outcomes.",
            "options_considered": pillar_titles + ["Lead with technical features"],
            "chosen_option": pillar_titles,
            "rationale": "Clarity, focus, and continuity make the product story easy to carry across formats.",
            "basis": "assumption",
        },
        {
            "id": "visual_identity",
            "decision": "Choose a calm, high-contrast color and type system.",
            "options_considered": [tokens["palette"]["primary"], "A neutral-only palette", "A warm red palette"],
            "chosen_option": tokens["palette"]["primary"],
            "rationale": f"The {tokens['logo']['concept']} mark and selected palette give the fictional identity a recognizable visual anchor.",
            "basis": "assumption",
        },
        {
            "id": "product_story",
            "decision": "Show an inbox, theme view, and decision board as the core workflow.",
            "options_considered": [screen["title"] for screen in tokens["product"]["screens"]] + ["A reporting dashboard"],
            "chosen_option": [screen["title"] for screen in tokens["product"]["screens"]],
            "rationale": "The sequence connects incoming feedback to a recorded next step without implying unverified product results.",
            "basis": "assumption",
        },
        {
            "id": "launch_narrative",
            "decision": "Frame the launch around moving from scattered feedback to a clear next step.",
            "options_considered": [company["tagline"], "A feature-first announcement", "A scale-first announcement"],
            "chosen_option": company["tagline"],
            "rationale": "The narrative stays close to the positioning and avoids unsupported performance claims.",
            "basis": "assumption",
        },
        {
            "id": "campaign",
            "decision": "Use an educational campaign that demonstrates the workflow.",
            "options_considered": ["Show the workflow", "Lead with a discount", "Lead with a fictional metric"],
            "chosen_option": "Show the workflow",
            "rationale": "A practical walkthrough expresses the product idea without inventing customers or results.",
            "basis": "assumption",
        },
    ]
    return {"schema_version": "studio.reasoning/v1", "fictional": True, "decisions": decisions}


def validate_reasoning(reasoning: dict[str, Any]) -> list[str]:
    """Return structural issues that prevent a safe, traceable build."""
    issues: list[str] = []
    decisions = reasoning.get("decisions") if isinstance(reasoning, dict) else None
    if not isinstance(decisions, list):
        return ["reasoning log must contain a decisions list"]
    by_id: dict[str, dict[str, Any]] = {}
    for record in decisions:
        if isinstance(record, dict) and isinstance(record.get("id"), str):
            by_id[record["id"]] = record
    for decision_id in REQUIRED_DECISIONS:
        record = by_id.get(decision_id)
        if record is None:
            issues.append(f"missing reasoning entry: {decision_id}")
            continue
        for field in ("decision", "chosen_option", "rationale"):
            if not record.get(field):
                issues.append(f"reasoning entry {decision_id} has no {field}")
        if not isinstance(record.get("options_considered"), list) or not record["options_considered"]:
            issues.append(f"reasoning entry {decision_id} has no options_considered")
        if record.get("basis") not in ("evidence", "assumption"):
            issues.append(f"reasoning entry {decision_id} basis must be evidence or assumption")
    return issues


def synchronize_reasoning(tokens: dict[str, Any], reasoning: dict[str, Any]) -> bool:
    """Record token-driven choice changes while retaining their prior rationale."""
    by_id = {record["id"]: record for record in reasoning["decisions"] if isinstance(record, dict) and isinstance(record.get("id"), str)}
    choices = {
        "company_name": tokens["company"]["name"],
        "positioning": tokens["company"]["positioning"],
        "messaging": [pillar["title"] for pillar in tokens["messaging_pillars"]],
        "visual_identity": tokens["palette"]["primary"],
        "product_story": [screen["title"] for screen in tokens["product"]["screens"]],
        "launch_narrative": tokens["company"]["tagline"],
    }
    changed = False
    for decision_id, selected in choices.items():
        record = by_id[decision_id]
        previous = record["chosen_option"]
        if previous == selected:
            continue
        record.setdefault("previous_choices", []).append({
            "chosen_option": previous,
            "rationale": record["rationale"],
            "basis": record["basis"],
        })
        options = record.setdefault("options_considered", [])
        if selected not in options:
            options.append(selected)
        record["chosen_option"] = selected
        old_text = json.dumps(previous, ensure_ascii=False, sort_keys=True)
        new_text = json.dumps(selected, ensure_ascii=False, sort_keys=True)
        record["rationale"] = f"A token edit changed the selected value from {old_text} to {new_text}. This rebuild follows the token file. The rationale is an assumption."
        record["basis"] = "assumption"
        changed = True
    return changed


def write_brand(out_dir: Path, seed: int) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tokens, reasoning = generate_brand(seed)
    token_path = out_dir / "tokens.json"
    reasoning_path = out_dir / "reasoning.json"
    token_path.write_text(json.dumps(tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    reasoning_path.write_text(json.dumps(reasoning, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return token_path, reasoning_path


def load_brand(brand_dir: Path) -> tuple[dict[str, Any], dict[str, Any], bytes]:
    token_path = brand_dir / "tokens.json"
    reasoning_path = brand_dir / "reasoning.json"
    token_bytes = token_path.read_bytes()
    tokens = json.loads(token_bytes.decode("utf-8"))
    reasoning = json.loads(reasoning_path.read_text(encoding="utf-8"))
    if tokens.get("fictional") is not True:
        raise ValueError("brand tokens must identify the company as fictional")
    if tokens.get("schema_version") != TOKEN_VERSION:
        raise ValueError(f"unsupported token schema: {tokens.get('schema_version')}")
    return tokens, reasoning, token_bytes
