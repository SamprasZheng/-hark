"""Decision layer — one standardized checklist + risk policy + eval-function calibration.

Composes the existing scoring / regime / valuation modules into a single GATED
scorecard per ticker (see philosophy/_proposals/standard-decision-checklist.md):

    exclusion gate (06) -> regime (classifier) -> FOM tilt (fom) ->
    valuation + order/demand trajectory -> RF cycle (rfpm) ->
    4-dimension arbitration (02) -> 4-quadrant route (03) ->
    horizon bucket + position size (01 + 08) -> invalidation -> confidence.

RECOMMEND-ONLY / observe-first. This layer never places trades, never changes the
position caps in risk_config.yaml, and honours as_of (no lookahead). Kept import-light
so `from sharks.decision import _yamlite` does not pull in pandas.
"""
