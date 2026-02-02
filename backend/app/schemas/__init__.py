# Schemas module - Use relative imports to avoid circular dependencies

# Layer 1: Universal SD Core
from .core import (
    SDStock,
    SDFlow,
    SDParameter,
    SDAuxiliary,
    SDTimeConfig,
    TimeUnit,
    WHITELISTED_FUNCTIONS,
    GraphConstraintChecker,
)

# Layer 2: Company Domain Schemas
from .company_schemas import (
    AerodinSchema,
    EuromotionSchema,
    COMPANY_SCHEMAS,
    get_company_schema,
    validate_model,
)

# Generic model (for simulator compatibility)
from .model import (
    SystemDynamicsModel,
    Stock,
    Flow,
    Parameter,
    Auxiliary,
    TimeConfig,
    SimulationRequest,
    SimulationResult,
    AgentRequest,
    AgentResponse,
    ModelListItem
)

__all__ = [
    # Core SD types
    "SDStock",
    "SDFlow", 
    "SDParameter",
    "SDAuxiliary",
    "SDTimeConfig",
    "TimeUnit",
    "WHITELISTED_FUNCTIONS",
    "GraphConstraintChecker",
    # Company schemas
    "AerodinSchema",
    "EuromotionSchema",
    "COMPANY_SCHEMAS",
    "get_company_schema",
    "validate_model",
    # Generic model
    "SystemDynamicsModel",
    "Stock",
    "Flow",
    "Parameter",
    "Auxiliary",
    "TimeConfig",
    "SimulationRequest",
    "SimulationResult",
    "AgentRequest",
    "AgentResponse",
    "ModelListItem"
]
