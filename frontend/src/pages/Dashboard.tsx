import { Link } from 'react-router-dom'
import {
  Sparkles,
  Play,
  ArrowRight,
  Shield,
  Car,
  Target,
  TrendingUp,
  Zap,
} from 'lucide-react'

const features = [
  {
    icon: Sparkles,
    title: 'AI-Powered Modeling',
    description: 'Describe your system in natural language and get a complete model instantly',
  },
  {
    icon: Target,
    title: 'Deterministic Simulation',
    description: 'Same inputs always produce the same outputs. 100% reproducible results.',
  },
  {
    icon: TrendingUp,
    title: 'What-If Analysis',
    description: 'Compare multiple scenarios and understand parameter sensitivity',
  },
]

const useCases = [
  {
    icon: Shield,
    name: 'Aerodin Systems',
    industry: 'Defense',
    description: 'Workforce planning and contract delivery optimization',
    color: 'from-blue-500 to-indigo-600',
  },
  {
    icon: Car,
    name: 'Euromotion Automotive',
    industry: 'EV Components',
    description: 'Market growth and supply chain dynamics',
    color: 'from-green-500 to-emerald-600',
  },
]

export default function Dashboard() {
  return (
    <div className="space-y-12 animate-fadeIn">
      {/* Hero Section */}
      <section className="text-center py-12">
        <div className="inline-flex items-center space-x-2 bg-primary-500/10 text-primary-400 px-4 py-2 rounded-full text-sm mb-6">
          <Zap className="w-4 h-4" />
          <span>AI + Deterministic Simulation</span>
        </div>
        
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
          Strategic System Dynamics
          <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-cyan-400">
            Platform
          </span>
        </h1>
        
        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
          Transform complex business dynamics into actionable insights.
          Build models with AI, simulate with precision.
        </p>
        
        <div className="flex items-center justify-center space-x-4">
          <Link
            to="/build"
            className="btn-primary flex items-center space-x-2"
          >
            <Sparkles className="w-5 h-5" />
            <span>Start Building</span>
          </Link>
          <Link
            to="/examples"
            className="btn-secondary flex items-center space-x-2"
          >
            <Play className="w-5 h-5" />
            <span>View Examples</span>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section>
        <h2 className="text-2xl font-semibold text-white mb-6 text-center">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature, idx) => (
            <div key={idx} className="card group">
              <div className="w-12 h-12 bg-primary-500/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <feature.icon className="w-6 h-6 text-primary-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Use Cases */}
      <section>
        <h2 className="text-2xl font-semibold text-white mb-6 text-center">
          Built For Enterprise
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {useCases.map((useCase, idx) => (
            <div key={idx} className="card group cursor-pointer">
              <div className="flex items-start space-x-4">
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${useCase.color} flex items-center justify-center flex-shrink-0`}>
                  <useCase.icon className="w-7 h-7 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="text-lg font-semibold text-white">
                      {useCase.name}
                    </h3>
                    <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded-full">
                      {useCase.industry}
                    </span>
                  </div>
                  <p className="text-gray-400">{useCase.description}</p>
                </div>
                <ArrowRight className="w-5 h-5 text-gray-500 group-hover:text-primary-400 group-hover:translate-x-1 transition-all" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Quick Stats */}
      <section className="glass rounded-2xl p-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-primary-400">100%</div>
            <div className="text-gray-400 text-sm">Deterministic</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-400">∞</div>
            <div className="text-gray-400 text-sm">Scenarios</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-400">AI</div>
            <div className="text-gray-400 text-sm">Powered</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-400">&lt;1s</div>
            <div className="text-gray-400 text-sm">Simulation</div>
          </div>
        </div>
      </section>
    </div>
  )
}
