import logging
from src.utils.config import CONFIG
from src.utils.s3 import ensure_bucket_exist , write_csv
from sklearn.datasets import fetch_california_housing


def ingest_raw_datset()->str:
    ensure_bucket_exist()
    logging.info("Fetch the california dataset here")
    bunch = fetch_california_housing(as_frame=True)
    df = bunch.frame  # includes features + target column (MedHouseVal)
    
    key = f"{CONFIG.s3.raw_prefix}/dataset.csv"
    uri = write_csv(df , key)

    logging.info("Upload raw dataset t0", uri , len(df))

    return uri

if __name__ == "__main__":
    print(ingest_raw_datset())

