// sandbox-run — wrapper invoked via --subagents-workflow-file so the
// team-pipeline workflow starts with zero model involvement. The CLI flag
// cannot pass args, so the sandbox test args are baked in here.

export const meta = {
  name: 'sandbox-run',
  description: 'Run team-pipeline with the fixed docker-sandbox test args',
};

const result = await workflow('team-pipeline', {
  task: 'add word_count(text) to textstats.py plus plain-assert test_textstats.py printing OK',
  files: ['/tmp/team-sandbox-proj/textstats.py', '/tmp/team-sandbox-proj/test_textstats.py'],
  verify: 'cd /tmp/team-sandbox-proj && python3 test_textstats.py',
});

return result;
