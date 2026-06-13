#!/usr/bin/env python3
"""Strategy C: Opus-4.8 plan -> local model implements -> Opus reviews (md handoff) -> revise, <=3 rounds.
Reuses Strategy B's plan as the round-1 input, so C = B + review loop (isolates the loop's effect).
Reviewer sees ONLY problem_statement + plan + the candidate patch (no gold/test) -> leak-free.
Same 12 pilot instances + same models as baseline/B for a clean 3-way comparison.
Agent: mini-swe-agent (text/backticks) on vLLM; eval: official swebench. Spot-safe (artifacts on disk)."""
import json, os, subprocess, time, sys, shutil
from datasets import load_dataset, Dataset
sys.path.insert(0, "/home/serbulentunsal/agentic-bench")
import opus_client

ROOT = "/home/serbulentunsal/agentic-bench"
BASE = f"{ROOT}/repo/benchmarks/agentic-runs/swe-c"
HAND = f"{BASE}/handoff"
ROUNDS = 3
PY = f"{ROOT}/.venv/bin/python"
os.makedirs(HAND, exist_ok=True)
PILOT = [l.strip() for l in open(f"{ROOT}/repo/benchmarks/agentic-runs/swe-verified/pilot_ids.txt")]
PLANS = {json.loads(l)["instance_id"]: json.loads(l)["plan"]
         for l in open(f"{ROOT}/repo/benchmarks/agentic-runs/swe-verified/plans_pilot.jsonl")}
OFFICIAL = {r["instance_id"]: r for r in load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
            if r["instance_id"] in set(PILOT)}
MODELS = [("microsoft/phi-4","phi-4","0.90","4",""),
          ("google/gemma-4-31B-it","gemma-4-31B","0.92","1","--kv-cache-dtype fp8 --enforce-eager")]
ENV = {**os.environ, "PATH": f"{os.path.expanduser('~')}/.local/bin:"+os.environ["PATH"],
       "HF_HOME": f"{ROOT}/hf", "VLLM_LOGGING_LEVEL":"WARNING", "OPENAI_API_KEY":"dummy",
       "MSWEA_COST_TRACKING":"ignore_errors", "TOKENIZERS_PARALLELISM":"false"}

def log(m): 
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)
    open(f"{ROOT}/logs/swe_c.progress.log","a").write(f"[{time.strftime('%H:%M:%S')}] {m}\n")
def push(m): subprocess.run(["bash", f"{ROOT}/checkpoint_push.sh", m], cwd=ROOT)

def serve(mid, short, util, extra):
    subprocess.run("pkill -f 'vllm serve'", shell=True); time.sleep(4)
    cmd = (f"setsid nohup {ROOT}/.venv/bin/vllm serve {mid} --port 8000 --max-model-len 16384 "
           f"--gpu-memory-utilization {util} --trust-remote-code --served-model-name {short} {extra} "
           f"> {ROOT}/logs/serve_{short}_c.log 2>&1 < /dev/null &")
    subprocess.run(cmd, shell=True, env=ENV)
    import requests
    for _ in range(120):
        try:
            if requests.get("http://localhost:8000/health", timeout=5).status_code == 200: return True
        except Exception: pass
        time.sleep(10)
    return False

PLAN_BLOCK = ("\n\n---\n## Implementation plan (from a senior Opus 4.8 planner — follow these steps)\n{plan}\n---\n")
REVISE_BLOCK = ("\n\n---\n## YOUR PREVIOUS ATTEMPT WAS REVIEWED\nYour previous patch:\n```diff\n{patch}\n```\n"
                "A senior reviewer (Opus 4.8) gave this feedback — address ALL of it:\n{review}\n"
                "Produce a corrected, complete solution.\n---\n")

def run_agent(rows, short, workers, outdir):
    os.makedirs(outdir, exist_ok=True)
    dsdir = f"{outdir}/ds"; shutil.rmtree(dsdir, ignore_errors=True); os.makedirs(dsdir)
    Dataset.from_list(rows).to_parquet(f"{dsdir}/test-00000-of-00001.parquet")
    cmd = [PY, "-m", "minisweagent.run.benchmarks.swebench", "--subset", dsdir, "--split", "test",
           "--redo-existing", "-m", f"openai/{short}", "--model-class", "litellm_textbased",
           "-c", "swebench_backticks.yaml", "-c", "model.model_kwargs.api_base=http://localhost:8000/v1",
           "-c", "model.model_kwargs.temperature=0", "-c", "agent.step_limit=30", "-w", str(workers), "-o", outdir]
    subprocess.run(cmd, cwd=ROOT, env=ENV,
                   stdout=open(f"{ROOT}/logs/{short}_c.agent.log","a"), stderr=subprocess.STDOUT)
    return json.load(open(f"{outdir}/preds.json"))

def opus_review(iid, patch):
    sys_p = ("You are a meticulous senior software engineer reviewing a junior's patch for a real GitHub issue. "
             "You can see only the issue and the candidate patch (no hidden tests). Decide if the patch fully and "
             "correctly resolves the issue. Reply with FIRST line exactly 'VERDICT: APPROVED' or 'VERDICT: REVISE'. "
             "If REVISE, follow with concise, specific, actionable feedback (root cause, exact file/function, what to "
             "change, edge cases). Do NOT write the full patch yourself; guide the junior.")
    usr = f"# Issue\n{OFFICIAL[iid]['problem_statement']}\n\n# Plan given\n{PLANS[iid]}\n\n# Candidate patch\n```diff\n{patch or '(empty - no patch produced)'}\n```"
    out = opus_client.chat([{"role":"system","content":sys_p},{"role":"user","content":usr}], max_tokens=1200)
    approved = out.strip().upper().startswith("VERDICT: APPROVED")
    return approved, out

def main():
    sumf = f"{BASE}/summary_c.tsv"
    if not os.path.exists(sumf): open(sumf,"w").write("model\tresolved\ttotal\tpass@1_pct\tresolved_ids\trounds_used\n")
    for mid, short, util, workers, extra in MODELS:
        if any(l.startswith(short+"\t") for l in open(sumf) if "\t" in l): log(f"skip {short} (done)"); continue
        log(f"########## STRATEGY C: {short} ##########")
        if not serve(mid, short, util, extra): log(f"{short} SERVE FAILED"); continue
        active = list(PILOT); final = {}; prev = {}; rev = {}; rounds_used = {i:0 for i in PILOT}
        for r in range(1, ROUNDS+1):
            if not active: break
            log(f"{short} round {r}: implementing {len(active)} instances")
            rows = []
            for iid in active:
                row = dict(OFFICIAL[iid]); task = row["problem_statement"] + PLAN_BLOCK.format(plan=PLANS[iid])
                if r > 1: task += REVISE_BLOCK.format(patch=prev[iid][:4000], review=rev[iid])
                row["problem_statement"] = task; rows.append(row)
                open(f"{HAND}/{short}__{iid}__round{r}_task.md","w").write(task)
            preds = run_agent(rows, short, workers, f"{BASE}/{short}/round{r}")
            still = []
            for iid in active:
                patch = preds.get(iid, {}).get("model_patch", "")
                final[iid] = patch; rounds_used[iid] = r
                open(f"{HAND}/{short}__{iid}__round{r}_patch.diff","w").write(patch or "(empty)")
                log(f"{short} round {r}: reviewing {iid}")
                approved, review = opus_review(iid, patch)
                open(f"{HAND}/{short}__{iid}__round{r}_review.md","w").write(review)
                if approved or r == ROUNDS:
                    log(f"  {iid}: {'APPROVED' if approved else 'max rounds'} -> final")
                else:
                    prev[iid] = patch; rev[iid] = review; still.append(iid)
            active = still
            push(f"swe-c {short} round {r}")
        subprocess.run("pkill -f 'vllm serve'", shell=True); time.sleep(4)
        # final preds + eval (official dataset)
        outp = f"{BASE}/{short}/preds_final.json"
        json.dump({i: {"instance_id": i, "model_name_or_path": f"openai/{short}", "model_patch": final.get(i,"")} for i in PILOT},
                  open(outp,"w"), indent=2)
        log(f"{short}: evaluating final patches")
        subprocess.run([PY, "-m", "swebench.harness.run_evaluation", "-d", "princeton-nlp/SWE-bench_Verified",
                        "-s", "test", "-p", outp, "--instance_ids", *PILOT, "--run_id", f"{short}_c",
                        "--max_workers", "4", "--cache_level", "base", "--clean", "True"],
                       cwd=ROOT, env=ENV, stdout=open(f"{ROOT}/logs/{short}_c.eval.log","a"), stderr=subprocess.STDOUT)
        subprocess.run("docker image prune -af; docker container prune -f", shell=True)
        rep = f"{ROOT}/openai__{short}.{short}_c.json"; d = json.load(open(rep))
        res = d["resolved_instances"]; rids = d.get("resolved_ids", [])
        open(sumf,"a").write(f"{short}\t{res}\t12\t{100*res/12:.1f}\t{','.join(rids)}\t{json.dumps(rounds_used)}\n")
        subprocess.run(f"rm -rf {ROOT}/hf/hub/models--{mid.replace('/','--')}", shell=True)
        log(f"{short} STRATEGY C COMPLETE: resolved {res}/12  {rids}")
        push(f"swe-c {short} complete")
    log("===== STRATEGY C COMPLETE ====="); push("swe-c complete")

if __name__ == "__main__":
    main()
