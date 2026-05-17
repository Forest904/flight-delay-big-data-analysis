# Dataset Download

The raw Kaggle dataset is not committed to this repository.

Dataset page:

```text
https://www.kaggle.com/datasets/hrishitpatil/flight-data-2024
```

## Kaggle CLI Setup

1. Create a Kaggle API token from your Kaggle account settings.
2. Place `kaggle.json` under:

```text
C:\Users\<your-user>\.kaggle\kaggle.json
```

3. Activate the project environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Download and unzip the dataset:

```powershell
kaggle datasets download -d hrishitpatil/flight-data-2024 -p data/raw --unzip
```

The expected default raw file is:

```text
data/raw/flight_data_2024.csv
```

If Kaggle provides a different filename, update `config/local.yaml` before running preparation.
