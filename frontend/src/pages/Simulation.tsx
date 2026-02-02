import { useState, useEffect } from 'react'
import {
  Play,
  Loader2,
  Settings,
  BarChart3,
  RefreshCw,
  Download,
} from 'lucide-react'
import { getExampleModel, runSimulation } from '../api/client'
import type { SystemDynamicsModel, SimulationResult } from '../api/client'
import SimulationChart from '../components/SimulationChart'

export default function Simulation() {
  const [model, setModel] = useState<SystemDynamicsModel | null>(null)
  const [results, setResults] = useState<SimulationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [paramOverrides, setParamOverrides] = useState<Record<string, number>>({})
  const [selectedExample, setSelectedExample] = useState('aerodin_workforce')

  useEffect(() => {
    loadExample(selectedExample)
  }, [selectedExample])

  const loadExample = async (exampleId: string) => {
    setLoading(true)
    setError(null)
    try {
      const exampleModel = await getExampleModel(exampleId)
      setModel(exampleModel)
      // Initialize param overrides with current values
      const overrides: Record<string, number> = {}
      exampleModel.parameters.forEach((p) => {
        overrides[p.id] = p.value
      })
      setParamOverrides(overrides)
      setResults(null)
    } catch (err: any) {
      setError('Failed to load example model')
    } finally {
      setLoading(false)
    }
  }

  const handleSimulate = async () => {
    if (!model) return
    
    setLoading(true)
    setError(null)
    
    try {
      const simResults = await runSimulation(model, paramOverrides)
      setResults(simResults)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Simulation failed')
    } finally {
      setLoading(false)
    }
  }

  const handleParamChange = (paramId: string, value: number) => {
    setParamOverrides((prev) => ({ ...prev, [paramId]: value }))
  }

  const resetParams = () => {
    if (!model) return
    const overrides: Record<string, number> = {}
    model.parameters.forEach((p) => {
      overrides[p.id] = p.value
    })
    setParamOverrides(overrides)
  }

  const exportResults = () => {
    if (!results) return
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'simulation_results.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Interactive Simulation</h1>
          <p className="text-gray-400">Adjust parameters and see results in real-time</p>
        </div>
        <select
          value={selectedExample}
          onChange={(e) => setSelectedExample(e.target.value)}
          className="input w-64"
        >
          <option value="aerodin_workforce">Aerodin Systems - Workforce</option>
          <option value="euromotion_growth">Euromotion - EV Market Growth</option>
        </select>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 text-red-400">
          {error}
        </div>
      )}

      {model && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Parameters Panel */}
          <div className="card lg:col-span-1">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Settings className="w-5 h-5 text-primary-400" />
                <h2 className="text-lg font-semibold text-white">Parameters</h2>
              </div>
              <button
                onClick={resetParams}
                className="text-gray-400 hover:text-white transition-colors"
                title="Reset to defaults"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
              {model.parameters.map((param) => (
                <div key={param.id} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <label className="text-sm text-gray-300">{param.name}</label>
                    <span className="text-xs text-gray-500">{param.unit}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="range"
                      min={param.value * 0.1}
                      max={param.value * 3}
                      step={param.value * 0.01}
                      value={paramOverrides[param.id] ?? param.value}
                      onChange={(e) => handleParamChange(param.id, parseFloat(e.target.value))}
                      className="flex-1 accent-primary-500"
                    />
                    <input
                      type="number"
                      value={paramOverrides[param.id] ?? param.value}
                      onChange={(e) => handleParamChange(param.id, parseFloat(e.target.value))}
                      className="w-20 bg-dark-300 border border-gray-700 rounded px-2 py-1 text-sm text-white text-right"
                    />
                  </div>
                  <p className="text-xs text-gray-500">{param.description}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-4 border-t border-gray-700 space-y-3">
              <button
                onClick={handleSimulate}
                disabled={loading}
                className="btn-primary w-full flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Play className="w-5 h-5" />
                )}
                <span>Run Simulation</span>
              </button>
              
              {results && (
                <button
                  onClick={exportResults}
                  className="btn-secondary w-full flex items-center justify-center space-x-2"
                >
                  <Download className="w-5 h-5" />
                  <span>Export Results</span>
                </button>
              )}
            </div>
          </div>

          {/* Results Panel */}
          <div className="card lg:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <BarChart3 className="w-5 h-5 text-primary-400" />
              <h2 className="text-lg font-semibold text-white">Simulation Results</h2>
            </div>

            {results ? (
              <SimulationChart results={results} model={model} />
            ) : (
              <div className="h-[400px] flex items-center justify-center bg-dark-300 rounded-xl">
                <div className="text-center">
                  <BarChart3 className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-500">
                    Adjust parameters and click "Run Simulation" to see results
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
