import logging
from src.utils.config import CONFIG
from src.utils.s3 import read_csv , write_parquet


logger = logging.getLogger(__name__)
EXPECTED_COLUMNS = {
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
    "MedHouseVal",
}
MAX_MISSING_FRACTION = 0.05

def validation_uri(raw_uri:str):
    data = read_csv(raw_uri)
    missing_columns = EXPECTED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(f"Dataset is missing expected columns : {missing_columns}")
    if data.empty:
        raise ValueError("data has zero rows here")
    missing_value = df.isna().mean()
    bad_columns = missing_value>MAX_MISSING_FRACTION

    if bad_columns:
        raise ValueError("Missing value error threshold has crossed here")

    target = CONFIG.data.target_column
    if (df[target] <= 0).any():
        raise ValueError(f"the target column {target} has non-positive value here")
        
    key = f"{CONFIG.s3.validated_prefix}/dataset.parquet"
    return write_parquet(data , key )

