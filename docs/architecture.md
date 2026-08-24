# V1 Architecture

## Flow

`source connector -> observations -> normalization -> employer grouping -> scoring -> prioritized opportunities -> dashboard/API`

Every observation carries source, source URL, timestamp, external ID, and verification status. This is intentional: Driftless Workforce needs evidence behind every prospect rather than a list of unverified names.

## Initial source

The first production connector will target Wisconsin Job Center / Wisconsin workforce job data for the La Crosse area. The connector should map source records into `JobObservation` without embedding source-specific logic into scoring.

## Scoring

The initial 100-point model uses:

- opening volume: up to 30
- hiring momentum: up to 25
- target-industry signal: up to 20
- leadership hiring signal: up to 15
- source quality/verification: up to 10

Thresholds:

- **Pursue:** 70–100
- **Monitor:** 40–69
- **Low:** 0–39

This is a V1 scoring model, not a claim that the score is predictive. The next iteration should calibrate weights against actual recruiting outcomes.

## Data integrity rules

1. Demo records must be explicitly marked `DEMO`.
2. Production observations must retain a source URL whenever the source provides one.
3. Employer names are normalized for matching but the original employer name is preserved.
4. Scores are derived from observations and should be reproducible.
5. The engine should prefer evidence-backed changes over raw opening counts.
