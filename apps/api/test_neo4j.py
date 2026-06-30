from knowledge_graph.neo4j_client import Neo4jGraphManager

neo4j = Neo4jGraphManager("bolt://localhost:7687", "neo4j", "aiekp_password")
query = """
MATCH (n {id: $node_id})
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, collect({type: type(r), target: m.id, target_name: m.name, target_type: labels(m)[0]}) as relationships
"""
node_id = r"D:\AIEKP\plugins\python_parser\tests\test_parser.py::test_python_parser"
records, _, _ = neo4j.driver.execute_query(query, node_id=node_id)
print("Records found:", len(records))
if len(records) > 0:
    print(records[0]["n"])
