# Roadmap To A 28+/30 Submission

This roadmap turns the harsh-review feedback into a concrete improvement plan
for the final Big Data submission. The target is a **28+/30 or better** by
removing visible report defects, closing the weakest analysis-semantics gaps,
making Spark SQL and Spark Core benchmarks fairer, and adding stronger
scalability evidence.

The milestones are ordered by grading impact. Milestone 1 should be completed
first because report polish and internal consistency are the easiest marks to
recover before submission.

## Milestone 1 - Report Consistency And PDF Polish

**Goal:** Make the final PDF look submission-ready and remove stale claims that
could make the grader distrust the evidence.

**Why this matters:** The current project is technically strong, but clipped
tables, overlapping chart labels, and contradictory benchmark statements are
high-visibility deductions.

**Tasks**

- Fix stale Docker benchmark statements in
  [`report/draft_final_report.md`](report/draft_final_report.md).
  - Remove the old limitation saying Docker stops at `1m`.
  - Keep the newer evidence that Docker simulation completed `100k`, `500k`,
    `1m`, `3m`, `full`, `14m`, and `28m` for Spark SQL, Spark Core, and Hive.
- Fix stale AWS EMR larger-cluster statements.
  - Update the AWS comparison table so the larger profile reflects `1m`,
    `full`, `14m`, and `28m` evidence where applicable.
  - Keep the distinction that `28m` is single-run smoke/stress evidence.
- Rework clipped tables in the generated PDF.
  - Split wide requirement-mapping and benchmark tables into narrower tables.
  - Prefer short column labels in the PDF while keeping full column names in
    source CSV artifacts.
  - Use landscape pages only if splitting is not enough.
- Improve benchmark chart readability in
  [`scripts/generate_charts.py`](scripts/generate_charts.py).
  - Shorten x-axis labels.
  - Rotate or wrap tick labels.
  - Increase figure width or bottom margin where needed.
- Rebuild charts and the PDF.

**Acceptance Criteria**

- The PDF has no visibly clipped tables.
- Chart x-axis labels do not overlap.
- `rg "Docker benchmark matrix stops at|limited to \`1m\` and \`full\`" report/draft_final_report.md`
  returns no stale contradiction.
- The report still honestly labels Docker as single-host simulation and EMR
  `28m` as smoke/stress evidence.

## Milestone 2 - Analysis 3.2 Cancellation Semantics

**Goal:** Account for cancelled flights with null `departure_delay` instead of
only explaining why they are excluded from low/medium/high delay ranges.

**Why this matters:** Assignment Analysis 3.2 asks for frequent cancellation or
delay causes if available. Most null-`departure_delay` rows are cancelled rows
with cancellation codes, so a harsh grader may treat their exclusion as
incomplete.

**Tasks**

- Add a supplementary `cancelled_no_departure_delay` bucket or companion output
  for cancelled flights where `departure_delay IS NULL`.
- Preserve existing delay ranges exactly for flights with known departure delay:
  - `low`: `departure_delay < 15`
  - `medium`: `15 <= departure_delay <= 60`
  - `high`: `departure_delay > 60`
- Compute cancellation-cause counts for the new bucket using
  `cancellation_code`.
- Apply the behavior consistently across:
  - [`src/spark_sql/run_spark_sql.py`](src/spark_sql/run_spark_sql.py)
  - [`src/spark_core/run_spark_core.py`](src/spark_core/run_spark_core.py)
  - [`src/hive/analysis_delay_by_airport_month.sql`](src/hive/analysis_delay_by_airport_month.sql)
  - MapReduce stretch code where feasible.
- Update validators and first-10 report tables to include the new bucket or
  supplementary output.
- Explain the policy clearly in the report: known delays use the assignment
  ranges; cancelled flights without departure delay are reported separately.

**Acceptance Criteria**

- The report clearly accounts for cancelled flights that cannot be assigned to
  the three numeric delay ranges.
- Spark SQL, Spark Core, Hive, and MapReduce validators pass.
- First-10 samples or a compact summary table show the new cancellation bucket
  evidence.

## Milestone 3 - Dominant Cause Plus All Positive Causes

**Goal:** Keep the current dominant-cause metric for comparability, then add an
all-positive-cause view that counts every available positive delay-cause field.

**Why this matters:** Counting only the largest cause per flight is defensible,
but the assignment wording can also be read as asking for frequent causes
overall. Reporting both removes the ambiguity.

**Tasks**

- Keep the existing `top_1_cause`, `top_2_cause`, and `top_3_cause` dominant
  cause output.
- Add a companion output for all positive causes.
  - Count every positive `carrier_delay`, `weather_delay`, `nas_delay`,
    `security_delay`, and `late_aircraft_delay` field.
  - Include cancellation causes for cancelled flights with available
    `cancellation_code`.
  - Use deterministic tie-breaking: count descending, then cause label
    ascending.
- Decide on a compact output contract before implementation.
  - Preferred: create companion files instead of widening the existing core
    output tables too much.
  - Suggested companion name: `delay_by_airport_month_all_causes`.
- Implement across Spark SQL, Spark Core, Hive, and MapReduce stretch where
  feasible.
- Update the report to explain the difference:
  - **Dominant cause:** one cause selected per flight.
  - **All positive causes:** every positive cause field contributes.

**Acceptance Criteria**

- Dominant-cause outputs remain available and comparable with current evidence.
- All-positive-cause outputs exist for the required technologies.
- The final report includes either first-10 rows or a compact summary for the
  all-positive-cause view.
- Validators verify Spark Core and Hive against the Spark SQL reference.

## Milestone 4 - Spark SQL Optimization

**Goal:** Make the Spark SQL implementation faster and document the measured
impact without sacrificing correctness.

**Why this matters:** Spark SQL is currently the clearest implementation but
has visibly higher timings than Spark Core in several cells. A focused
optimization pass can improve both the implementation and the critical
discussion.

**Tasks**

- Inspect Spark SQL physical plans for both analyses.
  - Use representative inputs such as `1m`, `full`, and one stress input.
  - Save notes about scans, exchanges, windows, and sorts.
- Reduce repeated work where possible.
  - Reuse derived columns instead of recomputing cause and range expressions.
  - Persist intermediate DataFrames only when the plan shows repeated scans.
  - Avoid unnecessary global ordering before full output writes unless required
    for deterministic samples.
- Revisit top-three cause logic.
  - Compare current window-based ranking with alternatives such as grouped
    aggregation followed by compact ranking.
  - Keep deterministic ordering.
- Benchmark before and after.
  - Record timings for the same inputs and environments.
  - Label optimized runs clearly so they do not mix silently with baseline
    evidence.
- Update the report with a short before/after section.

**Acceptance Criteria**

- Spark SQL outputs remain byte/schema-compatible where intended.
- Validators pass after optimization.
- The report documents measured improvement, no improvement, or tradeoff with
  concrete benchmark rows.
- The discussion explains that SQL expressiveness does not automatically remove
  shuffle, sort, or window costs.

## Milestone 5 - Spark SQL vs Spark Core Benchmark Fairness

**Goal:** Align timing boundaries so Spark SQL and Spark Core comparisons are
credible.

**Why this matters:** Spark Core currently materializes small final result sets
through Pandas, while Spark SQL writes distributed CSV output. That can make the
benchmark compare different work, especially when outputs are small.

**Tasks**

- Define benchmark phases explicitly:
  - input read
  - transformation/aggregation
  - full output materialization
  - first-10 sample materialization
- Make Spark SQL and Spark Core report comparable timing fields.
  - Preferred: keep total job duration but add phase timings.
  - Include output row count and input path as already done today.
- Remove or clearly label Spark Core-only shortcuts.
  - If Spark Core keeps Pandas materialization because the aggregate output is
    small, label this as small-result materialization.
  - Otherwise, write Spark Core outputs through Spark DataFrame writers to
    match Spark SQL output work more closely.
- Update benchmark tables and report language to state exactly what is timed.

**Acceptance Criteria**

- Spark SQL and Spark Core benchmark rows include comparable timing boundaries
  or explicitly documented phase timings.
- The report no longer implies that raw job duration is a perfect apples-to-
  apples comparison when output materialization differs.
- Existing validators and submission checks still pass.

## Milestone 6 - Higher-Cardinality Spark Core Stress Test

**Goal:** Add stress evidence that increases key cardinality and shuffle
pressure, not only row count through replicated inputs.

**Why this matters:** The current `14m` and `28m` inputs increase row volume but
preserve the same airport, airline, month, and output cardinality. This makes
flat timings easier to achieve and weaker as scalability evidence.

**Tasks**

- Design a controlled high-cardinality input generator.
  - Preserve source row shape and numeric semantics.
  - Add controlled variants of grouping keys, such as airport or airline
    suffixes, only for benchmark stress datasets.
  - Mark these datasets clearly as synthetic cardinality stress inputs, not
    flight-behavior observations.
- Add manifest metadata that distinguishes:
  - original prepared input
  - row-volume replication input
  - high-cardinality stress input
- Benchmark Spark Core and Spark SQL on at least one high-cardinality input.
- Update the report to compare:
  - row-volume stress behavior
  - cardinality/shuffle stress behavior

**Acceptance Criteria**

- Stress inputs increase output key cardinality measurably.
- Benchmark tables identify stress inputs clearly.
- The report does not present synthetic high-cardinality rows as real flight
  statistics.
- Spark Core remains correct under increased key cardinality.

## Affected Interfaces And Artifacts

Future implementation may add output columns or companion outputs for:

- `cancelled_no_departure_delay`
- dominant cause counts
- all-positive cause counts
- phase-level benchmark timings
- high-cardinality stress input metadata

Any schema or output-contract change must update these areas together:

- analysis runners under `src/`
- validators under [`scripts/`](scripts/)
- benchmark and chart generation in
  [`scripts/generate_charts.py`](scripts/generate_charts.py)
- report tables and first-10 samples under [`report/tables/`](report/tables/)
- final report source in
  [`report/draft_final_report.md`](report/draft_final_report.md)
- reproducibility and benchmark docs under [`docs/`](docs/)

## Final Verification Gate

Before submitting after these milestones, run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\validate_spark_sql_outputs.py
.\.venv\Scripts\python.exe scripts\validate_spark_core_outputs.py
.\.venv\Scripts\python.exe scripts\validate_hive_outputs.py
.\.venv\Scripts\python.exe scripts\validate_mapreduce_outputs.py
.\.venv\Scripts\python.exe scripts\submission_check.py --audit-only
make charts
make report
```

Then visually inspect the PDF pages containing:

- assignment coverage tables
- benchmark summary excerpts
- local, Docker, and EMR benchmark charts
- first-10 result samples

The submission is ready when the PDF is visually clean, the report claims are
internally consistent, all validators pass, and the benchmark discussion is
skeptical about the limits of each environment.

## Working Assumptions

- Required technologies remain Spark SQL, Spark Core, and Hive.
- MapReduce remains stretch evidence, not the required baseline.
- The raw Kaggle dataset and generated large inputs remain untracked.
- The roadmap is a planning document only; implementing the milestones should
  happen in separate focused changes.
- The grade target is **28+/30**, so visible report quality and analysis
  completeness come before optional performance polish.
