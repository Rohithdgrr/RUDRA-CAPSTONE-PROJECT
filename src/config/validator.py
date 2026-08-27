"""Campaign YAML validator — used by CLI and GUI."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

from src.config.schemas import CampaignConfig


def validate_file(path: str | Path) -> CampaignConfig:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Campaign file not found: {p}")
    if p.stat().st_size == 0:
        raise ValueError(f"Empty campaign file: {p}")
    text = p.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Empty campaign file: {p}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {p}: {e}") from e
    if data is None:
        raise ValueError(f"Empty campaign file (no YAML document): {p}")
    if not isinstance(data, dict):
        raise ValueError(f"Campaign YAML must be a mapping, got {type(data).__name__}: {p}")
    return CampaignConfig.model_validate(data)


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.config.validator <campaign.yaml>")
        sys.exit(2)
    try:
        cfg = validate_file(sys.argv[1])
        print(f"OK: {cfg.name} ({len(cfg.faults)} faults)")
    except ValidationError as e:
        print(e)
        sys.exit(1)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
