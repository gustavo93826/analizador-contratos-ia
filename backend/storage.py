# backend/storage.py

import json
import uuid
from pathlib import Path

UPLOADS_DIR = Path("data/uploads")
PROCESSED_DIR = Path("data/processed")
REGISTRY_PATH = Path("data/contracts.json")

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def _load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_registry(registry: dict) -> None:
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)


def generate_contract_id() -> str:
    return uuid.uuid4().hex[:12]


def register_contract(contract_id: str, filename: str, num_paginas: int) -> None:
    registry = _load_registry()
    registry[contract_id] = {"filename": filename, "num_paginas": num_paginas}
    _save_registry(registry)


def contract_exists(contract_id: str) -> bool:
    return contract_id in _load_registry()


def get_contract_metadata(contract_id: str) -> dict | None:
    return _load_registry().get(contract_id)


def save_processed_pages(contract_id: str, pages_data: list[dict]) -> None:
    path = PROCESSED_DIR / f"{contract_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(pages_data, f, ensure_ascii=False, indent=2)


def load_processed_pages(contract_id: str) -> list[dict]:
    path = PROCESSED_DIR / f"{contract_id}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_upload_path(contract_id: str, filename: str) -> Path:
    return UPLOADS_DIR / f"{contract_id}_{filename}"