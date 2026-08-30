---
name: enhanced-sampling-free-energy
description: Use when computing binding or conformational free energies, or accelerating sampling beyond plain MD (FEP, TI, umbrella sampling, metadynamics, GaMD, MM/PBSA).
---

# Enhanced Sampling and Free Energy

## Purpose
Compute free energies and sample rare events with a method matched to the question, then prove the number converged instead of trusting a point estimate.

## When to use
- Estimating relative or absolute binding free energies of ligands.
- Mapping a conformational free-energy landscape along a reaction coordinate.
- Accelerating exploration past barriers that plain MD cannot cross in feasible time.

When NOT to use: a plain unbiased equilibrium simulation with no free-energy question (use molecular-dynamics-simulation), or routine trajectory observables (use md-trajectory-analysis).

## Method
1. Match the method to the question. Alchemical FEP/TI for relative or absolute binding; umbrella sampling or metadynamics when a good reaction coordinate or CV is known; GaMD for unbiased boosted exploration without a predefined CV; MM/PBSA only for fast, approximate ranking.
2. Design the coordinate or schedule. Choose a collective variable that captures the slow degree of freedom, or a lambda schedule with enough windows that adjacent states have adequate phase-space overlap.
3. Equilibrate every window or state. Each lambda window or umbrella restraint needs its own equilibration before data is collected, just like a production run.
4. Check convergence and overlap. Estimate with BAR/MBAR, inspect phase-space overlap between neighbors, confirm the free-energy estimate is stable over time and that forward/backward or independent replicas agree.
5. Report statistical error. Quote an uncertainty from bootstrap or block analysis — never a bare number.
6. Validate against a reference. Compare to experiment or a known calculation whenever one exists, and treat MM/PBSA magnitudes as relative rankings, not absolute affinities.

## Red flags
- Too few windows or poor overlap between adjacent lambda/umbrella states.
- A collective variable that misses the slow degree of freedom being studied.
- Treating MM/PBSA absolute numbers as quantitative binding free energies.
- A free energy reported with no error bar and no convergence check.
- Insufficient sampling per window, so histograms barely overlap.
- Forward and backward (or replica) estimates that disagree, ignored.

## Checklist
- [ ] Method chosen to fit the specific free-energy or sampling question.
- [ ] CV or lambda schedule gives adequate overlap across windows.
- [ ] Every window/state equilibrated before data collection.
- [ ] Convergence and overlap checked (BAR/MBAR, stability over time).
- [ ] Statistical error reported from bootstrap or block analysis.
- [ ] Result validated against experiment or a known reference where possible.
