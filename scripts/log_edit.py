#!/usr/bin/env python3
"""
Append a single edit entry to the sidecar log at edits/.pending/<filename>.yaml.

Usage:
 python scripts/log_edit.py --file <path> --line <N> \
 --original <text> --edited <text> --reason <text> \
 [--rule <rule-id>] [--style blog|technical|whitepaper] [--flagged]

Called by the agent after each Edit tool call when /capture on is active.
Each invocation appends one entry to the sidecar file. The sidecar is
human-readable during editing sessions and merges into the final corpus
via /capture-edits.
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path

import yaml


def parse_args:
 p = argparse.ArgumentParser(
 description="Log a single edit entry to the sidecar append log"
 )
 p.add_argument("--file", required=True, help="Path of the file being edited")
 p.add_argument("--line", type=int, required=True, help="Line number of the edit")
 p.add_argument("--original", required=True, help="Original text before edit")
 p.add_argument("--edited", required=True, help="Edited text after edit")
 p.add_argument("--reason", required=True, help="Why the edit was made")
 p.add_argument("--rule", default=None, help="Style guide rule reference (e.g. blog.md#voice-active)")
 p.add_argument("--style", default=None, choices=["blog", "technical", "whitepaper", "marketing-narrative", "github-readme"],
 help="Content style type")
 p.add_argument("--flagged", action="store_true", help="Flag as important for rule extraction")
 return p.parse_args


def main:
 args = parse_args

 # Build the edit entry
 entry = {
 "original": args.original,
 "edited": args.edited,
 "line_number": args.line,
 "reason": args.reason,
 "editor_type": "agent",
 "timestamp": datetime.now(timezone.utc).isoformat,
 }
 if args.rule:
 entry["rule_applied"] = args.rule
 if args.style:
 entry["style"] = args.style
 if args.flagged:
 entry["flagged"] = True

 # Determine sidecar path
 pending_dir = Path("edits/.pending")
 pending_dir.mkdir(parents=True, exist_ok=True)
 stem = Path(args.file).stem
 sidecar = pending_dir / f"{stem}.yaml"

 # Load existing sidecar or create new
 if sidecar.exists:
 data = yaml.safe_load(sidecar.read_text) or {"source_file": args.file, "edits": []}
 else:
 data = {"source_file": args.file, "edits": []}

 # Auto-increment edit ID
 n = len(data.get("edits", [])) + 1
 entry["id"] = f"edit-{n:03d}"
 data.setdefault("edits", []).append(entry)

 # Write back
 sidecar.write_text(
 yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
 )

 print(f"Logged {entry['id']} to {sidecar}")


if __name__ == "__main__":
 main
