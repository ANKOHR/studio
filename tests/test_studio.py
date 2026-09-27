from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from studio.brand import generate_brand, write_brand
from studio.build import build_package, check_package


ROOT = Path(__file__).resolve().parents[1]


def make_brand(tmp_path: Path, seed: int = 42) -> tuple[Path, Path]:
    brand = tmp_path / "brand"
    write_brand(brand, seed)
    artifacts, _ = build_package(brand)
    return brand, artifacts


def test_brand_generation_reproducibility(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    write_brand(first, 42)
    write_brand(second, 42)
    assert (first / "tokens.json").read_bytes() == (second / "tokens.json").read_bytes()
    assert (first / "reasoning.json").read_bytes() == (second / "reasoning.json").read_bytes()
    assert generate_brand(42) == generate_brand(42)


def test_build_refuses_incomplete_reasoning_before_writing(tmp_path: Path) -> None:
    brand = tmp_path / "brand"
    write_brand(brand, 42)
    log_path = brand / "reasoning.json"
    reasoning = json.loads(log_path.read_text(encoding="utf-8"))
    reasoning["decisions"] = [item for item in reasoning["decisions"] if item["id"] != "messaging"]
    log_path.write_text(json.dumps(reasoning, indent=2) + "\n", encoding="utf-8")
    output = brand / "launch"
    with pytest.raises(ValueError, match="incomplete reasoning log.*messaging"):
        build_package(brand)
    assert not output.exists()


def test_checker_accepts_clean_build(tmp_path: Path) -> None:
    brand, artifacts = make_brand(tmp_path)
    report = check_package(brand, artifacts)
    assert report["ok"] is True
    assert report["artifact_count"] >= 20


def test_checker_catches_off_palette_color(tmp_path: Path) -> None:
    brand, artifacts = make_brand(tmp_path)
    path = artifacts / "web" / "landing-page.html"
    path.write_text(path.read_text(encoding="utf-8") + "\n<div style=\"color:#ff00ff\">Injected color</div>\n", encoding="utf-8")
    report = check_package(brand, artifacts)
    assert not report["ok"]
    assert any("off-palette color #ff00ff" in issue for issue in report["issues"])


def test_checker_catches_wrong_font(tmp_path: Path) -> None:
    brand, artifacts = make_brand(tmp_path)
    path = artifacts / "web" / "landing-page.html"
    path.write_text(path.read_text(encoding="utf-8") + "\n<div style=\"font-family: 'Unlisted Typeface'\">Injected font</div>\n", encoding="utf-8")
    report = check_package(brand, artifacts)
    assert not report["ok"]
    assert any("font family outside token type scale" in issue for issue in report["issues"])


def test_checker_catches_wrong_font_attribute_in_svg(tmp_path: Path) -> None:
    brand, artifacts = make_brand(tmp_path)
    path = artifacts / "visual" / "mark.svg"
    path.write_text(path.read_text(encoding="utf-8").replace("role=\"img\"", "font-family=\"Unlisted Typeface\" role=\"img\"", 1), encoding="utf-8")
    report = check_package(brand, artifacts)
    assert not report["ok"]
    assert any("font family outside token type scale" in issue for issue in report["issues"])


def test_checker_catches_tagline_mismatch(tmp_path: Path) -> None:
    brand, artifacts = make_brand(tmp_path)
    path = artifacts / "editorial" / "launch-article.md"
    content = path.read_text(encoding="utf-8")
    content = content.replace("Tagline: " + json.loads((brand / "tokens.json").read_text(encoding="utf-8"))["company"]["tagline"], "Tagline: Changed fictional line", 1)
    path.write_text(content, encoding="utf-8")
    report = check_package(brand, artifacts)
    assert not report["ok"]
    assert any("tagline trace mismatch" in issue for issue in report["issues"])


def test_primary_color_change_propagates_everywhere(tmp_path: Path) -> None:
    brand, artifacts = make_brand(tmp_path)
    token_path = brand / "tokens.json"
    tokens = json.loads(token_path.read_text(encoding="utf-8"))
    old_color = tokens["palette"]["primary"]
    new_color = "#0B7A69"
    tokens["palette"]["primary"] = new_color
    token_path.write_text(json.dumps(tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    artifacts, _ = build_package(brand)
    texts = [path.read_text(encoding="utf-8") for path in artifacts.rglob("*") if path.is_file()]
    assert all(old_color.lower() not in text.lower() for text in texts)
    visuals = [path for path in artifacts.rglob("*") if path.suffix in (".svg", ".html")]
    assert visuals
    assert all(new_color in path.read_text(encoding="utf-8") for path in visuals)
    visual_decision = next(item for item in json.loads((brand / "reasoning.json").read_text(encoding="utf-8"))["decisions"] if item["id"] == "visual_identity")
    assert visual_decision["chosen_option"] == new_color
    assert visual_decision["previous_choices"][0]["chosen_option"] == old_color
    assert check_package(brand, artifacts)["ok"]


def test_build_is_byte_deterministic_including_export(tmp_path: Path) -> None:
    brand = tmp_path / "brand"
    write_brand(brand, 19)
    first, first_zip = build_package(brand, tmp_path / "first-package")
    second, second_zip = build_package(brand, tmp_path / "second-package")
    first_files = {p.relative_to(first).as_posix(): p.read_bytes() for p in first.rglob("*") if p.is_file()}
    second_files = {p.relative_to(second).as_posix(): p.read_bytes() for p in second.rglob("*") if p.is_file()}
    assert first_files == second_files
    assert first_zip.read_bytes() == second_zip.read_bytes()


def test_cli_smoke_for_each_subcommand(tmp_path: Path) -> None:
    brand = tmp_path / "cli-brand"
    commands = [
        ["new-brand", "--seed", "7", "--out", str(brand)],
        ["build", "--brand", str(brand)],
        ["check", "--brand", str(brand)],
        ["export", "--format", "zip", "--brand", str(brand)],
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    for command in commands:
        result = subprocess.run([sys.executable, "-m", "studio", *command], cwd=ROOT, env=env, text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
    with zipfile.ZipFile(brand / "launch.zip") as archive:
        assert "manifest.json" in archive.namelist()


def test_generated_package_is_complete_and_fictional(tmp_path: Path) -> None:
    brand, artifacts = make_brand(tmp_path, 4)
    manifest = json.loads((artifacts / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["fictional"] is True
    assert "deck/investor-deck.html" in manifest["artifacts"]
    assert "diagrams/how-it-works.svg" in manifest["artifacts"]
    assert "product/inbox.html" in manifest["artifacts"]
    for relative in manifest["artifacts"]:
        content = (artifacts / relative).read_text(encoding="utf-8")
        assert "FICTIONAL CONCEPT" in content
        assert "Token version: studio.brand/v1" in content
        assert "Decision refs:" in content
        assert "\u2014" not in content
    assert check_package(brand, artifacts)["ok"]
