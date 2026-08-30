"""Skill wiring checks (no GPU): every skill has a valid name+description, and each
opencode agent's allowed skills actually exist on disk."""

from __future__ import annotations

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
AGENTS = os.path.join(ROOT, ".opencode", "agent")


def skill_names():
    names = set()
    for d in os.listdir(SKILLS):
        p = os.path.join(SKILLS, d, "SKILL.md")
        if os.path.isfile(p):
            with open(p) as fh:
                txt = fh.read()
            m = re.search(r"^name:\s*(\S+)", txt, re.M)
            desc = re.search(r"^description:\s*(.+)", txt, re.M)
            names.add((d, m.group(1) if m else None, bool(desc)))
    return names


def agent_allowed_skills(path):
    with open(path) as fh:
        txt = fh.read()
    m = re.search(r"skill:\n((?:\s+.+\n)+)", txt)
    if not m:
        return []
    block = m.group(1)
    return re.findall(r"^\s{4}([a-z0-9][a-z0-9-]*):\s*allow", block, re.M)


class TestSkills(unittest.TestCase):
    def test_each_skill_has_name_and_description(self):
        names = skill_names()
        self.assertGreater(len(names), 30)
        for d, name, has_desc in names:
            self.assertEqual(d, name, f"folder {d} != skill name {name}")
            self.assertTrue(has_desc, f"skill {d} missing description")

    def test_agent_skills_exist(self):
        valid = {n for _, n, _ in skill_names()}
        for fn in os.listdir(AGENTS):
            if not fn.endswith(".md"):
                continue
            for s in agent_allowed_skills(os.path.join(AGENTS, fn)):
                self.assertIn(s, valid, f"{fn} allows unknown skill '{s}'")

    def test_every_agent_mentions_consult_skills_first(self):
        for fn in os.listdir(AGENTS):
            if not fn.endswith(".md"):
                continue
            with open(os.path.join(AGENTS, fn)) as fh:
                self.assertIn("consult", fh.read().lower(),
                              f"{fn} does not instruct consulting skills first")


if __name__ == "__main__":
    unittest.main()
