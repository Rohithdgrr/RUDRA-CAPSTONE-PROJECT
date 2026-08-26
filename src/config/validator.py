"""Campaign YAML validator — used by CLI and GUI."""
from __future__ import annotations

import sys
from pathlib import Path
import yaml
from pydantic import ValidationError
from src.config.schemas import CampaignConfig


def validate_file(path: str | Path) -> CampaignConfig:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
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
