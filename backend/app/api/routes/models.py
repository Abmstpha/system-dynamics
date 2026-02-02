"""
Models API routes - CRUD operations for System Dynamics models
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel
import uuid
import json
from datetime import datetime

router = APIRouter(prefix="/models", tags=["models"])

# In-memory storage (replace with database in production)
models_db: Dict[str, dict] = {}


class ModelCreate(BaseModel):
    """Create model request"""
    model: dict
    
class ModelUpdate(BaseModel):
    """Update model request"""
    model: dict

class ModelResponse(BaseModel):
    """Model response"""
    id: str
    model: dict
    created_at: str
    updated_at: str


# Pre-loaded example models
EXAMPLE_MODELS = {
    "aerodin_workforce": {
        "name": "Aerodin Systems - Workforce Dynamics",
        "description": "Defense contractor workforce planning and project delivery model",
        "stocks": [
            {
                "id": "skilled_engineers",
                "name": "Skilled Engineers",
                "initial_value": 500,
                "unit": "people",
                "description": "Current number of trained engineers"
            },
            {
                "id": "active_contracts",
                "name": "Active Contracts",
                "initial_value": 15,
                "unit": "contracts",
                "description": "Number of active defense contracts"
            },
            {
                "id": "backlog",
                "name": "Project Backlog",
                "initial_value": 200,
                "unit": "work_units",
                "description": "Accumulated work waiting to be completed"
            }
        ],
        "flows": [
            {
                "id": "hiring_rate",
                "name": "Hiring Rate",
                "from_stock": None,
                "to_stock": "skilled_engineers",
                "equation": "max(0, hiring_target * (1 - skilled_engineers / max_workforce))",
                "unit": "people/month",
                "description": "Rate of new engineer hiring"
            },
            {
                "id": "attrition_rate",
                "name": "Attrition Rate",
                "from_stock": "skilled_engineers",
                "to_stock": None,
                "equation": "skilled_engineers * attrition_fraction",
                "unit": "people/month",
                "description": "Engineers leaving the company"
            },
            {
                "id": "contract_acquisition",
                "name": "Contract Acquisition",
                "from_stock": None,
                "to_stock": "active_contracts",
                "equation": "base_contract_rate * (skilled_engineers / 500)",
                "unit": "contracts/month",
                "description": "New contracts won"
            },
            {
                "id": "contract_completion",
                "name": "Contract Completion",
                "from_stock": "active_contracts",
                "to_stock": None,
                "equation": "active_contracts * completion_rate",
                "unit": "contracts/month",
                "description": "Contracts completed"
            },
            {
                "id": "work_generation",
                "name": "Work Generation",
                "from_stock": None,
                "to_stock": "backlog",
                "equation": "active_contracts * work_per_contract",
                "unit": "work_units/month",
                "description": "New work from contracts"
            },
            {
                "id": "work_completion",
                "name": "Work Completion",
                "from_stock": "backlog",
                "to_stock": None,
                "equation": "min(backlog, skilled_engineers * productivity)",
                "unit": "work_units/month",
                "description": "Work completed by engineers"
            }
        ],
        "parameters": [
            {"id": "hiring_target", "name": "Hiring Target", "value": 20, "unit": "people/month", "description": "Target monthly hires"},
            {"id": "max_workforce", "name": "Max Workforce", "value": 800, "unit": "people", "description": "Maximum workforce capacity"},
            {"id": "attrition_fraction", "name": "Attrition Fraction", "value": 0.02, "unit": "1/month", "description": "Monthly attrition rate"},
            {"id": "base_contract_rate", "name": "Base Contract Rate", "value": 0.5, "unit": "contracts/month", "description": "Base rate of new contracts"},
            {"id": "completion_rate", "name": "Completion Rate", "value": 0.08, "unit": "1/month", "description": "Contract completion rate"},
            {"id": "work_per_contract", "name": "Work Per Contract", "value": 50, "unit": "work_units/contract", "description": "Work generated per contract"},
            {"id": "productivity", "name": "Productivity", "value": 0.8, "unit": "work_units/person/month", "description": "Engineer productivity"}
        ],
        "auxiliaries": [
            {
                "id": "workforce_gap",
                "name": "Workforce Gap",
                "equation": "max(0, (backlog / productivity) - skilled_engineers)",
                "unit": "people",
                "description": "Gap between needed and available workforce"
            },
            {
                "id": "delivery_pressure",
                "name": "Delivery Pressure",
                "equation": "backlog / (skilled_engineers * productivity + 1)",
                "unit": "months",
                "description": "Months of backlog"
            }
        ],
        "time": {"start": 0, "end": 60, "dt": 1, "unit": "months"}
    },
    "euromotion_growth": {
        "name": "Euromotion Automotive - EV Market Growth",
        "description": "Electric vehicle component supplier market dynamics",
        "stocks": [
            {
                "id": "market_share",
                "name": "Market Share",
                "initial_value": 5,
                "unit": "percent",
                "description": "Current market share percentage"
            },
            {
                "id": "production_capacity",
                "name": "Production Capacity",
                "initial_value": 10000,
                "unit": "units/month",
                "description": "Monthly production capacity"
            },
            {
                "id": "customer_satisfaction",
                "name": "Customer Satisfaction",
                "initial_value": 80,
                "unit": "score",
                "description": "Customer satisfaction score (0-100)"
            },
            {
                "id": "rd_knowledge",
                "name": "R&D Knowledge Base",
                "initial_value": 100,
                "unit": "innovations",
                "description": "Accumulated R&D knowledge"
            }
        ],
        "flows": [
            {
                "id": "market_growth",
                "name": "Market Share Growth",
                "from_stock": None,
                "to_stock": "market_share",
                "equation": "growth_rate * market_share * (1 - market_share / 100) * (customer_satisfaction / 80)",
                "unit": "percent/month",
                "description": "Organic market share growth"
            },
            {
                "id": "market_loss",
                "name": "Market Share Loss",
                "from_stock": "market_share",
                "to_stock": None,
                "equation": "market_share * churn_rate * (1 - customer_satisfaction / 100)",
                "unit": "percent/month",
                "description": "Market share lost to competitors"
            },
            {
                "id": "capacity_expansion",
                "name": "Capacity Expansion",
                "from_stock": None,
                "to_stock": "production_capacity",
                "equation": "investment_rate * (market_share / 5)",
                "unit": "units/month²",
                "description": "Production capacity growth"
            },
            {
                "id": "satisfaction_improvement",
                "name": "Satisfaction Improvement",
                "from_stock": None,
                "to_stock": "customer_satisfaction",
                "equation": "quality_investment * (1 - customer_satisfaction / 100)",
                "unit": "score/month",
                "description": "Satisfaction improvement from quality"
            },
            {
                "id": "satisfaction_decline",
                "name": "Satisfaction Decline",
                "from_stock": "customer_satisfaction",
                "to_stock": None,
                "equation": "if_then_else(delivery_ratio < 1, (1 - delivery_ratio) * 5, 0)",
                "unit": "score/month",
                "description": "Satisfaction loss from delivery issues"
            },
            {
                "id": "rd_investment",
                "name": "R&D Progress",
                "from_stock": None,
                "to_stock": "rd_knowledge",
                "equation": "rd_spending * (1 + rd_knowledge / 200)",
                "unit": "innovations/month",
                "description": "R&D knowledge accumulation"
            }
        ],
        "parameters": [
            {"id": "growth_rate", "name": "Growth Rate", "value": 0.05, "unit": "1/month", "description": "Base market growth rate"},
            {"id": "churn_rate", "name": "Churn Rate", "value": 0.02, "unit": "1/month", "description": "Base customer churn"},
            {"id": "investment_rate", "name": "Investment Rate", "value": 500, "unit": "units/month²", "description": "Capacity investment rate"},
            {"id": "quality_investment", "name": "Quality Investment", "value": 2, "unit": "score/month", "description": "Investment in quality"},
            {"id": "rd_spending", "name": "R&D Spending", "value": 5, "unit": "innovations/month", "description": "R&D investment level"},
            {"id": "total_market_demand", "name": "Total Market Demand", "value": 200000, "unit": "units/month", "description": "Total EV market demand"}
        ],
        "auxiliaries": [
            {
                "id": "demand",
                "name": "Our Demand",
                "equation": "total_market_demand * market_share / 100",
                "unit": "units/month",
                "description": "Demand for our products"
            },
            {
                "id": "delivery_ratio",
                "name": "Delivery Ratio",
                "equation": "min(1, production_capacity / (demand + 1))",
                "unit": "ratio",
                "description": "Ability to meet demand"
            },
            {
                "id": "innovation_factor",
                "name": "Innovation Factor",
                "equation": "1 + rd_knowledge / 500",
                "unit": "multiplier",
                "description": "Competitive advantage from R&D"
            }
        ],
        "time": {"start": 0, "end": 48, "dt": 1, "unit": "months"}
    }
}


@router.get("/", response_model=List[dict])
async def list_models():
    """List all saved models"""
    return [
        {
            "id": model_id,
            "name": data["model"]["name"],
            "description": data["model"].get("description", ""),
            "created_at": data["created_at"],
            "updated_at": data["updated_at"]
        }
        for model_id, data in models_db.items()
    ]


@router.get("/examples", response_model=List[dict])
async def list_example_models():
    """List available example models"""
    return [
        {
            "id": model_id,
            "name": model["name"],
            "description": model["description"]
        }
        for model_id, model in EXAMPLE_MODELS.items()
    ]


@router.get("/examples/{example_id}")
async def get_example_model(example_id: str):
    """Get an example model by ID"""
    if example_id not in EXAMPLE_MODELS:
        raise HTTPException(status_code=404, detail="Example model not found")
    return EXAMPLE_MODELS[example_id]


@router.post("/", response_model=dict)
async def create_model(request: ModelCreate):
    """Create a new model"""
    model_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    models_db[model_id] = {
        "model": request.model,
        "created_at": now,
        "updated_at": now
    }
    
    return {
        "id": model_id,
        "message": "Model created successfully"
    }


@router.get("/{model_id}")
async def get_model(model_id: str):
    """Get a model by ID"""
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    data = models_db[model_id]
    return {
        "id": model_id,
        "model": data["model"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"]
    }


@router.put("/{model_id}")
async def update_model(model_id: str, request: ModelUpdate):
    """Update a model"""
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    models_db[model_id]["model"] = request.model
    models_db[model_id]["updated_at"] = datetime.utcnow().isoformat()
    
    return {"message": "Model updated successfully"}


@router.delete("/{model_id}")
async def delete_model(model_id: str):
    """Delete a model"""
    if model_id not in models_db:
        raise HTTPException(status_code=404, detail="Model not found")
    
    del models_db[model_id]
    return {"message": "Model deleted successfully"}
