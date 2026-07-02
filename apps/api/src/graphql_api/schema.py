import strawberry
from typing import List, Optional
from src.graphql_api.types import EntityNode
from src.graphql_api.resolvers import get_node_by_id, search_nodes


@strawberry.type
class Query:
    @strawberry.field
    async def node(self, id: str) -> Optional[EntityNode]:
        """Fetch a single node and its edges by exact ID."""
        return await get_node_by_id(id)

    @strawberry.field
    async def nodes(
        self, label: Optional[str] = None, limit: int = 10
    ) -> List[EntityNode]:
        """Search for nodes optionally filtered by a label."""
        return await search_nodes(label, limit)


schema = strawberry.Schema(query=Query)
