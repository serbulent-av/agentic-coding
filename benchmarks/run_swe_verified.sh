#!/usr/bin/env bash
# SWE-bench Verified (50-instance seeded subset) on local models via mini-swe-agent + vLLM.
# Spot-safe: chunked (agent->eval->prune), resumable, pushes after every chunk.
set -uo pipefail
cd /home/serbulentunsal/agentic-bench
export PATH="$HOME/.local/bin:$PATH"
export HF_HOME=/home/serbulentunsal/agentic-bench/hf
export VLLM_LOGGING_LEVEL=WARNING
export TOKENIZERS_PARALLELISM=false
export OPENAI_API_KEY=dummy
export MSWEA_COST_TRACKING=ignore_errors
PY=./.venv/bin/python
BASE=repo/benchmarks/agentic-runs/swe-verified
SUMMARY=$BASE/summary.tsv
PROG=logs/swe.progress.log
mkdir -p "$BASE" logs
[ -f "$SUMMARY" ] || printf "model\tresolved\tsubmitted\tempty_patch\terrors\n" > "$SUMMARY"
log(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$PROG"; }
ckpt(){ bash /home/serbulentunsal/agentic-bench/checkpoint_push.sh "$1" >/dev/null 2>&1 || true; }

# id|short|gpu_util|workers|extra_serve_args
MODELS=(
  "microsoft/phi-4|phi-4|0.90|4|"
  "google/gemma-4-26B-A4B-it|gemma-4-26B-A4B|0.90|4|"
  "Qwen/Qwen3-Coder-30B-A3B-Instruct|Qwen3-Coder-30B-A3B|0.90|3|--kv-cache-dtype fp8"
  "zai-org/GLM-4.7-Flash|GLM-4.7-Flash|0.92|2|--kv-cache-dtype fp8 --enforce-eager"
  "google/gemma-4-31B-it|gemma-4-31B|0.92|1|--kv-cache-dtype fp8 --enforce-eager"
  "Qwen/Qwen2.5-Coder-32B-Instruct|Qwen2.5-Coder-32B|0.92|1|--kv-cache-dtype fp8 --enforce-eager"
)

start_server(){ # id short util extra
  local id="$1" short="$2" util="$3" extra="$4"
  pkill -f "vllm serve" 2>/dev/null; sleep 4
  setsid nohup ./.venv/bin/vllm serve "$id" --port 8000 --max-model-len 16384 \
    --gpu-memory-utilization "$util" --trust-remote-code --served-model-name "$short" $extra \
    > "logs/serve_${short}.log" 2>&1 < /dev/null &
  for i in $(seq 1 120); do  # up to ~20 min for download+load
    [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null)" = "200" ] && return 0
    sleep 10
  done
  return 1
}

run_model(){
  local id="$1" short="$2" util="$3" workers="$4" extra="$5"
  local out="$BASE/$short"; mkdir -p "$out"
  if grep -qP "^${short}\t[0-9]" "$SUMMARY" 2>/dev/null; then log "SKIP $short (already in summary)"; return; fi
  log "########## $short ##########"
  log "$short: starting vLLM (util=$util workers=$workers $extra)"
  if ! start_server "$id" "$short" "$util" "$extra"; then
    log "$short: SERVE FAILED (see logs/serve_${short}.log)"
    printf "%s\tSERVE_FAILED\t-\t-\t-\n" "$short" >> "$SUMMARY"; ckpt "swe: $short serve failed"; return
  fi
  log "$short: server healthy"
  for ci in 0 1 2 3 4; do
    local rep="$out/openai__${short}.${short}_c${ci}.json"
    [ -f "$rep" ] && { log "$short chunk $ci: already evaluated, skip"; continue; }
    local ids; ids=$(tr '\n' ' ' < "$BASE/chunk_${ci}.txt")
    local rgx; rgx="($(paste -sd'|' "$BASE/chunk_${ci}.txt"))"
    log "$short chunk $ci: agent on 10 instances"
    $PY -m minisweagent.run.benchmarks.swebench --subset verified --split test \
      --filter "$rgx" -m "openai/${short}" --model-class litellm_textbased -c swebench_backticks.yaml \
      -c model.model_kwargs.api_base=http://localhost:8000/v1 \
      -c model.model_kwargs.temperature=0 -c agent.step_limit=40 -w "$workers" \
      -o "$out" >> "logs/${short}.agent.log" 2>&1 || log "$short chunk $ci: agent returned nonzero"
    log "$short chunk $ci: evaluating"
    $PY -m swebench.harness.run_evaluation -d princeton-nlp/SWE-bench_Verified -s test \
      -p "$out/preds.json" --instance_ids $ids --run_id "${short}_c${ci}" \
      --max_workers 4 --cache_level base --clean True --report_dir "$out" >> "logs/${short}.eval.log" 2>&1 || log "$short chunk $ci: eval returned nonzero"
    docker container prune -f >/dev/null 2>&1; docker image prune -af >/dev/null 2>&1
    log "$short chunk $ci: done; disk $(df -h / | awk 'NR==2{print $4}')"
    ckpt "swe: $short chunk $ci done"
  done
  # aggregate across chunk reports
  $PY - "$out" "$short" <<'PY' >> "$PROG" 2>&1
import sys, json, glob, os
out, short = sys.argv[1], sys.argv[2]
res=sub=emp=err=0
for f in glob.glob(f"{out}/openai__{short}.{short}_c*.json"):
    d=json.load(open(f)); res+=d.get("resolved_instances",0); sub+=d.get("submitted_instances",0)
    emp+=d.get("empty_patch_instances",0); err+=d.get("error_instances",0)
open(f"{out}/AGG.tsv","w").write(f"{short}\t{res}\t{sub}\t{emp}\t{err}\n")
print(f"[AGG] {short}: resolved {res}/{sub} (empty {emp}, err {err})")
PY
  cat "$out/AGG.tsv" >> "$SUMMARY"
  pkill -f "vllm serve" 2>/dev/null; sleep 4
  rm -rf "hf/hub/models--$(echo "$id" | sed 's#/#--#g')"
  docker image prune -af >/dev/null 2>&1
  log "$short: COMPLETE; weights cleaned; disk $(df -h / | awk 'NR==2{print $4}')"
  ckpt "swe: $short complete"
}

log "===== SWE-bench Verified (50, seed=0) RUN START ====="
for m in "${MODELS[@]}"; do
  IFS='|' read -r id short util workers extra <<< "$m"
  run_model "$id" "$short" "$util" "$workers" "$extra"
done
log "===== RUN COMPLETE ====="
ckpt "swe: full run complete"
