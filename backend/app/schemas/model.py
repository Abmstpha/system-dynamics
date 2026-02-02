"""
Pydantic schemas for System Dynamics models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class TimeConfig(BaseModel):
    """Time configuration for simulation"""
    start: float = Field(default=0, description="Start time")
    end: float = Field(default=100, description="End time")
    dt: float = Field(default=1, description="Time step")


class Stock(BaseModel):
    """Stock (accumulation) in the system"""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Display name")
    initial_value: float = Field(..., description="Initial value")
    unit: str = Field(default="units", description="Unit of measurement")
    description: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class Flow(BaseModel):
    """Flow (rate of change) between stocks"""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Display name")
    from_stock: Optional[str] = Field(None, description="Source stock ID (null for inflow)")
    to_stock: Optional[str] = Field(None, description="Target stock ID (null for outflow)")
    equation: str = Field(..., description="Mathematical equation")
    unit: str = Field(default="units/time", description="Unit of measurement")
    description: Optional[str] = None


class Parameter(BaseModel):
    """Adjustable parameter"""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Display name")
    value: float = Field(..., description="Current value")
    min_value: float = Field(default=0, description="Minimum allowed value")
    max_value: float = Field(default=100, description="Maximum allowed value")
    step: float = Field(default=1, description="Step size for adjustments")
    unit: str = Field(default="", description="Unit of measurement")
    description: Optional[str] = None


class Auxiliary(BaseModel):
    """Auxiliary variable (intermediate calculation)"""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Display name")
    equation: str = Field(..., description="Mathematical equation")
    unit: str = Field(default="", description="Unit of measurement")
    description: Optional[str] = None


class SystemDynamicsModel(BaseModel):
    """Complete System Dynamics model definition"""
    id: Optional[str] = None
    name: str = Field(..., description="Model name")
    description: Optional[str] = Field(None, description="Model description")
    version: str = Field(default="1.0", description="Model version")
    company: Optional[str] = Field(None, description="Company (Aerodin/Euromotion)")
    
    time: TimeConfig = Field(default_factory=TimeConfig)
    stocks: List[Stock] = Field(default_factory=list)
    flows: List[Flow] = Field(default_factory=list)
    parameters: List[Parameter] = Field(default_factory=list)
    auxiliaries: List[Auxiliary] = Field(default_factory=list)
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Supply Chain Model",
                "description": "Basic inventory and supply chain dynamics",
                "company": "Euromotion",
                "time": {"start": 0, "end": 365, "dt": 1},
                "stocks": [
                    {"id": "inventory", "name": "Inventory", "initial_value": 1000, "unit": "units"}
                ],
                "flows": [
                    {"id": "production", "name": "Production", "from_stock": None, "to_stock": "inventory", "equation": "production_rate"},
                    {"id": "shipments", "name": "Shipments", "from_stock": "inventory", "to_stock": None, "equation": "min(demand, inventory)"}
                ],
                "parameters": [
                    {"id": "production_rate", "name": "Production Rate", "value": 100, "min_value": 0, "max_value": 500, "unit": "units/day"},
                    {"id": "demand", "name": "Daily Demand", "value": 80, "min_value": 0, "max_value": 300, "unit": "units/day"}
                ]
            }
        }


class SimulationRequest(BaseModel):
    """Request to run a simulation"""
    model: SystemDynamicsModel
    parameter_overrides: Optional[Dict[str, float]] = None


class SimulationResult(BaseModel):
    """Simulation results"""
    time: List[float]
    stocks: Dict[str, List[float]]
    flows: Dict[str, List[float]]
    auxiliaries: Dict[str, List[float]]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentRequest(BaseModel):
    """Request to the LLM agent"""
    prompt: str = Field(..., description="Natural language description")
    context: Optional[str] = Field(None, description="Additional context (company, domain)")
    existing_model: Optional[SystemDynamicsModel] = Field(None, description="Existing model to modify")


class AgentResponse(BaseModel):
    """Response from the LLM agent"""
    model: SystemDynamicsModel
    explanation: str
    suggestions: List[str] = Field(default_factory=list)


class ModelListItem(BaseModel):
    """Model list item for API responses"""
    id: str
    name: str
    description: Optional[str]
    company: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
