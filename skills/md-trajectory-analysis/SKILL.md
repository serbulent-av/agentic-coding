---
name: md-trajectory-analysis
description: Use when analyzing molecular dynamics trajectories — RMSD/RMSF, clustering, contacts, hydrogen bonds, or convergence (MDAnalysis or GROMACS tools).
---

# MD Trajectory Analysis

## Purpose
Turn a trajectory into defensible numbers — aligned correctly, separated from equilibration, and reported with convergence and error rather than a single cherry-picked frame.

## When to use
- Measuring RMSD, RMSF, distances, contacts, hydrogen bonds, SASA, or dihedrals from a trajectory.
- Clustering conformations or assessing whether sampling has converged.
- Reviewing someone's analysis pipeline with MDAnalysis or GROMACS tools.

When NOT to use: building or running the simulation itself (use molecular-dynamics-simulation) or computing free energies (use enhanced-sampling-free-energy).

## Method
1. Fix periodicity and align first. Unwrap PBC, make the molecule whole, then remove rotation and translation by fitting to a reference before any geometric measurement.
2. Separate equilibration from production. Plot RMSD versus time, decide where the system stabilizes, and analyze only the production portion.
3. Quantify flexibility and the target observable. Compute per-residue RMSF, then the specific quantity the question needs — distances, contacts, hydrogen bonds, SASA, dihedrals, or conformational clustering.
4. Assess convergence and error. Use block averaging and autocorrelation for statistical error, and compare across independent replicas rather than trusting one run.
5. Visualize and sanity-check. Look at representative structures to confirm the numbers match what the molecule is actually doing.
6. Document tools and selections. Record tool versions and the exact atom selections so the analysis is reproducible.

## Red flags
- Computing RMSD without PBC correction or structural fitting.
- Analyzing the equilibration phase as if it were production.
- Reporting an average with no error bar or convergence estimate.
- Drawing conclusions from a single replica.
- Cherry-picking one frame that supports the desired story.
- Undocumented atom selections, so the analysis can't be reproduced.

## Checklist
- [ ] PBC corrected and trajectory fit to a reference before measuring.
- [ ] Equilibration identified and excluded from production analysis.
- [ ] RMSF and the question-specific observable computed.
- [ ] Convergence and statistical error estimated (block averaging, autocorrelation).
- [ ] Independent replicas compared, not a single run.
- [ ] Results sanity-checked against structure; tool versions and selections recorded.
