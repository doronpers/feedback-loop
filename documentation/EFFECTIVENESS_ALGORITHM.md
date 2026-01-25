# Pattern Effectiveness Algorithm Documentation

## Overview

The pattern effectiveness algorithm measures how well patterns prevent recurring issues over time. This document describes the enhanced statistical methods used to calculate effectiveness scores.

## Algorithm Components

### 1. Data Collection

Pattern occurrences are collected from:

- Bug reports (`metrics_data.bugs`)
- Test failures (`metrics_data.test_failures`)
- Code reviews (`metrics_data.code_reviews`)

Each occurrence includes a timestamp for time-series analysis.

### 2. Statistical Methods

The enhanced algorithm uses three complementary statistical approaches:

#### 2.1 Exponential Smoothing

**Purpose:** Reduce noise and identify underlying trends

**Method:**

- Converts timestamps to daily occurrence counts
- Applies exponential smoothing with alpha = 0.3
- Calculates average rates for first and second half of time window
- Formula: `smoothed[i] = alpha * count[i] + (1 - alpha) * smoothed[i-1]`

**Benefits:**

- Reduces impact of outliers
- Provides smoother trend visualization
- Better handles irregular data collection

#### 2.2 Mann-Whitney U Test

**Purpose:** Determine if trend change is statistically significant

**Method:**

- Converts timestamps to numeric values (days since first occurrence)
- Splits data into first and second half
- Calculates U statistic using rank-based approach
- Approximates p-value using normal distribution

**Interpretation:**

- p < 0.05: Statistically significant change
- p >= 0.05: Change may be due to random variation

**Benefits:**

- Non-parametric (no distribution assumptions)
- Robust to outliers
- Works with small sample sizes

#### 2.3 Bootstrap Confidence Intervals

**Purpose:** Estimate uncertainty in effectiveness scores

**Method:**

- Resamples daily counts with replacement (1000 iterations)
- Calculates effectiveness score for each resample
- Determines 95% confidence interval from distribution

**Benefits:**

- Provides uncertainty estimates
- No distribution assumptions
- Works with any sample size

### 3. Effectiveness Score Calculation

**Formula:**

```
reduction_ratio = (first_half_rate - second_half_rate) / first_half_rate
score = max(0.0, min(1.0, (reduction_ratio + 1) / 2))
```

**Score Interpretation:**

- 0.0 - 0.4: Pattern not effective (issues increasing)
- 0.4 - 0.6: Pattern neutral (no clear trend)
- 0.6 - 0.8: Pattern moderately effective
- 0.8 - 1.0: Pattern highly effective (issues decreasing)

**Trend Classification:**

- `improving`: reduction_ratio > 0.2 (20% reduction)
- `stable`: -0.2 <= reduction_ratio <= 0.2
- `worsening`: reduction_ratio < -0.2

### 4. Minimum Sample Size

**Requirements:**

- Minimum 2 occurrences: Basic split-half analysis
- Minimum 4 occurrences: Enhanced statistical methods
- Recommended 10+ occurrences: Reliable confidence intervals

**Fallback Behavior:**

- Insufficient data: Returns score of 0.5 with `insufficient_data` trend
- Small samples: Uses simple split-half method
- Large samples: Uses full statistical analysis

## Output Format

```python
{
    "score": 0.75,  # Effectiveness score (0.0 - 1.0)
    "trend": "improving",  # improving | stable | worsening | insufficient_data
    "total_occurrences": 24,
    "first_half_rate": 0.8,  # Occurrences per day
    "second_half_rate": 0.4,  # Occurrences per day
    "confidence_interval": (0.65, 0.85),  # 95% CI
    "statistical_significance": True,  # p < 0.05
    "p_value": 0.03,  # Statistical test p-value
    "method": "enhanced_statistical",  # Algorithm used
    "smoothed_trend": [0.5, 0.6, 0.4, ...]  # Smoothed daily counts
}
```

## Configuration

**Time Window:**

- Default: 30 days
- Configurable via `analysis.time_window_days` in config
- Longer windows: More stable but slower to detect changes
- Shorter windows: Faster detection but more noise

**Smoothing Parameter:**

- Alpha = 0.3 (hardcoded, can be made configurable)
- Lower alpha: More smoothing, slower response
- Higher alpha: Less smoothing, faster response

## Limitations

1. **Temporal Patterns:** Assumes linear trend over time window
2. **Causality:** Correlation doesn't imply causation
3. **External Factors:** Doesn't account for external changes (team size, project phase)
4. **Pattern Interactions:** Doesn't model interactions between patterns

## Future Enhancements

1. **Seasonal Adjustments:** Account for time-based patterns
2. **Causal Inference:** Use difference-in-differences or regression discontinuity
3. **Pattern Interactions:** Model how patterns affect each other
4. **Bayesian Methods:** Use prior knowledge to improve estimates

## References

- Mann-Whitney U Test: Non-parametric test for comparing two groups
- Exponential Smoothing: Time series forecasting method
- Bootstrap Method: Resampling technique for confidence intervals

## Code Location

- Main algorithm: `metrics/analyzer.py::calculate_effectiveness()`
- Statistical methods: `metrics/analyzer.py::_calculate_effectiveness_statistics()`
- Helper functions: `metrics/analyzer.py::_*_analysis()`
