import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ModelBuilder from './pages/ModelBuilder'
import Simulation from './pages/Simulation'
import Examples from './pages/Examples'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="build" element={<ModelBuilder />} />
        <Route path="simulate" element={<Simulation />} />
        <Route path="examples" element={<Examples />} />
      </Route>
    </Routes>
  )
}

export default App
