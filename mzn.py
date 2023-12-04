import sys

import firefighter_cp
import firefighter_ilp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
import seaborn as sns
import tqdm
import concurrent.futures
def generate_variations(num_variations,min_nodes, max_nodes):
    variations = []

    num_nodes = np.linspace(min_nodes, max_nodes, num_variations, dtype=int)
    for num in num_nodes:
        #generate random edges
        edges = np.random.randint(2, size=(num, num))
        #make sure edges are symmetric
        edges = np.maximum(edges, edges.transpose())
        #make sure there are no self loops
        np.fill_diagonal(edges, 0)

        for x in range(num//2):
            initial_fire_nodes = random.sample(range(1, num), x)
            for y in range(num//2):
                budget = random.randint(1, num)
                variations.append((num, edges, initial_fire_nodes, budget))
    return variations


def main():
    num_variations = 2
    min_nodes = 5
    max_nodes = 8

    variations = generate_variations(num_variations, min_nodes, max_nodes)
    results = []

    # Using ThreadPoolExecutor to run tests in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for variation in variations:
            for _ in range(2):  # Run each variation 2 times
                futures.append(executor.submit(run_test, variation))

        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            results.append(future.result()[0])
            results.append(future.result()[1])

    # Convert results to DataFrame and plot
    df = pd.DataFrame(results, columns=['Solver', 'Variation', 'Time'])
    #save results to csv by time
    file_name = "results_" + str(min_nodes) + "_" + str(max_nodes) + "_" + str(num_variations) + ".csv"
    df.to_csv(file_name)
    df['Number of Nodes'] = df['Variation'].apply(lambda x: x[0])

    sns.scatterplot(data=df, x='Number of Nodes', y='Time', hue='Solver')
    plt.title('Time Comparison between CP and ILP Solvers')
    plt.ylabel('Time (s)')
    plt.show()

    avg_times = df.groupby('Solver')['Time'].mean()
    avg_times.plot(kind='bar')
    plt.title('Average Time Comparison between CP and ILP Solvers')
    plt.ylabel('Time (s)')
    plt.show()

def run_test(variation):
    numNodes, edges, initialFireNodes, budget = variation

    # Run CP Solver
    cp_solver = firefighter_cp.CP_Solver()
    cp_result = cp_solver.solve(numNodes, edges, initialFireNodes, numNodes, budget, "gecode")
    cp_time = ["CP", variation, cp_result[1]]

    # Run ILP Solver
    ilp_solver = firefighter_ilp.ILP_solver(numNodes, edges, initialFireNodes, numNodes, budget)
    ilp_result = ilp_solver.solve()
    ilp_time = ["ILP", variation, ilp_result["time"]]

    return [cp_time, ilp_time]

if __name__ == "__main__":
    main()

