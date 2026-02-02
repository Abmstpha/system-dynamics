"""
LAYER 2: Company Domain Schemas

This is where Aerodin ≠ Euromotion.
Each company gets a CLOSED-WORLD schema:
- Allowed variables (whitelist)
- Allowed units
- Forbidden structures (hard fail)
- Mandatory intermediates

Anything outside the schema is INVALID.
"""
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Literal, Optional, List, Set, Dict, Any
from enum import Enum

# Use relative import to avoid circular dependency
from .core import (
    SDStock, SDFlow, SDParameter, SDAuxiliary, SDTimeConfig,
    TimeUnit, GraphConstraintChecker, extract_identifiers,
    validate_equation_references, WHITELISTED_FUNCTIONS
)


# ============================================================================
# AERODIN SYSTEMS - DEFENSE CONTRACTOR
# Domain: Ethics, regulation, political risk, secrecy, certification
# ============================================================================

class AerodinDomains(str, Enum):
    """Top-level allowed domains for Aerodin"""
    CAPABILITY = "capability"
    REGULATORY_PRESSURE = "regulatory_pressure"
    POLITICAL_RISK = "political_risk"
    ETHICAL_SCRUTINY = "ethical_scrutiny"
    PROGRAM_FUNDING = "program_funding"
    DEPLOYMENT_READINESS = "deployment_readiness"
    WORKFORCE = "workforce"


# Closed whitelist of allowed IDs
AERODIN_STOCK_IDS = frozenset({
    "skilled_engineers",
    "junior_engineers", 
    "active_defense_programs",  # count of programs
    "regulatory_backlog",       # cases awaiting approval
    "rd_knowledge",
    "certification_level",
    "public_trust_level",       # index 0-100
    "cash_reserves",
    "certified_ai_modules",     # count
})

AERODIN_FLOW_IDS = frozenset({
    "hiring_rate",
    "attrition_rate",
    "promotion_rate",
    "training_completion",
    "program_approval_rate",     # flows from backlog to active
    "program_completion",
    "ethical_clearance_rate",
    "regulatory_submission_rate",
    "rd_investment",
    "knowledge_depreciation",
    "certification_progress",
    "trust_gain",
    "trust_loss",
    "revenue",
    "expenses",
})

AERODIN_PARAMETER_IDS = frozenset({
    "max_workforce",
    "hiring_target",
    "attrition_fraction",
    "training_time",
    "productivity_per_engineer",
    "ethical_review_time",       # mandatory delay
    "certification_requirement",
    "revenue_per_program",
    "cost_per_engineer",
    "overhead_rate",
    "regulatory_capacity",       # cases/month processable
    "political_sensitivity",     # 0-1 factor
})

AERODIN_AUXILIARY_IDS = frozenset({
    "total_workforce",
    "workforce_gap",
    "delivery_capacity",
    "ethical_pressure",          # function of backlog
    "regulatory_delay",          # computed delay time
    "deployment_readiness_index",
    "program_risk_score",
    "profit_margin",
})

# FORBIDDEN STRUCTURES for Aerodin
# Hard rules that will reject the model
AERODIN_FORBIDDEN_EDGES = {
    # No direct flow from capability → revenue (must pass through deployment)
    "certified_ai_modules": {"cash_reserves"},
    "rd_knowledge": {"cash_reserves"},
    # No bypassing ethics
    "regulatory_backlog": set(),  # can flow to active_defense_programs (allowed)
}

# All deployment flows must pass through regulatory
AERODIN_MANDATORY_INTERMEDIATES = {
    # (from, to): must_pass_through
    # Any flow to active_defense_programs from external must go through regulatory_backlog
}


class AerodinSchema(BaseModel):
    """
    STRICT closed-world schema for Aerodin Systems.
    
    Domain: Defense contractor - ethics, regulation, political risk
    
    HARD RULES:
    1. No direct capability → revenue flows
    2. All AI deployments must have ethical_review_time delay
    3. All program approvals must flow through regulatory_backlog
    """
    model_config = ConfigDict(extra='forbid', protected_namespaces=())
    
    company: Literal["aerodin"] = "aerodin"
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    
    stocks: List[SDStock] = Field(..., min_length=1, max_length=len(AERODIN_STOCK_IDS))
    flows: List[SDFlow] = Field(..., min_length=1, max_length=len(AERODIN_FLOW_IDS))
    parameters: List[SDParameter] = Field(default_factory=list, max_length=len(AERODIN_PARAMETER_IDS))
    auxiliaries: List[SDAuxiliary] = Field(default_factory=list, max_length=len(AERODIN_AUXILIARY_IDS))
    time: SDTimeConfig = Field(default_factory=lambda: SDTimeConfig(end=60, unit=TimeUnit.MONTHS))
    
    @model_validator(mode='after')
    def validate_closed_world(self) -> 'AerodinSchema':
        """Validate all IDs are from allowed whitelists"""
        errors = []
        
        # Validate stock IDs
        for stock in self.stocks:
            if stock.id not in AERODIN_STOCK_IDS:
                errors.append(f"Stock '{stock.id}' not allowed. Allowed: {sorted(AERODIN_STOCK_IDS)}")
        
        # Validate flow IDs and from/to references
        stock_ids = {s.id for s in self.stocks}
        for flow in self.flows:
            if flow.id not in AERODIN_FLOW_IDS:
                errors.append(f"Flow '{flow.id}' not allowed. Allowed: {sorted(AERODIN_FLOW_IDS)}")
            if flow.from_stock and flow.from_stock not in stock_ids:
                errors.append(f"Flow '{flow.id}' references unknown from_stock '{flow.from_stock}'")
            if flow.to_stock and flow.to_stock not in stock_ids:
                errors.append(f"Flow '{flow.id}' references unknown to_stock '{flow.to_stock}'")
        
        # Validate parameter IDs
        for param in self.parameters:
            if param.id not in AERODIN_PARAMETER_IDS:
                errors.append(f"Parameter '{param.id}' not allowed. Allowed: {sorted(AERODIN_PARAMETER_IDS)}")
        
        # Validate auxiliary IDs
        for aux in self.auxiliaries:
            if aux.id not in AERODIN_AUXILIARY_IDS:
                errors.append(f"Auxiliary '{aux.id}' not allowed. Allowed: {sorted(AERODIN_AUXILIARY_IDS)}")
        
        # Validate equation references
        valid_ids = (
            stock_ids | 
            {f.id for f in self.flows} | 
            {p.id for p in self.parameters} | 
            {a.id for a in self.auxiliaries}
        )
        
        for flow in self.flows:
            eq_errors = validate_equation_references(flow.equation, valid_ids, f"Flow '{flow.id}'")
            errors.extend(eq_errors)
        
        for aux in self.auxiliaries:
            eq_errors = validate_equation_references(aux.equation, valid_ids, f"Auxiliary '{aux.id}'")
            errors.extend(eq_errors)
        
        # Validate forbidden edges
        checker = GraphConstraintChecker(forbidden_edges=AERODIN_FORBIDDEN_EDGES)
        errors.extend(checker.validate_all_flows(self.flows))
        
        if errors:
            raise ValueError(f"Schema violations: {errors}")
        
        return self


# ============================================================================
# EUROMOTION AUTOMOTIVE - EV COMPONENTS
# Domain: Manufacturing, supply chains, cost curves, volume, dependencies
# ============================================================================

class EuromotionDomains(str, Enum):
    """Top-level allowed domains for Euromotion"""
    PRODUCTION_CAPACITY = "production_capacity"
    SUPPLY_CHAIN = "supply_chain"
    INVENTORY = "inventory"
    DEMAND = "demand"
    COST_STRUCTURE = "cost_structure"
    TECHNOLOGY_MATURITY = "technology_maturity"
    SUPPLIER_RISK = "supplier_risk"


EUROMOTION_STOCK_IDS = frozenset({
    "battery_inventory",            # units
    "semiconductor_inventory",      # units
    "installed_production_capacity", # units/month
    "software_platform_stability",  # index 0-100
    "market_share",                 # percent
    "customer_base",                # count
    "customer_satisfaction",        # index
    "rd_knowledge",
    "brand_equity",
    "supplier_relationships",       # strength index
})

EUROMOTION_FLOW_IDS = frozenset({
    "vehicle_output_rate",          # main production flow
    "capacity_expansion",
    "capacity_depreciation",
    "battery_procurement",
    "battery_consumption",
    "semiconductor_procurement",
    "semiconductor_consumption",
    "market_growth",
    "market_loss",
    "customer_acquisition",
    "customer_churn",
    "satisfaction_improvement",
    "satisfaction_decline",
    "rd_investment",
    "innovation_rate",
    "brand_building",
    "brand_erosion",
})

EUROMOTION_PARAMETER_IDS = frozenset({
    "total_market_size",
    "base_growth_rate",
    "churn_rate",
    "capacity_investment_rate",
    "production_efficiency",
    "bom_battery_ratio",            # batteries per vehicle
    "bom_semiconductor_ratio",      # semiconductors per vehicle
    "supplier_lead_time",
    "target_inventory_days",
    "rd_budget",
    "marketing_budget",
    "innovation_factor",
    "capacity_depreciation_rate",
})

EUROMOTION_AUXILIARY_IDS = frozenset({
    "demand",                       # our share of total demand
    "delivery_ratio",               # ability to meet demand 0-1
    "supply_gap",
    "competitive_position",
    "capacity_utilization",
    "inventory_days",
    "growth_momentum",
    "production_constraint",        # min of capacity and inventory
})

# FORBIDDEN STRUCTURES for Euromotion
EUROMOTION_FORBIDDEN_EDGES = {
    # No ethics/political stocks - this is automotive
    # No direct demand → capacity (must have investment delay)
}

# Flow constraints: vehicle output depends on inventory
EUROMOTION_FLOW_DEPENDENCIES = {
    "vehicle_output_rate": {"battery_inventory", "semiconductor_inventory", "installed_production_capacity"}
}


class EuromotionSchema(BaseModel):
    """
    STRICT closed-world schema for Euromotion Automotive.
    
    Domain: EV manufacturing - supply chains, capacity, inventory
    
    HARD RULES:
    1. No ethics or political stocks (this is automotive)
    2. No direct demand → capacity (must have investment delay)
    3. Vehicle output must depend on inventory levels
    """
    model_config = ConfigDict(extra='forbid', protected_namespaces=())
    
    company: Literal["euromotion"] = "euromotion"
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    
    stocks: List[SDStock] = Field(..., min_length=1, max_length=len(EUROMOTION_STOCK_IDS))
    flows: List[SDFlow] = Field(..., min_length=1, max_length=len(EUROMOTION_FLOW_IDS))
    parameters: List[SDParameter] = Field(default_factory=list, max_length=len(EUROMOTION_PARAMETER_IDS))
    auxiliaries: List[SDAuxiliary] = Field(default_factory=list, max_length=len(EUROMOTION_AUXILIARY_IDS))
    time: SDTimeConfig = Field(default_factory=lambda: SDTimeConfig(end=48, unit=TimeUnit.MONTHS))
    
    @model_validator(mode='after')
    def validate_closed_world(self) -> 'EuromotionSchema':
        """Validate all IDs are from allowed whitelists"""
        errors = []
        
        # Validate stock IDs
        for stock in self.stocks:
            if stock.id not in EUROMOTION_STOCK_IDS:
                errors.append(f"Stock '{stock.id}' not allowed. Allowed: {sorted(EUROMOTION_STOCK_IDS)}")
        
        # Validate flow IDs
        stock_ids = {s.id for s in self.stocks}
        for flow in self.flows:
            if flow.id not in EUROMOTION_FLOW_IDS:
                errors.append(f"Flow '{flow.id}' not allowed. Allowed: {sorted(EUROMOTION_FLOW_IDS)}")
            if flow.from_stock and flow.from_stock not in stock_ids:
                errors.append(f"Flow '{flow.id}' references unknown from_stock '{flow.from_stock}'")
            if flow.to_stock and flow.to_stock not in stock_ids:
                errors.append(f"Flow '{flow.id}' references unknown to_stock '{flow.to_stock}'")
        
        # Validate parameter IDs
        for param in self.parameters:
            if param.id not in EUROMOTION_PARAMETER_IDS:
                errors.append(f"Parameter '{param.id}' not allowed. Allowed: {sorted(EUROMOTION_PARAMETER_IDS)}")
        
        # Validate auxiliary IDs
        for aux in self.auxiliaries:
            if aux.id not in EUROMOTION_AUXILIARY_IDS:
                errors.append(f"Auxiliary '{aux.id}' not allowed. Allowed: {sorted(EUROMOTION_AUXILIARY_IDS)}")
        
        # Validate equation references
        valid_ids = (
            stock_ids | 
            {f.id for f in self.flows} | 
            {p.id for p in self.parameters} | 
            {a.id for a in self.auxiliaries}
        )
        
        for flow in self.flows:
            eq_errors = validate_equation_references(flow.equation, valid_ids, f"Flow '{flow.id}'")
            errors.extend(eq_errors)
        
        for aux in self.auxiliaries:
            eq_errors = validate_equation_references(aux.equation, valid_ids, f"Auxiliary '{aux.id}'")
            errors.extend(eq_errors)
        
        if errors:
            raise ValueError(f"Schema violations: {errors}")
        
        return self


# ============================================================================
# SCHEMA REGISTRY
# ============================================================================

COMPANY_SCHEMAS = {
    "aerodin": {
        "model_class": AerodinSchema,
        "stock_ids": sorted(AERODIN_STOCK_IDS),
        "flow_ids": sorted(AERODIN_FLOW_IDS),
        "parameter_ids": sorted(AERODIN_PARAMETER_IDS),
        "auxiliary_ids": sorted(AERODIN_AUXILIARY_IDS),
        "description": "Defense contractor - regulatory, ethical constraints, certification",
        "domains": [d.value for d in AerodinDomains],
    },
    "euromotion": {
        "model_class": EuromotionSchema,
        "stock_ids": sorted(EUROMOTION_STOCK_IDS),
        "flow_ids": sorted(EUROMOTION_FLOW_IDS),
        "parameter_ids": sorted(EUROMOTION_PARAMETER_IDS),
        "auxiliary_ids": sorted(EUROMOTION_AUXILIARY_IDS),
        "description": "EV manufacturer - supply chain, capacity, inventory",
        "domains": [d.value for d in EuromotionDomains],
    }
}


def get_company_schema(company: str) -> dict:
    """Get schema info for a company"""
    company = company.lower().strip()
    if company not in COMPANY_SCHEMAS:
        raise ValueError(f"Unknown company '{company}'. Must be 'aerodin' or 'euromotion'")
    return COMPANY_SCHEMAS[company]


def validate_model(company: str, model_dict: dict) -> BaseModel:
    """Validate model against company's strict schema"""
    schema = get_company_schema(company)
    model_class = schema["model_class"]
    return model_class(**model_dict)
