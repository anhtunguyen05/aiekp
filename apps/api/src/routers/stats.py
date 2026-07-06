from fastapi import APIRouter, Depends
from knowledge_graph import Neo4jGraphManager
from src.dependencies import get_neo4j_manager

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
async def get_stats(graph_manager: Neo4jGraphManager = Depends(get_neo4j_manager)):
    """
    Get graph statistics including total nodes, total edges, and node counts by label.
    """
    # Count total nodes
    query_total_nodes = "MATCH (n) RETURN count(n) as total_nodes"
    records_nodes, _, _ = graph_manager.driver.execute_query(query_total_nodes)
    total_nodes = records_nodes[0]["total_nodes"] if records_nodes else 0

    # Count total edges
    query_total_edges = "MATCH ()-[r]->() RETURN count(r) as total_edges"
    records_edges, _, _ = graph_manager.driver.execute_query(query_total_edges)
    total_edges = records_edges[0]["total_edges"] if records_edges else 0

    # Count nodes by label
    query_labels = "MATCH (n) RETURN labels(n)[0] as label, count(*) as count"
    records_labels, _, _ = graph_manager.driver.execute_query(query_labels)

    label_counts = {}
    for r in records_labels:
        label = r["label"]
        if label:
            label_counts[label] = r["count"]

    # Get nodes with most relationships (Complexity Hotspots)
    complexity_query = """
    MATCH (n)-[r]-()
    WITH n, count(r) AS rel_count
    ORDER BY rel_count DESC
    LIMIT 5
    RETURN coalesce(n.id, n.path) AS id, coalesce(labels(n)[0], 'Unknown') AS type, coalesce(n.name, n.path) AS label, rel_count
    """
    complexity_records, _, _ = graph_manager.driver.execute_query(complexity_query)

    hotspots = []
    for r in complexity_records:
        hotspots.append(
            {
                "id": r["id"],
                "type": r["type"],
                "label": r["label"],
                "connections": r["rel_count"],
            }
        )

    return {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "nodes_by_label": label_counts,
        "hotspots": hotspots,
    }
