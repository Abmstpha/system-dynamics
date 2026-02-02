import { useState } from 'react'
import {
  Sparkles,
  Send,
  Loader2,
  Code,
  Eye,
  Play,
  Download,
  RefreshCw,
  Lightbulb,
} from 'lucide-react'
import { translateQuery, runSimulation } from '../api/client'
import type { SystemDynamicsModel, SimulationResult } from '../api/client'
import SimulationChart from '../components/SimulationChart'

const samplePrompts = [
  "Model a defense contractor balancing workforce hiring with project delivery deadlines",
  "Create a model for EV battery supplier dealing with market growth and capacity constraints",
  "Show the dynamics of R&D investment affecting competitive advantage over time",
  "Model customer satisfaction affecting market share in a reinforcing loop",
]

export default function ModelBuilder() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [model, setModel] = useState<SystemDynamicsModel | null>(null)
  const [results, setResults] = useState<SimulationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<'model' | 'results'>('model')

  const handleTranslate = async () => {
    if (!query.trim()) return
    
    setLoading(true)
    setError(null)
    setResults(null)
    
    try {
      const generatedModel = await translateQuery(query)
      setModel(generatedModel)
      setView('model')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate model')
    } finally {
      setLoading(false)
    }
  }

  const handleSimulate = async () => {
    if (!model) return
    
    setLoading(true)
    setError(null)
    
    try {
      const simResults = await runSimulation(model)
      setResults(simResults)
      setView('results')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Simulation failed')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = () => {
    if (!model) return
    const blob = new Blob([JSON.stringify(model, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${model.name.replace(/\s+/g, '_').toLowerCase()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Build Your Model</h1>
          <p className="text-gray-400">Describe your system and let AI create the model</p>
        </div>
      </div>

      {/* Input Section */}
      <div className="card">
        <div className="flex items-start space-x-3 mb-4">
          <div className="w-10 h-10 bg-primary-500/20 rounded-xl flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-primary-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white">Natural Language Input</h3>
            <p className="text-sm text-gray-400">Describe the system you want to model</p>
          </div>
        </div>

        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Example: Model a company that needs to balance hiring new employees with training capacity. New hires increase productivity but require training time, which temporarily reduces output..."
          className="input min-h-[120px] resize-none mb-4"
        />

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Lightbulb className="w-4 h-4 text-yellow-500" />
            <span className="text-sm text-gray-400">Try a sample:</span>
            <div className="flex flex-wrap gap-2">
              {samplePrompts.slice(0, 2).map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => setQuery(prompt)}
                  className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded-full transition-colors"
                >
                  {prompt.slice(0, 40)}...
                </button>
              ))}
            </div>
          </div>
          
          <button
            onClick={handleTranslate}
            disabled={loading || !query.trim()}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            <span>Generate Model</span>
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 text-red-400">
          {error}
        </div>
      )}

      {/* Model Output */}
      {model && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold text-white">{model.name}</h2>
              <p className="text-gray-400">{model.description}</p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setView('model')}
                className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg transition-colors ${
                  view === 'model' ? 'bg-primary-500/20 text-primary-400' : 'text-gray-400 hover:text-white'
                }`}
              >
                <Code className="w-4 h-4" />
                <span className="text-sm">Model</span>
              </button>
              <button
                onClick={() => setView('results')}
                disabled={!results}
                className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50 ${
                  view === 'results' ? 'bg-primary-500/20 text-primary-400' : 'text-gray-400 hover:text-white'
                }`}
              >
                <Eye className="w-4 h-4" />
                <span className="text-sm">Results</span>
              </button>
            </div>
          </div>

          {view === 'model' && (
            <div className="space-y-6">
              {/* Model Stats */}
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-dark-300 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-primary-400">{model.stocks.length}</div>
                  <div className="text-sm text-gray-400">Stocks</div>
                </div>
                <div className="bg-dark-300 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-400">{model.flows.length}</div>
                  <div className="text-sm text-gray-400">Flows</div>
                </div>
                <div className="bg-dark-300 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-yellow-400">{model.parameters.length}</div>
                  <div className="text-sm text-gray-400">Parameters</div>
                </div>
                <div className="bg-dark-300 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-purple-400">{model.auxiliaries?.length || 0}</div>
                  <div className="text-sm text-gray-400">Auxiliaries</div>
                </div>
              </div>

              {/* Stocks */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Stocks</h3>
                <div className="space-y-2">
                  {model.stocks.map((stock) => (
                    <div key={stock.id} className="bg-dark-300 rounded-lg p-3 flex items-center justify-between">
                      <div>
                        <span className="text-white font-medium">{stock.name}</span>
                        <span className="text-gray-500 text-sm ml-2">({stock.id})</span>
                      </div>
                      <div className="text-right">
                        <span className="text-primary-400 font-mono">{stock.initial_value}</span>
                        <span className="text-gray-500 text-sm ml-1">{stock.unit}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Flows */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Flows</h3>
                <div className="space-y-2">
                  {model.flows.map((flow) => (
                    <div key={flow.id} className="bg-dark-300 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-white font-medium">{flow.name}</span>
                        <span className="text-gray-500 text-sm">
                          {flow.from_stock || '∞'} → {flow.to_stock || '∞'}
                        </span>
                      </div>
                      <code className="text-sm text-green-400 bg-dark-400 px-2 py-1 rounded">
                        {flow.equation}
                      </code>
                    </div>
                  ))}
                </div>
              </div>

              {/* Parameters */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Parameters</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {model.parameters.map((param) => (
                    <div key={param.id} className="bg-dark-300 rounded-lg p-3">
                      <div className="text-white font-medium text-sm">{param.name}</div>
                      <div className="flex items-baseline space-x-1">
                        <span className="text-yellow-400 font-mono">{param.value}</span>
                        <span className="text-gray-500 text-xs">{param.unit}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-3 pt-4 border-t border-gray-700">
                <button
                  onClick={handleSimulate}
                  disabled={loading}
                  className="btn-primary flex items-center space-x-2"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Play className="w-5 h-5" />
                  )}
                  <span>Run Simulation</span>
                </button>
                <button
                  onClick={handleExport}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Download className="w-5 h-5" />
                  <span>Export JSON</span>
                </button>
                <button
                  onClick={() => {
                    setModel(null)
                    setResults(null)
                    setQuery('')
                  }}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <RefreshCw className="w-5 h-5" />
                  <span>Start Over</span>
                </button>
              </div>
            </div>
          )}

          {view === 'results' && results && (
            <SimulationChart results={results} model={model} />
          )}
        </div>
      )}
    </div>
  )
}
