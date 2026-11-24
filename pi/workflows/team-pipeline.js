// team-pipeline — deterministic Plan -> Plan Gate -> Implement -> Review -> Fix
// pipeline for the agentic-coding team (lange, gerald, philipe/breguet, sohne).
//
// Hard gates: lange ALWAYS drafts the plan (no skipping), then gerald gates the
// plan adversarially (at most 2 plan-revision rounds, then BLOCKED). Only an
// APPROVEd plan reaches implementation. philipe implements, EXCEPT when
// args.bio is set — then breguet implements (breguet is never a reviewer).
// Code review is always sohne + gerald. Gate sequence:
// lange → gerald (plan gate) → philipe/breguet (implement) → sohne + gerald (code review)

export const meta = {
  name: 'team-pipeline',
  description: 'Plan (always), gate the plan adversarially, implement, review, and fix a task with the agentic-coding team',
  phases: [
    { title: 'Plan', detail: 'lange ALWAYS drafts the plan' },
    { title: 'Plan Gate', detail: 'gerald approves the plan (at most 2 revision rounds)' },
    { title: 'Implement', detail: 'philipe builds (breguet when args.bio), gated by the verify command' },
    { title: 'Review', detail: 'sohne and gerald review in parallel' },
    { title: 'Fix', detail: 'implementer addresses findings, reviewers re-check' },
  ],
};

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['APPROVE', 'REQUEST_CHANGES'] },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['CRITICAL', 'MAJOR', 'MINOR'] },
          title: { type: 'string' },
          detail: { type: 'string' },
        },
        required: ['severity', 'title', 'detail'],
      },
    },
  },
  required: ['verdict', 'findings'],
};

// --- Validate args ---
// Models sometimes pass args as a JSON-encoded string instead of an object;
// accept and parse that form rather than failing the whole run.
if (typeof args === 'string') {
  try {
    args = JSON.parse(args);
  } catch (e) {
    throw new Error('team-pipeline: args was a string but not valid JSON: ' + e.message);
  }
}
const task = args && args.task;
const files = args && args.files;
if (typeof task !== 'string' || task.trim() === '') {
  throw new Error('team-pipeline: args.task must be a non-empty string');
}
if (!Array.isArray(files) || files.length === 0 || !files.every(f => typeof f === 'string')) {
  throw new Error('team-pipeline: args.files must be a non-empty array of strings');
}
const verify = typeof args.verify === 'string' && args.verify.trim() !== '' ? args.verify : null;
const fileList = files.join(', ');

const boundary =
  'You may ONLY modify files: ' + fileList +
  '. All agents share one working directory with other teams.';

const diffHint =
  'To see the changes: if this is a git repo run `git diff -- ' + fileList +
  '` (also `git status` for untracked files); otherwise read the files directly.';

function planGateBlocked(findings, planSummary) {
  log('Plan gate REJECTED — plan still not approved after the bounded revision rounds; returning BLOCKED');
  return {
    status: 'BLOCKED',
    files,
    planSummary,
    reviews: {},
    rounds: 0,
    openFindings: findings,
    gateOk: false,
    planGate: 'REJECTED',
  };
}

function gateFindings(verdict) {
  const open = [];
  if (verdict && Array.isArray(verdict.findings)) {
    for (const f of verdict.findings) open.push({ reviewer: 'gerald (plan gate)', severity: f.severity, title: f.title, detail: f.detail });
  }
  if (open.length === 0) {
    open.push({ reviewer: 'gerald (plan gate)', severity: 'MAJOR', title: 'Plan not approved', detail: 'Gerald did not approve the plan and gave no actionable findings' });
  }
  return open;
}

// --- Plan (lange ALWAYS runs — no skipping) ---
phase('Plan');
log('Planning with lange (mandatory — the plan phase is never skipped)');
const planPrompt =
  boundary + '\n\nPlan (do NOT implement) this task:\n' + task +
  '\n\nFiles in scope: ' + fileList +
  '\n\nReturn a concise plan: ordered implementation steps and acceptance criteria.';
let planSummary = await agent(planPrompt, { label: 'plan', agentType: 'lange' });
if (planSummary === null) {
  log('lange returned null for the initial plan; retrying once with a fresh dispatch');
  planSummary = await agent(planPrompt, { label: 'plan', agentType: 'lange' });
}

// --- Plan Gate (gerald reviews the plan; at most 2 revision rounds) ---
phase('Plan Gate');
const planGateLens =
  'Review this plan adversarially before any implementation begins: are the steps executable, ' +
  'are the acceptance criteria real, what assumptions or failure modes are unaddressed?' +
  (args.bio
    ? ' This is biophysics/MD/FEP work — also scrutinize the scientific claims and protocol: force field/water model choice, ensembles, equilibration, sampling, convergence and error reporting, reproducibility.'
    : '');
let gateVerdict = null;
if (planSummary === null) {
  log('No plan ever materialized from lange — plan gate cannot pass');
  return planGateBlocked(
    [{ reviewer: '(pipeline)', severity: 'MAJOR', title: 'No plan produced', detail: 'lange returned null for every planning attempt' }],
    '(no plan produced)');
}
for (let gateRound = 0; gateRound <= 2; gateRound++) {
  log('Plan gate round ' + (gateRound + 1) + ': gerald reviewing the plan');
  gateVerdict = await agent(
    boundary + '\n\nTask:\n' + task +
    '\n\nProposed plan:\n' + planSummary + '\n\n' + planGateLens +
    '\nReturn your verdict via the structured output tool.',
    { label: 'gate-r' + (gateRound + 1), agentType: 'gerald', schema: VERDICT_SCHEMA }
  );
  if (gateVerdict !== null && gateVerdict.verdict === 'APPROVE') {
    log('Plan gate APPROVED on round ' + (gateRound + 1));
    break;
  }
  if (gateRound === 2) {
    return planGateBlocked(gateFindings(gateVerdict), planSummary);
  }
  const findings = gateFindings(gateVerdict);
  log(gateVerdict === null
    ? 'Plan gate round ' + (gateRound + 1) + ' returned null verdict — sending plan back to lange'
    : 'Plan gate round ' + (gateRound + 1) + ': REQUEST_CHANGES — lange revises');
  const findingsText = findings.map((f, i) => (i + 1) + '. [' + f.severity + '] ' + f.title + ' — ' + f.detail).join('\n');
  const revised = await agent(
    boundary + '\n\nGerald rejected the plan for this task:\n' + task +
    '\n\nYour previous plan:\n' + planSummary +
    '\n\nPlan-gate findings to address:\n' + findingsText +
    '\n\nRevise the plan (do NOT implement). Return the full revised plan.',
    { label: 'plan', resume: 'plan' }
  );
  if (revised !== null) planSummary = revised;
  else log('lange returned null during plan revision; gerald re-reviews the unrevised plan');
}

// --- Implement (philipe, or breguet when args.bio) ---
phase('Implement');
const implType = args.bio ? 'breguet' : 'philipe';
log('Implementing with ' + implType);
const implPrompt =
  boundary + '\n\nImplement this task:\n' + task +
  '\n\nPlan / acceptance criteria:\n' + planSummary +
  (verify ? '\n\nVerification command (MUST pass): `' + verify + '`' : '') +
  '\n\nReturn a short summary of what you changed and the verification result.';
const implOpts = { label: 'impl', agentType: implType };
if (verify) implOpts.gate = verify;
let implResult = await agent(implPrompt, implOpts);
let gateOk = true; // non-null impl with a gate means the gate passed
if (implResult === null) {
  if (verify) {
    const why = typeof agentError === 'function' ? agentError('impl') : null;
    log('Implementation failed' + (why ? ' (' + why + ')' : ' — gate `' + verify + '` failed') + ' — resuming ' + implType + ' to fix it');
    implResult = await agent(
      boundary + '\n\nThe verification command `' + verify +
      '` is still failing. Find the cause and fix it.',
      { label: 'impl', resume: 'impl' }
    );
    const verified = await agent(
      boundary + '\n\nRun `' + verify + '` and report the result. Change nothing.',
      { label: 'verify', phase: 'Implement', gate: verify }
    );
    gateOk = verified !== null;
    log(verified === null ? 'Verification still failing after retry' : 'Verification passed');
  } else {
    log(implType + ' returned null during implementation');
  }
}

// --- Review (reused by the fix loop) — sohne + gerald ONLY ---
function reviewThunks(round) {
  const make = (agentType, lens) => () =>
    agent(
      boundary + '\n\nYou are reviewing round ' + round + ' of this task:\n' + task +
      '\n\nPlan / acceptance criteria:\n' + planSummary + '\n\n' + diffHint +
      (verify ? '\nVerification command: `' + verify + '` (run it if useful).' : '') +
      '\n\n' + lens +
      '\nReturn your verdict via the structured output tool.',
      { label: agentType + '-r' + round, phase: round === 1 ? 'Review' : 'Fix', agentType, schema: VERDICT_SCHEMA }
    );
  return [
    make('sohne', 'Review for quality, simplicity, and documentation: over-engineering, readability, docs.'),
    make('gerald', 'Review adversarially for correctness: bugs, edge cases, plan deviations, security risks.'),
  ];
}

function collect(results) {
  const reviews = {};
  const names = ['sohne', 'gerald'];
  results.forEach((r, i) => {
    if (r === null) log('Reviewer ' + names[i] + ' returned null (failed or skipped)');
    else reviews[names[i]] = r;
  });
  return reviews;
}

function openFindings(reviews) {
  const open = [];
  for (const name of Object.keys(reviews)) {
    const r = reviews[name];
    if (r && r.verdict === 'REQUEST_CHANGES' && Array.isArray(r.findings)) {
      for (const f of r.findings) open.push({ reviewer: name, severity: f.severity, title: f.title, detail: f.detail });
    }
  }
  return open;
}

phase('Review');
log('Reviewing with sohne and gerald');
let reviews = collect(await parallel(reviewThunks(1)));
let open = openFindings(reviews);
let rounds = 0;
const noVerdicts = Object.keys(reviews).length === 0;
if (noVerdicts) {
  open = [{ reviewer: '(pipeline)', severity: 'MAJOR', title: 'Review unavailable', detail: 'All reviewers returned null' }];
  log('All reviewers returned null in round 1 — cannot confirm quality');
}

// --- Fix loop: at most 2 rounds ---
while (!noVerdicts && open.length > 0 && rounds < 2) {
  rounds++;
  phase('Fix');
  log('Fix round ' + rounds + ': ' + open.length + ' open finding(s)');
  const findingsText = open.map((f, i) => (i + 1) + '. [' + f.severity + '] (' + f.reviewer + ') ' + f.title + ' — ' + f.detail).join('\n');
  const fixResult = await agent(
    boundary + '\n\nReviewers request changes on this task:\n' + task +
    '\n\nFix each finding:\n' + findingsText +
    (verify ? '\n\nVerification command (MUST still pass): `' + verify + '`' : '') +
    '\n\nReturn a short summary of the fixes.',
    { label: 'impl', agentType: implType, resume: 'impl' }
  );
  if (fixResult === null) log(implType + ' returned null during fix round ' + rounds);
  log('Re-reviewing after fix round ' + rounds);
  const prevOpen = open;
  const prevReviews = reviews;
  reviews = collect(await parallel(reviewThunks(rounds + 1)));
  if (Object.keys(reviews).length === 0) {
    log('Re-review round ' + (rounds + 1) + ' returned no valid verdicts — findings remain open');
    open = prevOpen;
    reviews = prevReviews;
    break;
  }
  open = openFindings(reviews);
}

const blockers = open.filter(f => f.severity === 'CRITICAL' || f.severity === 'MAJOR');
const status = blockers.length > 0 || !gateOk ? 'BLOCKED' : 'DONE';
log('Pipeline finished: ' + status + ' (' + blockers.length + ' open CRITICAL/MAJOR finding(s)' + (gateOk ? '' : '; verification gate failing') + ')');

return {
  status,
  files,
  planSummary,
  reviews,
  rounds,
  openFindings: open,
  gateOk,
  planGate: 'APPROVED',
};
