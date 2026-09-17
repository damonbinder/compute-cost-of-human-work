# GNoME: stability screening of a supplied crystal

## sci-crystal-stability-gnome

Primary sources: [original GNoME paper](https://www.nature.com/articles/s41586-023-06735-9) and [authors' implementation/data repository](https://github.com/google-deepmind/materials_discovery), freshly cloned at commit `29cf9852b7e11327fb3eccff6620e600add65169`. Define the work as predicting formation energy and judging stability relative to supplied competing-phase energies for one supplied candidate crystal. This is one screening decision, not discovering a material, synthesizing it or computing an entire phase diagram.

A concrete representative input is the released Ta10AlGaSi4 primitive cell: 16 atoms (10 Ta, 1 Al, 1 Ga, 4 Si), volume 262.424 Å³. The complete original CIF is retained as `agent-work/sources/robotics-science/Ta10AlGaSi4.CIF`. It was extracted by byte range from the authors' public `gnome_data/by_reduced_formula.zip`; archive metadata is retained in the range directory records. The archive is the expanded December 2024 release. This is an illustrative application of the 2023 model recipe to an actual released structure, not a claim of a separately measured 2023 test prediction for this individual CIF.

## Neural operation count

Paper Methods specify 256-dimensional nodes/edges, three message-passing iterations by default, a 4 Å edge cutoff, ten independently trained ensemble members and twenty volume augmentations from 80% to 120%. The repository's `model/crystal.py` uses 94-element input vectors, 30 Gaussian edge features, and explicit node/edge/global MLP updates. The node update concatenates node, incoming edge, outgoing edge and global features; the edge update concatenates edge, sender, receiver and global features. The global update combines pooled nodes, pooled edges and the old global. Three graph passes consist of two ordinary updates followed by the readout pass.

The exact trained MLP width tuple is not in the released checkpoint configuration. Assume two dense layers with widths (256,256), consistent with the paper's shallow MLP description and fixed embedding width. This assumption is explicit, not a disclosed parameter count. A single dense projection would reduce most update work by about 20%; an extra hidden layer would increase it by about 20%.

`count_gnome.py` constructs the triclinic lattice from the CIF, enumerates periodic neighbours and computes edge counts separately at twenty linearly spaced volume factors; isotropic lattice lengths scale by the cube root of volume. The periodic-image enumeration was checked by extending its range. For E edges and N=16 atoms, D=256, one network's matrix work is:

- Input projections: 2×(N×94×D + E×30×D + D).
- Node and edge updates over three passes: 3×(E+N)×2×(4D²+D²).
- Two global updates and scalar readout: 2×2×(3D²+D²) + 2×(3D²+D).

Sum over all twenty graph sizes and multiply by ten models. Exact edge counts and arithmetic are in `research/gnome-operations.json`. Graph construction, pooling, Gaussian features and activations are small omitted terms. The estimate assumes neighbour graphs are rebuilt for each augmentation; reusing the unscaled graph would modestly alter the total. These are structural screening models, not the separate NequIP molecular-dynamics potential. No DFT verification, search, training or relaxation trajectories are counted in AI-model FLOPs.

## Human active-work estimate and quality

The comparator is a computational materials scientist using conventional DFT/VASP and phase-diagram tools, with the candidate CIF and compatible competing-phase energy database already supplied. Chemical intuition alone cannot be expected to reproduce an approximately 11 meV/atom energy predictor for a quaternary heavy-metal intermetallic. The original paper itself uses conventional DFT as the reference and details standard VASP/pymatgen workflows, including geometric relaxation and a static energy calculation.

Estimate **20 minutes of active human effort** for one prepared, routine case: inspect the 16-atom cell, occupations and composition (4 min); select consistent potentials, electronic settings and prepare/check a standard automated calculation (8 min); inspect convergence, geometry and energy outputs (5 min); compare compatible energies and report stable/not-stable with an appropriate near-hull caveat (3 min). This assumes installed workflows and available computational resources. Unattended DFT execution and queueing are excluded from human active time. Nonconvergence, magnetic alternatives or commissioning a new workflow could increase effort substantially; 10–60 minutes is a plausible routine-case sensitivity, not a measured interval. Heavy Ta and Ga potential consistency are relevant checks for this specific input, rather than assigning a generic reading time.

Classify the neural screen **below** this DFT-assisted expert reference in numerical fidelity. The paper's final structural model error is approximately 11 meV/atom against DFT, with greater than 80% hit rate among selected stable predictions; DFT is the verification target. These aggregate results do not establish an individual Ta10AlGaSi4 error or a measured human success rate. The human estimate targets the reference screening decision with conventional numerical tools; it is not a claim that an unaided scientist can predict these energies mentally. This is therefore not a parity-compute point.

## Model release provenance

The repository publishes architecture code and structure data, but no exact final ten-member screening ensemble weight-release date was established. Leave the release date blank; the paper date and structure archive update date are not equivalent to a release of the evaluated ensemble weights.
