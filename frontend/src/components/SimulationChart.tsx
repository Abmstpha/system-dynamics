import { useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { SimulationResult, SystemDynamicsModel } from '../api/client'

interface SimulationChartProps {
  results: SimulationResult
  model: SystemDynamicsModel
}

// Color palette for lines
const COLORS = [
  '#0ea5e9', // primary blue
  '#22c55e', // green
  '#f59e0b', // amber
  '#8b5cf6', // violet
  '#ef4444', // red
  '#14b8a6', // teal
  '#f97316', // orange
  '#ec4899', // pink
]

type DataType = 'stocks' | 'flows' | 'auxiliaries'

export default function SimulationChart({ results, model }: SimulationChartProps) {
  const [selectedType, setSelectedType] = useState<DataType>('stocks')
  const [selectedIds, setSelectedIds] = useState<string[]>([])

  // Get available items for current type
  const getItems = () => {
    switch (selectedType) {
      case 'stocks':
        return model.stocks.map((s) => ({ id: s.id, name: s.name }))
      case 'flows':
        return model.flows.map((f) => ({ id: f.id, name: f.name }))
      case 'auxiliaries':
        return model.auxiliaries?.map((a) => ({ id: a.id, name: a.name })) || []
    }
  }

  // Initialize selected items when type changes
  const items = getItems()
  if (selectedIds.length === 0 && items.length > 0) {
    setSelectedIds(items.slice(0, 3).map((i) => i.id))
  }

  // Toggle item selection
  const toggleItem = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    )
  }

  // Build chart data
  const chartData = results.time.map((t, idx) => {
    const point: Record<string, number> = { time: t }
    
    selectedIds.forEach((id) => {
      const data = results[selectedType]?.[id]
      if (data) {
        point[id] = data[idx]
      }
    })
    
    return point
  })

  // Get name for an ID
  const getName = (id: string) => {
    const item = items.find((i) => i.id === id)
    return item?.name || id
  }

  return (
    <div>
      {/* Type Selector */}
      <div className="flex items-center space-x-4 mb-4">
        <div className="flex items-center space-x-1 bg-dark-300 rounded-lg p-1">
          {(['stocks', 'flows', 'auxiliaries'] as DataType[]).map((type) => (
            <button
              key={type}
              onClick={() => {
                setSelectedType(type)
                const newItems = type === 'stocks' 
                  ? model.stocks.map((s) => s.id)
                  : type === 'flows'
                  ? model.flows.map((f) => f.id)
                  : model.auxiliaries?.map((a) => a.id) || []
                setSelectedIds(newItems.slice(0, 3))
              }}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                selectedType === type
                  ? 'bg-primary-500 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
        
        <div className="flex-1 flex flex-wrap gap-2">
          {items.map((item, idx) => (
            <button
              key={item.id}
              onClick={() => toggleItem(item.id)}
              className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium transition-colors ${
                selectedIds.includes(item.id)
                  ? 'bg-opacity-20 border'
                  : 'bg-gray-700 text-gray-400 hover:text-white'
              }`}
              style={{
                backgroundColor: selectedIds.includes(item.id) 
                  ? `${COLORS[idx % COLORS.length]}30` 
                  : undefined,
                borderColor: selectedIds.includes(item.id) 
                  ? COLORS[idx % COLORS.length] 
                  : undefined,
                color: selectedIds.includes(item.id) 
                  ? COLORS[idx % COLORS.length] 
                  : undefined,
              }}
            >
              <span>{item.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="h-[350px] bg-dark-300 rounded-xl p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="time" 
              stroke="#9ca3af" 
              fontSize={12}
              label={{ value: results.metadata.time_config.unit, position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
            />
            <YAxis stroke="#9ca3af" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#9ca3af' }}
            />
            <Legend />
            {selectedIds.map((id, idx) => (
              <Line
                key={id}
                type="monotone"
                dataKey={id}
                name={getName(id)}
                stroke={COLORS[idx % COLORS.length]}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
