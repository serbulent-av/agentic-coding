#!/usr/bin/env bash
cd /home/serbulentunsal/agentic-bench
export PATH="$HOME/.local/bin:$PATH"
# wait for Strategy B (gemma) to finish
while ! grep -q "gemma-4-31B COMPLETE" logs/pilot_planned.progress.log 2>/dev/null; do sleep 30; done
echo "[chain] B done; freeing GPU and launching Strategy C $(date)" >> logs/chain_c.log
pkill -f "vllm serve" 2>/dev/null; sleep 6
setsid nohup ./.venv/bin/python run_strategy_c.py >> logs/run_c.out 2>&1 < /dev/null &
echo "[chain] Strategy C launched pid $!" >> logs/chain_c.log
