"""
Agent API routes - LLM translation from natural language to models

The agent is a SCHEMA-BOUND COMPILER:
- It may select variables from schema
- It may NOT invent new variable types
- It may NOT bypass required constraints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.agent.translator import translate_to_model, get_agent
from app.schemas.company_schemas import COMPANY_SCHEMAS

router = APIRouter(prefix="/agent", tags=["agent"])


class TranslateRequest(BaseModel):
    """Request to translate natural language to a model"""
    query: str
    context: Optional[str] = None


class RefineRequest(BaseModel):
    """Request to refine an existing model"""
    current_model: dict
    feedback: str


class ChatMessage(BaseModel):
    """Chat message for conversational model building"""
    message: str
    conversation_id: Optional[str] = None
    current_model: Optional[dict] = None


# Simple conversation memory (replace with proper storage in production)
conversations: Dict[str, dict] = {}


@router.post("/translate")
async def translate_query(request: TranslateRequest):
    """
    Translate natural language to a System Dynamics model
    
    This is the ONLY non-deterministic endpoint.
    The LLM interprets the query and generates a model JSON.
    
    Once generated, all simulation is 100% deterministic.
    """
    try:
        model = translate_to_model(request.query, request.context)
        return {
            "success": True,
            "model": model,
            "message": "Model generated successfully. You can now simulate it deterministically."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")


@router.post("/refine")
async def refine_model(request: RefineRequest):
    """
    Refine an existing model based on user feedback
    
    Use this to iteratively improve a model.
    """
    try:
        agent = get_agent()
        refined = agent.refine(request.current_model, request.feedback)
        return {
            "success": True,
            "model": refined,
            "message": "Model refined successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement error: {str(e)}")


@router.post("/chat")
async def chat_build_model(request: ChatMessage):
    """
    Conversational model building
    
    Have a back-and-forth conversation to build and refine a model.
    """
    import uuid
    
    # Get or create conversation
    conv_id = request.conversation_id or str(uuid.uuid4())
    
    if conv_id not in conversations:
        conversations[conv_id] = {
            "messages": [],
            "current_model": None
        }
    
    conv = conversations[conv_id]
    
    # If model provided, use it
    if request.current_model:
        conv["current_model"] = request.current_model
    
    # Add user message
    conv["messages"].append({
        "role": "user",
        "content": request.message
    })
    
    try:
        if conv["current_model"] is None:
            # First message - generate new model
            model = translate_to_model(
                request.message, 
                f"Previous messages: {conv['messages']}"
            )
            conv["current_model"] = model
            response = "I've created an initial model based on your description. Would you like to modify anything?"
        else:
            # Refine existing model
            agent = get_agent()
            model = agent.refine(conv["current_model"], request.message)
            conv["current_model"] = model
            response = "I've updated the model. What else would you like to change?"
        
        conv["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        return {
            "success": True,
            "conversation_id": conv_id,
            "model": conv["current_model"],
            "response": response
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/schemas")
async def get_company_schemas():
    """
    Get the strict company schemas.
    
    Returns the CLOSED-WORLD schemas for both companies.
    The agent can ONLY use IDs from these lists.
    """
    return {
        "companies": {
            company: {
                "description": info["description"],
                "domains": info["domains"],
                "allowed_ids": {
                    "stocks": info["stock_ids"],
                    "flows": info["flow_ids"],
                    "parameters": info["parameter_ids"],
                    "auxiliaries": info["auxiliary_ids"],
                }
            }
            for company, info in COMPANY_SCHEMAS.items()
        },
        "rules": [
            "Agent may SELECT variables from schema",
            "Agent may INSTANTIATE templates",
            "Agent may CHANGE numeric parameters",
            "Agent may NOT INVENT new variable types",
            "Agent may NOT BYPASS required constraints",
            "Agent may NOT CREATE forbidden causal paths"
        ]
    }


@router.get("/prompts")
async def get_example_prompts():
    """Get example prompts for different domains"""
    return {
        "aerodin": [
            "Model Aerodin's workforce dynamics with hiring, training, and attrition",
            "Show how regulatory backlog affects defense program approvals",
            "Model the relationship between R&D knowledge and certification progress"
        ],
        "euromotion": [
            "Model Euromotion's production capacity vs battery inventory constraints",
            "Show market share growth driven by customer satisfaction",
            "Model supply chain dependencies for EV component manufacturing"
        ],
        "general": [
            "Model a reinforcing loop where success breeds success",
            "Create a balancing loop that shows diminishing returns",
            "Model the dynamics of a product launch with word-of-mouth marketing"
        ]
    }
