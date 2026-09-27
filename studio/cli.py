"""Command line interface for Studio."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .brand import write_brand
from .build import build_package, check_package, export_zip


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="studio", description="Build a fictional launch package from one brand token file.")
    commands = parser.add_subparsers(dest="command", required=True)

    new_brand = commands.add_parser("new-brand", help="generate deterministic fictional brand tokens")
    new_brand.add_argument("--seed", type=int, default=42, help="integer seed for reproducible brand choices")
    new_brand.add_argument("--out", type=Path, default=Path("brands/generated"), help="directory for tokens.json and reasoning.json")

    build = commands.add_parser("build", help="build, check, and zip a complete launch package")
    build.add_argument("--brand", type=Path, required=True, help="directory containing tokens.json and reasoning.json")
    build.add_argument("--out", type=Path, help="artifact directory, defaults to BRAND/launch")

    check = commands.add_parser("check", help="check a built package against its source tokens")
    check.add_argument("--brand", type=Path, required=True, help="directory containing tokens.json and reasoning.json")
    check.add_argument("--artifacts", type=Path, help="artifact directory, defaults to BRAND/launch")

    export = commands.add_parser("export", help="export a checked launch package as a deterministic ZIP")
    export.add_argument("--format", choices=("zip",), default="zip", help="archive format")
    export.add_argument("--brand", type=Path, required=True, help="directory containing tokens.json and reasoning.json")
    export.add_argument("--artifacts", type=Path, help="artifact directory, defaults to BRAND/launch")
    export.add_argument("--out", type=Path, help="archive destination, defaults beside the artifact directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "new-brand":
            token_path, reasoning_path = write_brand(args.out, args.seed)
            print(f"Created fictional brand tokens: {token_path}")
            print(f"Created reasoning log: {reasoning_path}")
            return 0
        if args.command == "build":
            out, archive = build_package(args.brand, args.out)
            print(f"Built and checked {out}")
            print(f"Exported {archive}")
            return 0
        if args.command == "check":
            report = check_package(args.brand, args.artifacts)
            if report["ok"]:
                print(f"PASS: {report['artifact_count']} fictional artifacts are consistent")
                return 0
            for issue in report["issues"]:
                print(f"FAIL: {issue}", file=sys.stderr)
            return 1
        if args.command == "export":
            artifact_dir = (args.artifacts or (args.brand / "launch")).resolve()
            report = check_package(args.brand, artifact_dir)
            if not report["ok"]:
                raise ValueError("package failed consistency checks: " + "; ".join(report["issues"]))
            archive_path = export_zip(artifact_dir, args.out)
            print(f"Exported {archive_path}")
            return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2

