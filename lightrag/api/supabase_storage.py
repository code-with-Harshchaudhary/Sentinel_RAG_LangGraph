"""Private Supabase Storage integration for durable source documents.

The RAG pipeline still parses normal local files. This adapter mirrors those
files to a private Supabase bucket and restores pending objects after an
ephemeral host restarts. It deliberately uses the Storage REST API through
``httpx`` so the backend does not need the full Supabase SDK.
"""

from __future__ import annotations

import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator
from urllib.parse import quote

import aiofiles
import httpx


class SupabaseStorageError(RuntimeError):
    """Raised when durable source-document storage cannot complete an action."""


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _clean_segment(value: str, field: str) -> str:
    cleaned = value.strip().strip("/")
    if not cleaned or cleaned in {".", ".."} or "/" in cleaned or "\\" in cleaned:
        raise ValueError(f"{field} must be one safe path segment")
    return cleaned


@dataclass(frozen=True)
class SupabaseStorageConfig:
    url: str
    service_role_key: str
    bucket: str
    prefix: str
    workspace: str
    timeout_seconds: float = 60.0

    @classmethod
    def from_env(cls, workspace: str = "") -> SupabaseStorageConfig | None:
        if not _as_bool(os.getenv("SUPABASE_STORAGE_ENABLED"), default=False):
            return None

        url = (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")
        key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
        if not url or not key:
            raise ValueError(
                "SUPABASE_STORAGE_ENABLED=true requires SUPABASE_URL and "
                "SUPABASE_SERVICE_ROLE_KEY"
            )
        if not url.startswith("https://"):
            raise ValueError("SUPABASE_URL must use https://")

        bucket = _clean_segment(
            os.getenv("SUPABASE_STORAGE_BUCKET", "sentinel-documents"),
            "SUPABASE_STORAGE_BUCKET",
        )
        prefix = (os.getenv("SUPABASE_STORAGE_PREFIX") or "documents").strip("/")
        if not prefix or any(part in {"", ".", ".."} for part in prefix.split("/")):
            raise ValueError("SUPABASE_STORAGE_PREFIX must be a safe relative path")

        workspace_segment = _clean_segment(workspace or "default", "WORKSPACE")
        timeout = float(os.getenv("SUPABASE_STORAGE_TIMEOUT", "60"))
        if timeout <= 0:
            raise ValueError("SUPABASE_STORAGE_TIMEOUT must be greater than zero")

        return cls(
            url=url,
            service_role_key=key,
            bucket=bucket,
            prefix=prefix,
            workspace=workspace_segment,
            timeout_seconds=timeout,
        )


class SupabaseDocumentStorage:
    """Mirror source files between the local parser workspace and Supabase."""

    def __init__(
        self,
        config: SupabaseStorageConfig,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.config = config
        self._transport = transport

    @classmethod
    def from_env(cls, workspace: str = "") -> SupabaseDocumentStorage | None:
        config = SupabaseStorageConfig.from_env(workspace)
        return cls(config) if config is not None else None

    @property
    def _api_url(self) -> str:
        return f"{self.config.url}/storage/v1"

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "apikey": self.config.service_role_key,
            "Authorization": f"Bearer {self.config.service_role_key}",
        }

    def _folder(self, state: str) -> str:
        if state not in {"pending", "processed"}:
            raise ValueError("document state must be pending or processed")
        return f"{self.config.prefix}/{state}/{self.config.workspace}"

    def _object_key(self, state: str, filename: str) -> str:
        safe_name = Path(filename).name
        if safe_name != filename or safe_name in {"", ".", ".."}:
            raise ValueError("filename must be a safe basename")
        return f"{self._folder(state)}/{safe_name}"

    def _object_url(self, key: str) -> str:
        bucket = quote(self.config.bucket, safe="")
        encoded_key = quote(key, safe="/")
        return f"{self._api_url}/object/{bucket}/{encoded_key}"

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            headers=self._headers,
            timeout=self.config.timeout_seconds,
            transport=self._transport,
        )

    @staticmethod
    async def _file_chunks(path: Path) -> AsyncIterator[bytes]:
        async with aiofiles.open(path, "rb") as source:
            while chunk := await source.read(1024 * 1024):
                yield chunk

    @staticmethod
    def _raise_for_status(response: httpx.Response, action: str) -> None:
        if response.is_success:
            return
        raise SupabaseStorageError(
            f"Supabase Storage {action} failed with HTTP {response.status_code}"
        )

    async def upload_file(
        self,
        path: Path,
        *,
        state: str = "pending",
        object_name: str | None = None,
    ) -> str:
        if not path.is_file():
            raise SupabaseStorageError(f"Source document does not exist: {path.name}")

        key = self._object_key(state, object_name or path.name)
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        headers = {
            "content-type": content_type,
            "cache-control": "no-store",
            "x-upsert": "true",
        }
        async with self._client() as client:
            response = await client.post(
                self._object_url(key),
                headers=headers,
                content=self._file_chunks(path),
            )
        self._raise_for_status(response, "upload")
        return key

    async def archive_file(self, source_name: str, archived_path: Path) -> None:
        """Persist the processed copy, then retire its pending object."""
        await self.upload_file(
            archived_path,
            state="processed",
            object_name=source_name,
        )
        await self._remove_keys([self._object_key("pending", source_name)])

    async def _list(self, state: str) -> list[str]:
        bucket = quote(self.config.bucket, safe="")
        url = f"{self._api_url}/object/list/{bucket}"
        folder = self._folder(state)
        names: list[str] = []
        offset = 0
        limit = 1000

        async with self._client() as client:
            while True:
                response = await client.post(
                    url,
                    json={
                        "prefix": folder,
                        "limit": limit,
                        "offset": offset,
                        "sortBy": {"column": "name", "order": "asc"},
                    },
                )
                self._raise_for_status(response, "list")
                page = response.json()
                if not isinstance(page, list):
                    raise SupabaseStorageError(
                        "Supabase Storage list returned an unexpected response"
                    )
                for item in page:
                    name = item.get("name") if isinstance(item, dict) else None
                    if isinstance(name, str) and name:
                        names.append(name)
                if len(page) < limit:
                    break
                offset += limit
        return names

    async def restore_pending(self, input_dir: Path) -> list[Path]:
        """Download missing pending objects for crash/restart recovery."""
        input_dir.mkdir(parents=True, exist_ok=True)
        restored: list[Path] = []
        for name in await self._list("pending"):
            safe_name = Path(name).name
            if safe_name != name or safe_name in {"", ".", ".."}:
                continue
            target = input_dir / safe_name
            if target.exists():
                continue
            key = self._object_key("pending", safe_name)
            async with self._client() as client:
                async with client.stream("GET", self._object_url(key)) as response:
                    self._raise_for_status(response, "download")
                    temporary = target.with_name(f".{target.name}.restore")
                    try:
                        async with aiofiles.open(temporary, "xb") as output:
                            async for chunk in response.aiter_bytes():
                                await output.write(chunk)
                        temporary.replace(target)
                    finally:
                        if temporary.exists():
                            temporary.unlink()
            restored.append(target)
        return restored

    async def _remove_keys(self, keys: list[str]) -> None:
        if not keys:
            return
        bucket = quote(self.config.bucket, safe="")
        url = f"{self._api_url}/object/{bucket}"
        async with self._client() as client:
            for start in range(0, len(keys), 1000):
                response = await client.request(
                    "DELETE", url, json={"prefixes": keys[start : start + 1000]}
                )
                self._raise_for_status(response, "delete")

    async def delete_document(self, filename: str) -> None:
        safe_name = Path(filename).name
        if not safe_name or safe_name in {".", ".."}:
            return
        await self._remove_keys(
            [
                self._object_key("pending", safe_name),
                self._object_key("processed", safe_name),
            ]
        )

    async def clear(self) -> int:
        keys: list[str] = []
        for state in ("pending", "processed"):
            keys.extend(self._object_key(state, name) for name in await self._list(state))
        await self._remove_keys(keys)
        return len(keys)

    async def check_connection(self) -> None:
        await self._list("pending")


_REGISTERED_INPUT_STORES: dict[Path, SupabaseDocumentStorage] = {}
_PERSISTED_LOCAL_SOURCES: set[Path] = set()


def _absolute_path(path: Path) -> Path:
    """Normalize a path lexically without touching the filesystem."""
    return Path(os.path.abspath(path))


def register_input_store(input_dir: Path, store: SupabaseDocumentStorage | None) -> None:
    root = _absolute_path(input_dir)
    if store is not None:
        _REGISTERED_INPUT_STORES[root] = store
    else:
        _REGISTERED_INPUT_STORES.pop(root, None)


def mark_source_persisted(path: Path) -> None:
    """Record that an upload was durably mirrored before background enqueue."""
    _PERSISTED_LOCAL_SOURCES.add(_absolute_path(path))


def take_source_persisted(path: Path) -> bool:
    """Consume the pre-persist marker used by the next enqueue attempt."""
    source = _absolute_path(path)
    if source not in _PERSISTED_LOCAL_SOURCES:
        return False
    _PERSISTED_LOCAL_SOURCES.remove(source)
    return True


def storage_for_source(path: Path) -> SupabaseDocumentStorage | None:
    if not _REGISTERED_INPUT_STORES:
        return None
    source = _absolute_path(path)
    for root, store in _REGISTERED_INPUT_STORES.items():
        try:
            source.relative_to(root)
            return store
        except ValueError:
            continue
    return None
