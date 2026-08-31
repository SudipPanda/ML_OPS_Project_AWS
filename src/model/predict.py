import pandas
import logging
EXPECTED_FEATURES = [
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
]


def predict_from_model(payload:dict):
    missing = [f for f in EXPECTED_FEATURES if f not in payload]
    if missing:
        raise ValueError(f"the missing feature here is {missing}")
    
    row = {f : payload[f] for f in EXPECTED_FEATURES}
    df = pd.pd.DataFrame([row])
    df["RoomsPerHousehold"] = df["AveRooms"] / df["AveOccup"].replace(0, 1)
    df["BedroomsPerRoom"] = df["AveBedrms"] / df["AveRooms"].replace(0, 1)
    return df

def predict_one(model, payload: dict) -> float:
    df = predict_from_model(payload)
    prediction = model.predict(df)[0]
    return float(prediction)


