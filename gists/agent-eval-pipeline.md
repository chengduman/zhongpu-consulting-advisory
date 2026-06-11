# Agent Evaluation Pipeline: Production-Ready Framework

A practical Python framework for evaluating AI agent systems across three levels: atomic tasks, multi-step workflows, and system-level outcomes.

```python
"""
agent_eval_pipeline.py — Production AI Agent Evaluation Framework
"""

from dataclasses import dataclass, field
from typing import Any, Callable
import time, json, statistics

# ─── Level 1: Atomic Task Evaluation ───

@dataclass
class AtomicTaskResult:
    tool_name: str
    params_extracted: dict
    params_ground_truth: dict
    output_valid: bool
    latency_ms: float

def evaluate_tool_selection(selected: str, expected: str) -> float:
    """Precision: 1.0 if correct tool, 0.0 otherwise."""
    return 1.0 if selected == expected else 0.0

def evaluate_parameter_fidelity(
    extracted: dict, ground_truth: dict
) -> float:
    """Token-level F1 for parameter extraction."""
    extracted_set = set(json.dumps(extracted, sort_keys=True).items())
    truth_set = set(json.dumps(ground_truth, sort_keys=True).items())
    if not truth_set:
        return 1.0
    tp = len(extracted_set & truth_set)
    fp = len(extracted_set - truth_set)
    fn = len(truth_set - extracted_set)
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    return 2 * precision * recall / (precision + recall) if (precision + recall) else 0

# ─── Level 2: Multi-Step Evaluation ───

@dataclass
class ScenarioResult:
    name: str
    steps_completed: int
    total_steps: int
    success: bool
    recovery: bool
    step_efficiency: float
    total_latency_ms: float

def evaluate_scenario(
    scenario_steps: list[dict],
    agent_executor: Callable,
    max_retries: int = 2
) -> ScenarioResult:
    """Evaluate a multi-step agent scenario end-to-end."""
    completed = 0
    recovered = False
    latencies = []
    
    for i, step in enumerate(scenario_steps):
        start = time.time()
        for attempt in range(max_retries + 1):
            result = agent_executor(step["action"], step.get("params"))
            if result.get("status") == step["expected"]:
                completed += 1
                if attempt > 0:
                    recovered = True
                break
        latencies.append((time.time() - start) * 1000)
    
    optimal_steps = len(scenario_steps)
    actual_steps = completed * (1 + (1 if recovered else 0))
    
    return ScenarioResult(
        name=scenario_steps[0].get("scenario", "unnamed"),
        steps_completed=completed,
        total_steps=len(scenario_steps),
        success=completed == len(scenario_steps),
        recovery=recovered,
        step_efficiency=optimal_steps / max(actual_steps, 1),
        total_latency_ms=sum(latencies)
    )

# ─── Level 3: System-Level Metrics ───

@dataclass
class SystemMetrics:
    task_completion_rate: float      # % fully resolved
    human_escalation_rate: float     # % needing handoff
    cost_per_resolution: float       # $ per success
    user_satisfaction: float         # 1-5 scale
    time_saved_pct: float            # % faster than human

def compute_system_metrics(
    total_tasks: int,
    completed: int,
    escalated: int,
    total_cost: float,
    satisfaction_scores: list[float],
    avg_human_time_min: float,
    avg_agent_time_min: float
) -> SystemMetrics:
    return SystemMetrics(
        task_completion_rate=completed / max(total_tasks, 1),
        human_escalation_rate=escalated / max(total_tasks, 1),
        cost_per_resolution=total_cost / max(completed, 1),
        user_satisfaction=statistics.mean(satisfaction_scores),
        time_saved_pct=(1 - avg_agent_time_min / max(avg_human_time_min, 0.01)) * 100
    )

# ─── Full Pipeline ───

def run_eval_pipeline(
    test_cases: list[dict],
    agent: Callable,
    human_baseline_min: float = 10.0
) -> dict:
    """Run the complete evaluation pipeline across all three levels."""
    
    level_1_results = []
    level_2_results = []
    all_costs = []
    all_satisfaction = []
    
    for case in test_cases:
        # Level 1
        step_results = []
        for step in case.get("steps", []):
            start = time.time()
            output = agent(step["action"], step.get("params", {}))
            latency = (time.time() - start) * 1000
            
            step_results.append(AtomicTaskResult(
                tool_name=step["action"],
                params_extracted=output.get("params", {}),
                params_ground_truth=step.get("expected_params", {}),
                output_valid=output.get("valid", False),
                latency_ms=latency
            ))
            all_costs.append(output.get("cost", 0))
        
        level_1_results.extend(step_results)
        
        # Level 2
        scenario_result = evaluate_scenario(case.get("steps", []), 
            lambda a, p: agent(a, p))
        level_2_results.append(scenario_result)
        
        all_satisfaction.append(case.get("satisfaction", 4.0))
    
    # Level 3
    total = len(test_cases)
    completed = sum(1 for s in level_2_results if s.success)
    escalated = sum(1 for s in level_2_results if not s.success)
    avg_agent_time = statistics.mean([s.total_latency_ms for s in level_2_results]) / 1000 / 60
    
    system_metrics = compute_system_metrics(
        total_tasks=total,
        completed=completed,
        escalated=escalated,
        total_cost=sum(all_costs),
        satisfaction_scores=all_satisfaction,
        avg_human_time_min=human_baseline_min,
        avg_agent_time_min=avg_agent_time
    )
    
    return {
        "level_1": {
            "avg_tool_precision": statistics.mean(
                [1.0 for r in level_1_results if r.output_valid]
            ),
            "avg_latency_ms": statistics.mean([r.latency_ms for r in level_1_results])
        },
        "level_2": {
            "e2e_success_rate": completed / max(total, 1),
            "avg_step_efficiency": statistics.mean(
                [s.step_efficiency for s in level_2_results]
            )
        },
        "level_3": system_metrics.__dict__
    }
```

## Usage

```python
# Define test cases
test_cases = [
    {
        "steps": [
            {"action": "lookup_customer", "expected": "found",
             "expected_params": {"customer_id": "12345"}},
            {"action": "check_balance", "expected": "sufficient"},
            {"action": "approve_payment", "expected": "approved"},
        ],
        "satisfaction": 4.5
    }
]

# Run evaluation
results = run_eval_pipeline(test_cases, your_agent_function)
print(json.dumps(results, indent=2))
```

---

*Part of Zhongpu Consulting's AI Agent Operations Framework. [More resources](https://chengduman.github.io/zhongpu-consulting-advisory/)*
