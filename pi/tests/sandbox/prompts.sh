#!/usr/bin/env bash
#
# prompts.sh — shared prompts for the delegation test runners.
#
# Sourced (not executed) by run-test.sh and run-docker-test.sh so the
# dispatch and workflow prompts stay byte-identical across both variants.
# Previously each runner embedded its own copy, which had already drifted
# once; this file is the single source of truth.

DISPATCH_PROMPT="Add a function word_count(text) to /tmp/team-sandbox-proj/textstats.py plus a plain-assert test_textstats.py that prints OK, using the agentic team."

# workflow mode uses --subagents-workflow-file=sandbox-run.js (no model
# involvement in launching the pipeline; the flag cannot pass args, so the
# wrapper script has them baked in). The prompt only asks the model to report
# the workflow result once its completion notification arrives.
WORKFLOW_PROMPT='A workflow was launched at startup via --subagents-workflow-file. Wait for its completion notification, then report its returned status, reviews, and openFindings verbatim.'
WORKFLOW_RUNNER="$SCRIPT_DIR/sandbox-run.js"
WORKFLOW_FLAG="--subagents-workflow-file=/sandbox-agent/workflows/sandbox-run.js"
