"""Pydantic schemas for campaign validation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

VALID_FAULT_IDS = [
    "SF-01",
    "SF-02",
    "SF-03",
    "SF-04",
    "SF-05",
    "SF-06",
    "SF-07",
    "TF-01",
    "TF-02",
    "TF-03",
    "TF-04",
    "TF-05",
    "CF-01",
    "CF-02",
    "CF-03",
    "CF-04",
    "CF-05",
    "CF-06",
    "MF-01",
    "MF-02",
    "MF-03",
    "MF-04",
    "PF-01",
    "PF-02",
    "PF-03",
    "GF-01",
    "GF-02",
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

    @model_validator(mode="after")
    def check_ordering(self):
        if not (self.grade_a > self.grade_b > self.grade_c > self.grade_d):
            raise ValueError(
                f"Thresholds must be ordered: grade_a({self.grade_a}) > "
                f"grade_b({self.grade_b}) > grade_c({self.grade_c}) > "
                f"grade_d({self.grade_d})"
            )
        return self


class ScoringConfig(BaseModel):
    weights: ScoringWeights = Field(default_factory=ScoringWeights)
    thresholds: ScoringThresholds = Field(default_factory=ScoringThresholds)


class FaultConfig(BaseModel):
    id: str = Field(..., description="Fault ID e.g. SF-01")
    name: str | None = None
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
    description: str | None = None
    firmware: str = Field(..., description="Path to ELF")
    platform: str = Field(..., description="REPL path or platform id")
    duration: int = Field(default=60, ge=1, le=3600)
    parallel: int = Field(default=1, ge=1, le=8)
    faults: list[FaultConfig] = Field(..., min_length=1, max_length=27)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)

    @field_validator("faults")
    @classmethod
    def validate_fault_count(cls, v):
        if len(v) < 1:
            raise ValueError("At least 1 fault required")
        if len(v) > 27:
            raise ValueError("Maximum 27 faults allowed")
        ids = [f.id for f in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate fault IDs in campaign")
        return v
