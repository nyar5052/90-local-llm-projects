"""CLI interface for Product Description Writer."""

import logging
import sys
import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core import (
    generate_descriptions,
    generate_ab_variants,
    load_config,
    get_platform_configs,
    get_feature_benefit_map,
    map_features_to_benefits,
    calculate_seo_score,
    PLATFORM_CONFIGS,
    LENGTH_GUIDE,
    DEFAULT_CONFIG,
)

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")


@click.group()
@click.option("--config", "config_path", default="config.yaml", help="Path to config file.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
@click.pass_context
def cli(ctx, config_path, verbose):
    """🛒 Product Description Writer - Generate SEO-optimized e-commerce descriptions."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)


@cli.command()
@click.option("--product", required=True, help="Product name.")
@click.option("--features", default="", help="Comma-separated product features.")
@click.option("--platform", type=click.Choice(list(PLATFORM_CONFIGS.keys()), case_sensitive=False), default="generic", help="E-commerce platform.")
@click.option("--length", type=click.Choice(list(LENGTH_GUIDE.keys()), case_sensitive=False), default="medium", help="Description length.")
@click.option("--variants", default=2, type=int, help="Number of variants.")
@click.option("--keywords", default="", help="Comma-separated SEO keywords.")
@click.option("--output", "-o", default=None, help="Save output to file.")
@click.pass_context
def generate(ctx, product, features, platform, length, variants, keywords, output):
    """Generate product descriptions."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import check_ollama_running

    config = ctx.obj["config"]
    console.print(Panel.fit("[bold yellow]🛒 Product Description Writer[/bold yellow]", border_style="yellow"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    feat_list = [f.strip() for f in features.split(",") if f.strip()] if features else []
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else None

    console.print(f"  [cyan]Product:[/cyan]   {product}")
    console.print(f"  [cyan]Features:[/cyan]  {', '.join(feat_list) if feat_list else 'None'}")
    console.print(f"  [cyan]Platform:[/cyan]  {platform}")
    console.print(f"  [cyan]Length:[/cyan]    {length}")
    console.print(f"  [cyan]Variants:[/cyan]  {variants}")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Writing product descriptions...", total=None)
        result = generate_descriptions(product, feat_list, platform, length, variants, kw_list, config)

    console.print(Panel(Markdown(result), title="🛒 Product Descriptions", border_style="yellow"))

    if kw_list:
        seo = calculate_seo_score(result, kw_list)
        console.print(f"\n[bold]SEO Score:[/bold] {seo['overall_score']}/100  |  Coverage: {seo['keyword_coverage']}%  |  Words: {seo['word_count']}")

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]✓ Saved to {output}[/green]")


@cli.command()
def platforms():
    """List supported e-commerce platforms."""
    table = Table(title="🏪 Supported Platforms", border_style="yellow")
    table.add_column("Key", style="cyan")
    table.add_column("", style="bold")
    table.add_column("Name", style="bold")
    table.add_column("Title Max")
    table.add_column("Tips")
    for key, plat in get_platform_configs().items():
        table.add_row(key, plat["icon"], plat["name"], str(plat.get("title_max", "N/A")), plat["tips"][:60] + "...")
    console.print(table)


@cli.command()
@click.option("--features", required=True, help="Comma-separated features to map.")
def benefits(features):
    """Map product features to customer benefits."""
    feat_list = [f.strip() for f in features.split(",") if f.strip()]
    mapped = map_features_to_benefits(feat_list)
    table = Table(title="✨ Feature → Benefit Mapping", border_style="yellow")
    table.add_column("Feature", style="cyan")
    table.add_column("Benefit", style="bold")
    for m in mapped:
        table.add_row(m["feature"], m["benefit"])
    console.print(table)


def main():
    cli()

if __name__ == "__main__":
    main()
