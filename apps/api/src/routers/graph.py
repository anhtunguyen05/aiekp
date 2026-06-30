from fastapi import APIRouter, Depends, HTTPException
from knowledge_graph import Neo4jGraphManager
from src.dependencies import get_neo4j_manager

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/nodes/{node_id:path}")
async def get_node_details(
    node_id: str, graph_manager: Neo4jGraphManager = Depends(get_neo4j_manager)
):
    # We can retrieve node details and its relationships
    # This requires a custom Cypher query
    # Handle cases where users copy-paste raw JSON with escaped backslashes (\\)
    node_id = node_id.replace("\\\\", "\\")

    query = """
    MATCH (n {id: $node_id})
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, collect({type: type(r), target: m.id, target_name: m.name, target_type: labels(m)[0]}) as relationships
    """

    records, summary, keys = graph_manager.driver.execute_query(query, node_id=node_id)

    if not records:
        raise HTTPException(status_code=404, detail="Node not found")

    node_data = records[0]["n"]
    relationships = records[0]["relationships"]

    return {
        "node_id": node_data.get("id"),
        "properties": dict(node_data),
        "relationships": relationships,
    }
