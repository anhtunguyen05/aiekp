import os
import typer
import httpx
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from typing import Optional

from aiekp_cli.config import API_URL

app = typer.Typer(
    help="AIEKP Command Line Interface - Interact with your AI Engineering Knowledge Platform"
)
console = Console()

@app.command()
def status():
    """Check the status of the AIEKP API and infrastructure."""
    with console.status("[bold green]Checking API status...") as status:
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
                    display_value = "[green]ok[/green]" if value == "ok" else f"[red]{value}[/red]"
                    table.add_row(str(key).capitalize(), display_value)
            else:
                table.add_row("API Status", f"[green]{data.get('status', 'ok')}[/green]")
            
            console.print(table)
            
        except httpx.ConnectError:
            console.print(f"[bold red]Error:[/bold red] Could not connect to API at {API_URL}.")
            console.print("Is the API server running? Run `uv run uvicorn src.main:app` in `apps/api`.")
        except httpx.HTTPStatusError as e:
            console.print(f"[bold red]API returned an error:[/bold red] {e.response.status_code}")
        except Exception as e:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")

@app.command()
def ingest(path: str = typer.Argument(..., help="Path to the directory to ingest")):
    """Trigger the ingestion pipeline for a specific local directory."""
    abs_path = os.path.abspath(path)
    
    if not os.path.exists(abs_path):
        console.print(f"[bold red]Error:[/bold red] Path does not exist: {abs_path}")
        raise typer.Exit(1)
        
    with console.status(f"[bold blue]Ingesting {abs_path}...") as status:
        try:
            response = httpx.post(f"{API_URL}/ingest/", json={"repo_path": abs_path}, timeout=120.0)
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
            console.print(f"[bold red]Error:[/bold red] Could not connect to API at {API_URL}.")
        except httpx.TimeoutException:
            console.print("[bold yellow]Warning:[/bold yellow] Request timed out waiting for ingestion to complete, but it might still be running in the background.")
        except httpx.HTTPStatusError as e:
            console.print(f"[bold red]Ingestion failed:[/bold red] {e.response.text}")

@app.command()
def context(query: str = typer.Argument(..., help="Query to retrieve context for")):
    """Fetch relevant architectural and code context from the Knowledge Graph."""
    with console.status(f"[bold blue]Retrieving context for:[/bold blue] '{query}'...") as status:
        try:
            response = httpx.post(f"{API_URL}/context/retrieve", json={"query": query}, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            console.print("[bold green]Context Retrieved![/bold green]\n")
            
            evidence = data.get("evidence", [])
            if not evidence:
                console.print("[yellow]No relevant context found.[/yellow]")
                return
                
            for i, item in enumerate(evidence, 1):
                console.print(f"[bold cyan]Evidence #{i}[/bold cyan] (Relevance: {item.get('relevance_score', 'N/A')})")
                console.print(f"[dim]Type: {item.get('entity_type', 'N/A')}[/dim]")
                if "content" in item and item["content"]:
                    # Try to format as markdown if it looks like code
                    md = Markdown(f"```python\n{item['content']}\n```" if "def " in item['content'] or "class " in item['content'] else item['content'])
                    console.print(md)
                elif "summary" in item and item["summary"]:
                    console.print(item["summary"])
                console.print("-" * 40)
                
        except httpx.ConnectError:
            console.print(f"[bold red]Error:[/bold red] Could not connect to API at {API_URL}.")
        except httpx.HTTPStatusError as e:
            console.print(f"[bold red]Context retrieval failed:[/bold red] {e.response.text}")

@app.command()
def reason(query: str = typer.Argument(..., help="Question or task for the reasoning engine")):
    """End-to-end question answering and code reasoning."""
    with console.status(f"[bold magenta]Thinking about:[/bold magenta] '{query}'...") as status:
        try:
            import uuid
            session_id = str(uuid.uuid4())
            # Assuming the reasoning endpoint takes a request body with 'query' and 'session_id'
            response = httpx.post(f"{API_URL}/reason/", json={"query": query, "session_id": session_id}, timeout=300.0)
            response.raise_for_status()
            data = response.json()
            
            answer = data.get("answer", "No answer provided.")
            
            console.print("\n[bold green]Answer:[/bold green]")
            console.print(Markdown(answer))
            
            # Display sources if available
            sources = data.get("sources_used", [])
            if sources:
                console.print("\n[bold cyan]Sources used:[/bold cyan]")
                for source in sources:
                    console.print(f"- {source}")
                    
        except httpx.ConnectError:
            console.print(f"[bold red]Error:[/bold red] Could not connect to API at {API_URL}.")
        except httpx.TimeoutException:
            console.print("[bold red]Error:[/bold red] Reasoning engine timed out. This task might be too complex or the LLM is taking too long.")
        except httpx.HTTPStatusError as e:
            console.print(f"[bold red]Reasoning failed:[/bold red] {e.response.text}")

if __name__ == "__main__":
    app()
