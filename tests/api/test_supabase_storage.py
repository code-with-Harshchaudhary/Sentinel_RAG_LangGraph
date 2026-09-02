from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from lightrag.api.supabase_storage import (
    SupabaseDocumentStorage,
    SupabaseStorageConfig,
)


def test_storage_config_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_STORAGE_ENABLED", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    assert SupabaseStorageConfig.from_env("sentinel") is None


def test_enabled_storage_requires_server_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPABASE_STORAGE_ENABLED", "true")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    with pytest.raises(ValueError, match="SUPABASE_URL"):
        SupabaseStorageConfig.from_env("sentinel")


@pytest.mark.asyncio
async def test_upload_archive_and_delete_use_private_storage_api(
    tmp_path: Path,
) -> None:
    requests: list[tuple[str, str, bytes]] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        body = await request.aread()
        requests.append((request.method, request.url.path, body))
        return httpx.Response(200, json={"ok": True})

    config = SupabaseStorageConfig(
        url="https://project.supabase.co",
        service_role_key="server-secret",
        bucket="sentinel-documents",
        prefix="documents",
        workspace="sentinel",
    )
    store = SupabaseDocumentStorage(config, transport=httpx.MockTransport(handler))
    source = tmp_path / "notes.txt"
    source.write_text("durable source", encoding="utf-8")

    pending_key = await store.upload_file(source)
    await store.archive_file(source.name, source)
    await store.delete_document(source.name)

    assert pending_key == "documents/pending/sentinel/notes.txt"
    assert requests[0] == (
        "POST",
        "/storage/v1/object/sentinel-documents/documents/pending/sentinel/notes.txt",
        b"durable source",
    )
    assert requests[1][1].endswith(
        "/documents/processed/sentinel/notes.txt"
    )
    delete_payloads = [
        json.loads(body)
        for method, _, body in requests
        if method == "DELETE"
    ]
    assert delete_payloads[0] == {
        "prefixes": ["documents/pending/sentinel/notes.txt"]
    }
    assert delete_payloads[1] == {
        "prefixes": [
            "documents/pending/sentinel/notes.txt",
            "documents/processed/sentinel/notes.txt",
        ]
    }


@pytest.mark.asyncio
async def test_restore_pending_downloads_only_missing_safe_files(
    tmp_path: Path,
) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if "/object/list/" in request.url.path:
            return httpx.Response(
                200,
                json=[{"name": "resume.pdf"}, {"name": "../unsafe.txt"}],
            )
        if request.method == "GET":
            return httpx.Response(200, content=b"pdf bytes")
        return httpx.Response(500)

    config = SupabaseStorageConfig(
        url="https://project.supabase.co",
        service_role_key="server-secret",
        bucket="sentinel-documents",
        prefix="documents",
        workspace="sentinel",
    )
    store = SupabaseDocumentStorage(config, transport=httpx.MockTransport(handler))

    restored = await store.restore_pending(tmp_path)

    assert restored == [tmp_path / "resume.pdf"]
    assert (tmp_path / "resume.pdf").read_bytes() == b"pdf bytes"
    assert not (tmp_path.parent / "unsafe.txt").exists()
