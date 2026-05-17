# Dataset Download

The raw Kaggle dataset is not committed to this repository.

Dataset page:

```text
https://www.kaggle.com/datasets/hrishitpatil/flight-data-2024
```

## Kaggle CLI Setup

1. Create a Kaggle API token from your Kaggle account settings.
2. Use one of the credential setup options below.

### Option A: Environment Variables

If Kaggle gives you a username and key instead of a `kaggle.json` file, copy the
example file and fill in your real values:

```powershell
Copy-Item .env.example .env
notepad .env
```

Load the values into the current PowerShell session before running Kaggle:

```powershell
Get-Content .env | Where-Object { $_ -and $_ -notmatch '^#' } | ForEach-Object {
    $name, $value = $_ -split '=', 2
    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
}
```

### Option B: Kaggle JSON

If Kaggle gives you a `kaggle.json` file, place it under:

```text
C:\Users\<your-user>\.kaggle\kaggle.json
```

## Download

Activate the project environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify the Kaggle CLI can see the dataset:

```powershell
kaggle datasets files hrishitpatil/flight-data-2024
```

Download and unzip the dataset:

```powershell
kaggle datasets download -d hrishitpatil/flight-data-2024 -p data/raw --unzip
```

The expected default raw file is:

```text
data/raw/flight_data_2024.csv
```

If Kaggle provides a different filename, update `config/local.yaml` before running preparation.
