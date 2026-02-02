"""
Simulation API routes - Run deterministic simulations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional, List
from app.engine.simulator import run_simulation
from app.api.routes.models import models_db, EXAMPLE_MODELS

router = APIRouter(prefix="/simulate", tags=["simulation"])


class SimulationRequest(BaseModel):
    """Simulation request with model and optional parameter overrides"""
    model_config = ConfigDict(protected_namespaces=())
    
    model: Optional[dict] = None
    model_id: Optional[str] = None
    example_id: Optional[str] = None
    parameter_overrides: Optional[Dict[str, float]] = None


class ScenarioComparison(BaseModel):
    """Compare multiple scenarios"""
    model: dict
    scenarios: List[Dict[str, Any]]  # List of {name: str, parameters: Dict[str, float]}


@router.post("/")
async def run_sim(request: SimulationRequest):
    """
    Run a deterministic simulation
    
    Provide EITHER:
    - model: Full model JSON
    - model_id: ID of a saved model
    - example_id: ID of an example model
    
    Optionally provide parameter_overrides to modify parameter values.
    
    GUARANTEE: Same input = Same output. Always.
    """
    # Get model from one of the sources
    model = None
    
    if request.model:
        model = request.model
    elif request.model_id:
        if request.model_id not in models_db:
            raise HTTPException(status_code=404, detail="Model not found")
        model = models_db[request.model_id]["model"]
    elif request.example_id:
        if request.example_id not in EXAMPLE_MODELS:
            raise HTTPException(status_code=404, detail="Example model not found")
        model = EXAMPLE_MODELS[request.example_id]
    else:
        raise HTTPException(
            status_code=400, 
            detail="Must provide model, model_id, or example_id"
        )
    
    try:
        results = run_simulation(model, request.parameter_overrides)
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@router.post("/compare")
async def compare_scenarios(request: ScenarioComparison):
    """
    Compare multiple scenarios with different parameters
    
    Useful for what-if analysis and sensitivity testing.
    """
    results = []
    
    for scenario in request.scenarios:
        try:
            sim_result = run_simulation(request.model, scenario.get("parameters", {}))
            results.append({
                "name": scenario.get("name", "Unnamed"),
                "parameters": scenario.get("parameters", {}),
                "results": sim_result
            })
        except Exception as e:
            results.append({
                "name": scenario.get("name", "Unnamed"),
                "error": str(e)
            })
    
    return {
        "success": True,
        "comparisons": results
    }


@router.post("/sensitivity")
async def sensitivity_analysis(
    model: dict,
    parameter_id: str,
    min_value: float,
    max_value: float,
    steps: int = 10
):
    """
    Run sensitivity analysis on a single parameter
    
    Varies the parameter from min_value to max_value in steps,
    running a simulation for each value.
    """
    results = []
    step_size = (max_value - min_value) / (steps - 1) if steps > 1 else 0
    
    for i in range(steps):
        value = min_value + i * step_size
        try:
            sim_result = run_simulation(model, {parameter_id: value})
            results.append({
                "parameter_value": value,
                "results": sim_result
            })
        except Exception as e:
            results.append({
                "parameter_value": value,
                "error": str(e)
            })
    
    return {
        "success": True,
        "parameter_id": parameter_id,
        "range": {"min": min_value, "max": max_value, "steps": steps},
        "sensitivity_results": results
    }
