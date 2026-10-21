from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

TARGET = "FloodProbability"
ID_COLUMN = "id"
FEATURES = [
    "MonsoonIntensity", "TopographyDrainage", "RiverManagement",
    "Deforestation", "Urbanization", "ClimateChange", "DamsQuality",
    "Siltation", "AgriculturalPractices", "Encroachments",
    "IneffectiveDisasterPreparedness", "DrainageSystems",
    "CoastalVulnerability", "Landslides", "Watersheds",
    "DeterioratingInfrastructure", "PopulationScore", "WetlandLoss",
    "InadequatePlanning", "PoliticalFactors",
]


def load_competition_data(raw_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paths = {name: raw_dir / name for name in ("train.csv", "test.csv", "sample_submission.csv")}
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing Kaggle files: " + ", ".join(missing))
    train = pd.read_csv(paths["train.csv"])
    test = pd.read_csv(paths["test.csv"])
    submission = pd.read_csv(paths["sample_submission.csv"])
    validate_schema(train, test, submission)
    return train, test, submission


def validate_schema(train: pd.DataFrame, test: pd.DataFrame, submission: pd.DataFrame) -> None:
    expected_train = [ID_COLUMN, *FEATURES, TARGET]
    expected_test = [ID_COLUMN, *FEATURES]
    if list(train.columns) != expected_train:
        raise ValueError(f"train.csv schema mismatch: {list(train.columns)}")
    if list(test.columns) != expected_test:
        raise ValueError(f"test.csv schema mismatch: {list(test.columns)}")
    if list(submission.columns) != [ID_COLUMN, TARGET]:
        raise ValueError("sample_submission.csv schema mismatch")
    if train[ID_COLUMN].duplicated().any() or test[ID_COLUMN].duplicated().any():
        raise ValueError("id must be unique")
    if len(test) != len(submission) or not test[ID_COLUMN].equals(submission[ID_COLUMN]):
        raise ValueError("test and sample submission ids do not align")
    if train.isna().any().any() or test.isna().any().any():
        raise ValueError("Unexpected missing values in official competition data")


def split_labeled_data(train: pd.DataFrame, seed: int = 42):
    x = train[FEATURES]
    y = train[TARGET]
    x_dev, x_test, y_dev, y_test = train_test_split(x, y, test_size=0.20, random_state=seed)
    x_train, x_val, y_train, y_val = train_test_split(
        x_dev, y_dev, test_size=0.20, random_state=seed
    )
    return x_train, x_val, x_test, y_train, y_val, y_test
