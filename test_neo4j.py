from neo4j import GraphDatabase

# Config
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "aiekp_password")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    with driver.session() as session:
        # Get edges where n has no id and no path
        result = session.run(
            "MATCH (n)-[r]->(m) RETURN coalesce(n.id, n.path) as source, coalesce(m.id, m.path) as target, type(r) as type LIMIT 5"
        )
        for record in result:
            print(
                f"Source: {record['source']}, Target: {record['target']}, Type: {record['type']}"
            )
