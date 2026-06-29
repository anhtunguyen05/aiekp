from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

from prisma import Client as PrismaClient

from aiekp_knowledge_engine import RepositoryScanner
from aiekp_shared.domain.models import FileChangeStatus

router = APIRouter(prefix="/scanner", tags=["scanner"])


class ScanRequest(BaseModel):
    repo_path: str


class ScanResponse(BaseModel):
    added: int
    modified: int
    deleted: int
    unchanged: int


@router.post("/scan", response_model=ScanResponse)
async def scan_repository(request: ScanRequest) -> ScanResponse:
    import os

    repo_path = os.path.abspath(request.repo_path)

    db = PrismaClient()
    if not db.is_connected():
        await db.connect()

    try:
        # Fetch existing state
        existing_records = await db.filemetadata.find_many(
            where={"repo_path": repo_path}
        )
        existing_files: Dict[str, str] = {
            record.file_path: record.file_hash for record in existing_records
        }

        scanner = RepositoryScanner(repo_path)

        added = 0
        modified = 0
        deleted = 0
        unchanged = 0

        # Note: Prisma Python doesn't natively support bulk upserts yet in a single query
        # so we will process sequentially. In production, this might be optimized or batched.
        async with db.tx() as transaction:
            async for event in scanner.scan_directory(existing_files):
                if event.status == FileChangeStatus.ADDED:
                    await transaction.filemetadata.create(
                        data={
                            "repo_path": event.repo_path,
                            "file_path": event.file_path,
                            "file_hash": event.file_hash,
                        }
                    )
                    added += 1
                elif event.status == FileChangeStatus.MODIFIED:
                    await transaction.filemetadata.update(
                        where={
                            "repo_path_file_path": {
                                "repo_path": event.repo_path,
                                "file_path": event.file_path,
                            }
                        },
                        data={
                            "file_hash": event.file_hash,
                        },
                    )
                    modified += 1
                elif event.status == FileChangeStatus.DELETED:
                    await transaction.filemetadata.delete(
                        where={
                            "repo_path_file_path": {
                                "repo_path": event.repo_path,
                                "file_path": event.file_path,
                            }
                        }
                    )
                    deleted += 1
                else:
                    unchanged += 1

        return ScanResponse(
            added=added, modified=modified, deleted=deleted, unchanged=unchanged
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # We might not want to disconnect if the app manages connection lifecycle,
        # but since we initialized it here, we disconnect or leave it to the app lifecycle.
        # In this API, we will just rely on the global Prisma instance usually,
        # but here we connect/disconnect or better, use dependency injection.
        # Let's fix this in a refactor to use a global db instance.
        if db.is_connected():
            await db.disconnect()
