from typing import List, Optional
from src.graphql.types import EntityNode, RelationshipEdge, Property
from src.dependencies import get_neo4j_manager


def dict_to_properties(d: dict) -> List[Property]:
    return [Property(key=k, value=str(v)) for k, v in d.items()]


async def get_node_by_id(id: str) -> Optional[EntityNode]:
    manager = get_neo4j_manager()
    query = """
    MATCH (n) WHERE elementId(n) = $id
    RETURN elementId(n) as id, labels(n) as labels, properties(n) as props
    """
    records, _, _ = manager.driver.execute_query(query, id=id)
    if not records:
        return None

    record = records[0]
    props = record["props"]
    labels = record["labels"]

    out_query = """
    MATCH (n)-[r]->(m) WHERE elementId(n) = $id
    RETURN type(r) as type, elementId(m) as target_id, properties(r) as props
    """
    out_records, _, _ = manager.driver.execute_query(out_query, id=id)
    outgoing = [
        RelationshipEdge(
            type=r["type"],
            source_id=id,
            target_id=r["target_id"],
            properties=dict_to_properties(r["props"]),
        )
        for r in out_records
    ]

    in_query = """
    MATCH (m)-[r]->(n) WHERE elementId(n) = $id
    RETURN type(r) as type, elementId(m) as source_id, properties(r) as props
    """
    in_records, _, _ = manager.driver.execute_query(in_query, id=id)
    incoming = [
        RelationshipEdge(
            type=r["type"],
            source_id=r["source_id"],
            target_id=id,
            properties=dict_to_properties(r["props"]),
        )
        for r in in_records
    ]

    return EntityNode(
        id=id,
        labels=labels,
        properties=dict_to_properties(props),
        outgoing_edges=outgoing,
        incoming_edges=incoming,
    )


async def search_nodes(
    label: Optional[str] = None, limit: int = 10
) -> List[EntityNode]:
    manager = get_neo4j_manager()
    match_clause = f"MATCH (n:{label})" if label else "MATCH (n)"
    query = f"""
    {match_clause}
    RETURN elementId(n) as id, labels(n) as labels, properties(n) as props
    LIMIT $limit
    """
    records, _, _ = manager.driver.execute_query(query, limit=limit)
    nodes = []
    for r in records:
        nodes.append(
            EntityNode(
                id=r["id"],
                labels=r["labels"],
                properties=dict_to_properties(r["props"]),
                outgoing_edges=[],
                incoming_edges=[],
            )
        )
    return nodes
