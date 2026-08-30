---
name: molecular-dynamics-simulation
description: Use when setting up, running, or reviewing a classical molecular dynamics simulation (GROMACS, NAMD, OpenMM, or AMBER).
---

# Molecular Dynamics Simulation

## Purpose
Set up and run a classical MD simulation that is physically sound, stable, and reproducible — so the trajectory means something before anyone analyzes it.

## When to use
- Building, solvating, and parameterizing a biomolecular system for MD.
- Designing an equilibration and production protocol for GROMACS, NAMD, OpenMM, or AMBER.
- Reviewing someone else's simulation setup for physical validity.

When NOT to use: post-hoc trajectory analysis (use md-trajectory-analysis) or free-energy/enhanced-sampling protocols (use enhanced-sampling-free-energy).

## Method
1. Choose a validated force field and matching water model. Pick a force field proven for the system (e.g. AMBER ff19SB or CHARMM36m for protein, a matched lipid set for membranes) and the water model it was parameterized with (TIP3P, OPC, etc.); never mix incompatible parameter sets.
2. Build, solvate, and neutralize. Place the solute in a box large enough that it never sees its periodic image, solvate, then add ions to neutralize total charge and reach the target salt concentration.
3. Energy-minimize. Relax steric clashes and bad contacts before adding heat, or the integrator will blow up.
4. Equilibrate in stages with restraints. Heat and equilibrate under NVT, then NPT, with position restraints on the solute, and release them gradually so solvent and box relax around a stable structure.
5. Choose a sound integrator and timestep. Use 2 fs with constraints on bonds to hydrogen (LINCS/SHAKE/SETTLE), or 4 fs with hydrogen-mass repartitioning; pair a proper thermostat and barostat, PME electrostatics, periodic boundary conditions, and a justified cutoff.
6. Run production as independent replicas. Launch several runs with different seeds, not one long trajectory, so results have statistical weight.
7. Record everything. Save force field, water model, inputs, seeds, and exact engine version so the run can be reproduced.

## Red flags
- Production started before equilibration converges (energy, temperature, density, box still drifting).
- Force field and water model mismatched or never validated for this kind of system.
- Box too small — the solute interacts with its own periodic image.
- A single trajectory treated as a conclusive result.
- Timestep, thermostat/barostat, or random seed unreported.
- Energy or temperature drift ignored instead of diagnosed.

## Checklist
- [ ] Force field and matching water model chosen and justified for the system.
- [ ] Box neutralized to target salt; solute clears its periodic image.
- [ ] Energy minimization run before heating.
- [ ] NVT then NPT equilibration with restraints; convergence confirmed.
- [ ] Integrator, timestep, constraints, thermostat/barostat, PME, and cutoff all set deliberately.
- [ ] Multiple independent replicas with distinct seeds.
- [ ] Force field, inputs, seeds, and engine version recorded for reproducibility.
