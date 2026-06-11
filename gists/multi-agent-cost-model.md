#!/usr/bin/env python3
"""
multi_agent_cost_model.py — Estimate and optimize multi-agent system costs.

This model helps you calculate the real cost of running a multi-agent system
before you build it. Supports tiered routing, caching, and batch processing.
"""

from dataclasses import dataclass
from typing import Optional

# ─── Pricing Data (June 2026) ───

MODEL_PRICING = {
    "gpt-4o":        {"input": 2.50,  "output": 10.00},
    "claude-opus-4": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4":{"input": 3.00,  "output": 15.00},
    "claude-haiku-3": {"input": 0.25,  "output": 1.25},
    "deepseek-chat":  {"input": 0.14,  "output": 0.28},
    "gemini-2.0-flash":{"input": 0.10, "output": 0.40},
    "llama-3-70b-tog": {"input": 0.90, "output": 0.90},  # Together AI
}

@dataclass
class AgentConfig:
    name: str
    model: str
    avg_input_tokens: int = 2000
    avg_output_tokens: int = 500
    requests_per_day: int = 1000
    cache_hit_rate: float = 0.0       # 0.0 - 1.0
    tiered_routing: bool = False      # route 70% to cheap model
    cheap_model: str = "deepseek-chat" 
    batch_discount: float = 0.0       # 0.0 - 0.5 (batch APIs)

@dataclass 
class CostReport:
    name: str
    daily: float
    monthly: float
    yearly: float
    savings_vs_default: float
    breakdown: dict

def estimate_agent_cost(cfg: AgentConfig) -> CostReport:
    """Estimate monthly cost for a single agent with optimizations."""
    
    pricing = MODEL_PRICING.get(cfg.model, {"input": 1.0, "output": 1.0})
    total_daily_tokens = (
        cfg.avg_input_tokens * cfg.requests_per_day +
        cfg.avg_output_tokens * cfg.requests_per_day
    )
    
    # Base cost (no optimizations)
    base_cost = (
        (cfg.avg_input_tokens * pricing["input"] / 1_000_000) +
        (cfg.avg_output_tokens * pricing["output"] / 1_000_000)
    ) * cfg.requests_per_day
    
    # Apply cache savings
    cache_factor = 1 - cfg.cache_hit_rate
    
    # Apply tiered routing
    if cfg.tiered_routing:
        cheap = MODEL_PRICING.get(cfg.cheap_model, {"input": 0.14, "output": 0.28})
        cheap_cost = (
            (cfg.avg_input_tokens * cheap["input"] / 1_000_000) +
            (cfg.avg_output_tokens * cheap["output"] / 1_000_000)
        ) * cfg.requests_per_day * 0.7  # 70% to cheap
        smart_cost = base_cost * 0.3     # 30% to main model
        tiered_cost = cheap_cost + smart_cost
        daily = tiered_cost * cache_factor * (1 - cfg.batch_discount)
    else:
        daily = base_cost * cache_factor * (1 - cfg.batch_discount)
    
    # Default cost (gpt-4o, no optimizations)
    default_pricing = MODEL_PRICING["gpt-4o"]
    default_daily = (
        (cfg.avg_input_tokens * default_pricing["input"] / 1_000_000) +
        (cfg.avg_output_tokens * default_pricing["output"] / 1_000_000)
    ) * cfg.requests_per_day
    
    return CostReport(
        name=cfg.name,
        daily=round(daily, 4),
        monthly=round(daily * 30, 2),
        yearly=round(daily * 365, 2),
        savings_vs_default=round((1 - daily / max(default_daily, 0.01)) * 100, 1),
        breakdown={
            "base_model": cfg.model,
            "requests/day": cfg.requests_per_day,
            "cache_hit_rate": f"{cfg.cache_hit_rate:.0%}",
            "tiered_routing": cfg.tiered_routing,
            "batch_discount": f"{cfg.batch_discount:.0%}",
        }
    )

# ─── Multi-Agent System Cost Estimator ───

def estimate_system_cost(agents: list[AgentConfig]) -> dict:
    """Estimate total cost for a multi-agent system."""
    results = [estimate_agent_cost(a) for a in agents]
    
    total_monthly = sum(r.monthly for r in results)
    default_monthly = 0
    for a in agents:
        d = AgentConfig(
            name=a.name, model="gpt-4o",
            avg_input_tokens=a.avg_input_tokens,
            avg_output_tokens=a.avg_output_tokens,
            requests_per_day=a.requests_per_day
        )
        default_monthly += estimate_agent_cost(d).monthly
    
    return {
        "agents": [r.__dict__ for r in results],
        "total_monthly": round(total_monthly, 2),
        "default_monthly": round(default_monthly, 2),
        "savings_pct": round((1 - total_monthly / max(default_monthly, 0.01)) * 100, 1),
        "annual": round(total_monthly * 12, 2),
        "recommendations": _generate_recommendations(results)
    }

def _generate_recommendations(results: list[CostReport]) -> list[str]:
    recs = []
    total_monthly = sum(r.monthly for r in results)
    
    if total_monthly > 500:
        recs.append("🔴 Consider semantic caching to reduce costs 30-50%")
    if total_monthly > 1000:
        recs.append("🔴 Evaluate batch API processing for non-urgent requests")
    if any(r.savings_vs_default < 30 for r in results):
        recs.append("🟡 Switch to tiered routing (70% cheap + 30% smart model)")
    if total_monthly < 100:
        recs.append("✅ System is cost-efficient. Focus on quality improvements.")
    
    return recs

# ─── Example Usage ───

if __name__ == "__main__":
    # Customer support system: 3 agents
    agents = [
        AgentConfig("Support Router", "deepseek-chat", 1500, 300, 2000),
        AgentConfig("KB Agent", "claude-haiku-3", 2000, 500, 1500, 
                    cache_hit_rate=0.4, tiered_routing=True),
        AgentConfig("Escalation Agent", "claude-sonnet-4", 3000, 800, 200,
                    cache_hit_rate=0.2),
    ]
    
    report = estimate_system_cost(agents)
    print("=== Multi-Agent Cost Report ===")
    for a in report["agents"]:
        print(f"  {a['name']:20s} ${a['monthly']:>7.2f}/mo (saves {a['savings_vs_default']}% vs GPT-4o)")
    print(f"\n  {'TOTAL':20s} ${report['total_monthly']:>7.2f}/mo")
    print(f"  {'Default (GPT-4o)':20s} ${report['default_monthly']:>7.2f}/mo")
    print(f"  {'Savings':20s} {report['savings_pct']}%")
    print(f"  {'Annual':20s} ${report['annual']:>7.2f}/yr")
    print("\nRecommendations:")
    for r in report["recommendations"]:
        print(f"  {r}")
