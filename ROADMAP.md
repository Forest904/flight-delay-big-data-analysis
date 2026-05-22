# 29/30 Recovery Roadmap

This roadmap is the execution board for moving the project from the current
professor-style grade estimate of **26/30** to a realistic **29/30**. It is a
punch list for fixing the deductions that remain before final submission.

The recovery strategy is:

1. Make validation artifacts consistent and reproducible.
2. Replace weak single-run benchmark evidence with repeated, auditable runs.
3. Include Hive strongly in local/Docker evidence, while keeping EMR Hive as a
   guarded stretch.
4. Tighten the report so it argues from evidence instead of self-grading.
5. Add a final submission gate so the repository cannot drift back into an
   inconsistent state.

## Current Grade Diagnosis

| Deduction area | Current risk | Recovery action | Expected impact |
| --- | --- | --- | --- |
| Output validation | Spark SQL, Hive, and MapReduce artifacts can point to different inputs | Regenerate all required outputs from one canonical input and rerun all validators | High |
| Benchmark rigor | Many report cells are `runs=1` | Rerun local/Docker/selected EMR cells with 3 repetitions and label smoke runs clearly | High |
| Hive comparison | Hive is present but cluster comparison is Spark-only | Strengthen local/Docker Hive evidence; keep EMR Hive as optional stretch | Medium |
| Scalability claims | Replicated inputs, cache effects, and tiny aggregate outputs can overstate throughput | Add explicit methodology caveats and input/output/shuffle discussion | Medium |
| Report framing | Some sections claim the project "satisfies" or "resolves" issues too strongly | Replace verdict language with measured evidence and limitations | Medium |
| Submission safety | No single command proves the repo is ready | Add or document a `submission-check` gate | High |
| Secret hygiene | Local `.env` contains real-looking credentials | Rotate/remove secrets before sharing or recording | Critical but easy |

## Sprint P0 - Submission Blockers

These tasks must be done before any further benchmark or report polish counts.

### P0.1 - Pick One Canonical Validation Input

**Decision:** use `data/prepared/flights_2024_clean.parquet` as the canonical
report-ready validation input for Spark SQL, Spark Core, Hive, and MapReduce.

**Why:** the current local outputs drifted: Spark SQL pointed at `14m`, Hive at
`1m`, and MapReduce at `full`. Validators correctly failed because they were
comparing different datasets.

**Commands:**

```powershell
make run-all-local
make run-mapreduce
make validate-spark-sql
make validate-spark-core
make validate-hive
make validate-mapreduce
```

**Done means:**

- All four validators pass.
- `outputs/*/runtime_metrics.json` record the same `input_path`.
- Spark SQL, Spark Core, Hive, and MapReduce first-10 samples are regenerated
  from the same input.

### P0.2 - Add A Submission Gate

**Goal:** add a future `make submission-check` target or equivalent script that
fails loudly when the repository is not submission-ready.

**Required checks:**

- Unit tests pass.
- All technology validators pass.
- Report tables and figures exist.
- Benchmark summary includes required technologies and input labels.
- No report-critical benchmark cell is silently `runs=1` unless explicitly
  marked as smoke or budget-limited evidence.
- `.env`, raw data, prepared data, generated Parquet, runtime outputs, and bulky
  AWS downloads are not tracked.
- No credential-like values appear in tracked files.

**Target command once implemented:**

```powershell
make submission-check
```

**Temporary manual gate until then:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q
make validate-spark-sql
make validate-spark-core
make validate-hive
make validate-mapreduce
make charts
make report
git status --short
```

**Done means:**

- One documented gate can be run before final submission.
- The gate prevents the exact artifact drift found in the 26/30 review.

### P0.3 - Secret And Artifact Hygiene

**Required before sharing the repo, screenshots, logs, or videos:**

- Rotate the Kaggle token and AWS Learner Lab credentials that appeared in local
  `.env`.
- Keep `.env` ignored and unstaged.
- Confirm only `.env.example` is tracked.
- Confirm `derby.log`, raw data, prepared data, generated datasets, outputs, and
  bulky benchmark logs are ignored.

**Commands:**

```powershell
git ls-files .env .env.example derby.log data outputs experiments/results
rg -n "AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|KAGGLE_KEY=KGAT|ASI[A-Z0-9]" .
```

**Done means:**

- `git ls-files` shows no private `.env`, large data, or runtime outputs except
  intentional `.gitkeep` files.
- `rg` finds no real credentials in tracked submission files.

## Sprint P1 - Benchmark Evidence

The goal of this sprint is to make the timing evidence defensible under a harsh
grading read.

### P1.1 - Generate Full Input Ladder Including 14m And 28m

**Inputs to cover:**

- `100k`
- `500k`
- `1m`
- `3m`
- `full`
- `14m`
- `28m`

**Guarded preflight:**

```powershell
Get-PSDrive -Name C
make check-env
make prepare
make generate-sizes GENERATE_LARGE=1 LARGE_LABEL=14m FORCE=1
make generate-sizes GENERATE_LARGE=1 LARGE_LABEL=28m FORCE=1
```

**Stop rules:**

- Stop before `28m` if free disk space is not comfortably above the expected
  generated Parquet size plus working space.
- Stop if generation does not validate exact row counts.
- Do not use `28m` as statistical flight evidence; use it only as scalability
  stress evidence.

**Done means:**

- `data/generated/input_size_manifest.json` contains successful entries for
  `14m` and `28m`.
- The report explains controlled replication and its limits.

### P1.2 - Rerun Local Benchmarks With Three Repetitions

**Required technologies:**

- Spark SQL
- Spark Core
- Hive

**Required inputs:**

- `100k`
- `500k`
- `1m`
- `3m`
- `full`
- `14m`
- `28m`, if P1.1 passes and runtime remains reasonable

**Commands:**

```powershell
make benchmark-local BENCHMARK_FLAGS="--repetitions 3"
make charts
```

**Guarded large-input fallback:**

```powershell
make benchmark-local BENCHMARK_FLAGS="--input-label 14m --repetitions 3"
make benchmark-local BENCHMARK_FLAGS="--input-label 28m --repetitions 3"
```

**Done means:**

- `report/tables/benchmark_summary.md` shows `runs=3` for report-critical local
  Spark SQL, Spark Core, and Hive rows.
- Any `runs=1` cell is explicitly explained as smoke, budget-limited, or failed
  resource-limited evidence.
- Charts are regenerated from median durations.

### P1.3 - Rerun Docker Simulation Benchmarks

**Required Docker matrix:**

- Inputs: `100k`, `500k`, `1m`
- Technologies: Spark SQL, Spark Core, Hive
- Repetitions: `3`

**Command:**

```powershell
make benchmark-docker-simulation BENCHMARK_FLAGS="--repetitions 3"
make charts
```

**Optional guarded extension:**

- Add Docker config entries for `3m`, `full`, `14m`, and `28m`.
- Run only if Docker Desktop memory, disk, and time are acceptable.
- Treat large Docker Hive runs as best-effort, not required for 29/30.

**Done means:**

- Docker evidence clearly remains "standalone simulation," not a real cluster.
- Required Docker cells have repeated measurements.
- Missing large Docker cells are marked `N/A` with notes, not inferred.

### P1.4 - Keep MapReduce As Stretch Evidence

**Required:**

```powershell
make run-mapreduce
make validate-mapreduce
make benchmark-mapreduce-local BENCHMARK_FLAGS="--input-label 100k --repetitions 3"
```

**Done means:**

- MapReduce validates against Spark SQL on the canonical input.
- MapReduce benchmark evidence is presented as optional stretch evidence, not
  part of the three required technology baseline.

## Sprint P1 - Report Upgrade

The report should read like careful experimental work, not like a victory lap.

### P1.5 - Rename Analyses By Assignment Section

**Change:**

- Rename current "Analysis 1" to **Assignment Analysis 3.2 - Delay Report by
  Airport and Time Period**.
- Rename current "Analysis 2" to **Assignment Analysis 3.3 - Ranking of
  Airline-Airport Pairs**.

**Done means:**

- The assignment mapping is unambiguous.
- The report does not force the professor to translate local analysis numbers
  back to the PDF specification.

### P1.6 - Add Null-Delay And Cancelled-Flight Audit

**Required discussion:**

- Count rows with null `departure_delay`.
- Count cancelled rows with null `departure_delay`.
- Explain which rows are excluded from the delay-range job and why.
- State whether cancellation causes are undercounted in delay-range groups.

**Suggested evidence command:**

```powershell
.\.venv\Scripts\python.exe scripts\inspect_raw_dataset.py
```

**Done means:**

- The report no longer hides the semantic consequence of excluding null
  departure-delay rows from assignment analysis 3.2.

### P1.7 - Tighten Benchmark Methodology Language

**Replace broad claims with evidence-first wording:**

- "The project satisfies..." -> "The submitted artifacts show..."
- "This resolves..." -> "This reduces the earlier risk, with the following
  limits..."
- "Scalability improves..." -> "Throughput appears higher under this measured
  setup, but fixed costs and caching affect interpretation."

**Must discuss:**

- Spark/JVM startup and container startup.
- Warm local filesystem and OS cache.
- Prepared Parquet columnar reads.
- Small aggregate output cardinality.
- Shuffle and aggregation pressure.
- Replicated `14m` and `28m` inputs as stress tests, not new statistical
  observations.
- S3 I/O and EMR step scheduling overhead.

**Done means:**

- A harsh reader can see exactly what the timings measure and what they do not.

### P1.8 - Repair Benchmark Tables And Captions

**Required table/caption policy:**

- Show `runs`, median, mean, min, max, and standard deviation.
- Use "smoke" in labels for one-off verification runs.
- Use `N/A` for cells that were not run.
- Add notes for budget-limited or resource-limited cells.

**Done means:**

- No single-run result is presented as statistically equivalent to a repeated
  benchmark campaign.

## Sprint P2 - Stretch Evidence

These tasks can lift the submission closer to 30/30, but they are guarded so
they do not endanger the 29/30 recovery.

### P2.1 - EMR Spark SQL/Core Reruns For Weak Cells

**Required only if AWS budget and credentials are available.**

**Targets:**

- Baseline EMR `500k`, `3m`, and `14m` cells currently represented by one run.
- Larger EMR profile with `14m`, if budget allows.
- Optional `28m` Spark SQL/Core run, only after local `28m` validates.

**Commands:**

```powershell
make aws-check
make aws-upload
make benchmark-aws-emr AWS_RUN_ID=m4-emr-rerun
make aws-fetch-results AWS_RUN_ID=m4-emr-rerun
make charts
```

**Stop rules:**

- Do not start a cluster unless `make aws-check` passes.
- Do not run if Learner Lab remaining budget is below the configured safety
  threshold.
- Terminate all clusters after each run.

**Done means:**

- EMR Spark evidence has more repeated cells, or the report explicitly states
  why remaining single-run cells are budget-limited.

### P2.2 - Optional EMR Hive

**Status:** stretch, not required for 29/30.

**Goal:** if time and AWS budget allow, add a real EMR Hive lane so the third
required technology also has cluster evidence.

**Required design before implementation:**

- Decide whether EMR Hive reads the same S3 Parquet inputs directly or through
  external tables.
- Add config support for `technology=hive` in the EMR benchmark lane.
- Capture Hive step timing, output samples, and benchmark rows with the same
  schema as Spark.
- Keep local/container Hive evidence as the fallback if EMR Hive is not
  completed.

**Done means:**

- The report can compare Spark SQL, Spark Core, and Hive on a real cluster.
- If not completed, the report honestly says Hive cluster evidence is not part
  of the submission.

### P2.3 - Docker Large-Input Extension

**Optional targets:**

- `3m`
- `full`
- `14m`
- `28m`

**Done means:**

- Docker simulation charts have broader input coverage, or missing cells are
  marked `N/A` with resource-limit notes.

## Execution Order

Follow this order. Do not skip P0.

### Phase 1 - Stabilize Required Outputs

```powershell
make check-env
make prepare
make generate-sizes GENERATE_LARGE=1 LARGE_LABEL=14m FORCE=1
make run-all-local
make run-mapreduce
make validate-spark-sql
make validate-spark-core
make validate-hive
make validate-mapreduce
```

**Stop if:** any validator fails.

### Phase 2 - Add 28m Only If Safe

```powershell
Get-PSDrive -Name C
make generate-sizes GENERATE_LARGE=1 LARGE_LABEL=28m FORCE=1
```

**Stop if:** disk space, runtime, or validation is not acceptable.

### Phase 3 - Rebuild Local Benchmark Evidence

```powershell
make benchmark-local BENCHMARK_FLAGS="--repetitions 3"
make benchmark-mapreduce-local BENCHMARK_FLAGS="--input-label 100k --repetitions 3"
```

**Stop if:** Hive fails on required inputs; fix or document the failure before
moving on.

### Phase 4 - Rebuild Docker Evidence

```powershell
make benchmark-docker-simulation BENCHMARK_FLAGS="--repetitions 3"
```

**Stop if:** Docker Desktop cannot complete the required `100k`/`500k`/`1m`
matrix.

### Phase 5 - Optional AWS Reruns

```powershell
make aws-check
make aws-upload
make benchmark-aws-emr AWS_RUN_ID=m4-emr-rerun
make aws-fetch-results AWS_RUN_ID=m4-emr-rerun
make aws-cleanup
```

**Stop if:** budget, credentials, instance availability, or cluster cleanup is
uncertain.

### Phase 6 - Regenerate Report

```powershell
make charts
make report
.\.venv\Scripts\python.exe -m pytest -q
git status --short
```

**Stop if:** report tables are stale, tests fail, or unexpected large/private
artifacts are tracked.

## Acceptance Criteria For 29/30

- [ ] Spark SQL, Spark Core, Hive, and MapReduce outputs validate against the
      same canonical input.
- [ ] Local benchmark evidence includes Spark SQL, Spark Core, and Hive with
      3 repetitions for the required input ladder.
- [ ] `14m` is generated, validated, benchmarked, and explained as replicated
      scalability evidence.
- [ ] `28m` is either generated and benchmarked with guardrails or explicitly
      marked as not run due to resource limits.
- [ ] Docker standalone simulation has repeated evidence for `100k`, `500k`,
      and `1m`.
- [ ] EMR Spark SQL/Core evidence remains included and honestly bounded.
- [ ] EMR Hive is either completed as stretch evidence or clearly listed as not
      part of the final claim.
- [ ] The report labels analyses as assignment `3.2` and `3.3`.
- [ ] The report includes a null-delay/cancelled-flight exclusion audit.
- [ ] The report distinguishes repeated benchmarks from smoke runs.
- [ ] The report discusses caching, startup costs, shuffle, aggregation, S3 I/O,
      output cardinality, and replicated-input limitations.
- [ ] The final PDF is rebuilt from the final Markdown.
- [ ] Tests pass.
- [ ] No secrets, raw data, generated data, bulky logs, or runtime outputs are
      staged for Git.

## Out Of Scope

- Production AWS infrastructure-as-code.
- AWS Glue, Athena, or other new services.
- Long-running clusters.
- Unbounded AWS reruns.
- Claiming Docker standalone simulation as a real distributed cluster.
- Treating replicated `14m` or `28m` data as new statistical evidence about
  flight behavior.

## Final Notes

The fastest path to 29/30 is not more cloud work. It is:

1. Clean validation.
2. Repeated local and Docker evidence.
3. Strong Hive coverage outside EMR.
4. Conservative report language.
5. A submission gate that prevents artifact drift.

EMR Hive and broader EMR reruns are useful stretch goals, but only after the
P0 and P1 work is complete.
