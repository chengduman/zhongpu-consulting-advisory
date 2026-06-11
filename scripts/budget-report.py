#!/usr/bin/env python3
"""
budget-report.py — 中普咨询 DeepSeek 预算自动追踪脚本

功能：
  1. 尝试通过 DeepSeek API 查询账户余额
  2. 如 API 不可用，从本地历史记录文件推断余额
  3. 输出简要预算报告（stdout），同时追加日志到本地记录

运行方式：
  python scripts/budget-report.py

依赖：requests（pip install requests）
配置：环境变量 DEEPSEEK_API_KEY，或编辑下方 DEEPSEEK_API_KEY 占位符
"""

import os
import sys
import json
import csv
import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# ─── 配置 ────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
BUDGET_LOG_DIR = PROJECT_DIR / "data" / "budget"
BUDGET_LOG_FILE = BUDGET_LOG_DIR / "deepseek_balance.csv"
BUDGET_HISTORY_FILE = BUDGET_LOG_DIR / "balance_history.json"

# DeepSeek API 配置
DEEPSEEK_API_URL = "https://api.deepseek.com/user/balance"
# 优先从环境变量读取，否则用空（首次使用需设置）
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

# 默认预算配置（如查不到任何记录时的初始假设）
DEFAULT_MONTHLY_BUDGET = 100.0  # 月度预算 USD
DEFAULT_STARTING_BALANCE = 100.0

# DeepSeek 模型定价（每百万 token，USD）
DEEPSEEK_PRICING = {
    "deepseek-chat":   {"input": 0.14, "output": 0.28},
    "deepseek-coder":  {"input": 0.14, "output": 0.28},
    "deepseek-r1":     {"input": 0.55, "output": 2.19},
}

# 估算的内部 Token 消耗量（从实际运营记录推算）
# 可根据实际数据更新
ESTIMATED_USAGE = {
    "daily_avg_input_tokens": 150000,
    "daily_avg_output_tokens": 50000,
    "monthly_est_cost": 0.0,  # 自动计算
}


# ─── 辅助函数 ─────────────────────────────────────────────

def _ensure_log_dir():
    """确保预算日志目录存在"""
    BUDGET_LOG_DIR.mkdir(parents=True, exist_ok=True)


def _estimate_daily_cost(input_tokens: int, output_tokens: int, model="deepseek-chat") -> float:
    """估算每日 token 消耗费用（USD）"""
    pricing = DEEPSEEK_PRICING.get(model, DEEPSEEK_PRICING["deepseek-chat"])
    cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
    return round(cost, 4)


def _load_local_history() -> Dict[str, Any]:
    """加载本地余额历史记录"""
    if BUDGET_HISTORY_FILE.exists():
        try:
            with open(BUDGET_HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "last_balance": DEFAULT_STARTING_BALANCE,
        "last_check": None,
        "total_spent": 0.0,
        "monthly_budget": DEFAULT_MONTHLY_BUDGET,
    }


def _save_local_history(history: Dict[str, Any]):
    """保存本地余额历史记录"""
    _ensure_log_dir()
    with open(BUDGET_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def _append_csv_log(date: str, balance: Optional[float], spent: float,
                     source: str, status: str, note: str = ""):
    """追加一条 CSV 日志"""
    _ensure_log_dir()
    file_exists = BUDGET_LOG_FILE.exists()
    with open(BUDGET_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "balance_usd", "spent_today_usd",
                             "source", "status", "note"])
        writer.writerow([date,
                         f"{balance:.4f}" if balance is not None else "N/A",
                         f"{spent:.4f}", source, status, note])


# ─── API 查询 ──────────────────────────────────────────────

def check_balance_via_api() -> Optional[float]:
    """
    通过 DeepSeek API 查询账户余额。
    需设置 DEEPSEEK_API_KEY 环境变量。
    """
    if not DEEPSEEK_API_KEY:
        return None

    try:
        import requests
    except ImportError:
        print("[WARN] requests 未安装，跳过 API 查询。请运行: pip install requests")
        return None

    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Accept": "application/json",
        }
        resp = requests.get(DEEPSEEK_API_URL, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # DeepSeek balance API 返回格式: {"balance": 123.45, "status": "ok"}
            balance = data.get("balance")
            if balance is not None:
                return float(balance)
        else:
            print(f"[WARN] DeepSeek API 返回异常: HTTP {resp.status_code}")
    except requests.RequestException as e:
        print(f"[WARN] 无法连接 DeepSeek API: {e}")

    return None


# ─── 本地推断 ──────────────────────────────────────────────

def infer_balance_from_history() -> Dict[str, Any]:
    """
    从本地历史记录推断当前余额。
    使用最后记录的余额减去估算的消耗。
    """
    history = _load_local_history()
    last_balance = history.get("last_balance", DEFAULT_STARTING_BALANCE)
    last_check = history.get("last_check")
    total_spent = history.get("total_spent", 0.0)

    # 估算每日消耗
    est_daily = _estimate_daily_cost(
        ESTIMATED_USAGE["daily_avg_input_tokens"],
        ESTIMATED_USAGE["daily_avg_output_tokens"],
    )

    # 计算距上次检查的天数
    if last_check:
        try:
            last_dt = datetime.datetime.fromisoformat(last_check)
            days_passed = (datetime.datetime.now() - last_dt).total_seconds() / 86400.0
            days_passed = max(0, days_passed)
        except (ValueError, TypeError):
            days_passed = 0
    else:
        days_passed = 0

    estimated_spent_since_check = round(est_daily * days_passed, 4)
    inferred_balance = round(last_balance - estimated_spent_since_check, 4)

    # 预算剩余比例
    monthly_budget = history.get("monthly_budget", DEFAULT_MONTHLY_BUDGET)
    budget_remaining_pct = round(
        (inferred_balance / monthly_budget) * 100 if monthly_budget > 0 else 0, 1
    )

    return {
        "current_balance": max(inferred_balance, 0),
        "estimated_daily_cost": est_daily,
        "days_since_last_check": round(days_passed, 1),
        "estimated_spent_since_check": estimated_spent_since_check,
        "monthly_budget": monthly_budget,
        "budget_remaining_pct": budget_remaining_pct,
        "total_spent": round(total_spent + estimated_spent_since_check, 2),
        "source": "inferred",
    }


# ─── 主流程 ────────────────────────────────────────────────

def generate_report() -> Dict[str, Any]:
    """生成预算报告"""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 56)
    print("  中普咨询 · DeepSeek 预算追踪报告")
    print(f"  {date_str}")
    print("=" * 56)

    # 步骤 1: 尝试 API 查询
    print("\n[1/3] 正在查询 DeepSeek 账户余额...")
    balance = check_balance_via_api()

    if balance is not None:
        print(f"  ✅ API 查询成功: 余额 ${balance:.4f}")
        source = "api"
        status = "ok"
    else:
        print("  ⚠️  API 不可用或无 API Key，使用本地记录推断")
        result = infer_balance_from_history()
        balance = result["current_balance"]
        source = "inferred"
        status = "inferred"
        print(f"  📊 本地推断余额: ${balance:.4f}")

    # 步骤 2: 计算当日消耗估算
    print("\n[2/3] 计算消耗估算...")
    est_daily = _estimate_daily_cost(
        ESTIMATED_USAGE["daily_avg_input_tokens"],
        ESTIMATED_USAGE["daily_avg_output_tokens"],
    )
    print(f"  📈 预估日消耗: ${est_daily:.4f}")
    print(f"     (输入: {ESTIMATED_USAGE['daily_avg_input_tokens']:,} tokens, "
          f"输出: {ESTIMATED_USAGE['daily_avg_output_tokens']:,} tokens)")

    # 步骤 3: 预算状态评估
    print("\n[3/3] 预算状态评估...")
    history = _load_local_history()
    monthly_budget = history.get("monthly_budget", DEFAULT_MONTHLY_BUDGET)
    budget_pct = round((balance / monthly_budget) * 100, 1) if monthly_budget > 0 else 0

    if budget_pct >= 50:
        level = "🟢 充足"
        action = "无需操作"
    elif budget_pct >= 20:
        level = "🟡 注意"
        action = "建议关注消耗趋势，评估是否需要追加预算"
    elif budget_pct >= 10:
        level = "🟠 警告"
        action = "余额较低，建议减少非必要调用或追加预算"
    else:
        level = "🔴 紧急"
        action = "余额即将耗尽！请立即处理"

    print(f"  月度预算: ${monthly_budget:.2f}")
    print(f"  当前余额: ${balance:.4f} ({budget_pct}%)")
    print(f"  状态:     {level}")
    print(f"  建议:     {action}")

    # 预计可用天数
    if est_daily > 0:
        days_left = round(balance / est_daily, 1)
        print(f"  预计可用: {days_left} 天（按当前消耗速率）")

    # 保存历史记录
    print(f"\n  📝 正在保存日志...")
    history["last_balance"] = balance
    history["last_check"] = now.isoformat()
    history["total_spent"] = history.get("total_spent", 0) + est_daily
    _save_local_history(history)
    _append_csv_log(now.strftime("%Y-%m-%d"), balance, est_daily, source, status)

    print(f"  ✅ 日志已保存到 {BUDGET_LOG_FILE}")
    print("=" * 56)

    return {
        "date": date_str,
        "balance": balance,
        "estimated_daily_cost": est_daily,
        "budget_remaining_pct": budget_pct,
        "source": source,
        "status": status,
        "action": action,
    }


# ─── 入口 ──────────────────────────────────────────────────

if __name__ == "__main__":
    report = generate_report()
    sys.exit(0)
