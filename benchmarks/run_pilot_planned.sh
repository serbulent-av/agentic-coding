#!/usr/bin/env bash
# PILOT: Opus-4.8-planned tasks, local model implements. 12 instances, phi-4 + gemma-4-31B.
# Agent reads planned_pilot (problem_statement + Opus plan); EVAL uses official dataset (no leak).
set -uo pipefail
cd /home/serbulentunsal/agentic-bench
export PATH="$HOME/.local/bin:$PATH"
export HF_HOME=/home/serbulentunsal/agentic-bench/hf
export VLLM_LOGGING_LEVEL=WARNING TOKENIZERS_PARALLELISM=false
export OPENAI_API_KEY=dummy MSWEA_COST_TRACKING=ignore_errors
PY=./.venv/bin/python
PLANNED=/home/serbulentunsal/agentic-bench/planned_pilot
BASE=repo/benchmarks/agentic-runs/swe-verified-planned
SUM=$BASE/summary_planned.tsv
PROG=logs/pilot_planned.progress.log
mkdir -p "$BASE" logs
[ -f "$SUM" ] || printf "model\tresolved\ttotal\tpass@1_pct\tempty\terrors\tresolved_ids\n" > "$SUM"
log(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$PROG"; }
ckpt(){ bash /home/serbulentunsal/agentic-bench/checkpoint_push.sh "$1" >/dev/null 2>&1 || true; }
IDS=$(tr '\n' ' ' < repo/benchmarks/agentic-runs/swe-verified/pilot_ids.txt)

# id|short|util|workers|extra
MODELS=(
  "microsoft/phi-4|phi-4|0.90|4|"
  "google/gemma-4-31B-it|gemma-4-31B|0.92|1|--kv-cache-dtype fp8 --enforce-eager"
)
serve(){ local id="$1" short="$2" util="$3" extra="$4"
  pkill -f "vllm serve" 2>/dev/null; sleep 4
  setsid nohup ./.venv/bin/vllm serve "$id" --port 8000 --max-model-len 16384 \
    --gpu-memory-utilization "$util" --trust-remote-code --served-model-name "$short" $extra \
    > "logs/serve_${short}_planned.log" 2>&1 < /dev/null &
  for i in $(seq 1 120); do
    [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null)" = "200" ] && return 0; sleep 10; done
  return 1; }

log "===== PILOT PLANNED RUN START (12 instances) ====="
for m in "${MODELS[@]}"; do
  IFS='|' read -r id short util workers extra <<< "$m"
  out="$BASE/$short"; mkdir -p "$out"
  rep="openai__${short}.${short}_planned.json"
  if grep -qP "^${short}\t[0-9]" "$SUM" 2>/dev/null; then log "skip $short (done)"; continue; fi
  log "$short: serving"; if ! serve "$id" "$short" "$util" "$extra"; then log "$short SERVE_FAILED"; printf "%s\tSERVE_FAILED\t-\t-\t-\t-\t-\n" "$short">>"$SUM"; ckpt "pilot $short serve failed"; continue; fi
  log "$short: agent on 12 planned instances"
  $PY -m minisweagent.run.benchmarks.swebench --subset "$PLANNED" --split test \
    -m "openai/${short}" --model-class litellm_textbased -c swebench_backticks.yaml \
    -c model.model_kwargs.api_base=http://localhost:8000/v1 \
    -c model.model_kwargs.temperature=0 -c agent.step_limit=40 -w "$workers" \
    -o "$out" >> "logs/${short}_planned.agent.log" 2>&1 || log "$short agent nonzero"
  log "$short: evaluating (official dataset)"
  $PY -m swebench.harness.run_evaluation -d princeton-nlp/SWE-bench_Verified -s test \
    -p "$out/preds.json" --instance_ids $IDS --run_id "${short}_planned" \
    --max_workers 4 --cache_level base --clean True >> "logs/${short}_planned.eval.log" 2>&1 || log "$short eval nonzero"
  docker container prune -f >/dev/null 2>&1; docker image prune -af >/dev/null 2>&1
  $PY - "$rep" "$short" "$SUM" <<'PYP'
import sys, json
rep, short, sumf = sys.argv[1], sys.argv[2], sys.argv[3]
d=json.load(open(rep))
res=d["resolved_instances"]; tot=d["completed_instances"]+d["empty_patch_instances"]+d["error_instances"]
ids=",".join(d.get("resolved_ids",[]))
open(sumf,"a").write(f"{short}\t{res}\t{tot}\t{100*res/tot if tot else 0:.1f}\t{d['empty_patch_instances']}\t{d['error_instances']}\t{ids}\n")
print(f"[PILOT] {short}: resolved {res}/{tot}  ids={ids}")
PYP
  pkill -f "vllm serve" 2>/dev/null; sleep 4
  rm -rf "hf/hub/models--$(echo "$id" | sed 's#/#--#g')"; docker image prune -af >/dev/null 2>&1
  log "$short COMPLETE; disk $(df -h / | awk 'NR==2{print $4}')"; ckpt "pilot $short planned done"
done
log "===== PILOT PLANNED COMPLETE ====="; ckpt "pilot planned complete"
