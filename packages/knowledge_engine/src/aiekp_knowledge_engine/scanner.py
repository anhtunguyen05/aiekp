import os
import hashlib
from typing import AsyncGenerator, Dict, Set

from aiekp_shared.domain.models import FileScanEvent, FileChangeStatus

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".next",
    "dist",
    "build",
}
WHITELISTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".prisma",
}


def hash_file(filepath: str) -> str:
    """Calculate SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in chunks
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


class RepositoryScanner:
    """Scans a repository to detect ADDED, MODIFIED, DELETED, and UNCHANGED files."""

    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)

    async def scan_directory(
        self, existing_files: Dict[str, str]
    ) -> AsyncGenerator[FileScanEvent, None]:
        """
        Scan directory and yield FileScanEvents based on existing_files map.
        existing_files is a dict mapping relative file paths to their last known SHA-256 hash.
        """
        seen_files: Set[str] = set()

        for root, dirs, files in os.walk(self.repo_path):
            # Modify dirs in-place to avoid traversing ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in WHITELISTED_EXTENSIONS:
                    continue

                full_path = os.path.join(root, file)
                # Convert to relative path with forward slashes for cross-platform consistency
                rel_path = os.path.relpath(full_path, self.repo_path).replace("\\", "/")
                seen_files.add(rel_path)

                try:
                    current_hash = hash_file(full_path)
                except Exception:
                    # Skip files that can't be read
                    continue

                if rel_path not in existing_files:
                    yield FileScanEvent(
                        repo_path=self.repo_path,
                        file_path=rel_path,
                        file_hash=current_hash,
                        status=FileChangeStatus.ADDED,
                    )
                elif existing_files[rel_path] != current_hash:
                    yield FileScanEvent(
                        repo_path=self.repo_path,
                        file_path=rel_path,
                        file_hash=current_hash,
                        status=FileChangeStatus.MODIFIED,
                    )
                else:
                    yield FileScanEvent(
                        repo_path=self.repo_path,
                        file_path=rel_path,
                        file_hash=current_hash,
                        status=FileChangeStatus.UNCHANGED,
                    )

        # Detect deleted files
        for rel_path in existing_files:
            if rel_path not in seen_files:
                yield FileScanEvent(
                    repo_path=self.repo_path,
                    file_path=rel_path,
                    file_hash=None,
                    status=FileChangeStatus.DELETED,
                )
