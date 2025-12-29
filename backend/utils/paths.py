from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return repository root (folder containing `backend/` and `data/`)."""
    # backend/utils/paths.py -> backend/ -> repo root
    return Path(__file__).resolve().parents[2]


def data_root() -> Path:
    return project_root() / "data"


def raw_root() -> Path:
    return data_root() / "raw"


def raw_pdfs_dir() -> Path:
    return raw_root() / "raw_pdfs"


def raw_text_dir() -> Path:
    return raw_root() / "raw_text"


def raw_web_dir() -> Path:
    return raw_root() / "raw_web"


def vectors_dir() -> Path:
    return data_root() / "vectors"
