#!/usr/bin/env python3
"""
Export markdown files to PDF using Pandoc with custom LaTeX templates.

Usage:
    uv run scripts/export_pdf.py input.md -o output.pdf
    uv run scripts/export_pdf.py input.md --template semops
    uv run scripts/export_pdf.py docs/*.md --outdir pdfs/

Features:
    - Mermaid diagram rendering (requires mermaid-cli: npm install -g @mermaid-js/mermaid-cli)
    - Custom LaTeX templates from semops-sites design system
    - Syntax highlighting for code blocks

Diagram Support:
    Mermaid diagrams in fenced code blocks are automatically rendered to PNG:

    ```mermaid
    flowchart LR
        A[Markdown] --> B[PDF]
    ```
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import click


# Templates live in semops-sites design system (ADR-0005)
TEMPLATES_DIR = Path(os.environ.get("SEMOPS_SITES_DIR", "../semops-sites")) / "packages" / "pdf-templates"
MERMAID_CONFIG = TEMPLATES_DIR / "mermaid-config.json"
PUPPETEER_CONFIG = TEMPLATES_DIR / "puppeteer-config.json"
DEFAULT_TEMPLATE = "semops"


def get_template_path(template_name: str) -> Path:
    """Get the path to a template file."""
    template_path = TEMPLATES_DIR / f"{template_name}.latex"
    if not template_path.exists():
        available = [f.stem for f in TEMPLATES_DIR.glob("*.latex")]
        raise click.ClickException(
            f"Template '{template_name}' not found. Available: {', '.join(available)}"
        )
    return template_path


def find_mmdc() -> Path | None:
    """Find mermaid-cli (mmdc) executable."""
    mmdc = shutil.which("mmdc")
    if mmdc:
        return Path(mmdc)
    return None


def render_mermaid_diagram(
    mmdc_path: Path,
    mermaid_code: str,
    output_file: Path,
    verbose: bool = False,
) -> bool:
    """Render a Mermaid diagram to PNG."""
    # Write mermaid code to temp file
    input_file = output_file.with_suffix(".mmd")
    input_file.write_text(mermaid_code)

    cmd = [
        str(mmdc_path),
        "-i", str(input_file),
        "-o", str(output_file),
        "-b", "white",  # White background for PDF
        "-s", "2",  # Scale factor for crisp output
    ]

    # Use custom mermaid config if available
    if MERMAID_CONFIG.exists():
        cmd.extend(["-c", str(MERMAID_CONFIG)])

    # Use puppeteer config if available (needed for --no-sandbox on Ubuntu)
    if PUPPETEER_CONFIG.exists():
        cmd.extend(["-p", str(PUPPETEER_CONFIG)])

    if verbose:
        click.echo(f"    Rendering Mermaid diagram -> {output_file.name}", err=True)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return output_file.exists()
    except subprocess.CalledProcessError as e:
        if verbose:
            click.echo(f"    Mermaid error: {e.stderr}", err=True)
        return False
    except subprocess.TimeoutExpired:
        if verbose:
            click.echo("    Mermaid timeout", err=True)
        return False
    finally:
        # Clean up temp .mmd file
        if input_file.exists():
            input_file.unlink()


def process_mermaid_in_markdown(
    input_path: Path,
    work_dir: Path,
    mmdc_path: Path | None,
    verbose: bool = False,
) -> Path:
    """
    Process markdown file, rendering Mermaid code blocks to PNG images.

    Returns path to processed markdown (may be original if no changes needed).
    """
    content = input_path.read_text()

    # Find mermaid code blocks: ```mermaid ... ```
    mermaid_pattern = r'```mermaid\n(.*?)```'
    matches = list(re.finditer(mermaid_pattern, content, re.DOTALL))

    if not matches:
        return input_path  # No mermaid diagrams

    if not mmdc_path:
        click.echo("  Warning: Mermaid diagrams found but mmdc not installed", err=True)
        click.echo("  Install: npm install -g @mermaid-js/mermaid-cli", err=True)
        return input_path

    # Process each mermaid block
    new_content = content
    rendered_count = 0

    for i, match in enumerate(matches):
        mermaid_code = match.group(1).strip()
        png_name = f"mermaid-{i}.png"
        png_path = work_dir / png_name

        if render_mermaid_diagram(mmdc_path, mermaid_code, png_path, verbose):
            # Replace mermaid block with image reference
            old_block = match.group(0)
            new_block = f"![Diagram]({png_path})"
            new_content = new_content.replace(old_block, new_block, 1)
            rendered_count += 1
        else:
            click.echo(f"  Warning: Failed to render Mermaid diagram {i + 1}", err=True)

    if rendered_count > 0:
        # Write processed markdown to work directory
        processed_md = work_dir / input_path.name
        processed_md.write_text(new_content)
        click.echo(f"  Rendered {rendered_count} Mermaid diagram(s)", err=True)
        return processed_md

    return input_path


def check_dependencies() -> Path | None:
    """Check that required system dependencies are installed. Returns mmdc path if found."""
    # Check pandoc
    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        version_line = result.stdout.split("\n")[0]
        click.echo(f"  Found {version_line}", err=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise click.ClickException(
            "pandoc not found. Install with: sudo apt install pandoc"
        )

    # Check xelatex
    try:
        result = subprocess.run(
            ["xelatex", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        version_line = result.stdout.split("\n")[0]
        click.echo(f"  Found {version_line}", err=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise click.ClickException(
            "xelatex not found. Install with: sudo apt install texlive-xetex"
        )

    # Check mermaid-cli (optional)
    mmdc_path = find_mmdc()
    if mmdc_path:
        click.echo(f"  Found mermaid-cli: {mmdc_path}", err=True)
    else:
        click.echo("  mermaid-cli not found (optional - install: npm install -g @mermaid-js/mermaid-cli)", err=True)

    return mmdc_path


def export_single(
    input_path: Path,
    output_path: Path,
    template: str,
    toc: bool = False,
    verbose: bool = False,
    mmdc_path: Path | None = None,
) -> bool:
    """Export a single markdown file to PDF."""
    template_path = get_template_path(template)

    # Create temp directory for diagram renders
    with tempfile.TemporaryDirectory() as tmp_dir:
        work_dir = Path(tmp_dir)

        # Process any Mermaid diagrams in the markdown
        processed_input = process_mermaid_in_markdown(
            input_path, work_dir, mmdc_path, verbose
        )

        cmd = [
            "pandoc",
            str(processed_input),
            "-o",
            str(output_path),
            "--pdf-engine=xelatex",
            f"--template={template_path}",
            "--highlight-style=tango",
            "-V",
            "colorlinks=true",
        ]

        if toc:
            cmd.append("--toc")

        if verbose:
            click.echo(f"  Command: {' '.join(cmd)}", err=True)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            if verbose and result.stderr:
                click.echo(f"  {result.stderr}", err=True)
            return True
        except subprocess.CalledProcessError as e:
            click.echo(f"  Error: {e.stderr}", err=True)
            return False


@click.command()
@click.argument("inputs", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output PDF path (for single file)",
)
@click.option(
    "--outdir",
    type=click.Path(path_type=Path),
    help="Output directory (for batch export)",
)
@click.option(
    "-t",
    "--template",
    default=DEFAULT_TEMPLATE,
    help=f"Template name (default: {DEFAULT_TEMPLATE})",
)
@click.option("--toc", is_flag=True, help="Include table of contents")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
@click.option("--check", is_flag=True, help="Check dependencies and exit")
def main(
    inputs: tuple[Path, ...],
    output: Path | None,
    outdir: Path | None,
    template: str,
    toc: bool,
    verbose: bool,
    check: bool,
):
    """Export markdown to PDF with custom templates.

    Examples:

        # Single file with explicit output
        uv run scripts/export_pdf.py proposal.md -o proposal.pdf

        # Single file with default output (same name, .pdf extension)
        uv run scripts/export_pdf.py proposal.md

        # Batch export to directory
        uv run scripts/export_pdf.py docs/*.md --outdir pdfs/

        # Use different template
        uv run scripts/export_pdf.py bio.md --template timjmitchell
    """
    click.echo("PDF Export", err=True)
    click.echo("=" * 40, err=True)

    # Check dependencies
    click.echo("\nChecking dependencies...", err=True)
    mmdc_path = check_dependencies()

    if check:
        click.echo("\nDependencies OK!", err=True)
        return

    if not inputs:
        raise click.ClickException("No input files specified")

    # Validate template exists
    template_path = get_template_path(template)
    click.echo(f"\nTemplate: {template} ({template_path})", err=True)

    # Handle single file vs batch
    if len(inputs) == 1 and output:
        # Single file with explicit output
        input_path = inputs[0]
        click.echo(f"\nExporting: {input_path} -> {output}", err=True)
        if export_single(input_path, output, template, toc, verbose, mmdc_path):
            click.echo(f"  ✓ Created {output}", err=True)
        else:
            sys.exit(1)

    elif len(inputs) == 1 and not output and not outdir:
        # Single file with default output
        input_path = inputs[0]
        output = input_path.with_suffix(".pdf")
        click.echo(f"\nExporting: {input_path} -> {output}", err=True)
        if export_single(input_path, output, template, toc, verbose, mmdc_path):
            click.echo(f"  ✓ Created {output}", err=True)
        else:
            sys.exit(1)

    else:
        # Batch export
        if not outdir:
            outdir = Path(".")

        outdir.mkdir(parents=True, exist_ok=True)
        click.echo(f"\nBatch export to: {outdir}", err=True)

        success = 0
        failed = 0

        for input_path in inputs:
            output_path = outdir / input_path.with_suffix(".pdf").name
            click.echo(f"  {input_path.name} -> {output_path.name}", err=True)

            if export_single(input_path, output_path, template, toc, verbose, mmdc_path):
                click.echo(f"    ✓ OK", err=True)
                success += 1
            else:
                click.echo(f"    ✗ Failed", err=True)
                failed += 1

        click.echo(f"\nComplete: {success} succeeded, {failed} failed", err=True)
        if failed > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
