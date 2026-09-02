import logging
from src.model.registery import get_production_model_metrics, load_production_model
from src.utils.config import CONFIG

logger = logging.getLogger(__name__)

def passes_quality_gate(train_result: dict)->bool:
    rmse = train_result["rmse"]
    threshold = CONFIG.quality_gate.max_rmse

    if tmse>=threshold:
        logger.info(
            "Model failed quality gate: RMSE %.4f exceeds threshold %.4f", rmse, threshold
        )
        return False
    
    current_prod_metrics = get_production_model_metrics()
    if current_prod_metrics is not None:
        current_prod_rmse = current_prod_metrics["rmse"]
        if rmse >= current_prod_rmse:
            logger.info(
                "Model failed quality gate: RMSE %.4f is not better than current production RMSE %.4f",
                rmse, current_prod_rmse
            )
            return False
        else:
            logger.info(
                "Model passed quality gate: RMSE %.4f is better than current production RMSE %.4f",
                rmse, current_prod_rmse
            )
            
    return True