"""Tests for MDX generation from final.md."""

import textwrap

import pytest

from scripts.generate_mdx import (
 generate_mdx,
 map_frontmatter,
 transform_mermaid_blocks,
 validate_frontmatter,
 _extract_from_frontmatter_yaml,
)


class TestMapFrontmatter:
 def test_renames_description_to_excerpt(self):
 result = map_frontmatter({"description": "A summary"})
 assert "excerpt" in result
 assert "description" not in result
 assert result["excerpt"] == "A summary"

 def test_passes_through_standard_fields(self):
 meta = {
 "title": "My Post",
 "date": "2025-01-01",
 "author": "Tim",
 "category": "AI",
 "tags": ["a", "b"],
 }
 result = map_frontmatter(meta)
 assert result["title"] == "My Post"
 assert result["tags"] == ["a", "b"]

 def test_drops_unknown_fields(self):
 result = map_frontmatter({"title": "T", "word_count": 500})
 assert "word_count" not in result

 def test_preserves_field_order(self):
 meta = {
 "tags": ["a"],
 "title": "T",
 "date": "2025-01-01",
 "author": "A",
 "category": "C",
 "description": "D",
 }
 result = map_frontmatter(meta)
 keys = list(result.keys)
 assert keys == ["title", "date", "author", "category", "tags", "excerpt"]


class TestValidateFrontmatter:
 def test_all_present(self):
 meta = {
 "title": "T",
 "date": "D",
 "excerpt": "E",
 "category": "C",
 "author": "A",
 }
 assert validate_frontmatter(meta) == []

 def test_missing_fields(self):
 assert validate_frontmatter({"title": "T"}) == [
 "author",
 "category",
 "date",
 "excerpt",
 ]


class TestTransformMermaidBlocks:
 def test_converts_mermaid_block(self):
 content = textwrap.dedent("""\
 Some text.

 ```mermaid
 flowchart TD
 A --> B
 ```

 More text.
 """)
 result = transform_mermaid_blocks(content)
 assert "```mermaid" not in result
 assert '<MermaidDiagram chart={`flowchart TD' in result
 assert "`} />" in result
 assert "Some text." in result
 assert "More text." in result

 def test_no_mermaid_blocks(self):
 content = "Just plain text.\n\n```python\nprint('hi')\n```\n"
 assert transform_mermaid_blocks(content) == content

 def test_multiple_mermaid_blocks(self):
 content = "```mermaid\nA\n```\n\ntext\n\n```mermaid\nB\n```\n"
 result = transform_mermaid_blocks(content)
 assert result.count("MermaidDiagram") == 2


class TestExtractFromFrontmatterYaml:
 def test_extracts_fields(self):
 raw = {
 "title": "My Post",
 "date_created": "2025-01-01",
 "author": "Tim",
 "categories": ["ai-stuff", "tech"],
 "tags": ["a", "b"],
 }
 result = _extract_from_frontmatter_yaml(raw)
 assert result["title"] == "My Post"
 assert result["date"] == "2025-01-01"
 assert result["category"] == "Ai Stuff"
 assert result["tags"] == ["a", "b"]

 def test_falls_back_to_date_field(self):
 raw = {"date": "2025-06-01"}
 result = _extract_from_frontmatter_yaml(raw)
 assert result["date"] == "2025-06-01"


class TestGenerateMdx:
 def test_produces_valid_mdx(self):
 meta = {
 "title": "Test Post",
 "date": "2025-01-01",
 "author": "Tim",
 "category": "AI",
 "tags": ["a", "b"],
 "excerpt": "A test post",
 }
 content = "# Hello\n\nSome content."
 result = generate_mdx(meta, content)

 assert result.startswith("---\n")
 assert 'title: "Test Post"' in result
 assert 'excerpt: "A test post"' in result
 assert 'tags: ["a", "b"]' in result
 assert "# Hello" in result
 assert result.endswith("\n")
