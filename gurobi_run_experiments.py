# MIT License

# Copyright (c) 2025 [QL Yuan,SIT]

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import gurobipy as gp
from gurobipy import GRB
import random
import math
import matplotlib.pyplot as plt
import numpy as np
import glob
import pandas as pd

df =None

for filepath in glob.glob("datasets/experimental_n_32_ic_data.csv"):
    print("Reading:", filepath)
    df = pd.read_csv(filepath)

# Get unique experiment IDs
exp_ids = df["Experiment"].unique()

n_pairs = len(df[df["Experiment"] == exp_ids[0]][["pX", "pY"]].to_numpy())+1
print(f"Number of pairs:{n_pairs}.")

data=[]

items = list(range(n_pairs))
placeholders = list(range(n_pairs, 2 * n_pairs))
nodes = items + placeholders

# Collect pieces and targets for each experiment
for exp_id in exp_ids[5:30]:
    subset = df[df["Experiment"] == exp_id]
    pieces = subset[["pX", "pY"]].to_numpy()
    targets = subset[["tX", "tY"]].to_numpy()

    coords = {}
    for i in items[:-1]:
        coords[i] = (pieces[i,0],pieces[i,1])
    for p in placeholders[:-1]:
        coords[p] = (targets[p-n_pairs,0], targets[p-n_pairs,1])

    coords[items[-1]] = (0, 0)
    coords[placeholders[-1]] = (0, 0)


    cost = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                dx = coords[i][0] - coords[j][0]
                dy = coords[i][1] - coords[j][1]
                cost[i, j] = math.hypot(dx, dy)

    m = gp.Model("BigCycleWithLazySubtourElimination")

    x = m.addVars(cost.keys(), vtype=GRB.BINARY, name="x")
    a = m.addVars(items, placeholders, vtype=GRB.BINARY, name="a")

    m.setObjective(gp.quicksum(cost[i, j] * x[i, j] for i, j in cost), GRB.MINIMIZE)

    # Degree constraints: each node has total degree 2 (undirected)
    for node in nodes:
        m.addConstr(
            gp.quicksum(x[node, j] for j in nodes if j != node) + gp.quicksum(x[j, node] for j in nodes if j != node) == 2,
            name=f"degree_{node}")

    # Linking constraints
    for i in items:
        m.addConstr(gp.quicksum(a[i, p] for p in placeholders) == 2, name=f"item_link_{i}")

    for p in placeholders:
        m.addConstr(gp.quicksum(a[i, p] for i in items) == 2, name=f"placeholder_link_{p}")

    m.addConstr(a[items[-1], placeholders[-1]] == 1, name="force_last_link")

    # Edges only between linked pairs
    for i in nodes:
        for j in nodes:
            if i != j:
                if (i in items and j in items) or (i in placeholders and j in placeholders):
                    m.addConstr(x[i, j] == 0)
                else:
                    if i in items and j in placeholders:
                        m.addConstr(x[i, j] <= a[i, j])
                    elif i in placeholders and j in items:
                        m.addConstr(x[i, j] <= a[j, i])

    # Callback for subtour elimination
    def subtourelim(model, where):
        if where == GRB.Callback.MIPSOL:
            vals = model.cbGetSolution(x)
            # Build graph from solution edges
            selected = [(i, j) for i, j in x.keys() if vals[i, j] > 0.5]
            
            # Find all cycles in solution (subtours)
            # We'll use a simple helper function to find connected components / cycles
            
            def find_cycles(selected_edges):
                unvisited = set(nodes)
                cycles = []
                while unvisited:
                    current = unvisited.pop()
                    cycle = [current]
                    stack = [current]
                    while stack:
                        node = stack.pop()
                        neighbors = [j for i, j in selected_edges if i == node] + [i for i, j in selected_edges if j == node]
                        for neigh in neighbors:
                            if neigh in unvisited:
                                unvisited.remove(neigh)
                                stack.append(neigh)
                                cycle.append(neigh)
                    cycles.append(cycle)
                return cycles
            
            cycles = find_cycles(selected)
            
            # If more than 1 cycle found, add lazy subtour elimination constraints
            if len(cycles) > 1:
                for cycle in cycles:
                    if len(cycle) < len(nodes):
                        # subtour elimination constraint: sum of edges in subtour <= |S| - 1
                        expr = gp.quicksum(x[i, j] for i in cycle for j in cycle if i != j and (i, j) in x)
                        model.cbLazy(expr <= len(cycle) - 1)

    m.Params.OutputFlag = 1
    m.Params.TimeLimit = 3600

    m.Params.LazyConstraints = 1
    m.optimize(subtourelim)

    if m.status == GRB.OPTIMAL or m.status == GRB.TIME_LIMIT:
        print(f"Objective: {m.ObjVal:.2f}")
        print(f"Total time used: {m.Runtime:.2f} seconds")

        route_edges = [(i, j) for i, j in x.keys() if x[i, j].X > 0.5]
        assignments = [(i, p) for i in items for p in placeholders if a[i, p].X > 0.5]

        print("\nAssignments (Item -> Placeholder):")
        for i, p in assignments:
            print(f"Item {i} linked to Placeholder {p}")

        

        results = {
            "experiment_id": exp_id-1000,
            "best_cost": m.ObjVal,
            "dt": m.Runtime,
            "assignment": assignments,
            "edges": route_edges
        }
        data.append(results)
        if 0:
            # Plotting as before
            plt.figure(figsize=(10, 8))
            for i in items:
                x_, y_ = coords[i]
                plt.scatter(x_, y_, c='blue', label='Item' if i == 0 else "")
                #plt.text(x_ + 0.5, y_, f"I{i}", color='blue')

            for p in placeholders:
                x_, y_ = coords[p]
                plt.scatter(x_, y_, c='red', label='Placeholder' if p == n_pairs else "")
                #plt.text(x_ + 0.5, y_, f"P{p - n_pairs}", color='red')

            drawn = set()
            for i, j in route_edges:
                edge = tuple(sorted((i, j)))
                if edge not in drawn:
                    x0, y0 = coords[i]
                    x1, y1 = coords[j]
                    plt.plot([x0, x1], [y0, y1], 'k-', linewidth=2)
                    drawn.add(edge)

            plt.legend()
            plt.title("Optimal Path")
            plt.grid(True)
            plt.axis('equal')
            #plt.show()
            plt.savefig("xq"+str(exp_id)+"final100.png")  # saves as PNG file
            plt.close()

    else:
        print("No feasible solution found or time limit reached.")

df = pd.DataFrame(data)

#df.to_csv("experiment_"+str(n_pairs-1)+"results5_30.csv", index=False)
#print("Data written to '*.csv'")

