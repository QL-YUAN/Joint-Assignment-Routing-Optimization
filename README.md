# Joint Assignment–Routing Solver (Gurobi-based)
This repository is linked to arXiv paper (https://arxiv.org/abs/2510.17888). 

It contains the implementation of a mixed-integer programming (MIP) model for solving a joint assignment–routing problem. It was developed for academic research and uses [Gurobi Optimizer](https://www.gurobi.com/) to solve the underlying MIP formulation.

## Description

The code solves the following problem:

- Given a set of items and placeholders,
- Assign each item to a unique placeholder,
- And find a Hamiltonian cycle through the item–placeholder pairs,
- Minimizing total travel cost.
- Can solve problem with additional constraints
[Watch the chess animation](https://github.com/QL-YUAN/Joint-Assignment-Routing-Optimization/blob/main/chess_allocation.webm)
## Requirements

- Python 3.11.13
- Gurobi Optimizer (I tested version: gurobi12.0.3)
- Gurobi Python interface (`gurobipy==12.0.3`)
- Valid Gurobi license (academic or commercial)

> Note: This project uses the [Gurobi Optimizer](https://www.gurobi.com/), which is a commercial solver. You must obtain your own license to run the solver.

- Academic users can request a free license: https://www.gurobi.com/academia/academic-program/
- Installation instructions: https://www.gurobi.com/documentation/

Install dependencies:
```
python3 -m venv gurobi-env
source gurobi-env/bin/activate
pip install -r requirements.txt
```

