"""
Deterministic System Dynamics Simulation Engine
Uses scipy for ODE solving - 100% reproducible
"""
import numpy as np
from scipy.integrate import odeint
from typing import Dict, List, Any, Callable
import math
import re


class EquationParser:
    """Parse and evaluate equations safely"""
    
    SAFE_FUNCTIONS = {
        'min': min,
        'max': max,
        'abs': abs,
        'sqrt': math.sqrt,
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'pow': pow,
        'floor': math.floor,
        'ceil': math.ceil,
        'clip': lambda x, a, b: max(a, min(b, x)),
        'if_then_else': lambda cond, a, b: a if cond else b,
        'step': lambda t, start, height: height if t >= start else 0,
        'pulse': lambda t, start, duration, height: height if start <= t < start + duration else 0,
        'ramp': lambda t, start, slope: slope * max(0, t - start),
    }
    
    def __init__(self):
        self.variables = {}
    
    def set_variables(self, variables: Dict[str, float]):
        """Set current variable values"""
        self.variables = variables.copy()
    
    def evaluate(self, equation: str) -> float:
        """Safely evaluate an equation"""
        try:
            # Create safe namespace
            namespace = {
                **self.SAFE_FUNCTIONS,
                **self.variables,
                'time': self.variables.get('time', 0),
                't': self.variables.get('time', 0),
            }
            
            # Clean equation
            clean_eq = equation.strip()
            
            # Evaluate
            result = eval(clean_eq, {"__builtins__": {}}, namespace)
            
            # Ensure numeric result
            if isinstance(result, bool):
                result = 1.0 if result else 0.0
            
            return float(result)
        
        except Exception as e:
            print(f"Equation error '{equation}': {e}")
            return 0.0


class SystemDynamicsEngine:
    """
    Deterministic System Dynamics Simulation Engine
    
    Key guarantee: Same input → Same output, always.
    """
    
    def __init__(self, model_dict: Dict[str, Any]):
        self.model = model_dict
        self.parser = EquationParser()
        
        # Extract components
        self.time_config = model_dict.get('time', {'start': 0, 'end': 100, 'dt': 1})
        self.stocks = {s['id']: s for s in model_dict.get('stocks', [])}
        self.flows = {f['id']: f for f in model_dict.get('flows', [])}
        self.parameters = {p['id']: p['value'] for p in model_dict.get('parameters', [])}
        self.auxiliaries = {a['id']: a for a in model_dict.get('auxiliaries', [])}
        
        # Stock order for ODE solver
        self.stock_ids = list(self.stocks.keys())
    
    def _compute_auxiliaries(self, variables: Dict[str, float]) -> Dict[str, float]:
        """Compute all auxiliary variables"""
        self.parser.set_variables(variables)
        aux_values = {}
        
        for aux_id, aux in self.auxiliaries.items():
            aux_values[aux_id] = self.parser.evaluate(aux['equation'])
            variables[aux_id] = aux_values[aux_id]
            self.parser.set_variables(variables)
        
        return aux_values
    
    def _compute_flows(self, variables: Dict[str, float]) -> Dict[str, float]:
        """Compute all flow values"""
        self.parser.set_variables(variables)
        flow_values = {}
        
        for flow_id, flow in self.flows.items():
            flow_values[flow_id] = self.parser.evaluate(flow['equation'])
        
        return flow_values
    
    def _derivatives(self, stock_values: np.ndarray, t: float) -> np.ndarray:
        """Compute derivatives for ODE solver"""
        # Build current state
        variables = {'time': t, 't': t}
        variables.update(self.parameters)
        
        for i, stock_id in enumerate(self.stock_ids):
            variables[stock_id] = stock_values[i]
        
        # Compute auxiliaries first
        self._compute_auxiliaries(variables)
        
        # Compute flows
        flow_values = self._compute_flows(variables)
        
        # Compute net change for each stock
        derivatives = np.zeros(len(self.stock_ids))
        
        for i, stock_id in enumerate(self.stock_ids):
            net_flow = 0.0
            
            for flow_id, flow in self.flows.items():
                flow_value = flow_values[flow_id]
                
                # Inflow to this stock
                if flow.get('to_stock') == stock_id:
                    net_flow += flow_value
                
                # Outflow from this stock
                if flow.get('from_stock') == stock_id:
                    net_flow -= flow_value
            
            derivatives[i] = net_flow
        
        return derivatives
    
    def simulate(self, parameter_overrides: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Run deterministic simulation
        
        Returns:
            Dictionary with time, stocks, flows, and auxiliaries history
        """
        # Apply parameter overrides
        if parameter_overrides:
            self.parameters.update(parameter_overrides)
        
        # Time array
        t_start = self.time_config['start']
        t_end = self.time_config['end']
        dt = self.time_config['dt']
        time_points = np.arange(t_start, t_end + dt, dt)
        
        # Initial stock values
        initial_values = np.array([
            self.stocks[stock_id]['initial_value'] 
            for stock_id in self.stock_ids
        ])
        
        # Solve ODE
        stock_history = odeint(self._derivatives, initial_values, time_points)
        
        # Build results
        results = {
            'time': time_points.tolist(),
            'stocks': {},
            'flows': {},
            'auxiliaries': {},
            'metadata': {
                'model_name': self.model.get('name', 'Unnamed'),
                'parameters': self.parameters.copy(),
                'time_config': self.time_config.copy()
            }
        }
        
        # Store stock histories
        for i, stock_id in enumerate(self.stock_ids):
            results['stocks'][stock_id] = stock_history[:, i].tolist()
        
        # Compute flows and auxiliaries at each time point
        for flow_id in self.flows:
            results['flows'][flow_id] = []
        for aux_id in self.auxiliaries:
            results['auxiliaries'][aux_id] = []
        
        for t_idx, t in enumerate(time_points):
            variables = {'time': t, 't': t}
            variables.update(self.parameters)
            
            for i, stock_id in enumerate(self.stock_ids):
                variables[stock_id] = stock_history[t_idx, i]
            
            # Auxiliaries
            aux_values = self._compute_auxiliaries(variables)
            for aux_id, value in aux_values.items():
                results['auxiliaries'][aux_id].append(value)
            
            # Flows
            flow_values = self._compute_flows(variables)
            for flow_id, value in flow_values.items():
                results['flows'][flow_id].append(value)
        
        return results


def run_simulation(model_dict: Dict[str, Any], parameter_overrides: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Main entry point for running simulations
    
    This function is DETERMINISTIC:
    - Same model_dict + same parameter_overrides = Same results, always
    """
    engine = SystemDynamicsEngine(model_dict)
    return engine.simulate(parameter_overrides)
