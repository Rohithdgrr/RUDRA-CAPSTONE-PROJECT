"""Pydantic schemas for campaign validation — see docs/05-CAMPAIGN_SCHEMA.md."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from src.config.defaults import DEFAULT_WEIGHTS, DEFAULT_THRESHOLDS

VALID_FAULT_IDS = [
    # Sensor SF-01..07
    "SF-01", "SF-02", "SF-03", "SF-04", "SF-05", "SF-06", "SF-07",
    # Timing TF-01..05
    "TF-01", "TF-02", "TF-03", "TF-04", "TF-05",
    # Comm CF-01..06
    "CF-01", "CF-02", "CF-03", "CF-04", "CF-05", "CF-06",
    # Memory MF-01..04
    "MF-01", "MF-02", "MF-03", "MF-04",
    # Power PF-01..03
    "PF-01", "PF-02", "PF-03",
    # GPIO GF-01..02
    "GF-01", "GF-02",
]

SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class ScoringWeights(BaseModel):
    detection: float = Field(default=0.4, ge=0, le=1)
    recovery: float = Field(default=0.3, ge=0, le=1)
    safety: float = Field(default=0.3, ge=0, le=1)

    @model_validator(mode="after")
    def check_sum(self):
        total = self.detection + self.recovery + self.safety
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"weights must sum to 1.0, got {total}")
        return self


class ScoringThresholds(BaseModel):
    grade_a: int = Field(default=90, ge=0, le=100)
    grade_b: int = Field(default=70, ge=0, le=100)
    grade_c: int = Field(default=50, ge=0, le=100)
    grade_d: int = Field(default=30, ge=0, le=100)


class ScoringConfig(BaseModel):
    weights: ScoringWeights = Field(default_factory=ScoringWeights)
    thresholds: ScoringThresholds = Field(default_factory=ScoringThresholds)


class FaultConfig(BaseModel):
    id: str = Field(..., description="Fault ID e.g. SF-01")
    name: Optional[str] = None
    params: dict[str, Any] = Field(default_factory=dict)
    expected: str = Field(default="", description="expected behavior expression")
    timeout_ms: int = Field(default=5000, ge=100, le=60000)
    severity: str = Field(default="MEDIUM")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        if v not in VALID_FAULT_IDS:
            raise ValueError(f"Unknown fault ID '{v}'. Valid: {VALID_FAULT_IDS}")
        return v

    @field_validator("severity")
    @classmethod
    def validate_sev(cls, v):
        if v not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}")
        return v


class CampaignConfig(BaseModel):
    name: str = Field(..., min_length=3, max_length=64)
    description: Optional[str] = None
    firmware: str = Field(..., description="Path to ELF")
    platform: str = Field(..., description="REPL path or platform id")
    duration: int = Field(default=60, ge=1, le=3600)
    parallel: int = Field(default=1, ge=1, le=8)
    faults: list[FaultConfig] = Field(..., min_length=1, max_length=27)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)

    @field_validator("faults")
    @classmethod
    def unique_ids(cls, v):
        ids = [f.id for f in v]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate fault ids in campaign")
        return v
