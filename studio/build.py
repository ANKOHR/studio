"""Build, inspect, and export deterministic fictional launch packages."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any

from .brand import REQUIRED_DECISIONS, load_brand, validate_reasoning
from .render import generate_artifacts


BUILD_VERSION = "studio.build/v1"
HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3,8})\b")
FONT_RE = re.compile(r"font-family\s*:\s*(?:\"([^\"]+)\"|'([^']+)'|([^;}]+))", re.IGNORECASE)
FONT_ATTR_RE = re.compile(r"font-family\s*=\s*(?:\"([^\"]+)\"|'([^']+)')", re.IGNORECASE)


def _canonical_hash(data: Any) -> str:
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _validate_tokens(tokens: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    company = tokens.get("company")
    if not isinstance(company, dict) or not all(isinstance(company.get(k), str) and company[k].strip() for k in ("name", "tagline", "positioning", "product_name")):
        issues.append("brand tokens need a company name, tagline, positioning statement, and product name")
    palette = tokens.get("palette")
    required_colors = ("primary", "ink", "paper", "accent", "muted")
    if not isinstance(palette, dict) or any(not isinstance(palette.get(k), str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", palette[k]) for k in required_colors):
        issues.append("brand palette needs six-digit hex values for primary, ink, paper, accent, and muted")
    typography = tokens.get("typography")
    if not isinstance(typography, dict) or any(not isinstance(typography.get(role), dict) or not typography[role].get("family") for role in ("display", "heading", "body", "mono")):
        issues.append("brand typography needs display, heading, body, and mono families")
    pillars = tokens.get("messaging_pillars")
    if not isinstance(pillars, list) or len(pillars) < 3 or any(not isinstance(p, dict) or not p.get("id") or not p.get("title") or not p.get("message") for p in pillars):
        issues.append("brand tokens need at least three complete messaging pillars")
    product = tokens.get("product")
    if not isinstance(product, dict) or not isinstance(product.get("screens"), list) or len(product["screens"]) != 3:
        issues.append("brand tokens need three product screens")
    return issues


def _reasoning_by_id(reasoning: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in reasoning["decisions"] if isinstance(record, dict) and isinstance(record.get("id"), str)}


def _prepare_output(output_dir: Path) -> None:
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        return
    if not output_dir.is_dir():
        raise ValueError(f"build output is not a directory: {output_dir}")
    existing = list(output_dir.iterdir())
    if not existing:
        return
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"refusing to replace non-Studio files in {output_dir}")
    try:
        old_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"refusing to replace an invalid Studio package in {output_dir}") from exc
    if old_manifest.get("schema_version") != BUILD_VERSION:
        raise ValueError(f"refusing to replace an unrecognized package in {output_dir}")
    for child in existing:
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def build_package(brand_dir: Path, output_dir: Path | None = None) -> tuple[Path, Path]:
    """Render a complete package and a sibling deterministic ZIP archive."""
    brand_dir = brand_dir.resolve()
    tokens, reasoning, _token_bytes = load_brand(brand_dir)
    token_issues = _validate_tokens(tokens)
    if token_issues:
        raise ValueError("invalid brand tokens: " + "; ".join(token_issues))
    reasoning_issues = validate_reasoning(reasoning)
    if reasoning_issues:
        raise ValueError("incomplete reasoning log: " + "; ".join(reasoning_issues))
    out = (output_dir or (brand_dir / "launch")).resolve()
    if out == brand_dir or brand_dir in out.parents:
        if out == brand_dir:
            raise ValueError("build output must be a child of the brand directory or a separate directory")
    artifacts = generate_artifacts(tokens)
    _prepare_output(out)
    for relative_path, content in artifacts.items():
        destination = out / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8", newline="\n")
    manifest = {
        "schema_version": BUILD_VERSION,
        "fictional": True,
        "label": "FICTIONAL CONCEPT",
        "company_name": tokens["company"]["name"],
        "tagline": tokens["company"]["tagline"],
        "token_version": tokens["schema_version"],
        "token_sha256": _canonical_hash(tokens),
        "reasoning_sha256": _canonical_hash(reasoning),
        "decision_ids": list(REQUIRED_DECISIONS),
        "artifacts": list(artifacts),
        "trace_counts": {
            relative: {
                "company_name": content.count(tokens["company"]["name"]),
                "tagline": content.count(tokens["company"]["tagline"]),
            }
            for relative, content in artifacts.items()
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    report = check_package(brand_dir, out)
    if not report["ok"]:
        raise ValueError("consistency check failed: " + "; ".join(report["issues"]))
    archive = out.parent / (out.name + ".zip")
    export_zip(out, archive)
    return out, archive


def check_package(brand_dir: Path, output_dir: Path | None = None) -> dict[str, Any]:
    brand_dir = brand_dir.resolve()
    tokens, reasoning, _token_bytes = load_brand(brand_dir)
    out = (output_dir or (brand_dir / "launch")).resolve()
    issues: list[str] = []
    issues.extend(_validate_tokens(tokens))
    issues.extend(validate_reasoning(reasoning))
    manifest_path = out / "manifest.json"
    if not manifest_path.is_file():
        return {"ok": False, "issues": [*issues, f"missing build manifest: {manifest_path}"]}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "issues": [*issues, f"invalid build manifest: {exc}"]}
    if manifest.get("schema_version") != BUILD_VERSION:
        issues.append("unsupported build manifest version")
    if manifest.get("fictional") is not True or manifest.get("label") != "FICTIONAL CONCEPT":
        issues.append("manifest must identify the package as fictional")
    if manifest.get("token_version") != tokens.get("schema_version") or manifest.get("token_sha256") != _canonical_hash(tokens):
        issues.append("package was built from a different token file, rebuild it")
    if manifest.get("reasoning_sha256") != _canonical_hash(reasoning):
        issues.append("package was built from a different reasoning log, rebuild it")
    decision_map = _reasoning_by_id(reasoning)
    listed_artifacts = manifest.get("artifacts")
    if not isinstance(listed_artifacts, list) or not listed_artifacts:
        return {"ok": False, "issues": [*issues, "manifest has no artifact list"]}
    expected_files = {str(path).replace("\\", "/") for path in listed_artifacts}
    trace_counts = manifest.get("trace_counts", {})
    actual_files = {path.relative_to(out).as_posix() for path in out.rglob("*") if path.is_file() and path.name != "manifest.json"}
    if expected_files != actual_files:
        missing = sorted(expected_files - actual_files)
        unexpected = sorted(actual_files - expected_files)
        if missing:
            issues.append("missing artifacts: " + ", ".join(missing))
        if unexpected:
            issues.append("unexpected files in package: " + ", ".join(unexpected))
    palette = {value.lower() for value in tokens.get("palette", {}).values() if isinstance(value, str)}
    font_families = {str(style["family"]).strip("\"'") for style in tokens.get("typography", {}).values() if isinstance(style, dict) and style.get("family")}
    company = tokens.get("company", {})
    for relative in sorted(expected_files & actual_files):
        path = out / relative
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(f"artifact is not readable UTF-8: {relative}: {exc}")
            continue
        if "FICTIONAL CONCEPT" not in content:
            issues.append(f"fictional label missing: {relative}")
        company_lines = re.findall(r"^Fictional company: (.*)$", content, re.MULTILINE)
        tagline_lines = re.findall(r"^Tagline: (.*)$", content, re.MULTILINE)
        if company_lines != [company.get("name")]:
            issues.append(f"company name trace mismatch: {relative}")
        if tagline_lines != [company.get("tagline")]:
            issues.append(f"tagline trace mismatch: {relative}")
        count_record = trace_counts.get(relative, {}) if isinstance(trace_counts, dict) else {}
        if content.count(str(company.get("name", ""))) != count_record.get("company_name"):
            issues.append(f"company name mismatch in artifact content: {relative}")
        if content.count(str(company.get("tagline", ""))) != count_record.get("tagline"):
            issues.append(f"tagline mismatch in artifact content: {relative}")
        refs_match = re.search(r"^Decision refs: (.*)$", content, re.MULTILINE)
        if not refs_match:
            issues.append(f"decision references missing: {relative}")
        else:
            refs = [part.strip() for part in refs_match.group(1).split(",") if part.strip()]
            if not refs or any(ref not in decision_map for ref in refs):
                issues.append(f"unknown decision reference: {relative}")
            required_refs = _required_refs(relative)
            if any(ref not in refs for ref in required_refs):
                issues.append(f"key reasoning references missing: {relative}")
        for color in HEX_RE.findall(content):
            if color.lower() not in palette:
                issues.append(f"off-palette color {color}: {relative}")
        for match in list(FONT_RE.finditer(content)) + list(FONT_ATTR_RE.finditer(content)):
            family = next((value for value in match.groups() if value is not None), "").strip().strip("\"'")
            if family and family not in font_families:
                issues.append(f"font family outside token type scale ({family}): {relative}")
        if "\u2014" in content:
            issues.append(f"em dash found in artifact: {relative}")
    voice = tokens.get("voice", {})
    markers = [str(word).casefold() for word in voice.get("check_words", [])]
    banned = [str(word).casefold() for word in voice.get("avoid_words", [])]
    for relative in ("editorial/launch-article.md", "campaign/launch-plan.md"):
        path = out / relative
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8").casefold()
        if markers and not any(re.search(r"\b" + re.escape(marker) + r"\b", content) for marker in markers):
            issues.append(f"voice spot check failed, no approved voice marker in {relative}")
        for term in banned:
            if re.search(r"\b" + re.escape(term) + r"\b", content):
                issues.append(f"voice spot check found avoided term {term}: {relative}")
    return {"ok": not issues, "issues": issues, "artifact_count": len(expected_files)}


def _required_refs(relative: str) -> tuple[str, ...]:
    if relative == "visual/mark.svg":
        return ("company_name", "visual_identity")
    if relative.startswith("visual/"):
        return ("visual_identity",)
    if relative.startswith("web/"):
        return ("company_name", "positioning", "messaging", "launch_narrative")
    if relative.startswith("product/") or relative.startswith("diagrams/"):
        return ("product_story", "messaging")
    if relative == "editorial/launch-article.md":
        return ("positioning", "messaging", "launch_narrative")
    if relative == "deck/investor-deck.html":
        return ("positioning", "messaging", "product_story", "campaign")
    if relative == "social/launch-announcement.svg":
        return ("launch_narrative", "company_name")
    if relative.startswith("social/"):
        return ("messaging", "company_name")
    if relative.startswith("ads/"):
        return ("messaging", "campaign")
    if relative == "video/storyboard.md":
        return ("visual_identity", "product_story", "launch_narrative")
    if relative == "campaign/launch-plan.md":
        return ("messaging", "launch_narrative", "campaign")
    if relative == "docs/brand-guide.md":
        return ("company_name", "positioning", "messaging", "visual_identity")
    return ()


def export_zip(output_dir: Path, archive_path: Path | None = None) -> Path:
    out = output_dir.resolve()
    target = (archive_path or (out.parent / (out.name + ".zip"))).resolve()
    if target == out or out in target.parents:
        raise ValueError("archive must be outside the package directory")
    if not (out / "manifest.json").is_file():
        raise ValueError(f"not a Studio package: {out}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".tmp")
    if temp.exists():
        temp.unlink()
    try:
        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(item for item in out.rglob("*") if item.is_file()):
                relative = path.relative_to(out).as_posix()
                info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                info.create_system = 3
                archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        temp.replace(target)
    except Exception:
        if temp.exists():
            temp.unlink()
        raise
    return target
