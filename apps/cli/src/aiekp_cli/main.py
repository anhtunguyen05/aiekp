import os
import typer
import httpx
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from aiekp_cli.config import API_URL
from aiekp_cli import config_manager
import subprocess

app = typer.Typer(
    help="AIEKP Command Line Interface - Interact with your AI Engineering Knowledge Platform"
)
console = Console()

config_app = typer.Typer(help="Manage AIEKP global configuration")
app.add_typer(config_app, name="config")

try:
    from aiekp_cli.commands.eval import eval_app
    app.add_typer(eval_app, name="eval")
except ImportError:
    pass


@config_app.command("set")
def config_set(key: str, value: str):
    """Set a global configuration value (e.g., GEMINI_API_KEY)."""
    config_manager.write_config(key, value)
    console.print(f"[bold green]Successfully set {key}![/bold green]")


@config_app.command("list")
def config_list():
    """List all global configuration values."""
    config = config_manager.read_config()
    if not config:
        console.print(
            "[yellow]No configuration found. Use 'aiekp config set' to add keys.[/yellow]"
        )
        return

    table = Table(title="AIEKP Global Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    for key, value in config.items():
        # Mask API keys and passwords
        display_value = value
        if "KEY" in key.upper() or "PASSWORD" in key.upper() or "SECRET" in key.upper():
            if len(value) > 8:
                display_value = value[:4] + "*" * (len(value) - 8) + value[-4:]
            else:
                display_value = "***"
        table.add_row(key, display_value)

    console.print(table)


@app.command()
def init():
    """Initialize AIEKP infrastructure (Neo4j, etc.) via Docker."""
    console.print("[bold blue]Initializing AIEKP Infrastructure...[/bold blue]")
    try:
        # Check if docker is installed
        subprocess.run(["docker", "--version"], check=True, capture_output=True)

        # Check if container already exists
        result = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                "name=aiekp-neo4j",
                "--format",
                "{{.Names}}",
            ],
            capture_output=True,
            text=True,
        )
        if "aiekp-neo4j" in result.stdout:
            console.print(
                "[yellow]Container 'aiekp-neo4j' already exists. Starting it...[/yellow]"
            )
            subprocess.run(["docker", "start", "aiekp-neo4j"], check=True)
        else:
            # Run Neo4j container
            console.print("Starting new Neo4j container...")
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    "aiekp-neo4j",
                    "-p",
                    "7474:7474",
                    "-p",
                    "7687:7687",
                    "-e",
                    "NEO4J_AUTH=neo4j/password",
                    "-e",
                    'NEO4J_PLUGINS=["apoc"]',
                    "neo4j:5.14.0",
                ],
                check=True,
            )

        console.print("[bold green]Neo4j started successfully![/bold green]")
        console.print("UI available at: http://localhost:7474 (neo4j / password)")
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Failed to start Docker container:[/bold red] {e}")
    except FileNotFoundError:
        console.print(
            "[bold red]Docker is not installed or not in PATH. Please install Docker first.[/bold red]"
        )


@app.command()
def server(port: int = 8000, host: str = "0.0.0.0"):
    """Start the AIEKP API server locally."""
    console.print(
        f"[bold blue]Starting AIEKP API Server on {host}:{port}...[/bold blue]"
    )
    try:
        # Assuming the user runs this from the root of the AIEKP repository
        import subprocess
        import os

        # Check if apps/api/src/main.py exists relative to current dir
        api_dir = os.path.join(os.getcwd(), "apps", "api")
        if not os.path.exists(api_dir):
            # Try to resolve relative to this file's location
            # __file__ is apps/cli/src/aiekp_cli/main.py
            root_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
            )
            api_dir = os.path.join(root_dir, "apps", "api")

        if not os.path.exists(api_dir):
            console.print(
                "[bold yellow]Warning:[/bold yellow] 'apps/api' not found. Please run this command from the AIEKP repository root."
            )

        console.print("Running API Server...")
        subprocess.run(
            [
                "uv",
                "run",
                "uvicorn",
                "src.main:app",
                "--host",
                host,
                "--port",
                str(port),
            ],
            cwd=api_dir,
            check=True,
        )

    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]API Server exited with error:[/bold red] {e}")
    except FileNotFoundError:
        console.print("[bold red]uv is not installed or not in PATH.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")


@app.command()
def status():
    """Check the status of the AIEKP API and infrastructure."""
    with console.status("[bold green]Checking API status..."):
        try:
            response = httpx.get(f"{API_URL}/health/", timeout=5.0)
            response.raise_for_status()
            data = response.json()

            table = Table(title="AIEKP Services Status")
            table.add_column("Service", style="cyan", no_wrap=True)
            table.add_column("Status", style="magenta")

            services = data.get("services", {})
            if services:
                for key, value in services.items():
                    display_value = (
                        "[green]ok[/green]" if value == "ok" else f"[red]{value}[/red]"
                    )
                    table.add_row(str(key).capitalize(), display_value)
            else:
                table.add_row(
                    "API Status", f"[green]{data.get('status', 'ok')}[/green]"
                )

            console.print(table)

        except httpx.ConnectError:
            console.print(
                f"[bold red]Error:[/bold red] Could not connect to API at {API_URL}."
            )
            console.print(
                "Is the API server running? Run `uv run uvicorn src.main:app` in `apps/api`."
            )
        except httpx.HTTPStatusError as e:
            console.print(
                f"[bold red]API returned an error:[/bold red] {e.response.status_code}"
            )
        except Exception as e:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")


@app.command()
def ingest(path: str = typer.Argument(..., help="Path to the directory to ingest")):
    """Trigger the ingestion pipeline for a specific local directory."""
    abs_path = os.path.abspath(path)

    # If run via `uv run --directory apps/cli`, CWD is apps/cli, but the user might pass a path relative to the root.
    if not os.path.exists(abs_path):
        root_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        fallback_path = os.path.abspath(os.path.join(root_dir, path))
        if os.path.exists(fallback_path):
            abs_path = fallback_path

    if not os.path.exists(abs_path):
        console.print(f"[bold red]Error:[/bold red] Path does not exist: {abs_path}")
        raise typer.Exit(1)

    with console.status(f"[bold blue]Ingesting {abs_path}..."):
        try:
            response = httpx.post(
                f"{API_URL}/ingest/", json={"repo_path": abs_path}, timeout=120.0
            )
            response.raise_for_status()
            data = response.json()

            console.print("[bold green]Ingestion completed successfully![/bold green]")

            # Print a summary table if the API provides details
            if isinstance(data, dict) and "summary" in data:
                summary = data["summary"]
                table = Table(title="Ingestion Summary")
                table.add_column("Metric", style="cyan")
                table.add_column("Count", style="magenta")

                for k, v in summary.items():
                    table.add_row(str(k), str(v))

                console.print(table)
            else:
                console.print(data)

        except httpx.ConnectError:
            console.print(
                f"[bold red]Error:[/bold red] Could not connect to API at {API_URL}."
            )
        except httpx.TimeoutException:
            console.print(
                "[bold yellow]Warning:[/bold yellow] Request timed out waiting for ingestion to complete, but it might still be running in the background."
            )
        except httpx.HTTPStatusError as e:
            console.print(f"[bold red]Ingestion failed:[/bold red] {e.response.text}")


@app.command()
def context(query: str = typer.Argument(..., help="Query to retrieve context for")):
    """Fetch relevant architectural and code context from the Knowledge Graph."""
    with console.status(f"[bold blue]Retrieving context for:[/bold blue] '{query}'..."):
        try:
            response = httpx.post(
                f"{API_URL}/context/retrieve", json={"query": query}, timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            console.print("[bold green]Context Retrieved![/bold green]\n")

            evidence = data.get("evidence", [])
            if not evidence:
                console.print("[yellow]No relevant context found.[/yellow]")
                return

            for i, item in enumerate(evidence, 1):
                console.print(
                    f"[bold cyan]Evidence #{i}[/bold cyan] (Relevance: {item.get('relevance_score', 'N/A')})"
                )
                console.print(f"[dim]Type: {item.get('entity_type', 'N/A')}[/dim]")
                if "content" in item and item["content"]:
                    # Try to format as markdown if it looks like code
                    md = Markdown(
                        f"```python\n{item['content']}\n```"
                        if "def " in item["content"] or "class " in item["content"]
                        else item["content"]
                    )
                    console.print(md)
                elif "summary" in item and item["summary"]:
                    console.print(item["summary"])
                console.print("-" * 40)

        except httpx.ConnectError:
            console.print(
                f"[bold red]Error:[/bold red] Could not connect to API at {API_URL}."
            )
        except httpx.HTTPStatusError as e:
            console.print(
                f"[bold red]Context retrieval failed:[/bold red] {e.response.text}"
            )


@app.command()
def reason(
    query: str = typer.Argument(..., help="Question or task for the reasoning engine"),
    project_path: str = typer.Option(
        None, "--project-path", help="Optional project path to restrict context to"
    ),
):
    """End-to-end question answering and code reasoning."""
    console.print(f"[bold magenta]Thinking about:[/bold magenta] '{query}'...\n")
    try:
        import uuid
        import json

        session_id = str(uuid.uuid4())
        payload = {"query": query, "session_id": session_id}
        if project_path:
            # We can add this to the request if the backend supports it,
            # for now we'll just include it in the query context.
            payload["query"] = f"[Project: {project_path}] {query}"

        # Connect to stream endpoint
        with httpx.stream(
            "POST", f"{API_URL}/reason/stream", json=payload, timeout=300.0
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        # Print the stream chunk directly without newline to simulate typing
                        # We use console.print with end="" so it doesn't add newlines
                        print(chunk.get("content", ""), end="", flush=True)
                    except json.JSONDecodeError:
                        pass
        print("\n")
        console.print("[bold green]Reasoning Complete![/bold green]")

    except httpx.ConnectError:
        console.print(
            f"\n[bold red]Error:[/bold red] Could not connect to API at {API_URL}."
        )
    except httpx.TimeoutException:
        console.print(
            "\n[bold red]Error:[/bold red] Reasoning engine timed out. This task might be too complex or the LLM is taking too long."
        )
    except httpx.HTTPStatusError as e:
        console.print(f"\n[bold red]Reasoning failed:[/bold red] {e.response.text}")


if __name__ == "__main__":
    app()
