"""Immutable content-addressed local evidence storage."""

import hashlib
import io
import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class StoredFile:
    file_id: str
    uri: str
    sha256: str


class LocalEvidenceStorage:
    def __init__(self, root: Path) -> None:
        self._root = root

    def store_path(self, source: Path, category: str) -> StoredFile:
        with source.open("rb") as stream:
            return self.store_bytes(stream.read(), source.suffix.lower(), category)

    def store_bytes(self, content: bytes, suffix: str, category: str) -> StoredFile:
        digest = hashlib.sha256(content).hexdigest()
        file_id = f"FILE-{uuid4().hex}"
        relative = Path(category) / digest[:2] / f"{file_id}{suffix}"
        destination = self._root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with io.BytesIO(content) as reader, destination.open("xb") as writer:
            shutil.copyfileobj(reader, writer)
        return StoredFile(file_id=file_id, uri=relative.as_posix(), sha256=digest)

    @staticmethod
    def hash_path(source: Path) -> str:
        digest = hashlib.sha256()
        with source.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def discard(self, uri: str) -> None:
        """Delete a stored file, constrained to the evidence root.

        The uri must be the relative path previously returned by store_bytes/
        store_path. Absolute paths and path traversal are refused with
        ValueError; a missing file is a no-op.
        """
        relative = Path(uri)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"refusing to discard outside the evidence root: {uri}")
        target = (self._root / relative).resolve()
        root = self._root.resolve()
        if root != target and root not in target.parents:
            raise ValueError(f"refusing to discard outside the evidence root: {uri}")
        target.unlink(missing_ok=True)
