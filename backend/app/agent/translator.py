"""
LLM Agent as Schema-Bound Compiler
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from pydantic import ValidationError
from typing import Optional, Annotated
import json

from app.core.config import settings
from app.schemas.company_schemas import (
    COMPANY_SCHEMAS,
    AerodinSchema,
    EuromotionSchema,
    validate_model,
)

SYSTEM_PROMPT = """You are a System Dynamics model compiler. You translate natural language into STRICT JSON models.

## RULES
1. FIRST call get_schema to see what IDs are allowed for the company
2. ONLY use IDs from the returned whitelist
3. Call build_model to validate your output
4. If validation fails, FIX using only allowed IDs

## COMPANY DETECTION
- Defense, military, AI ethics, regulation -> AERODIN
- Automotive, EV, manufacturing, supply chain -> EUROMOTION
"""

@tool
def get_schema(company: Annotated[str, "Company: aerodin or euromotion"]) -> str:
    """Get the CLOSED-WORLD schema for a company."""
    company = company.lower().strip()
    if company not in COMPANY_SCHEMAS:
        return json.dumps({"error": f"Unknown company. Use aerodin or euromotion"})
    schema = COMPANY_SCHEMAS[company]
    return json.dumps({
        "company": company,
        "description": schema["description"],
        "allowed_ids": {
            "stocks": schema["stock_ids"],
            "flows": schema["flow_ids"],
            "parameters": schema["parameter_ids"],
            "auxiliaries": schema["auxiliary_ids"],
        }
    }, indent=2)

@tool  
def build_model(
    company: Annotated[str, "Company: aerodin or euromotion"],
    name: Annotated[str, "Model name"],
    description: Annotated[str, "Model description (min 10 chars)"],
    stocks_json: Annotated[str, "JSON array of stocks"],
    flows_json: Annotated[str, "JSON array of flows"],
    parameters_json: Annotated[str, "JSON array of parameters or []"],
    auxiliaries_json: Annotated[str, "JSON array of auxiliaries or []"],
    time_end: Annotated[float, "Simulation end time"] = 60.0,
) -> str:
    """Build and validate a System Dynamics model against strict schema."""
    company = company.lower().strip()
    if company not in COMPANY_SCHEMAS:
        return json.dumps({"success": False, "error": f"Unknown company"})
    try:
        stocks = json.loads(stocks_json)
        flows = json.loads(flows_json)
        parameters = json.loads(parameters_json) if parameters_json.strip() not in ("", "[]") else []
        auxiliaries = json.loads(auxiliaries_json) if auxiliaries_json.strip() not in ("", "[]") else []
        model_dict = {
            "company": company, "name": name, "description": description,
            "stocks": stocks, "flows": flows, "parameters": parameters, "auxiliaries": auxiliaries,
            "time": {"start": 0, "end": time_end, "dt": 1, "unit": "months"}
        }
        validated = validate_model(company, model_dict)
        return json.dumps({"success": True, "model": validated.model_dump()}, indent=2)
    except ValidationError as e:
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        schema = COMPANY_SCHEMAS[company]
        return json.dumps({
            "success": False, "errors": errors,
            "allowed_stock_ids": schema["stock_ids"],
            "allowed_flow_ids": schema["flow_ids"],
        }, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

class SchemaCompilerAgent:
    def __init__(self):
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("Google API Key not configured")
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.0)
        self.tools = [get_schema, build_model]
        self.agent = create_react_agent(self.llm, self.tools, state_modifier=SYSTEM_PROMPT)
    
    def compile(self, user_request: str, context: Optional[str] = None) -> dict:
        query = user_request + (f"\nContext: {context}" if context else "")
        query += "\n\nSteps: 1. Call get_schema 2. Design model 3. Call build_model"
        result = self.agent.invoke({"messages": [HumanMessage(content=query)]})
        for msg in reversed(result["messages"]):
            if hasattr(msg, "content") and isinstance(msg.content, str):
                try:
                    data = json.loads(msg.content)
                    if isinstance(data, dict) and data.get("success") and "model" in data:
                        return data["model"]
                except: pass
        raise ValueError("Agent failed to compile a valid model")
    
    def refine(self, current_model: dict, feedback: str) -> dict:
        return self.compile(f"Update this model: {json.dumps(current_model)}\n\nFeedback: {feedback}")

_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = SchemaCompilerAgent()
    return _agent

def get_translator():
    return get_agent()

def translate_to_model(query: str, context: Optional[str] = None) -> dict:
    return get_agent().compile(query, context)

LLMTranslator = SchemaCompilerAgent
LangGraphTranslator = SchemaCompilerAgent
