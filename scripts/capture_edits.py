#!/usr/bin/env python3
"""
Extract edits from AI-generated content and output as YAML corpus.

Usage:
 python scripts/capture_edits.py <file-path> <ai-draft-commit>

This script:
1. Diffs the specified file between the ai-draft commit and current state
2. Extracts edit pairs with sentence-level context
3. Merges sidecar data from edits/.pending/ if available (agent intent metadata)
4. Outputs structured YAML to edits/<date>-<filename>.yaml

The output format captures:
- Original and edited text
- Sentence-level context (sentence before, full sentences)
- Line numbers for reference
- Editorial intent: reason, rule_applied, editor_type, style, flagged
"""

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def get_file_at_commit(file_path: str, commit: str) -> str | None:
 """Get file contents at a specific commit."""
 try:
 result = subprocess.run(
 ["git", "show", f"{commit}:{file_path}"],
 capture_output=True,
 text=True,
 check=True,
 )
 return result.stdout
 except subprocess.CalledProcessError:
 return None


def get_current_file_content(file_path: str) -> str | None:
 """Get current file contents (working directory or HEAD)."""
 path = Path(file_path)
 if path.exists:
 return path.read_text

 # Try HEAD if file doesn't exist in working directory
 try:
 result = subprocess.run(
 ["git", "show", f"HEAD:{file_path}"],
 capture_output=True,
 text=True,
 check=True,
 )
 return result.stdout
 except subprocess.CalledProcessError:
 return None


def get_unified_diff(file_path: str, commit: str) -> str:
 """Get unified diff between commit and current state."""
 # Check if there are uncommitted changes
 result = subprocess.run(
 ["git", "diff", "--name-only", "--", file_path],
 capture_output=True,
 text=True,
 )
 has_uncommitted = bool(result.stdout.strip)

 if has_uncommitted:
 # Diff against working directory
 result = subprocess.run(
 ["git", "diff", commit, "--", file_path],
 capture_output=True,
 text=True,
 )
 else:
 # Diff against HEAD
 result = subprocess.run(
 ["git", "diff", commit, "HEAD", "--", file_path],
 capture_output=True,
 text=True,
 )

 return result.stdout


def split_into_sentences(text: str) -> list[str]:
 """Split text into sentences, treating markdown headings as sentence boundaries."""
 # First, handle markdown headings as sentence boundaries
 # Replace headings with a special marker
 text = re.sub(r"(^#{1,6}\s+.+$)", r"\1| ||SENT_BREAK| ||", text, flags=re.MULTILINE)

 # Split on sentence endings (. ! ?) followed by space or newline
 # But not on abbreviations like "e.g." or "i.e."
 sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])|(?<=\|\|\|SENT_BREAK\|\|\|)", text)

 # Clean up and filter
 cleaned = []
 for s in sentences:
 s = s.replace("| ||SENT_BREAK| ||", "").strip
 if s:
 cleaned.append(s)

 return cleaned


def find_sentence_context(lines: list[str], line_number: int) -> dict:
 """Find the sentence containing the line and the sentence before it."""
 # Join all lines into text
 full_text = "\n".join(lines)

 # Find the character position of our target line
 char_pos = sum(len(lines[i]) + 1 for i in range(line_number - 1))

 # Split into sentences
 sentences = split_into_sentences(full_text)

 # Find which sentence contains our position
 current_pos = 0
 target_sentence_idx = 0

 for i, sentence in enumerate(sentences):
 sentence_start = full_text.find(sentence, current_pos)
 sentence_end = sentence_start + len(sentence)

 if sentence_start <= char_pos <= sentence_end:
 target_sentence_idx = i
 break

 current_pos = sentence_end

 # Get the sentence before (if exists)
 sentence_before = ""
 if target_sentence_idx > 0:
 sentence_before = sentences[target_sentence_idx - 1]

 # Get full sentence
 full_sentence = sentences[target_sentence_idx] if target_sentence_idx < len(sentences) else ""

 return {
 "sentence_before": sentence_before,
 "full_sentence": full_sentence,
 }


def parse_unified_diff(diff_text: str, original_content: str, edited_content: str) -> list[dict]:
 """Parse unified diff and extract edit pairs with context."""
 edits = []
 edit_counter = 0

 original_lines = original_content.split("\n")
 edited_lines = edited_content.split("\n")

 # Parse diff hunks
 hunk_pattern = r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@"
 lines = diff_text.split("\n")

 current_orig_line = 0
 current_edit_line = 0
 in_hunk = False

 i = 0
 while i < len(lines):
 line = lines[i]

 # Check for hunk header
 hunk_match = re.match(hunk_pattern, line)
 if hunk_match:
 current_orig_line = int(hunk_match.group(1))
 current_edit_line = int(hunk_match.group(2))
 in_hunk = True
 i += 1
 continue

 if not in_hunk:
 i += 1
 continue

 # Look for paired changes (- followed by +)
 if line.startswith("-") and not line.startswith("---"):
 original_text = line[1:]

 # Look ahead for corresponding + line
 if i + 1 < len(lines) and lines[i + 1].startswith("+") and not lines[i + 1].startswith("+++"):
 edited_text = lines[i + 1][1:]

 # Skip if both are empty or whitespace-only
 if original_text.strip or edited_text.strip:
 # Get context from original file
 orig_context = find_sentence_context(original_lines, current_orig_line)
 edit_context = find_sentence_context(edited_lines, current_edit_line)

 edit_counter += 1
 edits.append({
 "id": f"edit-{edit_counter:03d}",
 "original": original_text.strip,
 "edited": edited_text.strip,
 "sentence_before": orig_context["sentence_before"],
 "full_sentence_original": orig_context["full_sentence"],
 "full_sentence_edited": edit_context["full_sentence"],
 "line_number": current_orig_line,
 "reason": None,
 "rule_applied": None,
 "editor_type": "human",
 "style": None,
 "flagged": False,
 "timestamp": None,
 })

 i += 2 # Skip both - and + lines
 current_orig_line += 1
 current_edit_line += 1
 continue

 # Standalone deletion
 current_orig_line += 1
 i += 1
 continue

 elif line.startswith("+") and not line.startswith("+++"):
 # Standalone addition
 current_edit_line += 1
 i += 1
 continue

 elif line.startswith(" "):
 # Context line
 current_orig_line += 1
 current_edit_line += 1
 i += 1
 continue

 else:
 i += 1

 return edits


def merge_sidecar(edits: list[dict], sidecar_path: Path) -> list[dict]:
 """Merge .pending sidecar entries into diff-extracted edits.

 Matches sidecar entries to diff entries by original/edited text.
 Sidecar entries that don't match any diff entry are appended as
 agent-only edits (edits not captured by the diff).
 """
 if not sidecar_path.exists:
 return edits

 sidecar_data = yaml.safe_load(sidecar_path.read_text) or {}
 sidecar_edits = sidecar_data.get("edits", [])
 if not sidecar_edits:
 return edits

 # Index sidecar by (original, edited) for matching
 sidecar_by_text = {}
 for entry in sidecar_edits:
 key = (entry.get("original", "").strip, entry.get("edited", "").strip)
 sidecar_by_text[key] = entry

 matched_keys = set
 intent_fields = ("reason", "rule_applied", "editor_type", "style", "flagged", "timestamp")

 for edit in edits:
 key = (edit["original"], edit["edited"])
 if key in sidecar_by_text:
 sidecar_entry = sidecar_by_text[key]
 for field in intent_fields:
 if field in sidecar_entry and sidecar_entry[field] is not None:
 edit[field] = sidecar_entry[field]
 matched_keys.add(key)

 # Append unmatched sidecar entries (agent edits not in diff)
 edit_counter = len(edits)
 for entry in sidecar_edits:
 key = (entry.get("original", "").strip, entry.get("edited", "").strip)
 if key not in matched_keys:
 edit_counter += 1
 edits.append({
 "id": f"edit-{edit_counter:03d}",
 "original": entry.get("original", "").strip,
 "edited": entry.get("edited", "").strip,
 "sentence_before": "",
 "full_sentence_original": "",
 "full_sentence_edited": "",
 "line_number": entry.get("line_number", 0),
 "reason": entry.get("reason"),
 "rule_applied": entry.get("rule_applied"),
 "editor_type": entry.get("editor_type", "agent"),
 "style": entry.get("style"),
 "flagged": entry.get("flagged", False),
 "timestamp": entry.get("timestamp"),
 })

 return edits


def capture_edits(
 file_path: str,
 ai_draft_commit: str,
 style: str | None = None,
 session_reason: str | None = None,
 source_repo: str | None = None,
) -> tuple[dict, int, int]:
 """Main function to capture edits between ai-draft and current state.

 Returns (corpus_dict, sidecar_count, flagged_count).
 """
 # Get original content at ai-draft commit
 original_content = get_file_at_commit(file_path, ai_draft_commit)
 if original_content is None:
 raise ValueError(f"Could not get file at commit {ai_draft_commit}")

 # Get current content
 current_content = get_current_file_content(file_path)
 if current_content is None:
 raise ValueError(f"Could not get current file content for {file_path}")

 # Get the diff
 diff_text = get_unified_diff(file_path, ai_draft_commit)
 if not diff_text.strip:
 corpus = {
 "source_file": file_path,
 "ai_draft_commit": ai_draft_commit,
 "captured_at": datetime.now(timezone.utc).isoformat,
 "editor_type": "human",
 "style": style,
 "session_reason": session_reason,
 "edits": [],
 "message": "No edits found since the AI draft.",
 }
 if source_repo:
 corpus["source_repo"] = source_repo
 return corpus, 0, 0

 # Parse the diff and extract edits
 edits = parse_unified_diff(diff_text, original_content, current_content)

 # Merge sidecar data if available (agent intent metadata)
 sidecar_path = Path("edits/.pending") / f"{Path(file_path).stem}.yaml"
 sidecar_count = 0
 flagged_count = 0
 if sidecar_path.exists:
 sidecar_data = yaml.safe_load(sidecar_path.read_text) or {}
 sidecar_edits = sidecar_data.get("edits", [])
 sidecar_count = len(sidecar_edits)
 flagged_count = sum(1 for e in sidecar_edits if e.get("flagged"))
 edits = merge_sidecar(edits, sidecar_path)

 corpus = {
 "source_file": file_path,
 "ai_draft_commit": ai_draft_commit,
 "captured_at": datetime.now(timezone.utc).isoformat,
 "editor_type": "human",
 "style": style,
 "session_reason": session_reason,
 "edits": edits,
 }
 if source_repo:
 corpus["source_repo"] = source_repo
 return corpus, sidecar_count, flagged_count


def archive_sidecar(file_path: str) -> Path | None:
 """Move sidecar to archive directory. Returns archive path or None."""
 stem = Path(file_path).stem
 sidecar_path = Path("edits/.pending") / f"{stem}.yaml"
 if not sidecar_path.exists:
 return None

 archive_dir = Path("edits/.pending/archive")
 archive_dir.mkdir(parents=True, exist_ok=True)
 date_str = datetime.now.strftime("%Y-%m-%d")
 archive_path = archive_dir / f"{date_str}-{stem}.yaml"
 shutil.move(str(sidecar_path), str(archive_path))
 return archive_path


def main:
 parser = argparse.ArgumentParser(
 description="Extract edits from AI-generated content and output as YAML corpus."
 )
 parser.add_argument("file_path", help="Path to the edited file")
 parser.add_argument("ai_draft_commit", help="Commit hash of the [ai-draft] commit")
 parser.add_argument("--style", choices=["blog", "technical", "whitepaper", "marketing-narrative"], default=None,
 help="Style type for this content")
 parser.add_argument("--session-reason", default=None,
 help="Why this editing session was performed")
 parser.add_argument("--archive", action="store_true",
 help="Archive sidecar after merge")
 parser.add_argument("--source-repo", default=None,
 help="Source repo path for cross-repo edit capture")
 args = parser.parse_args

 file_path = args.file_path
 path = Path(file_path)

 # Validate file exists in git
 if not path.exists:
 result = subprocess.run(
 ["git", "ls-files", file_path],
 capture_output=True,
 text=True,
 )
 if not result.stdout.strip:
 print(f"Error: File not found: {file_path}")
 sys.exit(1)

 # Capture edits
 try:
 result, sidecar_count, flagged_count = capture_edits(
 file_path, args.ai_draft_commit,
 style=args.style, session_reason=args.session_reason,
 source_repo=args.source_repo,
 )
 except ValueError as e:
 print(f"Error: {e}", file=sys.stderr)
 sys.exit(1)

 # Print sidecar merge summary to stderr
 if sidecar_count > 0:
 print(f"Merged {sidecar_count} sidecar entries ({flagged_count} flagged)", file=sys.stderr)

 # Generate output filename
 date_str = datetime.now.strftime("%Y-%m-%d")
 filename = path.stem
 output_dir = Path("edits")
 output_dir.mkdir(exist_ok=True)
 output_path = output_dir / f"{date_str}-{filename}.yaml"

 # Write YAML output
 with open(output_path, "w") as f:
 yaml.dump(result, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

 # Archive sidecar if requested
 if args.archive:
 archive_path = archive_sidecar(file_path)
 if archive_path:
 print(f"Sidecar archived: {archive_path}", file=sys.stderr)

 # Report results
 edit_count = len(result.get("edits", []))
 print(f"Captured {edit_count} edit(s)")
 print(f"Output: {output_path}")

 if edit_count > 0:
 print("\nSample edits:")
 for edit in result["edits"][:3]:
 print(f" - {edit['id']}: \"{edit['original'][:50]}...\" -> \"{edit['edited'][:50]}...\"")


if __name__ == "__main__":
 main
