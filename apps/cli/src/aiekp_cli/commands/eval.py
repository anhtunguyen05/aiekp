import os
import sqlite3
import json
import typer
from rich.console import Console

eval_app = typer.Typer(help="Evaluate RAG pipelines and export telemetry data")
console = Console()


def get_db_path():
    # Assuming telemetry.db is at apps/api/telemetry.db
    # Find root by traversing up from current file
    default_db_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../api/telemetry.db")
    )
    db_path = os.environ.get("TELEMETRY_DB_PATH", default_db_path)
    if not os.path.exists(db_path):
        console.print(
            f"[bold yellow]Warning:[/bold yellow] telemetry.db not found at {db_path}."
        )
    return db_path


@eval_app.command("run")
def run_eval():
    """Run RAGAS evaluation on recent traces."""
    console.print(
        "[bold blue]Running RAGAS evaluation on telemetry data...[/bold blue]"
    )
    try:
        from ragas import evaluate
        from ragas.metrics import answer_relevancy, faithfulness
        from datasets import Dataset
    except ImportError:
        console.print(
            "[bold red]ragas or datasets library not found. Please install them using `pip install ragas datasets`.[/bold red]"
        )
        raise typer.Exit(1)

    db_path = get_db_path()
    if not os.path.exists(db_path):
        raise typer.Exit(1)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fetch traces with feedback
        cursor.execute("""
            SELECT t.id as trace_id, t.query, t.metadata, f.score, f.comment
            FROM traces t
            JOIN feedbacks f ON t.id = f.trace_id
            ORDER BY t.timestamp DESC
            LIMIT 50
        """)
        rows = cursor.fetchall()

        if not rows:
            console.print("[yellow]No traces with feedback found to evaluate.[/yellow]")
            return

        data = {
            "question": [],
            "answer": [],
            "contexts": [],
        }

        for row in rows:
            data["question"].append(row["query"])

            # Try to extract answer and contexts from metadata
            meta = {}
            if row["metadata"]:
                try:
                    meta = json.loads(row["metadata"])
                except Exception:
                    pass

            # These are placeholder extractions, depends on actual metadata structure
            data["answer"].append(meta.get("answer", "No answer recorded"))
            sources = meta.get("sources_used", [])
            data["contexts"].append(
                [s.get("label", "") + " " + s.get("snippet", "") for s in sources]
            )

        dataset = Dataset.from_dict(data)

        console.print(f"Evaluating {len(data['question'])} queries...")
        # Note: This requires OPENAI_API_KEY to be set in environment
        result = evaluate(dataset, metrics=[answer_relevancy, faithfulness])

        console.print("[bold green]Evaluation Complete![/bold green]")
        console.print(result)

    except Exception as e:
        console.print(f"[bold red]Evaluation failed:[/bold red] {e}")
    finally:
        if "conn" in locals():
            conn.close()


@eval_app.command("export-jsonl")
def export_jsonl(output: str = "finetune_data.jsonl"):
    """Export telemetry traces and positive feedback to JSONL for fine-tuning."""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        raise typer.Exit(1)

    console.print(f"[bold blue]Exporting data to {output}...[/bold blue]")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Export only traces with positive feedback (score > 0)
        cursor.execute("""
            SELECT t.id as trace_id, t.query, t.metadata, f.score, f.comment
            FROM traces t
            JOIN feedbacks f ON t.id = f.trace_id
            WHERE f.score > 0
            ORDER BY t.timestamp ASC
        """)
        rows = cursor.fetchall()

        count = 0
        with open(output, "w", encoding="utf-8") as f:
            for row in rows:
                meta = {}
                if row["metadata"]:
                    try:
                        meta = json.loads(row["metadata"])
                    except Exception:
                        pass

                # Format for OpenAI fine-tuning (messages format)
                # This assumes we want to train the model to output the recorded answer for the query
                answer = meta.get("answer", "")

                if not answer:
                    # Look in spans if answer not in metadata
                    cursor.execute(
                        "SELECT outputs FROM trace_spans WHERE trace_id = ? AND name = 'process_query'",
                        (row["trace_id"],),
                    )
                    span_row = cursor.fetchone()
                    if span_row and span_row["outputs"]:
                        answer = span_row["outputs"]

                if answer:
                    jsonl_record = {
                        "messages": [
                            {"role": "user", "content": row["query"]},
                            {"role": "assistant", "content": answer},
                        ]
                    }
                    f.write(json.dumps(jsonl_record, ensure_ascii=False) + "\n")
                    count += 1

        console.print(
            f"[bold green]Successfully exported {count} records to {output}[/bold green]"
        )

    except Exception as e:
        console.print(f"[bold red]Export failed:[/bold red] {e}")
    finally:
        if "conn" in locals():
            conn.close()
