from src.model.registery import load_production_model
import logging
from fastapi import FastAPI , HTTPException
from pydantic import BaseModel, Field

from src.model.predict import predict_one
logger =  logging.getLogger(__name__)

app = FastAPI(title="MLOPS")

class PredictRequest(BaseModel):
    MedInc: float = Field(..., description="Median income in block group (10k USD)")
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

class PredictResponse(BaseModel):
    predict : float

main_model : dict = {'model':None}


@app.get('/health')
def health():
    return {
        "status":"OK" ,
        "model_loaded" : main_model['model']
    }



@app.on_event("startup")
def _load_model_on_startup():
    try:
        main_model['model'] = load_production_model()
        logger.info("Loaded production model here")
    except Exception as e:
        logger.warning("somethign has went wrong here")
        main_model['model'] = None

@app.post("/reload")
def reload_model():
    
    _load_model_on_startup()

    return {"reloaded": main_model["model"] is not None}

@app.post('/predict' , response_model=PredictRequest)
def predict(request : PredictRequest)->PredictResponse:
    model = main_model['model']

    if model is None:
        raise HTTPException(status_code=503, detail="No Production model is currently loaded")
    try:
        value = predict_one(model, request.model_dump())
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    return PredictResponse(prediction=value)
