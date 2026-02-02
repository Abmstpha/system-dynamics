# 🔄 Strategic System Dynamics Platform

> **AI-Powered System Dynamics Modeling for Strategic Decision Making**

A FastAPI + React application that enables organizations to build, simulate, and explore system dynamics models through natural language — with **deterministic, reproducible results**.

---

## 🎯 Vision

Transform how strategic teams explore "what-if" scenarios. Instead of building complex models from scratch, describe your question in plain English and get a fully functional, mathematically rigorous simulation.

```
"What happens to our production if semiconductor supply drops 30% for 6 months?"
                                    ↓
                      [LLM Agent - Schema-Bound Compiler]
                                    ↓
                    [Strict Pydantic Validation - Closed World]
                                    ↓
                    [Deterministic Simulation Engine (scipy)]
                                    ↓
                      📊 Actionable insights & graphs
```

---

## 🏗️ Two-Layer Architecture

### Layer 1: Universal System Dynamics Core
Immutable concepts shared by ALL companies:
- **Stocks** (accumulations)
- **Flows** (rates of change)
- **Auxiliaries** (intermediate calculations)
- **Parameters** (constants)
- **Time settings** (start, end, dt)

### Layer 2: Company Domain Schemas (CLOSED-WORLD)
Each company gets a strict whitelist - anything outside = HARD FAIL:

| Company | Domain | Key Stocks | Forbidden Structures |
|---------|--------|------------|---------------------|
| **Aerodin Systems** | Defense | regulatory_backlog, certified_ai_modules, public_trust_level | No direct capability→revenue |
| **Euromotion Automotive** | EV Manufacturing | battery_inventory, semiconductor_inventory, production_capacity | No ethics/political stocks |

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React)                              │
│  • Natural language input          • Interactive visualizations         │
│  • Model builder UI                • Scenario comparison                │
│  • Parameter sliders               • Export reports                     │
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │ REST API
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │  LangGraph      │    │   Pydantic      │    │   Simulation    │     │
│  │  ReAct Agent    │───▶│   Strict Schema │───▶│   Engine        │     │
│  │ (Schema Compiler)│   │ (Closed-World)  │    │ (Deterministic) │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                         │
│  Agent MAY:              Validates:            Pure math (scipy):       │
│  • Select from schema    • Allowed IDs only    • ODE integration        │
│  • Change parameters     • Forbidden edges     • Reproducible           │
│  Agent MAY NOT:          • Equation refs       • Auditable              │
│  • Invent new types      • Graph constraints                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Principles

| Principle | Description |
|-----------|-------------|
| **Deterministic Core** | Same JSON input → Always same simulation output. No AI in the math. |
| **LLM as Translator** | AI only converts natural language to structured JSON. Nothing else. |
| **Strict Schema** | JSON structure is validated, versioned, and auditable. |
| **Reproducible** | Every simulation can be re-run with identical results. |
| **Low Friction** | Natural language → instant model. Minimal learning curve. |

---

## 📊 System Dynamics JSON Schema

```json
{
  "model": {
    "name": "Supply Chain Resilience",
    "version": "1.0",
    "time": {
      "start": 0,
      "end": 365,
      "dt": 1
    }
  },
  "stocks": [
    {
      "id": "inventory",
      "name": "Inventory Level",
      "initial_value": 1000,
      "unit": "units"
    }
  ],
  "flows": [
    {
      "id": "production",
      "name": "Production Rate",
      "from": null,
      "to": "inventory",
      "equation": "production_capacity * utilization"
    },
    {
      "id": "shipments",
      "name": "Shipment Rate",
      "from": "inventory",
      "to": null,
      "equation": "min(demand, inventory / delivery_time)"
    }
  ],
  "parameters": [
    {
      "id": "production_capacity",
      "name": "Production Capacity",
      "value": 100,
      "min": 0,
      "max": 500,
      "unit": "units/day"
    },
    {
      "id": "utilization",
      "name": "Utilization Rate",
      "value": 0.8,
      "min": 0,
      "max": 1,
      "unit": "fraction"
    }
  ],
  "auxiliaries": [
    {
      "id": "demand",
      "name": "Market Demand",
      "equation": "base_demand * (1 + demand_growth * time)"
    }
  ]
}
```

---

## 🏢 Use Cases

### **Aerodin Systems** (Defense Manufacturer)
European defense company designing AI-enabled systems for targeting, surveillance, and decision support.

**Example Questions:**
- "What if EU regulations ban autonomous targeting by 2027?"
- "How does a 50% R&D budget cut affect our 5-year capability roadmap?"
- "Simulate talent drain if we lose 20% of AI engineers to big tech"

**Typical Stocks:** R&D capacity, Talent pool, Regulatory approvals, Contract pipeline
**Typical Flows:** Hiring, Investment, Compliance cycles, Project completions

---

### **Euromotion Automotive** (EV Components)
European EV component manufacturer dependent on global semiconductor and battery supply chains.

**Example Questions:**
- "What if semiconductor shortage extends 18 more months?"
- "Simulate the impact of opening a battery plant in Poland"
- "How does 30% tariff on Chinese batteries affect margins?"

**Typical Stocks:** Inventory, Supplier relationships, Production capacity, Order backlog
**Typical Flows:** Supply rate, Production rate, Demand fulfillment, Capacity expansion

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance async API
- **Python 3.11+** - Core language
- **SciPy** - Deterministic ODE solver
- **NumPy** - Numerical computations
- **Pydantic** - Schema validation
- **LangChain** - LLM orchestration (only for NL→JSON)
- **SQLite/PostgreSQL** - Model storage

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Visualizations
- **React Query** - API state management

---

## 📁 Project Structure

```
AI TASK/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── models.py    # CRUD for SD models
│   │   │   │   ├── simulate.py  # Run simulations
│   │   │   │   └── agent.py     # LLM translation
│   │   ├── core/
│   │   │   ├── config.py        # Settings
│   │   │   └── security.py      # Auth
│   │   ├── engine/
│   │   │   ├── simulator.py     # Deterministic SD engine
│   │   │   ├── equations.py     # Equation parser
│   │   │   └── validator.py     # JSON schema validator
│   │   ├── agent/
│   │   │   ├── translator.py    # NL → JSON
│   │   │   └── prompts.py       # LLM prompts
│   │   ├── schemas/
│   │   │   ├── model.py         # Pydantic models
│   │   │   └── simulation.py    # Result schemas
│   │   └── db/
│   │       ├── database.py      # DB connection
│   │       └── models.py        # ORM models
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ModelBuilder/    # Visual model editor
│   │   │   ├── Simulator/       # Run & view results
│   │   │   ├── Chat/            # NL input interface
│   │   │   └── Charts/          # Visualization components
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ModelEditor.tsx
│   │   │   └── Scenarios.tsx
│   │   ├── hooks/
│   │   ├── services/
│   │   │   └── api.ts           # API client
│   │   ├── types/
│   │   │   └── model.ts         # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── docs/
│   ├── schema.md                # JSON schema documentation
│   ├── api.md                   # API documentation
│   └── examples/                # Example models
│
├── docker-compose.yml
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
```bash
# Navigate to workspace and activate virtual environment
cd "/Users/abdu07/Desktop/PGE5/Industrial AI"
source venv/bin/activate
cd "AI TASK"
```

### Backend Setup
```bash
cd backend

# Create .env file with your API keys
cat > .env << EOF
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT="systemdynamics"
Google_API_KEY=your_google_api_key
EOF

# Install dependencies and run
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🖥️ How to Use the UI

### 1. Dashboard (Home Page)
The landing page shows:
- Platform overview and capabilities
- Two company use cases: **Aerodin Systems** (Defense) and **Euromotion Automotive** (EV)
- Quick links to start building models

### 2. Model Builder (`/build`)
**This is the main AI-powered feature:**

1. **Enter a natural language prompt** in the text area, for example:
   - *"Model a defense contractor balancing workforce hiring with project delivery deadlines"*
   - *"Create a model for EV battery supplier dealing with market growth and capacity constraints"*

2. **Click "Generate Model"** — the LangGraph agent will:
   - Detect which company schema to use (Aerodin or Euromotion)
   - Call `get_schema` to retrieve allowed IDs
   - Build a valid model using ONLY whitelisted stocks, flows, parameters
   - Validate against strict Pydantic schema

3. **View the generated model** in JSON format

4. **Click "Run Simulation"** to execute the model

5. **See results** as interactive charts showing stock levels over time

6. **Export** the model as JSON for later use

### 3. Simulation Page (`/simulate`)
**For interactive what-if analysis:**

1. **Select a pre-built example** from the dropdown:
   - Aerodin Systems - Workforce Planning
   - Euromotion - EV Market Growth

2. **Adjust parameters** using sliders:
   - Change hiring rates, production capacity, etc.
   - See how different values affect the system

3. **Click "Run Simulation"** to see updated results

4. **Compare scenarios** by adjusting parameters and re-running

### 4. Examples Page (`/examples`)
Browse pre-built models and understand how System Dynamics works.

---

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/agent/schemas` | GET | Get company schemas (allowed IDs) |
| `/api/v1/agent/translate` | POST | Translate NL to SD model |
| `/api/v1/simulate/` | POST | Run simulation on a model |
| `/api/v1/models/examples/{id}` | GET | Get example model |

---

## 🔒 Determinism Guarantee

The simulation engine is **100% deterministic**:

```python
# Same input JSON will ALWAYS produce same output
result_1 = engine.simulate(model_json, params)
result_2 = engine.simulate(model_json, params)
assert result_1 == result_2  # Always true
```

The LLM agent is **sandboxed**:
- Can ONLY modify the JSON structure
- Cannot execute code
- Cannot affect simulation math
- All outputs are validated against strict schema

---

## 📈 Roadmap

- [x] Project setup & architecture
- [x] Core JSON schema definition (Layer 1: core.py)
- [x] Company-specific schemas (Layer 2: company_schemas.py)
- [x] Deterministic simulation engine (scipy)
- [x] FastAPI backend structure
- [x] LangGraph ReAct agent for NL→JSON
- [x] React frontend UI
- [x] Model builder interface
- [x] LangSmith tracing integration
- [ ] Scenario comparison (side-by-side)
- [ ] Export & reporting (PDF)
- [ ] Authentication & multi-tenant
- [ ] Pre-built templates library

---

## 🧪 Example Workflow

1. **User asks:** *"Create a model for semiconductor supply chain with 3 suppliers"*

2. **LLM generates JSON:**
   ```json
   {
     "stocks": [
       {"id": "inventory", "initial_value": 5000},
       {"id": "supplier_1_stock", "initial_value": 10000},
       ...
     ]
   }
   ```

3. **User adjusts:** Moves slider for "Supplier 1 capacity" from 100 → 50

4. **Engine simulates:** Pure scipy ODE solver runs

5. **Results displayed:** Graphs show inventory depletion over 6 months

---

## 📝 License

Internal use only - Aerodin Systems & Euromotion Automotive

---

## 👥 Team

**System Modeling AI Task Force**

*Building the future of strategic decision support.*
