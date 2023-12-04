import time

from minizinc import Instance, Model, Solver

class CP_Solver():
    def __init__(self):

        self.minizing_model = """
        % Parameters
        int: numNodes; % number of nodes
        set of int: Nodes = 1..numNodes;
        array[Nodes, Nodes] of 0..1: edges; % adjacency matrix
        set of int: initialFireNodes; % nodes where the fire starts
        int: maxTurns = numNodes;  % Maximum number of turns
        int: budget; % Maximum number of firefighters per turn
        
        
        % Decision variables
        array[1..maxTurns, Nodes] of var bool: protected;  % Whether a node is protected in a given turn
        array[1..maxTurns, Nodes] of var bool: onFire;  % Whether a node is on fire in a given turn
        
        % Initial conditions
        constraint forall(n in Nodes)(onFire[1, n] = (n in initialFireNodes));
        constraint forall(n in Nodes)(protected[1, n] = false); % No nodes are protected in the first round
        
        % Constraints
        
        % Ensuring continuity of protection
        constraint forall(t in 2..maxTurns, n in Nodes)(
            protected[t-1, n] -> protected[t, n]
        );
        % A node once on fire remains on fire
        constraint forall(t in 2..maxTurns, n in Nodes)(
            onFire[t-1, n] -> onFire[t, n]
        );
        
        %Ensure a node can have only one state at a time (protected or on fire)
        constraint forall(t in 1..maxTurns, n in Nodes)(
            protected[t, n] -> not onFire[t, n] % a node cannot be protected and on fire at the same time    
        );
        
        %Defender budget constraint difference between previous and current turn cannot be more than budget
        constraint forall(t in 2..maxTurns)(
            sum(n in Nodes)(protected[t, n] - protected[t-1, n]) <= budget
        );
        
        %Fire spreads to neighbors if not protected by a firefighter in the previous turn
        constraint forall(t in 2..maxTurns, n in Nodes)(
            onFire[t, n] = (
                exists(m in Nodes)(edges[n, m] = 1 /\ onFire[t-1, m] /\ not protected[t, n])
                \/ onFire[t-1, n]
            )
        );
        
        
        
        % Objective: minimize total number of nodes on fire at the end of the simulation
        var int: numNodesOnFire = sum(n in Nodes)(onFire[maxTurns, n]);
        solve minimize numNodesOnFire;
        
        
        
        
    
        """


    def solve(self, numNodes, edges, startNode, maxTurns,budget, solver_name):
        model = Model()
        model.add_string(self.minizing_model)
        model["numNodes"] = numNodes
        model["edges"] = edges
        model["initialFireNodes"] = startNode
        model["maxTurns"] = maxTurns
        model["budget"] = budget

        solver = Solver.lookup(solver_name)
        instance = Instance(solver, model)
        start_time = time.time()
        result = instance.solve()
        end_time = time.time()

        return (result,end_time-start_time)


