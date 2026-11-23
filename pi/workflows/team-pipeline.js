// team-pipeline — deterministic Plan -> Implement -> Review -> Fix pipeline for
// the agentic-coding team (lange, philipe, sohne, gerald, optionally breguet).

export const meta = {
  name: 'team-pipeline',
  description: 'Plan, implement, adversarially review, and fix a task with the agentic-coding team',
  phases: [
    { title: 'Plan', detail: 'lange drafts acceptance criteria' },
    { title: 'Implement', detail: 'philipe builds, gated by the verify command' },
    { title: 'Review', detail: 'sohne and gerald review in parallel' },
    { title: 'Fix', detail: 'philipe addresses findings, reviewers re-check' },
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

// --- Plan ---
phase('Plan');
let planSummary = '(planning skipped)';
if (args.skipPlan) {
  log('Plan phase skipped (args.skipPlan) — implementing directly from the task');
} else {
  log('Planning with lange');
  planSummary = await agent(
    boundary + '\n\nPlan (do NOT implement) this task:\n' + task +
    '\n\nFiles in scope: ' + fileList +
    '\n\nReturn a concise plan: ordered implementation steps and acceptance criteria.',
    { label: 'plan', agentType: 'lange' }
  );
  if (planSummary === null) {
    planSummary = '(lange produced no plan — philipe will plan inline)';
    log('Plan agent returned null; continuing without a written plan');
  }
}

// --- Implement ---
phase('Implement');
log('Implementing with philipe');
const implPrompt =
  boundary + '\n\nImplement this task:\n' + task +
  '\n\nPlan / acceptance criteria:\n' + planSummary +
  (verify ? '\n\nVerification command (MUST pass): `' + verify + '`' : '') +
  '\n\nReturn a short summary of what you changed and the verification result.';
const implOpts = { label: 'impl', agentType: 'philipe' };
if (verify) implOpts.gate = verify;
let implResult = await agent(implPrompt, implOpts);
let gateOk = true; // non-null impl with a gate means the gate passed
if (implResult === null) {
  if (verify) {
    const why = typeof agentError === 'function' ? agentError('impl') : null;
    log('Implementation failed' + (why ? ' (' + why + ')' : ' — gate `' + verify + '` failed') + ' — resuming philipe to fix it');
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
    log('philipe returned null during implementation');
  }
}

// --- Review (reused by the fix loop) ---
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
  const thunks = [
    make('sohne', 'Review for quality, simplicity, and documentation: over-engineering, readability, docs.'),
    make('gerald', 'Review adversarially for correctness: bugs, edge cases, plan deviations, security risks.'),
  ];
  if (args.bio) {
    thunks.push(make('breguet', 'Review the molecular-dynamics / free-energy aspects: physics correctness, units, protocols.'));
  }
  return thunks;
}

function collect(results) {
  const reviews = {};
  const names = args.bio ? ['sohne', 'gerald', 'breguet'] : ['sohne', 'gerald'];
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
log('Reviewing with sohne and gerald' + (args.bio ? ' and breguet' : ''));
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
    { label: 'impl', resume: 'impl' }
  );
  if (fixResult === null) log('philipe returned null during fix round ' + rounds);
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
};
