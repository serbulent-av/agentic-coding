#!/usr/bin/env bash
# Local LLM coding benchmark driver (single H100, vLLM + EvalPlus)
# Runs each model on HumanEval+ and MBPP+ (greedy pass@1), then frees weights.
set -uo pipefail

cd /home/serbulentunsal/agentic-bench
export PATH="$HOME/.local/bin:$PATH"
export HF_HOME=/home/serbulentunsal/agentic-bench/hf
export VLLM_LOGGING_LEVEL=WARNING
export TOKENIZERS_PARALLELISM=false
PY=./.venv/bin/python

mkdir -p results logs evalplus_results
PROG=logs/progress.log
SUMMARY=results/summary.tsv
[ -f "$SUMMARY" ] || echo -e "model\tdataset\tbase_pass@1\tplus_pass@1" > "$SUMMARY"

log(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$PROG"; }

# hf_id | shortname  (ordered: cached phi-4 first, then ascending size)
MODELS=(
  "microsoft/phi-4|phi-4"
  "google/gemma-4-26B-A4B-it|gemma-4-26B-A4B"
  "Qwen/Qwen3-Coder-30B-A3B-Instruct|Qwen3-Coder-30B-A3B"
  "zai-org/GLM-4.7-Flash|GLM-4.7-Flash"
  "google/gemma-4-31B-it|gemma-4-31B"
  "Qwen/Qwen2.5-Coder-32B-Instruct|Qwen2.5-Coder-32B"
)

run_ds(){
  local id="$1" short="$2" ds="$3"
  local jf="evalplus_results/${ds}/$(echo "$id" | sed 's#/#--#g')_vllm_temp_0.0.jsonl"
  log "START codegen  $short / $ds"
  if ! $PY -m evalplus.codegen "$id" "$ds" --backend vllm --greedy \
        --trust_remote_code True --tp 1 --root evalplus_results >> "logs/${short}.${ds}.log" 2>&1; then
    log "FAILED codegen $short / $ds (see logs/${short}.${ds}.log)"
    echo -e "${short}\t${ds}\tCODEGEN_FAILED\tCODEGEN_FAILED" >> "$SUMMARY"
    return 1
  fi
  log "START evaluate $short / $ds"
  $PY -m evalplus.evaluate "$ds" --samples "$jf" > "results/${short}.${ds}.txt" 2>> "logs/${short}.${ds}.log"
  # parse the two pass@1 values (base line first, plus line second)
  mapfile -t P < <(grep -E '^pass@1' "results/${short}.${ds}.txt" | grep -oE '[0-9]+\.[0-9]+')
  local base="${P[0]:-NA}" plus="${P[1]:-NA}"
  echo -e "${short}\t${ds}\t${base}\t${plus}" >> "$SUMMARY"
  log "DONE  $short / $ds  base=${base} plus=${plus}"
}

free_weights(){
  local id="$1" short="$2"
  rm -rf "hf/hub/models--$(echo "$id" | sed 's#/#--#g')"
  log "CLEANED $short weights; free disk: $(df -h / | awk 'NR==2{print $4}')"
}

log "===== BENCH RUN START ($(nvidia-smi --query-gpu=name --format=csv,noheader)) ====="
for m in "${MODELS[@]}"; do
  IFS='|' read -r id short <<< "$m"
  t0=$(date +%s)
  log "########## MODEL: $short ($id) ##########"
  run_ds "$id" "$short" humaneval
  run_ds "$id" "$short" mbpp
  free_weights "$id" "$short"
  log "##### $short total $(( ($(date +%s)-t0)/60 )) min #####"
done
log "===== BENCH RUN COMPLETE ====="
