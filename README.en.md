# Simulation-Based Statistical Test Selection Tool

A Monte Carlo simulation study systematically evaluating the Type I error control and statistical power of five two-sample comparison tests (Student's t, Welch's t, Mann-Whitney U, permutation, bootstrap-t) under varying data conditions: skewness, heavy tails, outlier contamination, heteroscedasticity, and sample-size imbalance.

**Status:** Active development — simulation complete, visualization/decision-tool/report stages in progress.

## Key Findings

From 180 scenarios × 3,000 replications (Monte Carlo standard error reported alongside every estimate):

1. **Student's t-test becomes severely conservative when larger variance is paired with larger sample size.** Under a normal distribution, variance ratio = 4, n = (10, 50), the empirical Type I error rate was **0.0027** (MC SE = 0.0009) — far below the nominal 0.05. Welch's t-test reached **0.0577** under the same condition, as expected. This conservatism directly costs statistical power: at d = 0.2 under the same scenario, Student's t power was only **0.019**, versus **0.130** for Welch's t and **0.111** for the permutation test — roughly a 6–7x difference.

2. **Mann-Whitney U inflates unexpectedly under skewness combined with a high variance ratio.** Under a skew-normal distribution, variance ratio = 4, n = (100, 100), the empirical Type I error rate was **0.194** (MC SE = 0.0072) — nearly 4x the nominal rate, while Welch's t remained at 0.0493 under the same condition. This directly challenges the common assumption that "Mann-Whitney is always the safe alternative to the t-test": the test does not actually assess mean equality but stochastic equality (P(X>Y)=0.5), and heteroscedasticity combined with skewness can decouple these two hypotheses.

3. **Under heavy-tailed distributions, Mann-Whitney provides a genuine power advantage.** Under a t-distribution (df=5), equal variances, d=0.5: at n=30, power was **0.554** for Mann-Whitney (MC SE=0.0091) versus 0.490 for Student's t; at n=100, **0.973** (MC SE=0.0030) versus 0.933. At the same time, under a purely normal distribution Mann-Whitney trails slightly at small sample sizes (n=10, d=0.5: 0.156 vs. 0.183 for Student's t) — the expected relative efficiency loss under normality.

*(Welch's t, the studentized permutation test, and bootstrap-t all maintained Type I error control within 0.032–0.062 across all 180 tested scenarios, confirming their robustness.)*

## Methodology

- **Target parameter:** All tests were compared under the same data-generating framework (a location shift). The fact that Mann-Whitney U's null hypothesis (stochastic equality) differs from the other tests' (mean equality) is explicitly noted — and is, in fact, part of the mechanism behind Finding 2.
- **Distributions:** Normal, skew-normal (α=5), t-distribution (df=5), and a contamination mixture (95% N(0,1) + 5% N(0,9)) — each standardized to a `hedef_varyans=1` (target variance = 1) reference, so that the effect size (Cohen's d) remains comparable across all conditions.
- **Effect size application:** n1/n2-weighted pooled SD (the same formula used internally by Student's t-test's own pooled-variance estimator).
- **Permutation test:** Studentized (based on the Welch statistic) rather than a raw mean-difference version, since the latter carries the same Type I error risk as Student's t-test under heteroscedasticity.
- **Bootstrap test:** Bootstrap-t (studentized bootstrap) rather than the percentile bootstrap, for better accuracy under skewed/heavy-tailed conditions.
- **Reproducibility:** Each scenario runs with its own fixed seed (`base_seed + scenario_index`); all results are exactly reproducible.

## Installation

```bash
pip install -r requirements.txt
```

## Running

Quick sanity check (verifies the setup in a few seconds):

```bash
python simulasyon_cekirdek.py
```

Full simulation (180 scenarios, 3,000 replications each — ~50 minutes on a 2-core machine, triggered manually by design):

```bash
python -c "from simulasyon_cekirdek import tam_simulasyonu_calistir; tam_simulasyonu_calistir()"
```

Results are saved to `simulasyon_sonuclari.csv`.

## Project Structure

```
├── simulasyon_cekirdek.py      # Core simulation code (distributions, tests, grid)
├── simulasyon_sonuclari.csv    # Full results for all 180 scenarios
├── notebooks/                  # Development notebooks (Colab)
├── rapor/                      # Technical report in LaTeX (in progress)
├── README.md / README.en.md
└── requirements.txt
```

## Roadmap

- [x] Distribution sampling functions (with variance standardization)
- [x] Five test functions (studentized permutation and bootstrap-t variants)
- [x] Full simulation run (180 scenarios, 3,000 replications)
- [x] Initial findings analysis (Type I error + power)
- [ ] Visualization (power curves, Type I error heatmaps)
- [ ] Simulation-derived test recommendation tool (`recommend_test()`)
- [ ] pytest unit tests
- [ ] LaTeX technical report
- [ ] Real-data case study

## References

- Delacre, M., Lakens, D., & Leys, C. (2017). *Why psychologists should by default use Welch's t-test instead of Student's t-test.* International Review of Social Psychology.
- Fagerland, M. W., & Sandvik, L. (2009). *Performance of five two-sample location tests for skewed distributions with unequal variances.* Contemporary Clinical Trials.
- Wilcox, R. R. — *Introduction to Robust Estimation and Hypothesis Testing.*
