from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT_DIR / "processed_dataset"


def candidate_paths(filename: str) -> list[Path]:
    return [
        DATASET_DIR / filename,
        ROOT_DIR / "backend" / filename,
        ROOT_DIR / filename,
    ]


def load_dataframe(preferred_files: Iterable[str]) -> pd.DataFrame:
    for file_name in preferred_files:
        for path in candidate_paths(file_name):
            if not path.exists():
                continue
            if path.suffix == ".parquet":
                return pd.read_parquet(path)
            if path.suffix == ".csv":
                return pd.read_csv(path)
            if path.suffix == ".json":
                return pd.read_json(path)
    return pd.DataFrame()


def pick_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    available = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in available:
            return available[candidate.lower()]
    return None


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def parse_possible_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return []
        try:
            parsed = json.loads(cleaned)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            try:
                parsed = ast.literal_eval(cleaned)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
    return []
