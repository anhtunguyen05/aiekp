from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from knowledge_graph import Neo4jGraphManager
from pydantic import BaseModel, Field
from src.dependencies import get_neo4j_manager

router = APIRouter(prefix="/rules", tags=["rules"])

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class RuleDefinition(BaseModel):
    type: str = Field(
        ...,
        description=(
            "Rule type. One of: no-circular-deps, max-fan-in, max-fan-out, "
            "no-cross-layer, max-complexity."
        ),
    )
    threshold: int | None = Field(
        None,
        ge=1,
        description="Numeric threshold used by fan-in, fan-out, and max-complexity rules.",
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Extra parameters per rule type. "
            "For no-cross-layer: {'source_pattern': '...', 'target_pattern': '...'}."
        ),
    )


class RuleViolation(BaseModel):
    rule_type: str
    node_id: str
    node_label: str
    node_type: str
    detail: str


class RuleCheckResponse(BaseModel):
    violations: list[RuleViolation]
    total_violations: int
    rules_run: list[str]


# ---------------------------------------------------------------------------
# Supported rule types
# ---------------------------------------------------------------------------

SUPPORTED_RULES = {
    "no-circular-deps",
    "max-fan-in",
    "max-fan-out",
    "no-cross-layer",
    "max-complexity",
}


# ---------------------------------------------------------------------------
# Cypher query builders
# ---------------------------------------------------------------------------


def _run_no_circular_deps(
    driver: Any,
    rule: RuleDefinition,
) -> list[RuleViolation]:
    """Detect cycles: any node reachable from itself via directed relationships."""
    query = """
    MATCH (n)-[*2..10]->(n)
    WITH DISTINCT n
    RETURN
        coalesce(n.id, n.path) AS node_id,
        coalesce(n.name, n.path)  AS node_label,
        coalesce(labels(n)[0], 'Unknown') AS node_type
    LIMIT 100
    """
    records, _, _ = driver.execute_query(query)
    return [
        RuleViolation(
            rule_type="no-circular-deps",
            node_id=r["node_id"],
            node_label=r["node_label"],
            node_type=r["node_type"],
            detail="Node participates in a circular dependency cycle.",
        )
        for r in records
        if r["node_id"]
    ]


def _run_max_fan_in(
    driver: Any,
    rule: RuleDefinition,
) -> list[RuleViolation]:
    """Detect nodes with more incoming edges than the threshold."""
    threshold = rule.threshold or 10
    query = """
    MATCH (m)<-[r]-(n)
    WITH m, count(r) AS incoming
    WHERE incoming > $threshold
    RETURN
        coalesce(m.id, m.path)  AS node_id,
        coalesce(m.name, m.path) AS node_label,
        coalesce(labels(m)[0], 'Unknown') AS node_type,
        incoming
    ORDER BY incoming DESC
    LIMIT 100
    """
    records, _, _ = driver.execute_query(query, threshold=threshold)
    return [
        RuleViolation(
            rule_type="max-fan-in",
            node_id=r["node_id"],
            node_label=r["node_label"],
            node_type=r["node_type"],
            detail=f"Fan-in = {r['incoming']} (threshold: {threshold}).",
        )
        for r in records
        if r["node_id"]
    ]


def _run_max_fan_out(
    driver: Any,
    rule: RuleDefinition,
) -> list[RuleViolation]:
    """Detect nodes with more outgoing edges than the threshold."""
    threshold = rule.threshold or 10
    query = """
    MATCH (n)-[r]->(m)
    WITH n, count(r) AS outgoing
    WHERE outgoing > $threshold
    RETURN
        coalesce(n.id, n.path)  AS node_id,
        coalesce(n.name, n.path) AS node_label,
        coalesce(labels(n)[0], 'Unknown') AS node_type,
        outgoing
    ORDER BY outgoing DESC
    LIMIT 100
    """
    records, _, _ = driver.execute_query(query, threshold=threshold)
    return [
        RuleViolation(
            rule_type="max-fan-out",
            node_id=r["node_id"],
            node_label=r["node_label"],
            node_type=r["node_type"],
            detail=f"Fan-out = {r['outgoing']} (threshold: {threshold}).",
        )
        for r in records
        if r["node_id"]
    ]


def _run_no_cross_layer(
    driver: Any,
    rule: RuleDefinition,
) -> list[RuleViolation]:
    """
    Detect edges that cross forbidden layer boundaries.

    Layer detection is path-based (regex on node `id` / `path` property) so it
    is easy to extend without a DSL.  Default: any UI-layer node must not have
    a direct relationship to a DB-layer node.

    Configurable via `params`:
        source_pattern (str) — regex that matches the *source* node path.
        target_pattern (str) — regex that matches the *target* node path.

    Defaults match common patterns found in Python / Next.js monorepos:
        source_pattern = ".*/ui/.*|.*/components/.*|.*/pages/.*|.*/app/.*"
        target_pattern = ".*/db/.*|.*/database/.*|.*/models/.*|.*/prisma/.*"
    """
    source_pattern = rule.params.get(
        "source_pattern",
        r".*/ui/.*|.*/components/.*|.*/pages/.*|.*/app/.*",
    )
    target_pattern = rule.params.get(
        "target_pattern",
        r".*/db/.*|.*/database/.*|.*/models/.*|.*/prisma/.*",
    )

    # Fetch candidate edges and filter in Python so we avoid Neo4j regex plugin dependency
    query = """
    MATCH (n)-[r]->(m)
    WHERE n.path IS NOT NULL AND m.path IS NOT NULL
    RETURN
        coalesce(n.id, n.path)  AS src_id,
        coalesce(n.name, n.path) AS src_label,
        coalesce(labels(n)[0], 'Unknown') AS src_type,
        n.path AS src_path,
        m.path AS tgt_path
    LIMIT 5000
    """
    records, _, _ = driver.execute_query(query)

    src_re = re.compile(source_pattern, re.IGNORECASE)
    tgt_re = re.compile(target_pattern, re.IGNORECASE)

    violations: list[RuleViolation] = []
    for r in records:
        if r["src_path"] and r["tgt_path"]:
            if src_re.search(r["src_path"]) and tgt_re.search(r["tgt_path"]):
                violations.append(
                    RuleViolation(
                        rule_type="no-cross-layer",
                        node_id=r["src_id"],
                        node_label=r["src_label"],
                        node_type=r["src_type"],
                        detail=(
                            f"Cross-layer dependency detected: "
                            f"'{r['src_path']}' → '{r['tgt_path']}'."
                        ),
                    )
                )
    # Deduplicate by node_id
    seen: set[str] = set()
    unique: list[RuleViolation] = []
    for v in violations:
        if v.node_id not in seen:
            seen.add(v.node_id)
            unique.append(v)
    return unique[:100]


def _run_max_complexity(
    driver: Any,
    rule: RuleDefinition,
) -> list[RuleViolation]:
    """Detect files/modules that contain more children than the threshold."""
    threshold = rule.threshold or 20
    query = """
    MATCH (n)-[r:CONTAINS]->(m)
    WITH n, count(r) AS children
    WHERE children > $threshold
    RETURN
        coalesce(n.id, n.path)  AS node_id,
        coalesce(n.name, n.path) AS node_label,
        coalesce(labels(n)[0], 'Unknown') AS node_type,
        children
    ORDER BY children DESC
    LIMIT 100
    """
    records, _, _ = driver.execute_query(query, threshold=threshold)
    return [
        RuleViolation(
            rule_type="max-complexity",
            node_id=r["node_id"],
            node_label=r["node_label"],
            node_type=r["node_type"],
            detail=f"Contains {r['children']} children (threshold: {threshold}).",
        )
        for r in records
        if r["node_id"]
    ]


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_RULE_RUNNERS = {
    "no-circular-deps": _run_no_circular_deps,
    "max-fan-in": _run_max_fan_in,
    "max-fan-out": _run_max_fan_out,
    "no-cross-layer": _run_no_cross_layer,
    "max-complexity": _run_max_complexity,
}


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/check", response_model=RuleCheckResponse)
async def check_rules(
    rules: list[RuleDefinition],
    graph_manager: Neo4jGraphManager = Depends(get_neo4j_manager),
):
    """
    Run one or more architectural rule checks against the Knowledge Graph.

    Returns all violations found, with the node ID, label, type, and a
    human-readable detail message for each.
    """
    if not rules:
        raise HTTPException(
            status_code=422, detail="At least one rule must be provided."
        )

    unknown = [r.type for r in rules if r.type not in SUPPORTED_RULES]
    if unknown:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown rule type(s): {unknown}. Supported: {sorted(SUPPORTED_RULES)}",
        )

    all_violations: list[RuleViolation] = []
    rules_run: list[str] = []

    for rule in rules:
        runner = _RULE_RUNNERS[rule.type]
        try:
            violations = runner(graph_manager.driver, rule)
            all_violations.extend(violations)
            rules_run.append(rule.type)
        except Exception as exc:
            # Surface individual rule failures without aborting the whole audit
            all_violations.append(
                RuleViolation(
                    rule_type=rule.type,
                    node_id="__error__",
                    node_label="Rule execution error",
                    node_type="Error",
                    detail=str(exc),
                )
            )
            rules_run.append(f"{rule.type}(ERROR)")

    return RuleCheckResponse(
        violations=all_violations,
        total_violations=len(all_violations),
        rules_run=rules_run,
    )
