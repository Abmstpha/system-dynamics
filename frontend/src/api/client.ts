import axios from 'axios'

const API_BASE = '/api/v1'

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface Stock {
  id: string
  name: string
  initial_value: number
  unit: string
  description: string
}

export interface Flow {
  id: string
  name: string
  from_stock: string | null
  to_stock: string | null
  equation: string
  unit: string
  description: string
}

export interface Parameter {
  id: string
  name: string
  value: number
  unit: string
  description: string
}

export interface Auxiliary {
  id: string
  name: string
  equation: string
  unit: string
  description: string
}

export interface TimeConfig {
  start: number
  end: number
  dt: number
  unit: string
}

export interface SystemDynamicsModel {
  name: string
  description: string
  stocks: Stock[]
  flows: Flow[]
  parameters: Parameter[]
  auxiliaries: Auxiliary[]
  time: TimeConfig
}

export interface SimulationResult {
  time: number[]
  stocks: Record<string, number[]>
  flows: Record<string, number[]>
  auxiliaries: Record<string, number[]>
  metadata: {
    model_name: string
    parameters: Record<string, number>
    time_config: TimeConfig
  }
}

// API Functions
export async function translateQuery(query: string, context?: string): Promise<SystemDynamicsModel> {
  const response = await api.post('/agent/translate', { query, context })
  return response.data.model
}

export async function runSimulation(
  model: SystemDynamicsModel,
  parameterOverrides?: Record<string, number>
): Promise<SimulationResult> {
  const response = await api.post('/simulate/', {
    model,
    parameter_overrides: parameterOverrides,
  })
  return response.data.results
}

export async function runExampleSimulation(
  exampleId: string,
  parameterOverrides?: Record<string, number>
): Promise<SimulationResult> {
  const response = await api.post('/simulate/', {
    example_id: exampleId,
    parameter_overrides: parameterOverrides,
  })
  return response.data.results
}

export async function getExampleModels(): Promise<{ id: string; name: string; description: string }[]> {
  const response = await api.get('/models/examples')
  return response.data
}

export async function getExampleModel(exampleId: string): Promise<SystemDynamicsModel> {
  const response = await api.get(`/models/examples/${exampleId}`)
  return response.data
}

export async function compareScenarios(
  model: SystemDynamicsModel,
  scenarios: { name: string; parameters: Record<string, number> }[]
): Promise<{ comparisons: any[] }> {
  const response = await api.post('/simulate/compare', { model, scenarios })
  return response.data
}

export async function getExamplePrompts(): Promise<Record<string, string[]>> {
  const response = await api.get('/agent/prompts')
  return response.data
}
