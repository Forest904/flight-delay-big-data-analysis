# AWS EMR Evidence

AWS EMR is an evidence extension for Spark SQL and Spark Core. It is useful for
managed-cluster comparison, but it is constrained by AWS Academy Learner Lab
credentials, budget, IAM permissions, and instance availability.

## Credential Hygiene

Copy `.env.example` to `.env` and fill only local temporary values. `.env` is
ignored and must never be committed.

Rotate AWS Learner Lab credentials before sharing the repository, screenshots,
logs, or videos if those credentials appeared in local files or terminals.

Required environment values:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN
AWS_DEFAULT_REGION
AWS_LEARNER_LAB_BUDGET_REMAINING_USD
AWS_FLIGHT_DELAY_BUCKET
```

## Feasibility Check

Run the read-only feasibility check before creating any EMR cluster:

```powershell
make aws-check
```

Write report-ready feasibility evidence with:

```powershell
make aws-check-report
```

The check covers credentials, region, budget field, S3, EMR, EC2, IAM role
readability, instance-type availability, and logging configuration.

## Dry Runs

Validate command construction without creating resources:

```powershell
make aws-upload AWS_DRY_RUN=1
make benchmark-aws-emr AWS_DRY_RUN=1
make benchmark-aws-emr AWS_DRY_RUN=1 AWS_SMOKE_ONLY=1 AWS_RUN_ID=m4-hardened-smoke
make aws-cleanup AWS_DRY_RUN=1
```

The final 3-repetition larger-profile campaign configs should also be dry-run
checked before any cluster is created:

```powershell
make benchmark-aws-emr AWS_DRY_RUN=1 AWS_CONFIG=config/aws_emr_campaign_3x_small.yaml AWS_RUN_ID=aws-3x-small
make benchmark-aws-emr AWS_DRY_RUN=1 AWS_CONFIG=config/aws_emr_campaign_3x_mid.yaml AWS_RUN_ID=aws-3x-mid
make benchmark-aws-emr AWS_DRY_RUN=1 AWS_CONFIG=config/aws_emr_campaign_3x_14m.yaml AWS_RUN_ID=aws-3x-14m
make benchmark-aws-emr AWS_DRY_RUN=1 AWS_CONFIG=config/aws_emr_campaign_3x_28m.yaml AWS_RUN_ID=aws-3x-28m
```

## Upload, Run, Fetch, Cleanup

Upload prepared/generated Parquet inputs, source bundle, and runtime config:

```powershell
make aws-upload
```

Run the configured EMR benchmark lane:

```powershell
make benchmark-aws-emr AWS_RUN_ID=m4-emr-rerun
```

Fetch result artifacts:

```powershell
make aws-fetch-results AWS_RUN_ID=m4-emr-rerun
```

Clean up tracked or tagged clusters:

```powershell
make aws-cleanup
```

For the final larger-cluster campaign, run each input group separately:

```powershell
make aws-check AWS_CHECK_FLAGS="--config config/aws_emr_campaign_3x_small.yaml"
make aws-upload AWS_CONFIG=config/aws_emr_campaign_3x_small.yaml AWS_RUN_ID=aws-3x-small
make benchmark-aws-emr AWS_CONFIG=config/aws_emr_campaign_3x_small.yaml AWS_RUN_ID=aws-3x-small
make aws-fetch-results AWS_CONFIG=config/aws_emr_campaign_3x_small.yaml AWS_RUN_ID=aws-3x-small
make aws-cleanup AWS_CONFIG=config/aws_emr_campaign_3x_small.yaml
```

Repeat the same sequence for:

- `config/aws_emr_campaign_3x_mid.yaml` / `aws-3x-mid`
- `config/aws_emr_campaign_3x_14m.yaml` / `aws-3x-14m`
- `config/aws_emr_campaign_3x_28m.yaml` / `aws-3x-28m`

Final AWS campaign completed:

- `aws-3x-small`: `100k`, `500k`, and `1m`; Spark SQL/Core; three repetitions.
- `aws-3x-mid`: `3m` and `full`; Spark SQL/Core; three repetitions.
- `aws-3x-14m`: `14m`; Spark SQL/Core; three repetitions.
- `aws-3x-28m`: `28m`; Spark SQL/Core; three repetitions.

## Evidence Policy

- EMR Spark SQL/Core evidence can strengthen the report, especially for managed
  execution discussion.
- EMR Hive is excluded from the current implementation. Hive evidence remains
  local and Docker-based, and the report must not claim Hive cluster evidence.
- Any future AWS cells with fewer than the intended repetitions should be
  explained in `report/tables/benchmark_notes.csv` with an appropriate note.
- Always terminate clusters after runs. Do not leave long-running clusters in
  Learner Lab.

## Output Artifacts

Fetched AWS evidence is stored under:

```text
experiments/results/aws-emr/
experiments/results/aws-emr-larger/
```

`make charts` reads timestamped benchmark CSVs, AWS run manifests, step timing,
cost logs, and downloaded first-10 outputs when present.
