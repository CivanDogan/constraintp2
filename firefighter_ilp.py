import pulp
import time


class ILP_solver():
    def __init__(self, numNodes, edges, startNode, maxTurns,budget):
        self.numNodes = numNodes
        self.edges = self.adjecency_matrix_to_edges(edges)
        self.startNode = startNode
        self.maxTurns = maxTurns
        self.budget = budget
        self.solve()

    def adjecency_matrix_to_edges(self, adjecency_matrix):
        edges = []
        for i in range(len(adjecency_matrix)):
            for j in range(len(adjecency_matrix)):
                if adjecency_matrix[i][j] == 1:
                    edges.append((i, j))
        return edges
    def solve(self):
        V = range(self.numNodes)  # Set of vertices
        E = self.edges
        T = self.maxTurns
        f = self.budget  # Budget of defenders per turn
        start_fire = self.startNode

        # Initialize the problem
        problem = pulp.LpProblem("Firefighting", pulp.LpMinimize)

        # Decision variables
        b = pulp.LpVariable.dicts("Burned", [(x, t) for x in V for t in range(T + 1)], cat='Binary')
        d = pulp.LpVariable.dicts("Defended", [(x, t) for x in V for t in range(T + 1)], cat='Binary')

        # Initial conditions
        for x in V:
            problem += b[x, 0] == (1 if x in start_fire else 0), f"Initial Condition Burning {x}"
            problem += d[x, 0] == 0, f"Initial Condition Defended {x}"

        # Constraints
        for x in V:
            for t in range(1, T + 1):
                problem += b[x, t] >= b[x, t - 1], f"Continuity of Burning {x} at {t}"
                problem += d[x, t] >= d[x, t - 1], f"Continuity of Defense {x} at {t}"
                problem += b[x, t] + d[x, t] <= 1, f"No Overlap {x} at {t}"

                # Fire spreads to neighbors
                for y in V:
                    if (x, y) in E or (y, x) in E:
                        problem += b[x, t] + d[x, t] >= b[y, t - 1], f"Fire Spreads {x} to {y} at {t}"

        # Defender budget constraint
        for t in range(1, T + 1):
            # can be defender count in t can be different from t-1 but not more than f
            problem += pulp.lpSum(d[x, t] - d[x, t - 1] for x in V) <= f, f"Defender Budget at {t}"

        # Objective function
        problem += pulp.lpSum(b[x, T] for x in V), "Minimize Burned Vertices"

        start_time = time.time()
        # Solve the problem without logging
        problem.solve(pulp.PULP_CBC_CMD(msg=0))
        end_time = time.time()
        run_time = end_time - start_time

        result = {"time" : run_time,
                  "protected" : [x for x in V if pulp.value(d[x, T]) == 1],
                  "on_fire" : [x for x in V if pulp.value(b[x, T]) == 1],}

        return result



        # Output the results
        for t in range(T + 1):
            print(f"Turn {t}:")
            print("Protected: ", [x for x in V if pulp.value(d[x, t]) == 1])
            print("On Fire: ", [x for x in V if pulp.value(b[x, t]) == 1])


