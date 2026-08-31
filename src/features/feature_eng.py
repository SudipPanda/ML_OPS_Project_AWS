import logging
from sklearn.model_selection import train_test_split

from src.utils.config import CONFIG
from src.utils.s3 import read_parquet , write_parquet
logger = logging.getLogger(__name__)

def engineering_feature(key_uri:str):
    df = read_parquet(key_uri)
    df["RoomsPerHousehold"] = df["AveRooms"] / df["AveOccup"].replace(0, 1)
    df["BedroomsPerRoom"] = df["AveBedrms"] / df["AveRooms"].replace(0, 1)
    
    target = CONFIG.data.target_column
    train_df , test_df = train_test_split(
       df , 
       test_size = CONFIG.data.test_size ,
       random_state = CONFIG.random_seed
    )

    train_df_uri = write_parquet(train_df , f"{CONFIG.s3.features_prefix}/train.parquet")
    test_df_uri = write_parquet(test_df ,f"{CONFIG.s3.features_prefix}/test.parquet")

    logger.info(f"the length of the train df is {len(train_df)} and test df is {len(test_df)}")
    return {"train_df_uri":train_df_uri , "test_df_uri":test_df_uri}

if __name__ == "__main__":
    pass