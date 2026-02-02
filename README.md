# 🔄 Strategic System Dynamics Platform

> **AI-Powered System Dynamics Modeling for Strategic Decision Making**

A FastAPI + React application that enables organizations to build, simulate, and explore system dynamics models through natural language — with **deterministic, reproducible results**.

---

## 🎯 Vision

Transform how strategic teams explore "what-if" scenarios. Instead of building complex models from scratch, describe your question in plain English and get a fully functional, mathematically rigorous simulation.

```
"What happens to our production if semiconductor supply drops 30% for 6 months?"
                                    ↓
                         [LLM translates to JSON]
                                    ↓
                    [Deterministic Simulation Engine]
                                    ↓
                      📊 Actionable insights & graphs
```

---

## 🏗️ Architecture

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
│  │   LLM Agent     │    │   JSON Schema   │    │   Simulation    │     │
│  │                 │───▶│   Validator     │───▶│   Engine        │     │
│  │ (Non-determin.) │    │ (Strict rules)  │    │ (Deterministic) │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                         │
│  • Translates NL → JSON  • Validates structure   • Pure math (scipy)   │
│  • ONLY touches schema   • Type checking         • Reproducible        │
│  • Guardrails            • Business rules        • Auditable           │
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
# Activate the virtual environment
cd "/Users/abdu07/Desktop/PGE5/Industrial AI/" && source venv/bin/activate && cd "AI TASK"
```

### Backend Setup
```bash
cd backend
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
- **API:** http://localhost:8000/api/v1

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
- [ ] Core JSON schema definition
- [ ] Deterministic simulation engine
- [ ] FastAPI backend structure
- [ ] LLM agent for NL→JSON
- [ ] React frontend UI
- [ ] Model builder interface
- [ ] Scenario comparison
- [ ] Export & reporting
- [ ] Authentication & multi-tenant
- [ ] Pre-built templates for defense & automotive

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
