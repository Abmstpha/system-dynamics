import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Shield,
  Car,
  Play,
  ArrowRight,
  Loader2,
} from 'lucide-react'
import { getExampleModels, getExampleModel, runSimulation } from '../api/client'
import type { SystemDynamicsModel, SimulationResult } from '../api/client'
import SimulationChart from '../components/SimulationChart'

const exampleInfo: Record<string, { icon: typeof Shield; color: string; industry: string }> = {
  aerodin_workforce: {
    icon: Shield,
    color: 'from-blue-500 to-indigo-600',
    industry: 'Defense',
  },
  euromotion_growth: {
    icon: Car,
    color: 'from-green-500 to-emerald-600',
    industry: 'Automotive',
  },
}

export default function Examples() {
  const [examples, setExamples] = useState<{ id: string; name: string; description: string }[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [model, setModel] = useState<SystemDynamicsModel | null>(null)
  const [results, setResults] = useState<SimulationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    loadExamples()
  }, [])

  const loadExamples = async () => {
    try {
      const data = await getExampleModels()
      setExamples(data)
    } catch (err) {
      console.error('Failed to load examples')
    }
  }

  const handleSelect = async (id: string) => {
    setSelectedId(id)
    setLoading(true)
    setResults(null)
    
    try {
      const exampleModel = await getExampleModel(id)
      setModel(exampleModel)
      
      // Auto-run simulation
      const simResults = await runSimulation(exampleModel)
      setResults(simResults)
    } catch (err) {
      console.error('Failed to load example')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenInSimulator = () => {
    if (selectedId) {
      navigate(`/simulate?example=${selectedId}`)
    }
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Example Models</h1>
        <p className="text-gray-400">Explore pre-built models for different industries</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Example List */}
        <div className="space-y-4">
          {examples.map((example) => {
            const info = exampleInfo[example.id] || { icon: Shield, color: 'from-gray-500 to-gray-600', industry: 'Other' }
            const Icon = info.icon
            
            return (
              <button
                key={example.id}
                onClick={() => handleSelect(example.id)}
                className={`w-full card text-left transition-all ${
                  selectedId === example.id
                    ? 'ring-2 ring-primary-500 border-primary-500/50'
                    : ''
                }`}
              >
                <div className="flex items-start space-x-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${info.color} flex items-center justify-center flex-shrink-0`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <h3 className="text-white font-semibold truncate">{example.name}</h3>
                    </div>
                    <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded-full">
                      {info.industry}
                    </span>
                    <p className="text-gray-400 text-sm mt-2 line-clamp-2">
                      {example.description}
                    </p>
                  </div>
                </div>
              </button>
            )
          })}
        </div>

        {/* Preview */}
        <div className="lg:col-span-2">
          {loading && (
            <div className="card h-[500px] flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
            </div>
          )}

          {!loading && !selectedId && (
            <div className="card h-[500px] flex items-center justify-center">
              <div className="text-center">
                <ArrowRight className="w-12 h-12 text-gray-600 mx-auto mb-3 rotate-180" />
                <p className="text-gray-500">Select an example to preview</p>
              </div>
            </div>
          )}

          {!loading && model && results && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold text-white">{model.name}</h2>
                  <p className="text-gray-400 text-sm">{model.description}</p>
                </div>
                <button
                  onClick={handleOpenInSimulator}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Play className="w-4 h-4" />
                  <span>Open in Simulator</span>
                </button>
              </div>

              <SimulationChart results={results} model={model} />

              {/* Model Summary */}
              <div className="mt-6 pt-4 border-t border-gray-700">
                <div className="grid grid-cols-4 gap-4 text-center">
                  <div>
                    <div className="text-lg font-bold text-primary-400">{model.stocks.length}</div>
                    <div className="text-xs text-gray-500">Stocks</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-green-400">{model.flows.length}</div>
                    <div className="text-xs text-gray-500">Flows</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-yellow-400">{model.parameters.length}</div>
                    <div className="text-xs text-gray-500">Parameters</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-purple-400">{model.time.end}</div>
                    <div className="text-xs text-gray-500">{model.time.unit}</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
