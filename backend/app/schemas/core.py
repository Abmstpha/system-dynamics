"""
LAYER 1: Universal System Dynamics Core

Immutable concepts shared by ALL companies:
- stocks
- flows  
- auxiliaries
- parameters
- time settings
- equations

This layer NEVER changes per company.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Set
from enum import Enum
import re


# ============================================================================
# WHITELISTED MATH OPERATIONS - Deterministic only
# ============================================================================

WHITELISTED_FUNCTIONS = frozenset({
    # Basic math
    'min', 'max', 'abs', 'sqrt', 'pow',
    # Exponential/logarithmic  
    'exp', 'log', 'log10',
    # Trigonometric (for cyclical patterns)
    'sin', 'cos',
    # Rounding
    'floor', 'ceil',
    # SD-specific
    'clip',           # clip(value, min, max)
    'if_then_else',   # if_then_else(cond, true_val, false_val)
    'step',           # step(height, step_time)
    'pulse',          # pulse(height, start_time, duration)
    'ramp',           # ramp(slope, start_time)
    'delay',          # delay(input, delay_time)
    'smooth',         # smooth(input, smooth_time)
})

FORBIDDEN_FUNCTIONS = frozenset({
    'random', 'rand', 'randint', 'uniform', 'normal', 'gauss',
    'eval', 'exec', 'compile', 'import', '__import__',
    'open', 'read', 'write', 'file',
})


class TimeUnit(str, Enum):
    """Standard time units for SD models"""
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    QUARTERS = "quarters"
    YEARS = "years"


# ============================================================================
# CORE SD COMPONENTS (Company-agnostic)
# ============================================================================

class SDStock(BaseModel):
    """Universal stock definition"""
    model_config = ConfigDict(extra='forbid')
    
    id: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-z][a-z0-9_]*$')
    name: str = Field(..., min_length=1, max_length=100)
    initial_value: float = Field(..., ge=0)
    unit: str = Field(default="units", max_length=30)
    description: Optional[str] = Field(default=None, max_length=200)


class SDFlow(BaseModel):
    """Universal flow definition"""
    model_config = ConfigDict(extra='forbid')
    
    id: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-z][a-z0-9_]*$')
    name: str = Field(..., min_length=1, max_length=100)
    from_stock: Optional[str] = Field(default=None, description="Source stock (null = inflow from outside)")
    to_stock: Optional[str] = Field(default=None, description="Target stock (null = outflow to outside)")
    equation: str = Field(..., min_length=1, max_length=500)
    unit: str = Field(default="units/time", max_length=30)
    description: Optional[str] = Field(default=None, max_length=200)
    
    @field_validator('equation')
    @classmethod
    def validate_equation_syntax(cls, v: str) -> str:
        """Block forbidden functions - no stochastic terms"""
        lower = v.lower()
        for forbidden in FORBIDDEN_FUNCTIONS:
            if forbidden in lower:
                raise ValueError(f"Forbidden function '{forbidden}' in equation. No stochastic/unsafe operations allowed.")
        return v


class SDParameter(BaseModel):
    """Universal parameter definition - constant values"""
    model_config = ConfigDict(extra='forbid')
    
    id: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-z][a-z0-9_]*$')
    name: str = Field(..., min_length=1, max_length=100)
    value: float = Field(...)
    unit: str = Field(default="", max_length=30)
    description: Optional[str] = Field(default=None, max_length=200)


class SDAuxiliary(BaseModel):
    """Universal auxiliary variable - computed from other variables"""
    model_config = ConfigDict(extra='forbid')
    
    id: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-z][a-z0-9_]*$')
    name: str = Field(..., min_length=1, max_length=100)
    equation: str = Field(..., min_length=1, max_length=500)
    unit: str = Field(default="", max_length=30)
    description: Optional[str] = Field(default=None, max_length=200)
    
    @field_validator('equation')
    @classmethod
    def validate_equation_syntax(cls, v: str) -> str:
        """Block forbidden functions"""
        lower = v.lower()
        for forbidden in FORBIDDEN_FUNCTIONS:
            if forbidden in lower:
                raise ValueError(f"Forbidden function '{forbidden}' in equation.")
        return v


class SDTimeConfig(BaseModel):
    """Universal time configuration"""
    model_config = ConfigDict(extra='forbid')
    
    start: float = Field(default=0, ge=0)
    end: float = Field(..., gt=0)
    dt: float = Field(default=1, gt=0, le=1, description="Fixed time step - no adaptive")
    unit: TimeUnit = Field(default=TimeUnit.MONTHS)


# ============================================================================
# EQUATION VALIDATION UTILITIES
# ============================================================================

def extract_identifiers(equation: str) -> Set[str]:
    """Extract all variable identifiers from an equation"""
    # Match word characters that aren't part of numbers
    pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
    return set(re.findall(pattern, equation))


def validate_equation_references(
    equation: str,
    valid_ids: Set[str],
    context_name: str = "equation"
) -> List[str]:
    """
    Validate equation only references valid identifiers.
    Returns list of errors (empty if valid).
    """
    errors = []
    identifiers = extract_identifiers(equation)
    
    # All valid: stocks, flows, params, auxs, functions, time
    all_valid = valid_ids | WHITELISTED_FUNCTIONS | {'time', 't'}
    
    unknown = identifiers - all_valid
    if unknown:
        errors.append(f"{context_name}: Unknown identifiers {unknown}")
    
    return errors


# ============================================================================
# GRAPH CONSTRAINT CHECKING
# ============================================================================

class GraphConstraintChecker:
    """
    Validates causal graph structure.
    Checks: allowed edges, mandatory intermediates, forbidden paths.
    """
    
    def __init__(self, 
                 allowed_edges: Optional[Dict[str, Set[str]]] = None,
                 forbidden_edges: Optional[Dict[str, Set[str]]] = None,
                 mandatory_intermediates: Optional[Dict[tuple, str]] = None):
        """
        Args:
            allowed_edges: {from_id: {to_id1, to_id2}} - if set, only these edges valid
            forbidden_edges: {from_id: {to_id1}} - these edges are never valid
            mandatory_intermediates: {(from, to): intermediate} - flow from->to must pass through intermediate
        """
        self.allowed_edges = allowed_edges or {}
        self.forbidden_edges = forbidden_edges or {}
        self.mandatory_intermediates = mandatory_intermediates or {}
    
    def validate_flow(self, from_stock: Optional[str], to_stock: Optional[str]) -> List[str]:
        """Validate a single flow against constraints"""
        errors = []
        
        if from_stock and to_stock:
            # Check forbidden
            if from_stock in self.forbidden_edges:
                if to_stock in self.forbidden_edges[from_stock]:
                    errors.append(f"Forbidden edge: {from_stock} → {to_stock}")
            
            # Check allowed (if allowlist exists)
            if self.allowed_edges and from_stock in self.allowed_edges:
                if to_stock not in self.allowed_edges[from_stock]:
                    errors.append(f"Edge not allowed: {from_stock} → {to_stock}")
        
        return errors
    
    def validate_all_flows(self, flows: List[SDFlow]) -> List[str]:
        """Validate all flows in model"""
        errors = []
        for flow in flows:
            errors.extend(self.validate_flow(flow.from_stock, flow.to_stock))
        return errors
