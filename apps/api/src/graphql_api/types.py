import strawberry
from typing import List


@strawberry.type
class Property:
    key: str
    value: str


@strawberry.type
class RelationshipEdge:
    type: str
    target_id: str
    source_id: str
    properties: List[Property]


@strawberry.type
class EntityNode:
    id: str
    labels: List[str]
    properties: List[Property]
    outgoing_edges: List[RelationshipEdge]
    incoming_edges: List[RelationshipEdge]
