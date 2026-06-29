import os
import asyncio
from fastapi import APIRouter, HTTPException

# DB Drivers
from prisma import Prisma
from neo4j import AsyncGraphDatabase
from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis
from minio import Minio

router = APIRouter(prefix="/health", tags=["Health"])


async def check_postgres():
    db = Prisma()
    try:
        await db.connect()
        # Prisma Python allows executing raw queries for health checks
        await db.query_raw("SELECT 1")
        return "ok"
    except Exception as e:
        return f"error: {str(e)}"
    finally:
        if db.is_connected():
            await db.disconnect()


async def check_neo4j():
    try:
        uri = f"bolt://{os.getenv('NEO4J_HOST', 'localhost')}:{os.getenv('NEO4J_PORT', '7687')}"
        auth = (
            os.getenv("NEO4J_USER", "neo4j"),
            os.getenv("NEO4J_PASSWORD", "aiekp_password"),
        )
        driver = AsyncGraphDatabase.driver(uri, auth=auth)
        async with driver.session() as session:
            await session.run("RETURN 1")
        await driver.close()
        return "ok"
    except Exception as e:
        return f"error: {str(e)}"


async def check_qdrant():
    try:
        client = AsyncQdrantClient(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", "6333")),
            timeout=2.0,
        )
        await client.get_collections()
        return "ok"
    except Exception as e:
        return f"error: {str(e)}"


async def check_redis():
    try:
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            client = Redis.from_url(redis_url, socket_connect_timeout=2.0)
        else:
            client = Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                socket_connect_timeout=2.0,
            )
        await client.ping()
        await client.close()
        return "ok"
    except Exception as e:
        return f"error: {str(e)}"


def check_minio_sync():
    try:
        client = Minio(
            f"{os.getenv('MINIO_HOST', 'localhost')}:{os.getenv('MINIO_PORT', '9000')}",
            access_key=os.getenv("MINIO_ROOT_USER", "aiekp_user"),
            secret_key=os.getenv("MINIO_ROOT_PASSWORD", "aiekp_password"),
            secure=False,
        )
        client.list_buckets()
        return "ok"
    except Exception as e:
        return f"error: {str(e)}"


@router.get("/")
async def health_check():
    """
    Check connection to all 5 infrastructure databases.
    """
    # Run async checks concurrently
    pg_task = check_postgres()
    neo_task = check_neo4j()
    qdrant_task = check_qdrant()
    redis_task = check_redis()

    # Run sync check in threadpool
    loop = asyncio.get_running_loop()
    minio_task = loop.run_in_executor(None, check_minio_sync)

    results = await asyncio.gather(
        pg_task, neo_task, qdrant_task, redis_task, minio_task
    )

    status = {
        "postgres": results[0],
        "neo4j": results[1],
        "qdrant": results[2],
        "redis": results[3],
        "minio": results[4],
    }

    # If any service failed, return 503
    if any(res != "ok" for res in status.values()):
        raise HTTPException(status_code=503, detail=status)

    return {"status": "all_systems_operational", "services": status}
