# ADR 003 — Resilience Index Weights 40/30/30

> **Date:** 2026-08-26 | **Status:** Accepted

## Context

Need quantitative `RI 0-100` (`README.md:52`) to turn "robust" into measurable. Components Detection, Recovery, Safety each 0-100.

## Decision

**Default `detection 0.4, recovery 0.3, safety 0.3`** — `RI=(D*0.4)+(Rec*0.3)+(S*0.3)` normalized (`08-RESILIENCE_INDEX.md`).

## Rationale

- Detection most critical: if firmware doesn't see fault, recovery/safety moot → weight 0.4.
- Recovery and Safety equal 0.3: recovery shows resilience, safety is non-negotiable but already gated by `safe==False → critical diagnosis` (`09-DIAGNOSIS_ENGINE.md`).
- Simple integer math, explains Grade thresholds A 90 B 70 C 50 D 30.
- Configurable per campaign `scoring.weights` sum 1.0 (`05-CAMPAIGN_SCHEMA.md`) for ASIL-D tuning `0.3/0.2/0.5`.

## Consequences

- Pass/fail Grade B ≥70 aligns with PRD objective 7 `Grade B (70+)`.
- Worked example: `D100 Rec0 S100 =70 B` vs `D0 Rec0 S100=30 D` → distinguishes detection failure.
- Future ML weighting can override defaults per `09-DIAGNOSIS_ENGINE.md` v1.1.

## Alternatives

Equal 33/33/34 rejected: under-weights detection. Safety-heavy 30/20/50 considered for automotive but not default general-purpose.

## References

`src/core/resilience_index.py`, `README.md:192`, `08-RESILIENCE_INDEX.md`
