import os
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from src.auth.database import SessionLocal
from src.auth.crud import get_user_by_email

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

def migrate_data():
    db = SessionLocal()
    try:
        admin_user = get_user_by_email(db, "admin@tenanta.com")
        if not admin_user:
            print("No admin user found. Please run the test_multi_tenancy.py script first to create Tenant A.")
            return
        tenant_id = admin_user.tenant_id
        print(f"Migrating data to default tenant_id: {tenant_id}")
    finally:
        db.close()
        
    print("Migrating Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        # Update all nodes that don't have a tenant_id
        result = session.run("""
            MATCH (n)
            WHERE n.tenant_id IS NULL
            SET n.tenant_id = $tenant_id
            RETURN count(n) as updated_count
        """, tenant_id=tenant_id)
        count = result.single()["updated_count"]
        print(f"  Neo4j updated {count} nodes.")
    driver.close()

    print("Migrating Qdrant...")
    qdrant = QdrantClient(url=QDRANT_URL)
    
    collections = qdrant.get_collections().collections
    for collection in collections:
        col_name = collection.name
        
        # Scroll and update payloads in batches
        offset = None
        updated_points = 0
        while True:
            records, offset = qdrant.scroll(
                collection_name=col_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            
            if not records:
                break
                
            point_ids = []
            for record in records:
                if not record.payload or "tenant_id" not in record.payload:
                    point_ids.append(record.id)

            if point_ids:
                qdrant.set_payload(
                    collection_name=col_name,
                    payload={"tenant_id": tenant_id},
                    points=point_ids
                )
                updated_points += len(point_ids)
            
            if offset is None:
                break
                
        print(f"  Qdrant collection '{col_name}' updated {updated_points} points.")

if __name__ == "__main__":
    migrate_data()
