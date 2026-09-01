SHELL := /bin/bash

.PHONY: help install frontend build dev test test-backend test-frontend lint clean

help:
	@echo "Sentinel RAG Ops"
	@echo "  make install        Install backend and frontend dependencies"
	@echo "  make build          Build the production WebUI"
	@echo "  make dev            Start the API server"
	@echo "  make test           Run backend and frontend tests"
	@echo "  make lint           Run Python and frontend linters"
	@echo "  make clean          Remove generated build and cache output"

install:
	uv sync --extra api --extra offline-storage --extra offline-llm --extra pytest
	cd lightrag_webui && bun install --frozen-lockfile

frontend:
	cd lightrag_webui && bun install --frozen-lockfile

build:
	cd lightrag_webui && bun run build

dev:
	uv run sentinel-rag-server

test: test-backend test-frontend

test-backend:
	uv run --no-sync pytest tests/ -m offline --tb=short

test-frontend:
	cd lightrag_webui && bun run test

lint:
	uv run ruff check lightrag tests
	cd lightrag_webui && bun run lint

clean:
	rm -rf build dist .pytest_cache .ruff_cache lightrag/api/webui
