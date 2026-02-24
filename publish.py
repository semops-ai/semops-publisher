#!/usr/bin/env python3
"""
Phase 1: Manual-First Blog Publishing CLI

Philosophy: Start manual, learn the workflow, automate what hurts.
"""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console


@click.group
def cli:
 """Blog publishing workflow - Phase 1: Manual & Learning"""
 pass


@cli.command
@click.argument("slug")
def new(slug: str):
 """Create a new post directory structure"""
 post_dir = Path("posts") / slug

 if post_dir.exists:
 console.print(f"[red]Error:[/red] Post directory already exists: {post_dir}")
 return

 # Create directory structure
 post_dir.mkdir(parents=True)
 (post_dir / "assets").mkdir

 # Create notes template
 notes_template = f"""# {slug.replace('-', ' ').title}

## Topic


## POV (Point of View)
What argument or perspective am I making?


## Key Points
-


## Knowledge Base & References
Topics for KB search (resolved automatically via RAG):
-

Optional pinned file references (read directly, bypassing KB):
-


## Initial Research Direction
What should the research agent focus on?


## Target Audience


## Publishing Goals
- Traffic-driving citations?
- Networking opportunities?
- Specific concepts to highlight?
"""

 (post_dir / "notes.md").write_text(notes_template)

 console.print(Panel(
 f"[green]✓[/green] Created post directory: [cyan]{post_dir}[/cyan]\n\n"
 f"Next steps:\n"
 f"1. Edit [cyan]{post_dir / 'notes.md'}[/cyan]\n"
 f"2. Run: [yellow]python publish.py research {slug}[/yellow]",
 title=f"New Post: {slug}",
 border_style="green"
 ))


@cli.command
@click.argument("slug")
def research(slug: str):
 """Run research phase for a post"""
 from agents.research import ResearchAgent

 post_dir = Path("posts") / slug
 notes_file = post_dir / "notes.md"

 if not notes_file.exists:
 console.print(f"[red]Error:[/red] Notes file not found: {notes_file}")
 console.print(f"Run: [yellow]python publish.py new {slug}[/yellow]")
 return

 console.print(Panel(
 f"Starting research for: [cyan]{slug}[/cyan]",
 border_style="blue"
 ))

 # Load notes
 notes_content = notes_file.read_text

 # Run research agent
 agent = ResearchAgent
 with console.status("[bold blue]Researching..."):
 research_output = agent.research(notes_content)

 # Save research output
 research_file = post_dir / "research.md"
 research_file.write_text(research_output)

 console.print(Panel(
 f"[green]✓[/green] Research complete!\n\n"
 f"Output saved to: [cyan]{research_file}[/cyan]\n\n"
 f"Next steps:\n"
 f"1. Review [cyan]{research_file}[/cyan]\n"
 f"2. Add any additional context to notes\n"
 f"3. Run: [yellow]python publish.py outline {slug}[/yellow]",
 title="Research Complete",
 border_style="green"
 ))


@cli.command
@click.argument("slug")
@click.option("--version", "-v", default=1, help="Outline version number")
def outline(slug: str, version: int):
 """Generate outline for a post"""
 from agents.outline import OutlineAgent

 post_dir = Path("posts") / slug
 notes_file = post_dir / "notes.md"
 research_file = post_dir / "research.md"

 if not research_file.exists:
 console.print(f"[red]Error:[/red] Research file not found: {research_file}")
 console.print(f"Run: [yellow]python publish.py research {slug}[/yellow]")
 return

 console.print(Panel(
 f"Generating outline v{version} for: [cyan]{slug}[/cyan]",
 border_style="blue"
 ))

 # Load inputs
 notes_content = notes_file.read_text
 research_content = research_file.read_text

 # Run outline agent
 agent = OutlineAgent
 with console.status("[bold blue]Generating outline..."):
 outline_output = agent.generate_outline(notes_content, research_content)

 # Save outline
 outline_file = post_dir / f"outline_v{version}.md"
 outline_file.write_text(outline_output)

 console.print(Panel(
 f"[green]✓[/green] Outline v{version} complete!\n\n"
 f"Output saved to: [cyan]{outline_file}[/cyan]\n\n"
 f"Next steps:\n"
 f"1. Review outline\n"
 f"2. Iterate with: [yellow]python publish.py outline {slug} -v {version + 1}[/yellow]\n"
 f"3. When satisfied, copy to: [cyan]{post_dir / 'outline_final.md'}[/cyan]\n"
 f"4. Then run: [yellow]python publish.py draft {slug}[/yellow]",
 title=f"Outline v{version} Complete",
 border_style="green"
 ))


@cli.command
@click.argument("slug")
def draft(slug: str):
 """Generate draft from final outline"""
 from agents.draft import DraftAgent

 post_dir = Path("posts") / slug
 outline_file = post_dir / "outline_final.md"

 if not outline_file.exists:
 console.print(f"[red]Error:[/red] Final outline not found: {outline_file}")
 console.print("Create outline_final.md from your best outline version")
 return

 console.print(Panel(
 f"Generating draft for: [cyan]{slug}[/cyan]",
 border_style="blue"
 ))

 # Load outline
 outline_content = outline_file.read_text

 # Load style references (if available)
 style_refs = []
 refs_dir = Path("posts") / "_references"
 if refs_dir.exists:
 for ref_file in refs_dir.glob("*.md"):
 style_refs.append(ref_file.read_text)

 # Run draft agent
 agent = DraftAgent
 with console.status("[bold blue]Generating draft..."):
 draft_output = agent.generate_draft(outline_content, style_refs)

 # Save draft
 draft_file = post_dir / "draft.md"
 draft_file.write_text(draft_output)

 console.print(Panel(
 f"[green]✓[/green] Draft complete!\n\n"
 f"Output saved to: [cyan]{draft_file}[/cyan]\n\n"
 f"Next steps:\n"
 f"1. Edit and refine draft\n"
 f"2. Save final version as: [cyan]{post_dir / 'final.md'}[/cyan]\n"
 f"3. Run: [yellow]python publish.py format {slug}[/yellow]",
 title="Draft Complete",
 border_style="green"
 ))


@cli.command
@click.argument("slug")
def format(slug: str):
 """Format final draft for publishing platforms"""
 from agents.formatter import FormatterAgent

 post_dir = Path("posts") / slug
 final_file = post_dir / "final.md"

 if not final_file.exists:
 console.print(f"[red]Error:[/red] Final draft not found: {final_file}")
 console.print(f"Edit {post_dir / 'draft.md'} and save as final.md")
 return

 console.print(Panel(
 f"Formatting for publishing: [cyan]{slug}[/cyan]",
 border_style="blue"
 ))

 # Load final draft
 final_content = final_file.read_text

 # Run formatter agent
 agent = FormatterAgent
 with console.status("[bold blue]Formatting for platforms..."):
 linkedin, frontmatter = agent.format_for_platforms(
 final_content, slug
 )

 # Save formatted outputs
 (post_dir / "linkedin.md").write_text(linkedin)
 (post_dir / "frontmatter.yaml").write_text(frontmatter)

 console.print(Panel(
 f"[green]✓[/green] Formatting complete!\n\n"
 f"Files created:\n"
 f" • [cyan]linkedin.md[/cyan] - Ready for LinkedIn\n"
 f" • [cyan]frontmatter.yaml[/cyan] - For semops-core\n\n"
 f"Next steps:\n"
 f"1. Post [cyan]linkedin.md[/cyan] to LinkedIn\n"
 f"2. Publish to semops-sites via ingestion script ",
 title="Ready to Publish!",
 border_style="green"
 ))


@cli.command
@click.argument("slug")
def status(slug: str):
 """Check status of a post"""
 post_dir = Path("posts") / slug

 if not post_dir.exists:
 console.print(f"[red]Error:[/red] Post not found: {slug}")
 return

 # Check which files exist
 files = {
 "notes.md": "📝 Notes",
 "research.md": "🔍 Research",
 "outline_final.md": "📋 Final Outline",
 "draft.md": "✍️ Draft",
 "final.md": "✅ Final",
 "linkedin.md": "💼 LinkedIn",
 "frontmatter.yaml": "📋 Frontmatter",
 }

 status_lines = [f"\n[bold]Post:[/bold] {slug}\n"]

 for filename, label in files.items:
 file_path = post_dir / filename
 if file_path.exists:
 status_lines.append(f" [green]✓[/green] {label}")
 else:
 status_lines.append(f" [dim]○[/dim] {label}")

 # Check for outline versions
 outline_versions = list(post_dir.glob("outline_v*.md"))
 if outline_versions:
 status_lines.append(f"\n [cyan]Outline versions:[/cyan] {len(outline_versions)}")

 # Check for assets
 assets = list((post_dir / "assets").glob("*"))
 if assets:
 status_lines.append(f" [cyan]Assets:[/cyan] {len(assets)} files")

 console.print(Panel(
 "\n".join(status_lines),
 title=f"Status: {slug}",
 border_style="cyan"
 ))


@cli.command
def list:
 """List all posts"""
 posts_dir = Path("posts")

 if not posts_dir.exists:
 console.print("[yellow]No posts directory found[/yellow]")
 return

 posts = [p for p in posts_dir.iterdir if p.is_dir and not p.name.startswith("_")]

 if not posts:
 console.print("[yellow]No posts found[/yellow]")
 return

 console.print("\n[bold]Posts:[/bold]\n")
 for post in sorted(posts):
 # Quick status check
 has_final = (post / "final.md").exists
 has_linkedin = (post / "linkedin.md").exists

 if has_linkedin:
 status = "[green]Ready to publish[/green]"
 elif has_final:
 status = "[yellow]Final draft[/yellow]"
 else:
 status = "[cyan]In progress[/cyan]"

 console.print(f" • {post.name}: {status}")

 console.print


if __name__ == "__main__":
 cli
