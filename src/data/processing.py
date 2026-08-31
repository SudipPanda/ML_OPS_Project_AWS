from src.utils.config import CONFIG
import pandas as pd 
from src.utils.s3 import read_parquet , read_csv , write_csv , write_parquet

def process_dataset(validate_uri:str):
    df = read_parquet(validate_uri)
    df = df.drop_duplicates()
    logger.info("the we have remove the duplicate from df here")
    
    key = f"{CONFIG.s3.processed_prefix}/dataset.csv"
    uri = write_parquet(df , key)
    
    return uri

