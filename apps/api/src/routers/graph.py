from fastapi import APIRouter, Depends, HTTPException, Query
from knowledge_graph import Neo4jGraphManager
from src.dependencies import get_neo4j_manager, get_current_user, CurrentUser

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/nodes")
async def get_all_nodes(
    limit: int = Query(10000, ge=1, le=50000),
    current_user: CurrentUser = Depends(get_current_user),
    graph_manager: Neo4jGraphManager = Depends(get_neo4j_manager),
):
    query = """
    MATCH (n {tenant_id: $tenant_id})
    RETURN coalesce(n.id, n.path) as id, labels(n)[0] as type, properties(n) as properties
    LIMIT $limit
    """
    records, _, _ = graph_manager.driver.execute_query(query, limit=limit, tenant_id=current_user.tenant_id)

    nodes = []
    for r in records:
        nodes.append({"id": r["id"], "type": r["type"], "properties": r["properties"]})
    return {"nodes": nodes}


@router.get("/edges")
async def get_all_edges(
    limit: int = Query(10000, ge=1, le=50000),
    current_user: CurrentUser = Depends(get_current_user),
    graph_manager: Neo4jGraphManager = Depends(get_neo4j_manager),
):
    query = """
    MATCH (n {tenant_id: $tenant_id})-[r]->(m {tenant_id: $tenant_id})
    RETURN coalesce(n.id, n.path) as source, coalesce(m.id, m.path) as target, type(r) as type, properties(r) as properties
    LIMIT $limit
    """
    records, _, _ = graph_manager.driver.execute_query(query, limit=limit, tenant_id=current_user.tenant_id)

    edges = []
    for r in records:
        edges.append(
            {
                "source": r["source"],
                "target": r["target"],
                "type": r["type"],
                "properties": r["properties"],
            }
        )
    return {"edges": edges}


@router.get("/nodes/{node_id:path}")
async def get_node_details(
    node_id: str, 
    current_user: CurrentUser = Depends(get_current_user),
    graph_manager: Neo4jGraphManager = Depends(get_neo4j_manager)
):
    # We can retrieve node details and its relationships
    # This requires a custom Cypher query
    # Handle cases where users copy-paste raw JSON with escaped backslashes (\\)
    node_id = node_id.replace("\\\\", "\\")

    query = """
    MATCH (n {tenant_id: $tenant_id})
    WHERE coalesce(n.id, n.path) = $node_id
    OPTIONAL MATCH (n)-[r]->(m {tenant_id: $tenant_id})
    RETURN n, collect({type: type(r), target: coalesce(m.id, m.path), target_name: coalesce(m.name, m.path), target_type: labels(m)[0]}) as relationships
    """

    records, summary, keys = graph_manager.driver.execute_query(query, node_id=node_id, tenant_id=current_user.tenant_id)

    if not records:
        raise HTTPException(status_code=404, detail="Node not found")

    node_data = records[0]["n"]
    relationships = records[0]["relationships"]

    return {
        "node_id": node_data.get("id", node_data.get("path")),
        "properties": dict(node_data),
        "relationships": relationships,
    }


@router.get("/impact/{node_id:path}")
async def get_impact_analysis(
    node_id: str,
    max_depth: int = Query(3, ge=1, le=5),
    rel_types: list[str] = Query(default=[]),
    current_user: CurrentUser = Depends(get_current_user),
    graph_manager: Neo4jGraphManager = Depends(get_neo4j_manager),
):
    """
    Finds nodes that depend on this node (up to `max_depth` levels).
    This simulates an 'impact analysis' where modifying `node_id` affects other components.
    """
    node_id = node_id.replace("\\\\", "\\")

    # First, verify the source node exists
    check_query = "MATCH (n {tenant_id: $tenant_id}) WHERE coalesce(n.id, n.path) = $node_id RETURN coalesce(n.id, n.path) as id, coalesce(labels(n)[0], 'Unknown') as type, coalesce(n.name, n.path) as label"
    check_records, _, _ = graph_manager.driver.execute_query(
        check_query, node_id=node_id, tenant_id=current_user.tenant_id
    )
    if not check_records:
        raise HTTPException(status_code=404, detail="Source node not found")

    source_node = {
        "id": check_records[0]["id"],
        "type": check_records[0]["type"],
        "label": check_records[0]["label"],
    }

    # Filter requested relationship types to avoid Neo4j warnings for non-existent types
    types_records, _, _ = graph_manager.driver.execute_query(
        "CALL db.relationshipTypes()"
    )
    existing_types = {r[0] for r in types_records}
    valid_rel_types = [t for t in rel_types if t in existing_types] if rel_types else []

    if rel_types and not valid_rel_types:
        # None of the specifically requested relationship types exist in the DB
        return {
            "source_node": source_node,
            "affected": {"direct": [], "indirect": []},
            "total_count": 0,
        }

    rel_filter = "|".join(valid_rel_types) if valid_rel_types else ""
    rel_query = (
        f"[r:{rel_filter}*1..{max_depth}]" if rel_filter else f"[*1..{max_depth}]"
    )

    # Trace along any relationship (undirected) to show general dependency impact
    # Use variable length path and return path length as depth
    query = f"""
    MATCH p=(n {{tenant_id: $tenant_id}})-{rel_query}-(m {{tenant_id: $tenant_id}})
    WHERE coalesce(n.id, n.path) = $node_id
    WITH m, n, p, length(p) as depth
    // Deduplicate by taking the shortest path (minimum depth)
    ORDER BY depth
    WITH m, n, min(depth) as min_depth, collect(p)[0] as shortest_p
    RETURN 
        coalesce(m.id, m.path) as id, 
        coalesce(labels(m)[0], 'Unknown') as type, 
        coalesce(m.name, m.path) as label,
        min_depth as depth,
        type(relationships(shortest_p)[-1]) as via_relation,
        coalesce(n.id, n.path) as source_id,
        coalesce(labels(n)[0], 'Unknown') as source_type,
        coalesce(n.name, n.path) as source_label
    ORDER BY depth
    """
    records, _, _ = graph_manager.driver.execute_query(query, node_id=node_id, tenant_id=current_user.tenant_id)

    if not records:
        return {
            "source_node": source_node,
            "affected": {"direct": [], "indirect": []},
            "total_count": 0,
        }

    direct = []
    indirect = []
    for r in records:
        node_info = {
            "id": r["id"],
            "type": r["type"],
            "label": r["label"],
            "via_relation": r["via_relation"],
        }
        if r["depth"] == 1:
            direct.append(node_info)
        else:
            node_info["depth"] = r["depth"]
            indirect.append(node_info)

    return {
        "source_node": source_node,
        "affected": {"direct": direct, "indirect": indirect},
        "total_count": len(direct) + len(indirect),
    }


@router.delete("/")
def clear_graph(
    current_user: CurrentUser = Depends(get_current_user),
    graph_manager: Neo4jGraphManager = Depends(get_neo4j_manager)
):
    """
    Clears the Knowledge Graph for the current tenant.
    """
    try:
        query = "MATCH (n {tenant_id: $tenant_id}) DETACH DELETE n"
        graph_manager.driver.execute_query(query, tenant_id=current_user.tenant_id)
        return {"message": "Knowledge Graph cleared successfully for the tenant."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
